

import os
"""
股票列表
每个对应的概念和板块
板块列表
概念列表
"""


info_stock_names = []
info_stock_codes = []

code_name_kv = {}

filtered_gainian = set(["融资融券", "转融券标的", "富时罗素概念", "富时罗素概念股","深股通", "沪股通"])
all_gainian = set()
all_bankuai_1 = set()
all_bankuai_2 = set()
all_bankuai_3 = set()

info_tables = {}

def loadcodes(filepath):
    with open(filepath, encoding="utf8") as f:
        for line in f:
            eles = line.strip().split(",")
            if len(eles) < 2: continue
            code, name = eles[0], eles[1]
            code_name_kv[name] = code
            code_name_kv[code] = name
            info_stock_names.append(name)
            info_stock_codes.append(code)

            if eles[2]:
                all_gainian.update(eles[2].split(";"))
            all_bankuai_1.add(eles[3])
            all_bankuai_2.add(eles[4])
            all_bankuai_3.add(eles[5])

            info_tables[name] = (eles[2], eles[3], eles[4], eles[5])


_filename = os.getenv("STOCK_INFO_FILE")
loadcodes(_filename)


def get_code_or_name(ele):
    return code_name_kv.get(ele, "")