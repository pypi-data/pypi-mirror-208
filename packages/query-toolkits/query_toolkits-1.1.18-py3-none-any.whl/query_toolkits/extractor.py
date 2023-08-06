#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
import os
import re
import regex
from datetime import datetime, timedelta
import query_toolkits.utils as utils

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))

class Extractor:
    def __init__(self):
        self.unit_transform = utils._read_table(_get_module_path("unit_transform"))
        self.organization = utils._read_list(_get_module_path("organization.txt"))
        self.keyword = utils._read_list(_get_module_path("keyword.txt"))
        self.financial_dict = utils.list2dict(utils._read_list(_get_module_path("financial_index.txt")))
        self.financial_dict_keys = set(self.financial_dict.keys())
        self.fund_name = utils._read_list(_get_module_path("fund_product.txt"))
        self.stock_dict = utils._stock_dict(_get_module_path("info.json"))
        self.product_dict = utils.list2dict(utils._read_list(_get_module_path("product.txt")))
        self.index_dict = utils.list2dict(utils._read_list(_get_module_path("index.txt")))


    def _check_time_valid(self, word):
        m = re.match("\d+$", word)
        if m:
            if len(word) <= 6:
                return None
        word1 = re.sub('[号|日]\d+$', '日', word)
        if word1 != word:
            return self._check_time_valid(word1)
        else:
            return word1


    def _check_valid(self, number_str, type):
        special_num_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
        if type == "year":
            if int(number_str) > 1000 and int(number_str) < 3000:
                return True
        elif type == "month":
            if number_str in list(map(str, range(1, 13))) + special_num_list:
                return True
        elif type == "day":
            if number_str in list(map(str, range(1, 32))) + special_num_list:
                return True
        elif type == "hour":
            if number_str in list(map(str, range(0, 25))) + special_num_list + ["00"]:
                return True
        elif type == "second":
            if number_str in list(map(str, range(0, 61))) + special_num_list + ["00"]:
                return True
        elif type == "minute":
            if number_str in list(map(str, range(0, 61))) + special_num_list + ["00"]:
                return True
        return False


    def _fill_slot(self, text):
        year = None
        month = None
        day = None
        hour = None
        second = None
        minute = None
        case_year = "(\d{4})年"
        case_month = "(\d{1,2})(月份|月)"
        case_day = "(\d{1,2})[日|号]"
        case_hour = "(\d{1,2})[点|时]"
        case_second = "(\d{1,2})(分钟|分)"
        case_minute = "(\d{1,2})秒"
        key_year = {'今年': 0, '去年': -1, '前年': -2, "明年": 1, "前一年": -1, "大前年":-3}
        for key in key_year:
            if key in text:
                year = str(datetime.now().year + key_year[key])
        res_year = re.search(case_year, text)
        res_month = re.search(case_month, text)
        res_day = re.search(case_day, text)
        res_hour = re.search(case_hour, text)
        res_second = re.search(case_second, text)
        res_minute = re.search(case_minute, text)
        if res_year:
            year = res_year.group(1)
        if res_month:
            month = res_month.group(1)
        if res_day:
            day = res_day.group(1)
        if res_hour:
            hour = res_hour.group(1)
        if res_second:
            second = res_second.group(1)
        if res_minute:
            minute = res_minute.group(1)
        case_year_month_day = "(\d{4})[-\./](\d{1,2})[-\./](\d{1,2})"
        res_year_month_day = re.search(case_year_month_day, text)
        if res_year_month_day:
            year = res_year_month_day.group(1)
            month = res_year_month_day.group(2)
            day = res_year_month_day.group(3)
            if not(self._check_valid(year, "year") and self._check_valid(month, "month") and self._check_valid(day, "day")):
                year = None
                month = None
                day = None

        case_year_month_day = "^(\d{4})年(\d{1,2})月(\d{1,2})$"
        res_year_month_day = re.search(case_year_month_day, text)
        if res_year_month_day:
            year = res_year_month_day.group(1)
            month = res_year_month_day.group(2)
            day = res_year_month_day.group(3)
            if not (self._check_valid(year, "year") and self._check_valid(month, "month") and self._check_valid(day, "day")):
                year = None
                month = None
                day = None

        case_year_month = "(\d{4})[-\./](\d{1,2})"
        res_year_month = re.search(case_year_month, text)
        if res_year_month:
            year = res_year_month.group(1)
            month = res_year_month.group(2)
            if not (self._check_valid(year, "year") and self._check_valid(month, "month")):
                year = None
                month = None

        case_hour_second_minute = "(\d{2})[:：](\d{2})[:：](\d{2})"
        res_hour_second_minute = re.search(case_hour_second_minute, text)
        if res_hour_second_minute:
            hour = res_hour_second_minute.group(1)
            second = res_hour_second_minute.group(2)
            minute = res_hour_second_minute.group(3)
            if not (self._check_valid(hour, "hour") and self._check_valid(second, "second") and self._check_valid(minute, "minute")):
                hour = None
                second = None
                minute = None

        case_month_day = "^(d{1,2})月(\d{1,2})$"
        res_month_day = re.search(case_month_day, text)
        if res_month_day:
            month = res_month_day.group(1)
            day = res_month_day.group(2)
            if not (self._check_valid(month, "month") and self._check_valid(day, "day")):
                month = None
                day = None


        case_hour_second = "(\d{2})[:：](\d{2})"
        res_hour_second = re.search(case_hour_second, text)
        if res_hour_second:
            hour = res_hour_second.group(1)
            second = res_hour_second.group(2)
            if not (self._check_valid(hour, "hour") and self._check_valid(second, "second")):
                hour = None
                second = None

        if year:
            year = int(year) if self._check_valid(year, "year") else None
        if month:
            month = int(month) if self._check_valid(month, "month") else None
        if day:
            day = int(day) if self._check_valid(day, "day") else None
        if hour:
            hour = int(hour) if self._check_valid(hour, "hour") else None
        if second:
            second = int(second) if self._check_valid(second, "second") else None
        if minute:
            minute = int(minute) if self._check_valid(minute, "minute") else None

        if year or month or day or hour or second or minute:
            return (year, month, day, hour, second, minute)
        return None



    def _compare_res(self, res1, res2):
        win1, win2 = True, True
        for elem1, elem2 in zip(res1, res2):
            if elem1 is not None and elem2 is not None and elem1 != elem2:
                return -1
            if elem1 is None and elem2 is not None:
                win1 = False
            elif elem2 is None and elem1 is not None:
                win2 = False
        if win1:
            return 1
        if win2:
            return 0
        return -1


    def _extract_special_time(self, text):
        date_list = []
        date_dig = re.finditer("(^|\D+)(\d{8})($|\D+)", text)
        if date_dig:
            for dd in date_dig:
                date_list.append(dd.group(2))
        final_res = []
        for elem in date_list:
            print(elem)
            year = int(elem[:4])
            month = int(elem[4:6])
            day = int(elem[6:])
            if year >= 1949 and year <= 2100 and month in range(13) and day in range(32):
                final_res.append((year, month, day))
        return final_res


    # 时间提取
    def extract_time(self, text, cut_res):
        time_res = []
        date_list = []
        index_list = []
        # 字典键值对用冒号分割，每个键值对之间用逗号分割，整个字典包括在花括号{}中
        # dict.get(key, default=None)返回指定键的值，如果值不在字典中返回default值
        key_date = utils.key_date
        week_day = utils.week_day

        # 检测英文写法日期8位数字
        date_dig = re.finditer(
            "(去年|今年|前年|明年|前一年)?\d{1,2}月\d{1,2}[号|日]|\d{4}年\d{1,2}月\d{1,2}[号|日]|\d{4}[-\./]\d{1,2}[-\./]\d{1,2}|"
            "\d{4}年\d{1,2}月|\d{4}年|\d{4}-\d{1,2}|\d{4}\.\d{1,2}|\d{4}/\d{1,2}|"
            "\d{2}[:：]\d{2}([:：]\d{2})?|\d{1,2}[点|时]\d{1,2}[分|分钟](\d{1,2}[秒])?",
            text)
        if date_dig:
            for dd in date_dig:
                date_list.append(dd.group(0))
                index_list.append(dd.span())
        phrase = ""
        phrase_list = []
        for i, (k, v) in enumerate(cut_res):
            if k in key_date:
                word = (datetime.today() + timedelta(days=key_date.get(k, 0))).strftime(
                    '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
                time_res.append(word)
            elif k in week_day:
                today_num = datetime.weekday(datetime.today())
                delta_num = (week_day.get(cut_res[i - 1].word + k) if (i >= 1 and (cut_res[i - 1].word + k) in week_day) else week_day.get(k)) - today_num
                word = (datetime.today() + timedelta(delta_num)).strftime(
                        '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
                time_res.append(word)
            elif v in ("m", "t", "x"):
                phrase += k
            elif v not in ("m", "t", "x") and phrase != "":
                phrase_list.append(phrase)
                phrase = ""
        if phrase != "":
            phrase_list.append(phrase)

        result = list(filter(lambda x: x is not None, [self._check_time_valid(w) for w in time_res + date_list + phrase_list]))
        final_res = [self._fill_slot(x) for x in result]
        final_res = [x for x in final_res if x is not None]
        final_res_copy = final_res.copy()
        remove_set = set()
        final_res = []
        for i1, res1 in enumerate(final_res_copy):
            for i2 in range(i1, len(final_res_copy)):
                res2 = final_res_copy[i2]
                if i1 != i2:
                    tmp_index = self._compare_res(res1, res2)
                    if tmp_index != -1:
                        remove_set.add([i1, i2][tmp_index])
        for i in range(len(final_res_copy)):
            if i not in remove_set:
                final_res.append(final_res_copy[i])
        final_res.extend(self._extract_special_time(text))
        return final_res


    def extract_number(self, cut_res):
        #direct_transform = utils.direct_transform
        direct_transform = self.unit_transform
        general_transform = utils.general_transform
        #分词、词性
        candidates = []
        candidate = ""
        start_index = None
        end_index = 0
        for i, (word, flag) in enumerate(cut_res):
            end_index += len(word)
            if flag in ("m", "q", "mq") or word.isdigit() or (flag in ("x", "eng") and word in direct_transform):
                if not start_index:
                    start_index = end_index - len(word)
                candidate += word
            elif word == "%":
                candidate += word
                candidates.append((candidate, start_index, end_index))
                start_index = None
                candidate = ""
            else:
                if candidate != "":
                    candidates.append((candidate, start_index, end_index))
                    start_index = None
                candidate = ""
        if candidate != "":
            candidates.append((candidate, start_index, end_index))

        final_res = []
        #再正则处理
        pattern = "^([0-9]+(\.[0-9]+)?)([^0-9]+)$"
        for candidate in candidates:
            word, start_index, end_index = candidate[0], candidate[1], candidate[2]
            res = re.search(pattern, word)
            if res:
                number = float(res.group(1))
                unit = res.group(3)
                if unit in direct_transform:
                    norm_unit = direct_transform[unit]
                    unit, times = norm_unit[0], norm_unit[1]
                    number *= times
                    final_res.append((number, unit, start_index, end_index))
                else:
                    for i in range(1, len(unit)):
                        if unit[i:] in direct_transform:
                            norm_unit = direct_transform[unit[i:]]
                            tmp_unit, times = norm_unit[0], norm_unit[1]
                            number *= times
                            if unit[:i] in general_transform:
                                number *= general_transform[unit[:i]]
                                final_res.append((number, tmp_unit, start_index, end_index))
        return final_res


    def extract_requirement(self, cut_res):
        #word: [变量名/类型，从大到小排序？]
        final_res = []
        word_dict = utils.word_dict
        word_list = [k for k, v in cut_res]
        res = utils.max_backward_match(word_list, set(word_dict.keys()), max_k=3)
        index_dict = utils.cut_text_index(word_list)
        for elem in res:
            tmp = word_dict[elem[0]]
            final_res.append((elem[0], tmp[0], tmp[1], index_dict[elem[1]], index_dict[elem[2]]))
        return final_res


    def extract_reference_no(self, text):
        final_res = {"document_no_full": "",
                     "document_department_with_tail": None,
                     "document_department_without_tail": None,
                     "year": None,
                     "number": None,
                     "number_with_tail": None,
                     "special": None,
                     "special_part1": None,
                     "special_part2": None,
                     "special_part3": None}
        org_name = None
        year = None
        number = None
        another_number = None
        query = text
        special_part1 = None
        special_part2 = None
        special_part3 = None
        p = re.compile(u'[\u4e00-\u9fa5]+')
        res = re.findall(p, query)
        for part in res:
            if part in self.organization:
                org_name = part
                break
        if not org_name:
            org = utils.max_backward_match(text, self.organization, 40)
            for elem in org:
                if len(elem[0]) >= 3:
                    org_name = elem[0]
                    query = query[elem[2]:]
                    break
        if org_name:
            final_res["document_no_full"] += org_name
            final_res["document_department_without_tail"] = utils.max_backward_match_end(org_name, self.keyword)

        res = re.search('[〔\[\(［]?\s*([0-9]{4})\s*[〕\]\)］]?\s*[年]?\s*[第]?\s*([0-9]+)\s*(号|期|号文)', query)
        if res:
            final_res["document_no_full"] += res.group(0)
            year = res.group(1)
            number = res.group(2)
            final_res["number_with_tail"] = number + res.group(3)
        else:
            res = re.search('[〔\[\(［]\s*([0-9]{4})\s*[〕\]\)］]\s*([0-9]+)', query)
            if res:
                final_res["document_no_full"] += res.group(0)
                year = res.group(1)
                number = res.group(2)
            else:
                res = re.search('[〔\[\(［]\s*([0-9]{4})\s*[〕\]\)］]', query)
                if res:
                    temp = int(res.group(1))
                    if temp >= 1900 and temp <= 2100:
                        final_res["document_no_full"] += res.group(0)
                        year = res.group(1)
                res = re.search('[第]?\s*([0-9]+)\s*(号|号文|期)', query)
                if res:
                    final_res["document_no_full"] += res.group(0)
                    number = res.group(1)
                    final_res["number_with_tail"] = number + res.group(2)
                else:
                    res = re.search('[（\(]([0-9]{6})[\)）]', query)
                    if res:
                        final_res["document_no_full"] += res.group(0)
                        number = res.group(1)

        res = re.search('([a-zA-Z]+/[a-zA-Z]+)\s*([0-9]+(\.[0-9]+)?)[—\-－一–]+([0-9]{4})', query)
        if res:
            another_number = res.group(0)
            final_res["document_no_full"] += ("" if final_res["document_no_full"] == "" else " ") + another_number
            special_part1 = res.group(1)
            special_part2 = res.group(2)
            special_part3 = res.group(4)
        final_res["document_department_with_tail"] = org_name
        final_res["year"] = year
        final_res["number"] = number
        final_res["special"] = another_number
        final_res["special_part1"] = special_part1
        final_res["special_part2"] = special_part2
        final_res["special_part3"] = special_part3
        if not final_res["number_with_tail"]:
            final_res["number_with_tail"] = number
        return final_res


    def extract_weapon(self, text):
        final_res = []
        res = regex.finditer('(^|[^a-zA-Z0-9—\-－一–/])([a-zA-Z]*[0-9]*[a-zA-Z]+[—\-－一–]*[0-9]+[a-zA-Z]*(/[a-zA-Z0-9]+([—\-－一–]+[a-zA-Z0-9]+)*)*)($|[^a-zA-Z0-9—\-－一–/])', text, overlapped=True)
        for elem in res:
            final_res.append(elem.group(2))
        res = re.finditer('(^|\s)[0-9]+[—\-－一–][0-9]+($|\s)', text)
        for elem in res:
            final_res.append(elem.group(2))
        res = regex.finditer('(^|[^a-zA-Z0-9—\-－一–/])([a-zA-Z]*[0-9]*[a-zA-Z]+([—\-－一–]+[a-zA-Z0-9]+)*([—\-－一–]+[0-9]+)+)($|[^a-zA-Z0-9—\-－一–/])', text, overlapped=True)
        for elem in res:
            final_res.append(elem.group(2))
        return set(final_res)


    def extract_letters(self, text):
        pinyin = []
        others = []
        pinyin_pattern = r'^(bang|ba[ino]?|beng|be[in]?|bing|bia[no]?|bi[en]?|bu|cang|ca[ino]?|ceng|ce[in]?|chang|cha[ino]?|cheng|che[n]?|chi|chong|chou|chuang|chua[in]|chu[ino]?|ci|cong|cou|cuan|cu[ino]?|dang|da[ino]?|deng|de[in]?|dia[no]?|ding|di[ae]?|dong|dou|duan|du[ino]?|fang|fan|fa|feng|fe[in]{1}|fo[u]?|fu|gang|ga[ino]?|geng|ge[in]?|gong|gou|guang|gua[in]?|gu[ino]?|hang|ha[ino]?|heng|he[in]?|hong|hou|huang|hua[in]?|hu[ino]?|jiang|jia[no]?|jiong|ji[nu]?|juan|ju[en]?|kang|ka[ino]?|keng|ke[n]?|kong|kou|kuang|kua[in]?|ku[ino]?|lang|la[ino]?|leng|le[i]?|liang|lia[no]?|ling|li[enu]?|long|lou|luan|lu[no]?|lv[e]?|mang|ma[ino]?|meng|me[in]?|mia[no]?|ming|mi[nu]?|mo[u]?|mu|nang|na[ino]?|neng|ne[in]?|niang|nia[no]?|ning|ni[enu]?|nong|nou|nuan|nu[on]?|nv[e]?|pang|pa[ino]?|pa|peng|pe[in]?|ping|pia[no]?|pi[en]?|po[u]?|pu|qiang|qia[no]?|qiong|qing|qi[aenu]?|quan|qu[en]?|rang|ra[no]{1}|reng|re[n]?|rong|rou|ri|ruan|ru[ino]?|sang|sa[ino]?|seng|se[n]?|shang|sha[ino]?|sheng|she[in]?|shi|shou|shuang|shua[in]?|shu[ino]?|si|song|sou|suan|su[ino]?|tang|ta[ino]?|teng|te|ting|ti[e]?|tia[no]?|tong|tou|tuan|tu[ino]?|wang|wa[ni]?|weng|we[in]{1}|w[ou]{1}|xiang|xia[no]?|xiong|xing|xi[enu]?|xuan|xu[en]|yang|ya[no]?|ye|ying|yi[n]?|yong|you|yo|yuan|yu[en]?|zang|za[ino]?|zeng|ze[in]?|zhang|zha[ino]?|zheng|zhe[in]?|zhi|zhong|zhou|zhuang|zhua[in]?|zhu[ino]?|zi|zong|zou|zuan|zu[ino]?)$'
        res = re.findall("[a-zA-Z]+", text)
        for elem in res:
            if re.match(pinyin_pattern, elem):
                pinyin.append(elem)
            else:
                others.append(elem)
        return pinyin, others


    def extract_financial_index(self, cut_words, word_dict=None):
        res = utils.max_backward_match(cut_words, self.financial_dict_keys if word_dict is None else word_dict, 15)
        res = [(elem[0], self.financial_dict[elem[0]]) for elem in res]
        return res


    def extract_fund_name(self, cut_words, word_set=None):
        res = utils.max_backward_match(cut_words, self.fund_name if word_set is None else word_set, 20)
        res = [elem[0] for elem in res]
        return res


    def extract_stock_name(self, cut_words, word_dict=None):
        # code/name:code
        di = self.stock_dict if word_dict is None else word_dict
        keys = di.keys()
        res = utils.max_backward_match(cut_words, keys, 20)
        res = [(elem[0], di[elem[0]]) for elem in res]
        return res


    def extract_product_name(self, cut_words, word_dict=None):
        di = self.product_dict if word_dict is None else word_dict
        keys = di.keys()
        res = utils.max_backward_match(cut_words, keys, 10)
        res = [(elem[0], di[elem[0]]) for elem in res]
        return res


    def extract_index_name(self, cut_words, word_dict=None):
        di = self.index_dict if word_dict is None else word_dict
        keys = di.keys()
        res = utils.max_backward_match(cut_words, keys, 10)
        res = [(elem[0], di[elem[0]]) for elem in res]
        return res




















# et = Extractor()
# import jieba.posseg as psg
# li = [
#     "今年产量10万吨",
#     "今年产量10.5L",
#     "pe 15倍的股票",
#     "涨了15%的股票",
#     "10万亿元",
#     "234立方厘米",
#     "目标是5个百分点",
#     "5L"
# ]
#
# for text in li:
#     cut_res = psg.lcut(text.lower())
#     res = et.extract_number(cut_res)
#     print(text)
#     print(res)


# et = Extractor()
# li = [
#     "www.data.com",
#     "提取字母",
#     "which one is the best?",
#     "daguanshuju",
#     "da guan shu ju"
# ]
# for elem in li:
#     print(elem)
#     print(et.extract_letters(elem))



# import time
# et = Extractor()
# import jieba.posseg as psg
# li = [
#     "最热的电视剧收藏最多最多点击erktkerktk3ktj34jr24j5   wqer423",
#     "32r534t5345j34jtjfhwerhwhe问人家二姐跳舞机4今日就很入味人家4日34234234日发放开阔任何男人文化"
# ]
#
# start = time.time()
# for text in li:
#     cut_res = psg.lcut(text)
#     res = et.extract_requirement(cut_res)
#     print(res)
# #print((time.time() - start) / 2000)

















# if __name__ == '__main__':
#     import time
#     import jieba.posseg as psg
#     et = Extractor()
#     cut_res = psg.cut("pe和市净率市盈率吃在2432净资产收益率在5%理财宝364天期470号 理财宝28天期580号中国平安贵州茅台SH000002 SH00000566")
#     cut_words = [k for k,v in cut_res]
#     print(cut_words)
#     print(cut_words)
#     res = et.extract_financial_index(cut_words)
#     print(res)
#     res = et.extract_fund_name(cut_words)
#     print(res)
#     res = et.extract_stock_name(cut_words)
#     print(res)
#
#
#     # res = et.extract_letters("wrw234ef4 4er53 3rr shen")
#     # print(res)
#     # exit(0)
#     count_all = 0
#     count = 0
#     with open("weapon.txt", "r") as f:
#         for line in f:
#             count_all += 1
#             res = et.extract_weapon(line)
#             print(line, res)
#             if not res:
#                 count += 1
#
#     print(count/count_all)
#
#     res = et.extract_reference_no("银发〔2015〕324号/JR/T 0125-2015")
#     print(res)
#     print(datetime.today())
#     start = time.time()
#     # text = "2021-03-0914:00开庭审理杨峰？"
#     # get_range_time_from_query(text)
#     # exit(0)
#     li = [
#         '20161204',
#         '23434455',
#         '现在是20110809',
#         '20110809oh',
#         '上周六的股票',
#         '我前天来的',
#         '我今天到的',
#         '12月26号的天气怎么样',
#         '2020.10.03的2022.1.5利率是多少？',
#         "周二的api是多少",
#         "2018/1/1,利率",
#         "现在，利率",
#         "8月1日，利率",
#         "9.8，利率",
#         "第3026期，利率",
#         "2019年7月1日的利率是多少",
#         "2020年8月1日 利率",
#         "8月1日 利率",
#         "1月5日 利率",
#         "2022年11月1日中国历史",
#         "中国2021年9月18日历史",
#         "利现在，率",
#         "利2018/1/1,率",
#         "利8月1日 率",
#         "20年8月1日 利率",
#         '的2022.1.5利率是多少？',
#         '去年9月10日利率是多少？',
#         '2020年12月利率是多少？',
#         '2020.1/26利率是多少？',
#         '利率2020.1/26是多少？',
#         '利率是多少？2020.1/26',
#         '利率2020.1月26是多少？',
#         '利率2020年1月2日是多少？',
#         '我可以9月10日利率是多少？',
#         '2021-03-09 14:00开庭审理杨峰',
#         '2021-03-0914:00开庭审理杨峰',
#         '01-09 14:00开庭审理杨峰',
#         '03 09 yuhuagangtie',
#         '2022年11月12日 14:00开庭审理杨峰',
#         '我上上周五的时候利率',
#         '2015年3月5日 14：32到5月22日 13：00',
#         '1993年5月28',
#         '大前年',
#         '达观数据']
#     for text in li:
#         cut_res = list(psg.cut(text))
#         print(text)
#         res = et.extract_time(text, cut_res)
#         print(res)


