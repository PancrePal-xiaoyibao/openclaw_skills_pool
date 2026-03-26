#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from qimen_calendar import get_calendar_snapshot

TIAN_GAN = "甲乙丙丁戊己庚辛壬癸"
DI_ZHI = "子丑寅卯辰巳午未申酉戌亥"
CNUMBER = list("一二三四五六七八九")
EIGHT_GUA = list("坎坤震巽中乾兑艮离")
CLOCKWISE_EIGHTGUA = list("坎艮震巽离坤兑乾")
STAR_TO_FULL = {
    "蓬": "天蓬",
    "任": "天任",
    "冲": "天冲",
    "辅": "天辅",
    "英": "天英",
    "禽": "天禽",
    "柱": "天柱",
    "心": "天心",
    "芮": "天芮",
}
GOD_TO_FULL = {
    "符": "值符",
    "蛇": "腾蛇",
    "阴": "太阴",
    "合": "六合",
    "勾": "勾陈",
    "雀": "朱雀",
    "地": "九地",
    "天": "九天",
    "虎": "白虎",
    "玄": "玄武",
}
PALACE_ELEMENT = {
    "坎": "water",
    "坤": "earth",
    "震": "wood",
    "巽": "wood",
    "中": "earth",
    "乾": "metal",
    "兑": "metal",
    "艮": "earth",
    "离": "fire",
}
BRANCH_TO_PALACE = {
    "子": "坎",
    "丑": "艮",
    "寅": "艮",
    "卯": "震",
    "辰": "巽",
    "巳": "巽",
    "午": "离",
    "未": "坤",
    "申": "坤",
    "酉": "兑",
    "戌": "乾",
    "亥": "乾",
}
HORSE_BRANCH_MAP = {
    "申子辰": "寅",
    "寅午戌": "申",
    "巳酉丑": "亥",
    "亥卯未": "巳",
}
JIEQI_CODE = {
    ("冬至", "惊蛰"): "一七四",
    ("小寒",): "二八五",
    ("大寒", "春分"): "三九六",
    ("立春",): "八五二",
    ("雨水",): "九六三",
    ("清明", "立夏"): "四一七",
    ("谷雨", "小满"): "五二八",
    ("芒种",): "六三九",
    ("夏至", "白露"): "九三六",
    ("小暑",): "八二五",
    ("大暑", "秋分"): "七一四",
    ("立秋",): "二五八",
    ("处暑",): "一四七",
    ("霜降", "小雪"): "五八二",
    ("寒露", "立冬"): "六九三",
    ("大雪",): "四七一",
}
STAR_RING = list("蓬任冲辅英禽柱心")
DOOR_RING = list("休死伤杜中开惊生景")
YANG_GODS = list("符蛇阴合勾雀地天")
YIN_GODS = list("符蛇阴合虎玄地天")
EARTH_STEMS_YANG = list("戊己庚辛壬癸丁丙乙")
EARTH_STEMS_YIN = list("戊乙丙丁癸壬辛庚己")
VALUE_STARS = list("蓬芮冲辅禽心柱任英")


@dataclass
class AutoPanResult:
    payload: dict[str, Any]
    auto_meta: dict[str, Any]


def multi_key_dict_get(mapping: dict[tuple[str, ...], str], key: str) -> str | None:
    for keys, value in mapping.items():
        if key in keys:
            return value
    return None


def new_list(items: list[str], anchor: str) -> list[str]:
    index = items.index(anchor)
    return items[index:] + items[:index]


def new_list_r(items: list[str], anchor: str) -> list[str]:
    index = items.index(anchor)
    result = []
    for _ in range(len(items)):
        result.append(items[index % len(items)])
        index -= 1
    return result


def jiazi() -> list[str]:
    return [f"{TIAN_GAN[i % len(TIAN_GAN)]}{DI_ZHI[i % len(DI_ZHI)]}" for i in range(60)]


def liujiashun_dict() -> dict[tuple[str, ...], str]:
    base = jiazi()[0::10]
    return {tuple(new_list(jiazi(), item)[0:10]): item for item in base}


def findyuen_dict() -> dict[tuple[str, ...], str]:
    base = jiazi()[0::5]
    labels = ["上元", "中元", "下元"] * 4
    return {tuple(new_list(jiazi(), item)[0:5]): labels[idx] for idx, item in enumerate(base)}


def find_yuan(day_gz: str) -> str:
    for keys, value in findyuen_dict().items():
        if day_gz in keys:
            return value
    raise ValueError(f"Unable to derive yuan from day gz: {day_gz}")


def shun(day_gz: str) -> str:
    d_value1 = dict(zip(DI_ZHI, range(1, 13))).get(day_gz[1])
    d_value2 = dict(zip(TIAN_GAN, range(1, 11))).get(day_gz[0])
    shun_value = d_value1 - d_value2
    if shun_value < 0:
        shun_value += 12
    return {0: "戊", 10: "己", 8: "庚", 6: "辛", 4: "壬", 2: "癸"}[shun_value]


def current_term_code(term: str) -> str:
    value = multi_key_dict_get(JIEQI_CODE, term)
    if not value:
        raise ValueError(f"Unsupported solar term: {term}")
    return value


def yinyang_dun(term: str) -> str:
    winter_cycle = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]
    return "阳遁" if term in winter_cycle else "阴遁"


def qimen_ju_name_chaibu(term: str, day_gz: str) -> dict[str, Any]:
    code = current_term_code(term)
    yuan = find_yuan(day_gz)
    ju_cnum = code[{"上元": 0, "中元": 1, "下元": 2}[yuan]]
    ju = CNUMBER.index(ju_cnum) + 1
    return {"method": "chaibu", "dun": yinyang_dun(term), "ju": ju, "ju_cnum": ju_cnum, "yuan": yuan, "term": term}


def qimen_ju_name_zhirun(term: str, day_gz: str) -> dict[str, Any]:
    code = current_term_code(term)
    yuan = find_yuan(day_gz)
    ju_cnum = code[{"上元": 0, "中元": 1, "下元": 2}[yuan]]
    ju = CNUMBER.index(ju_cnum) + 1
    return {"method": "zhirun", "dun": yinyang_dun(term), "ju": ju, "ju_cnum": ju_cnum, "yuan": yuan, "term": term}


def hourganghzi_zhifu(hour_gz: str) -> str:
    base = jiazi()
    segments = [new_list(base, item)[0:10] for item in base[0::10]]
    values = [base[0::10][idx] + TIAN_GAN[4:10][idx] for idx in range(6)]
    for keys, value in zip(segments, values):
        if hour_gz in keys:
            return value
    raise ValueError(f"Unable to derive hour zhifu from hour gz: {hour_gz}")


def qimen_context(year: int, month: int, day: int, hour: int, minute: int, method: str) -> dict[str, Any]:
    cal = get_calendar_snapshot(year, month, day, hour, minute)
    ju_meta = qimen_ju_name_chaibu(cal.current_term, cal.day_gz) if method == "chaibu" else qimen_ju_name_zhirun(cal.current_term, cal.day_gz)
    return {
        "calendar": cal,
        "ju_meta": ju_meta,
        "year_gz": cal.year_gz,
        "month_gz": cal.month_gz,
        "day_gz": cal.day_gz,
        "hour_gz": cal.hour_gz,
        "xunkong": cal.xun_kong,
        "term": cal.current_term,
        "season": cal.season,
        "xunshou_stem": shun(cal.day_gz),
        "hour_zhifu": hourganghzi_zhifu(cal.hour_gz),
    }


def earth_plate(ju_meta: dict[str, Any]) -> dict[str, str]:
    stems = EARTH_STEMS_YANG if ju_meta["dun"] == "阳遁" else EARTH_STEMS_YIN
    palaces = [dict(zip(CNUMBER, EIGHT_GUA))[item] for item in new_list(CNUMBER, ju_meta["ju_cnum"])]
    return dict(zip(palaces, stems))


def earth_plate_reverse(earth: dict[str, str]) -> dict[str, str]:
    return {stem: palace for palace, stem in earth.items()}


def zhifu_pai(ju_meta: dict[str, Any]) -> dict[str, str]:
    yinyang = ju_meta["dun"][0]
    kook = ju_meta["ju_cnum"]
    pai = {
        "阳": {
            "一": "九八七一二三四五六",
            "二": "一九八二三四五六七",
            "三": "二一九三四五六七八",
            "四": "三二一四五六七八九",
            "五": "四三二五六七八九一",
            "六": "五四三六七八九一二",
            "七": "六五四七八九一二三",
            "八": "七六五八九一二三四",
            "九": "八七六九一二三四五"
        },
        "阴": {
            "九": "一二三九八七六五四",
            "八": "九一二八七六五四三",
            "七": "八九一七六五四三二",
            "六": "七八九六五四三二一",
            "五": "六七八五四三二一九",
            "四": "五六七四三二一九八",
            "三": "四五六三二一九八七",
            "二": "三四五二一九八七六",
            "一": "二三四一九八七六五"
        }
    }[yinyang][kook]
    order = new_list_r(CNUMBER, kook)[0:6] if yinyang == "阴" else new_list(CNUMBER, kook)[0:6]
    values = [item + pai for item in order]
    return dict(zip(jiazi()[0::10], values))


def zhishi_pai(ju_meta: dict[str, Any]) -> dict[str, str]:
    yinyang = ju_meta["dun"][0]
    kook = ju_meta["ju_cnum"]
    order = new_list_r(CNUMBER, kook)[0:6] if yinyang == "阴" else new_list(CNUMBER, kook)[0:6]
    ring = "".join(order) * 3
    values = [item + ring[ring.index(item) + 1:][0:11] for item in order]
    return dict(zip(jiazi()[0::10], values))


def zhifu_n_zhishi(ctx: dict[str, Any], ju_meta: dict[str, Any]) -> dict[str, Any]:
    hour_gz = ctx["hour_gz"]
    hour_gan = hour_gz[0]
    chour = None
    for keys, value in liujiashun_dict().items():
        if hour_gz in keys:
            chour = value
            break
    if not chour:
        raise ValueError(f"Unable to derive xunshou from hour gz: {hour_gz}")
    zspai = zhishi_pai(ju_meta)
    zfpai = zhifu_pai(ju_meta)
    gongs_code = dict(zip(CNUMBER, EIGHT_GUA))
    h_index = dict(zip(TIAN_GAN, range(0, 10))).get(hour_gan)
    a = [dict(zip(CNUMBER, DOOR_RING)).get(item[0]) for item in zspai.values()]
    b = [dict(zip(CNUMBER, VALUE_STARS)).get(item[0]) for item in zfpai.values()]
    c = [gongs_code.get(item[h_index]) for item in zfpai.values()]
    d = [gongs_code.get(item[h_index]) for item in zspai.values()]
    door = dict(zip(zspai.keys(), a)).get(chour)
    if door == "中":
        door = "死"
    xunshou_stem = {"甲子": "戊", "甲戌": "己", "甲申": "庚", "甲午": "辛", "甲辰": "壬", "甲寅": "癸"}[chour]
    return {
        "值符天干": [chour, xunshou_stem],
        "值符星宫": [dict(zip(zfpai.keys(), b)).get(chour), dict(zip(zfpai.keys(), c)).get(chour)],
        "值使门宫": [door, dict(zip(zspai.keys(), d)).get(chour)]
    }


def pan_door(ju_meta: dict[str, Any], duty: dict[str, Any]) -> dict[str, str]:
    yinyang = ju_meta["dun"][0]
    rotate = CLOCKWISE_EIGHTGUA if yinyang == "阳" else list(reversed(CLOCKWISE_EIGHTGUA))
    starting_door = duty["值使门宫"][0]
    starting_gong = duty["值使门宫"][1]
    gong_reorder = new_list(rotate, "坤") if starting_gong == "中" else new_list(rotate, starting_gong)
    ring = [item for item in DOOR_RING if item != "中"]
    reordered = new_list(ring, starting_door) if yinyang == "阳" else new_list(list(reversed(ring)), starting_door)
    return dict(zip(gong_reorder, [f"{item}门" for item in reordered]))


def pan_star(ju_meta: dict[str, Any], duty: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    yinyang = ju_meta["dun"][0]
    rotate = CLOCKWISE_EIGHTGUA if yinyang == "阳" else list(reversed(CLOCKWISE_EIGHTGUA))
    starting_star = duty["值符星宫"][0].replace("芮", "禽")
    starting_gong = duty["值符星宫"][1]
    star_reorder = new_list(STAR_RING, starting_star) if yinyang == "阳" else new_list(list(reversed(STAR_RING)), starting_star)
    gong_reorder = new_list(rotate, "坤") if starting_gong == "中" else new_list(rotate, starting_gong)
    palace_to_star = dict(zip(gong_reorder, [STAR_TO_FULL[item] for item in star_reorder]))
    return palace_to_star, {v: k for k, v in palace_to_star.items()}


def pan_god(ju_meta: dict[str, Any], duty: dict[str, Any]) -> dict[str, str]:
    yinyang = ju_meta["dun"][0]
    rotate = CLOCKWISE_EIGHTGUA if yinyang == "阳" else list(reversed(CLOCKWISE_EIGHTGUA))
    starting_gong = duty["值符星宫"][1]
    gong_reorder = new_list(rotate, "坤") if starting_gong == "中" else new_list(rotate, starting_gong)
    gods = YANG_GODS if yinyang == "阳" else YIN_GODS
    return dict(zip(gong_reorder, [GOD_TO_FULL[item] for item in gods]))


def pan_sky(ctx: dict[str, Any], ju_meta: dict[str, Any], earth: dict[str, str], duty: dict[str, Any]) -> dict[str, str]:
    yinyang = ju_meta["dun"][0]
    rotate = CLOCKWISE_EIGHTGUA if yinyang == "阳" else list(reversed(CLOCKWISE_EIGHTGUA))
    earth_reverse = earth_plate_reverse(earth)
    fu_head = ctx["hour_zhifu"][2]
    hour_stem = ctx["hour_gz"][0]
    fu_location = earth_reverse.get(hour_stem)
    fu_head_location = duty["值符星宫"][1]
    zhifu = duty["值符星宫"][0]
    earth_rotate = [earth.get(p) for p in rotate]
    if fu_head_location == "中":
        start_stem = earth.get("坤")
        reordered = new_list(earth_rotate, start_stem)
        return dict(zip(new_list(rotate, "坤"), reordered))
    start_stem = earth.get("坤") if zhifu == "禽" else (fu_head if fu_head in earth_rotate else earth.get("坤"))
    reordered = new_list(earth_rotate, start_stem)
    gong_reorder = new_list(rotate, fu_head_location)
    if fu_location:
        gong_reorder = new_list(gong_reorder, fu_location)
    result = dict(zip(gong_reorder, reordered))
    result.setdefault("中", earth.get("中", "戊"))
    return result


def horse_branch(day_branch: str) -> str:
    for group, horse in HORSE_BRANCH_MAP.items():
        if day_branch in group:
            return horse
    return ""


def branch_to_palace(branch: str) -> str:
    return BRANCH_TO_PALACE.get(branch, "")


def empty_palaces(xunkong: str) -> set[str]:
    return {branch_to_palace(branch) for branch in xunkong if branch_to_palace(branch)}


def build_auto_chart(payload: dict[str, Any]) -> AutoPanResult:
    auto = deepcopy(payload)
    calendar = auto.get("calendar") or {}
    if not all(calendar.get(k) is not None for k in ["year", "month", "day", "hour"]):
        raise ValueError("auto-hour mode requires calendar.year/month/day/hour")
    minute = int(calendar.get("minute", 0) or 0)
    method = str((auto.get("auto_chart") or {}).get("method", "chaibu")).lower()
    ctx = qimen_context(int(calendar["year"]), int(calendar["month"]), int(calendar["day"]), int(calendar["hour"]), minute, method)
    ju_meta = ctx["ju_meta"]
    earth = earth_plate(ju_meta)
    duty = zhifu_n_zhishi(ctx, ju_meta)
    doors = pan_door(ju_meta, duty)
    stars, _ = pan_star(ju_meta, duty)
    gods = pan_god(ju_meta, duty)
    sky = pan_sky(ctx, ju_meta, earth, duty)
    empties = empty_palaces(ctx["xunkong"])
    horse = horse_branch(ctx["day_gz"][1])
    horse_palace = branch_to_palace(horse)

    auto_cfg = auto.get("auto_chart") or {}
    use_strategy = auto_cfg.get("use_deity_strategy", "day_stem_sky")
    target_strategy = auto_cfg.get("target_strategy", "custom")

    def palace_by_sky_stem(stem: str) -> str:
        for palace, sky_stem in sky.items():
            if sky_stem == stem:
                return palace
        return ""

    if use_strategy == "custom_palace":
        use_palace = auto_cfg.get("use_deity_palace") or ""
    elif use_strategy == "hour_stem_sky":
        use_palace = palace_by_sky_stem(ctx["hour_gz"][0]) or palace_by_sky_stem(ctx["hour_zhifu"][2])
    else:
        use_palace = palace_by_sky_stem(ctx["day_gz"][0]) or palace_by_sky_stem(ctx["hour_gz"][0])

    target_palace = auto_cfg.get("target_palace", "") if target_strategy == "custom" else ""
    duty_star_palace = duty["值符星宫"][1]
    duty_door_palace = duty["值使门宫"][1]

    palaces = []
    for palace in EIGHT_GUA:
        item = {
            "name": palace,
            "trigram": palace,
            "element": PALACE_ELEMENT[palace],
            "door": doors.get(palace, ""),
            "star": stars.get(palace, ""),
            "god": gods.get(palace, ""),
            "heaven_stem": sky.get(palace, ""),
            "earth_stem": earth.get(palace, ""),
            "empty": palace in empties,
            "horse": palace == horse_palace,
            "is_duty_star_palace": palace == duty_star_palace,
            "is_duty_door_palace": palace == duty_door_palace,
            "notes": ""
        }
        palaces.append(item)

    chart = {
        "method": f"auto-{method}",
        "dun": "yang" if ju_meta["dun"] == "阳遁" else "yin",
        "ju": ju_meta["ju"],
        "yuan": ju_meta["yuan"],
        "season": ctx["season"],
        "time_note": ctx["calendar"].solar_iso,
        "gan_zhi": {
            "year": ctx["year_gz"],
            "month": ctx["month_gz"],
            "day": ctx["day_gz"],
            "hour": ctx["hour_gz"]
        },
        "solar_term": ctx["term"],
        "current_jie": ctx["calendar"].current_jie,
        "current_qi": ctx["calendar"].current_qi,
        "xunkong": ctx["xunkong"],
        "horse": horse,
        "duty_star": {"name": duty["值符星宫"][0], "palace": duty_star_palace},
        "duty_door": {"name": duty["值使门宫"][0], "palace": duty_door_palace},
        "xunshou": {"jiazi": duty["值符天干"][0], "stem": duty["值符天干"][1]},
        "use_deity": {"label": "求测人", "palace": use_palace},
        "counterparty": {"label": auto.get("target_role", "target"), "palace": target_palace},
        "palaces": palaces
    }

    auto_meta = {
        "mode": "auto-hour",
        "calendar": {
            "solar": ctx["calendar"].solar_iso,
            "year_gz": ctx["year_gz"],
            "month_gz": ctx["month_gz"],
            "day_gz": ctx["day_gz"],
            "hour_gz": ctx["hour_gz"],
            "term": ctx["term"],
            "xunkong": ctx["xunkong"]
        },
        "auto_chart": {
            "method": method,
            "use_deity_strategy": use_strategy,
            "target_strategy": target_strategy
        }
    }
    auto["chart"] = chart
    auto["auto_meta"] = auto_meta
    return AutoPanResult(payload=auto, auto_meta=auto_meta)
