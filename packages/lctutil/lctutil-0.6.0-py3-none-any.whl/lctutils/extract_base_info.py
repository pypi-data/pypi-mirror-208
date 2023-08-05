
import requests
import os, json

filtered_gainian = set(["融资融券", "转融券标的", "富时罗素概念", "富时罗素概念股","深股通", "沪股通"])
all_gainian = set()
all_bankuai_1 = set()
all_bankuai_2 = set()
all_bankuai_3 = set()
stocks = []


page_num = os.environ.get("LCT_PAGE_NUM") or 105

def check_dir(dir_path):
    dir1 = os.path.join(dir_path, "output")
    if not os.path.exists(dir1):
        os.makedirs(dir1)

    dir2 = os.path.join(dir_path, "infos")
    if not os.path.exists(dir2):
        os.makedirs(dir2)


def req_ths(outpath = "."):
    check_dir(outpath)
    url = """http://www.iwencai.com/gateway/urp/v7/landing/getDataList?query=%E6%89%80%E6%9C%89%E6%A6%82%E5%BF%B5%E5%92%8C%E8%A1%8C%E4%B8%9A%E6%9D%BF%E5%9D%97&urp_sort_way=desc&urp_sort_index=%E6%9C%80%E6%96%B0%E6%B6%A8%E8%B7%8C%E5%B9%85&page={}&perpage=50&condition=%5B%7B%22chunkedResult%22%3A%22%E6%89%80%E6%9C%89%E6%A6%82%E5%BF%B5_%26_%E5%92%8C_%26_%E8%A1%8C%E4%B8%9A%E6%9D%BF%E5%9D%97%22%2C%22opName%22%3A%22and%22%2C%22opProperty%22%3A%22%22%2C%22sonSize%22%3A2%2C%22relatedSize%22%3A0%7D%2C%7B%22reportType%22%3A%22null%22%2C%22indexName%22%3A%22%E6%89%80%E5%B1%9E%E6%A6%82%E5%BF%B5%22%2C%22indexProperties%22%3A%5B%5D%2C%22valueType%22%3A%22_%E6%89%80%E5%B1%9E%E6%A6%82%E5%BF%B5%22%2C%22domain%22%3A%22abs_%E8%82%A1%E7%A5%A8%E9%A2%86%E5%9F%9F%22%2C%22uiText%22%3A%22%E6%89%80%E5%B1%9E%E6%A6%82%E5%BF%B5%22%2C%22sonSize%22%3A0%2C%22queryText%22%3A%22%E6%89%80%E5%B1%9E%E6%A6%82%E5%BF%B5%22%2C%22relatedSize%22%3A0%2C%22source%22%3A%22new_parser%22%2C%22type%22%3A%22index%22%2C%22indexPropertiesMap%22%3A%7B%7D%7D%2C%7B%22reportType%22%3A%22null%22%2C%22indexName%22%3A%22%E6%89%80%E5%B1%9E%E5%90%8C%E8%8A%B1%E9%A1%BA%E8%A1%8C%E4%B8%9A%22%2C%22indexProperties%22%3A%5B%5D%2C%22valueType%22%3A%22_%E6%89%80%E5%B1%9E%E5%90%8C%E8%8A%B1%E9%A1%BA%E8%A1%8C%E4%B8%9A%22%2C%22domain%22%3A%22abs_%E8%82%A1%E7%A5%A8%E9%A2%86%E5%9F%9F%22%2C%22uiText%22%3A%22%E6%89%80%E5%B1%9E%E5%90%8C%E8%8A%B1%E9%A1%BA%E8%A1%8C%E4%B8%9A%22%2C%22sonSize%22%3A0%2C%22queryText%22%3A%22%E6%89%80%E5%B1%9E%E5%90%8C%E8%8A%B1%E9%A1%BA%E8%A1%8C%E4%B8%9A%22%2C%22relatedSize%22%3A0%2C%22source%22%3A%22new_parser%22%2C%22type%22%3A%22index%22%2C%22indexPropertiesMap%22%3A%7B%7D%7D%5D&codelist=&indexnamelimit=&logid=57e19dcded50aa77f5c569cb30d50103&ret=json_all&sessionid=57e19dcded50aa77f5c569cb30d50103&source=Ths_iwencai_Xuangu&date_range%5B0%5D=20230403&iwc_token=0ac9664d16805352367887040&urp_use_sort=1&user_id=368976217&uuids%5B0%5D=24087&query_type=stock&comp_id=6623802&business_cat=soniu&uuid=24087"""

    headers = {
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    }

    for page in range(1, page_num):
        res = requests.post(url.format(page), headers=headers)
        if res.status_code == 200:
            with open(os.path.join(outpath, "output/res_%d"%page), "w", encoding="utf8") as f:
                txt = res.text.strip().encode("utf8").decode("raw_unicode_escape")
                txt2 = txt.split('"datas":')[1].split('"meta"')[0].strip(",")
                #js = json.loads(txt2)
                f.write(txt2)
        else:
            print(res.status_code)


def filter_codes(outpath=".", bks2=[]):
    res = []
    with open(os.path.join(outpath, "infos/info_table.csv"), "r") as f:
        lines = f.readlines()
        for line in lines:
            eles = line.strip().split(",")
            if bks2 and eles[4] in bks2:
                res.append(eles[0])

    
    obj = {"codes": res, "filtered": {"bks2": bks2}}
    with open(os.path.join(outpath, "infos/filtered_codes.json"), "w", encoding="utf8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

def filter_gainian(lst):
    return [e for e in lst if e not in filtered_gainian]

def extract_from_raw(outpath = "."):
    res = []
    for page in range(1, page_num):
        with open(os.path.join(outpath, "output/res_%d"%page), "r", encoding="utf8") as f:
            js = json.loads(f.read().strip())
            for ele in js:
                if ele["所属概念"]:
                    gainians = filter_gainian(ele["所属概念"].split(";"))
                    all_gainian.update(gainians)
                else:
                    gainians = []
                    print(ele)
                bks = ele["所属同花顺行业"].split("-")
                all_bankuai_1.add(bks[0])
                all_bankuai_2.add(bks[1])
                all_bankuai_3.add(bks[2])
                stocks.append((ele["股票简称"], ele["code"]))
                txt = ",".join([ele["code"], ele["股票简称"] ,";".join(gainians) , bks[0], bks[1], bks[2]])
                res.append(txt + "\n")

            
    with open(os.path.join(outpath, "infos/info_table.csv"), "w", encoding="utf8") as f:
        f.writelines(res)

    info_json = {
        "gainians": list(all_gainian),
        "bk1": list(all_bankuai_1),
        "bk2": list(all_bankuai_2),
        "bk3": list(all_bankuai_3),
        "stocks": stocks
    }
    with open(os.path.join(outpath, "infos/info.json"), "w", encoding="utf8") as f:
        json.dump(info_json, f, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    #filter_codes(bks2=["计算机设备", "计算机应用", "半导体及元件", "电子化学品"])
    #req_ths()
    extract_from_raw()