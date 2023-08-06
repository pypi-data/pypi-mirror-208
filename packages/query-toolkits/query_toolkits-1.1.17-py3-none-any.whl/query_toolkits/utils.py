import os
import re
import json



"""
direct_transform = {
    "个百分点": ["%", 1],

    "M": ["米", 1],
    "毫米": ["米", 0.001],
    "mm": ["米", 0.001],
    "厘米": ["米", 0.01],
    "cm":  ["米", 0.01],
    "分米": ["米", 0.1],
    "微米": ["米", 0.000001],
    "千米": ["米", 1000],
    "KM": ["米", 1000],
    "公里": ["米", 1000],
    "μm": ["米", 0.000001],
    "英寸": ["米", 0.0254],
    "inch": ["米", 0.0254],
    "里": ["米", 500],
    "尺": ["米", 0.3333333],

    "毫升": ["L", 0.001],
    "mL": ["L", 0.001],
    "升": ["L", 1],
    "L": ["L", 1],
    "nL": ["L", 0.000000001],
    "纳升": ["L", 0.000000001],
    "立方米": ["L", 1000],
    "立方分米": ["L", 1],
    "立方厘米": ["L", 0.001],
    "立方毫米": ["L", 0.000001],
    "分升": ["L", 0.1],
    "厘升": ["L", 0.01],

    "平方千米": ["平方米", 1000000],
    "公顷": ["平方米", 10000],
    "平": ["平方米", 1],
    "亩": ["平方米", 666.666666667],

    "千克": ["千克", 1],
    "吨": ["千克", 1000],
    "g": ["千克", 0.001],
    "克": ["千克", 0.001],
    "公斤": ["千克", 1],
    "斤": ["千克", 0.5],
    "kg": ["千克", 1],
    "t": ["千克", 1000],
    "lb": ["千克", 0.4535924],

    "人民币": ["元", 1],

    "倍": ["倍", 1],
    "辆": ["辆", 1],
    "元": ["元", 1],

    "米": ["米", 1],
    "%": ["%", 1],
    "平方米": ["平方米", 1],
    "个": ["个", 1],
    "股": ["股", 1],
    "人次": ["人次", 1],
    "颗": ["颗", 1],
    "台": ["台", 1],
    "瓶": ["瓶", 1],
    "张": ["张", 1],
    "篇": ["篇", 1],
    "件": ["件", 1],

    "伏特": ["V", 1],
    "V": ["V", 1],
    "伏": ["V", 1],

    "赫兹": ["Hz", 1],
    "Hz": ["Hz", 1],

    "瓦": ["W", 1],
    "瓦特": ["W", 1],
    "千瓦": ["W", 1000],
    "W": ["W", 1],
    "kW": ["W", 1000]
}
"""

general_transform = {
    "万": 10000,
    "亿": 100000000,
    "万亿": 1000000000000,
    "万万": 100000000,
    "千": 1000,
    "百": 100,
    "千万": 10000000,
    "万千": 10000000,
    "百万": 1000000
}

key_date = {'前天': -2, '前日': -2, '昨天': -1, '昨日': -1, '今天': 0, '今日': 0, '明天': 1, '明日': 1, '后天': 2, "现在": 0}
week_day = {'周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4, '周六': 5, '周天': 6, '周日': 6,
            "上周一": -7, "上周二": -6, "上周三": -5, "上周四": -4, "上周五": -3, "上周六": -2, "上周日": -1, "上周天": -1,
            "上上周一": -14, "上上周二": -13, "上上周三": -12, "上上周四": -11, "上上周五": -10, "上上周六": -9, "上上周日": -8, "上上周天": -8}

word_dict = {"最新": ["create_time", True],
             "最热": ["hot_val", True], "最火": ["hot_val", True], "最火爆": ["hot_val", True], "最火热": ["hot_val", True],
             "最流行": ["current_hot_val", True], "流行度最高": ["current_hot_val", True],
             "最多收藏": ["favorite_num", True], "收藏最多": ["favorite_num", True],
             "最多点击": ["click_num", True], "点击最多": ["click_num", True]
             }


def max_backward_match(word_list, vocab, max_k=5):
    res = []
    end = len(word_list)

    while end > 0:
        break_flag = False
        for i in range(max_k):
            start = end - max_k + i
            start = start if start >= 0 else 0
            temp = "".join(word_list[start:end])
            if temp in vocab:
                res.append([temp, start, end])
                end = start
                break_flag = True
                break
        if not break_flag:
            end -= 1
    res.reverse()
    return res


def max_backward_match_end(word_list, vocab, max_k=3):
    end = len(word_list)
    for i in range(max_k):
        start = end - max_k + i
        start = start if start >= 0 else 0
        temp = "".join(word_list[start:end])
        if temp in vocab:
            return word_list[:start]
    return None


def cut_text_index(word_list):
    index_dict = dict()
    ind = 0
    for i, word in enumerate(word_list):
        index_dict[i] = ind
        ind += len(word)
    index_dict[len(word_list)] = ind
    return index_dict


def _read_table(filename):
    res = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.split("\\s+", line.strip().lower())
            res.append(line)
    di = dict()
    if len(res) > 0:
        for i, line in enumerate(res):
            if i == 0:
                continue
            else:
                di[line[0]] = [line[1], float(line[2])]
    return di

def _read_list(filename):
    l_list = []
    res = set()
    with open(filename, "r") as f:
        for line in f:
            res.add(line.strip())
            l_list.append(len(line.strip()))
    return res


def list2dict(li):
    di = dict()
    for elem in li:
        one_line = re.split('[,，]', elem)
        first = one_line[0].strip()
        for e in one_line:
            e = e.strip()
            if e != "":
                di[e] = first
    return di


def _stock_dict(filename="info.json"):
    di = dict()
    json_dict = json.load(open(filename))
    for key in json_dict:
        elems = json_dict[key]
        for code in elems:
            di[code] = code
            di[elems[code]["stock_name"]] = code
    return di




