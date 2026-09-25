"""Normalize ministry CSV exports and count dispositions, not law rows."""
import csv
import re
from datetime import date

CITIES = set('臺北市 新北市 桃園市 臺中市 臺南市 高雄市 基隆市 新竹市 嘉義市 新竹縣 苗栗縣 彰化縣 南投縣 雲林縣 嘉義縣 屏東縣 宜蘭縣 花蓮縣 臺東縣 澎湖縣 金門縣 連江縣'.split())


def parse_date(value):
    try:
        year, month, day = map(int, re.split(r'[/.-]', value.strip()))
        return date(year + 1911 if year < 1911 else year, month, day)
    except (ValueError, TypeError):
        return None


def articles(value):
    result = set()
    for part in re.split(r'[;；]', value):
        match = re.search(r'第\s*(\d+)\s*(?:[-之]\s*(\d+))?\s*條(?:之\s*(\d+))?', part)
        if match:
            suffix = match[2] or match[3]
            result.add('第' + match[1] + (('-' + suffix) if suffix else '') + '條')
        elif part.strip():
            result.add('其他／未辨識條款')
    return sorted(result) or ['未提供條款']


def load_cases(path):
    groups = {}
    skipped = raw_count = 0
    with open(path, encoding='utf-8-sig', newline='') as file:
        for row in csv.reader(file):
            if not row or not any(v.strip() for v in row):
                continue
            if any('公告日期' in v for v in row[:4]) or len(row) == 1:
                continue
            # Exports may include serial numbers; current data omits them.
            if row[0].strip().isdigit() and len(row) >= 10:
                row = row[1:]
            if len(row) < 9:
                skipped += 1
                continue
            row = [v.strip() for v in row]
            raw_count += 1
            authority, announced, company, disposed, document, law, description, fine, note = row[:9]
            authority = authority.replace('台', '臺')
            key = (authority, document) if document else (authority, *row[1:9])
            money = fine.replace(',', '').replace('，', '')
            amount = int(money) if money.isdigit() else None
            if key not in groups:
                groups[key] = {'單位': authority, '事業單位': company,
                               '處分字號': document, '處分日期': parse_date(disposed),
                               '公告日期': parse_date(announced), '條款': set(),
                               '違反法規': set(), '法條敘述': set(), '備註': set(),
                               '_amounts': set(), '_dates': set(), '_companies': set()}
            case = groups[key]
            case['條款'].update(articles(law))
            for field, value in [('違反法規', law), ('法條敘述', description), ('備註', note)]:
                case[field].add(value)
            case['_companies'].add(company)
            if amount is not None:
                case['_amounts'].add(amount)
            if parse_date(disposed):
                case['_dates'].add(parse_date(disposed))
            announcement = parse_date(announced)
            if announcement and (not case['公告日期'] or announcement > case['公告日期']):
                case['公告日期'] = announcement
    result = []
    for case in groups.values():
        amounts = case.pop('_amounts')
        dates = case.pop('_dates')
        companies = case.pop('_companies')
        case['罰鍰金額'] = next(iter(amounts)) if len(amounts) == 1 else None
        case['金額狀態'] = '金額不一致，未計入' if len(amounts) > 1 else ('已提供' if amounts else '未提供')
        case['處分日期'] = next(iter(dates)) if len(dates) == 1 else None
        case['處分年度'] = case['處分日期'].year if case['處分日期'] else None
        case['事業單位'] = '；'.join(sorted(companies))
        case['條款'] = sorted(case['條款'])
        for field in ('違反法規', '法條敘述', '備註'):
            case[field] = '；'.join(sorted(v for v in case[field] if v))
        result.append(case)
    return result, {'原始列數': raw_count, '合併列數': raw_count - len(result), '略過列數': skipped}
