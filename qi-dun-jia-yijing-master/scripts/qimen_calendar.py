#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENDOR_DIR = SKILL_DIR / "vendor"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

from lunar_python import Solar  # type: ignore


TERM_ALIASES = {
    "穀雨": "谷雨",
    "處暑": "处暑",
    "驚蟄": "惊蛰",
}

TERM_TO_SEASON = {
    "立春": "spring",
    "雨水": "spring",
    "惊蛰": "spring",
    "春分": "spring",
    "清明": "spring",
    "谷雨": "spring",
    "立夏": "summer",
    "小满": "summer",
    "芒种": "summer",
    "夏至": "summer",
    "小暑": "summer",
    "大暑": "summer",
    "立秋": "autumn",
    "处暑": "autumn",
    "白露": "autumn",
    "秋分": "autumn",
    "寒露": "autumn",
    "霜降": "autumn",
    "立冬": "winter",
    "小雪": "winter",
    "大雪": "winter",
    "冬至": "winter",
    "小寒": "winter",
    "大寒": "winter",
}


@dataclass
class CalendarSnapshot:
    solar_iso: str
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str
    current_term: str
    current_jie: str
    current_qi: str
    xun: str
    xun_kong: str
    season: str
    jieqi_table: dict[str, str]


def normalize_term_name(name: str | None) -> str:
    if not name:
        return ""
    result = str(name)
    for old, new in TERM_ALIASES.items():
        result = result.replace(old, new)
    return result


def get_calendar_snapshot(year: int, month: int, day: int, hour: int, minute: int) -> CalendarSnapshot:
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    jieqi_table = {
        normalize_term_name(name): value.toYmdHms()
        for name, value in lunar.getJieQiTable().items()
    }
    current_term = normalize_term_name(lunar.getPrevJieQi() or lunar.getJieQi() or lunar.getPrevJie() or "")
    if not current_term:
        raise ValueError("Unable to determine current solar term")
    return CalendarSnapshot(
        solar_iso=solar.toYmdHms(),
        year_gz=lunar.getYearInGanZhiExact(),
        month_gz=lunar.getMonthInGanZhiExact(),
        day_gz=lunar.getDayInGanZhiExact(),
        hour_gz=lunar.getTimeInGanZhi(),
        current_term=current_term,
        current_jie=normalize_term_name(lunar.getPrevJie() or ""),
        current_qi=normalize_term_name(lunar.getPrevQi() or ""),
        xun=lunar.getDayXunExact(),
        xun_kong=lunar.getDayXunKongExact(),
        season=TERM_TO_SEASON.get(current_term, "transitional"),
        jieqi_table=jieqi_table,
    )
