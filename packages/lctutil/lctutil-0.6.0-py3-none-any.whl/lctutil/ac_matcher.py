import ahocorasick

def decrypt(s):
    result = ""
    for i in range(len(s)):
        v = ord(s[i])
        if v > 256:
            result += chr(v - i - 1)
        else:
            result += s[i]
    return result.strip()


class AC:
    """
        敏感词检查
        构建词表的AC自动机
    """

    def __init__(self, enc = False):
        self.slot_ac = ahocorasick.Automaton()
        self.enc = enc

    def init_slot_ac(self, files):
        import os
        """
           读入词表文件, 逐个词插入 word: (tag, 词长)
           tag是文件名， 取第一个“.”前的， 比如： 歌曲.txt =>  歌曲;  歌曲.cn.txt =>  歌曲
        """
        for f in files:
            tag = os.path.basename(f).split(".")[0]
            for line in open(f):
                if self.enc: line = decrypt(line)
                if not line: continue
                exists_flag = self.slot_ac.get(line, None)
                if exists_flag is not None:
                    if tag not in exists_flag[0]:
                        exists_flag[0].append(tag)
                        self.slot_ac.add_word(line, (exists_flag[0], len(line)))
                else:
                    self.slot_ac.add_word(line, ([tag], len(line)))


    def init_slot_list_ac(self, lst, tag: str):
        for line in lst:
            exists_flag = self.slot_ac.get(line, None)
            if exists_flag is None:
                self.slot_ac.add_word(line, ([tag], len(line)))

    def make_from_file(self):
        import os.path
        import glob
        file_dir = os.path.dirname(__file__) + "/keywords/"
        files = glob.glob(file_dir + '*.txt')
        print(files)
        self.init_slot_ac(files)
        self.slot_ac.make_automaton()

    def make_from_list(self, lst, tag):
        print("Init AC: %s %d"%(tag, len(lst)))
        self.init_slot_list_ac(lst, tag)
        self.slot_ac.make_automaton()

    def match(self, query, tag=None):
        """
            找出一个AC自动机所有匹配到的词
        """
        ans = []
        if self.slot_ac is None: return ans
        for end_index, (tags, key_length) in self.slot_ac.iter(query):
            if tag is None or tag in tags:
                start_index = end_index - key_length + 1
                ans.append(query[start_index: end_index + 1])
        return ans

    def match_all(self, query):
        """
            找出一个AC自动机所有匹配到的词
        """
        ans = []
        has_seen = []
        if self.slot_ac is None: return ans
        for end_index, (tags, key_length) in self.slot_ac.iter(query):
            start_index = end_index - key_length + 1
            mt = query[start_index: end_index + 1]
            if mt not in has_seen:
                has_seen.append(mt)
                ans.append((mt, tags))
        return ans

from .stock_infos import info_stock_names, info_stock_codes, all_gainian, all_bankuai_2, all_bankuai_3

S_NAME_TAG = "STOCK"
S_CODE_TAG = "SCODE"
S_BK_TAG = "BK"
S_GAINIAN_TAG = "GAINIAN"

stock_ac = AC()
stock_ac.init_slot_list_ac(info_stock_names, S_NAME_TAG)
stock_ac.init_slot_list_ac(info_stock_codes, S_CODE_TAG)
stock_ac.init_slot_list_ac(all_gainian, S_GAINIAN_TAG)
stock_ac.make_from_list(set(list(all_bankuai_2) + list(all_bankuai_3)), S_BK_TAG)
