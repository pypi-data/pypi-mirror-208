

from lctutil import [ac_matcher, openai,  stock_infos, extract_base_info]

# ac_matcher
关键词匹配， 需要配置环境变量"STOCK_INFO_FILE"

# openai
openai调用， 需要配置环境变量“API_KEYS”， 分号分割的keys

# stock_infos
加载股票基本信息， 需要配置环境变量"STOCK_INFO_FILE"

# extract_base_info
爬虫， 更新股票信息