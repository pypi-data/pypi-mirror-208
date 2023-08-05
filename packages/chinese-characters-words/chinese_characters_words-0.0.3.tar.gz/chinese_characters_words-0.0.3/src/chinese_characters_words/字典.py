from json import load as json_load
import importlib.resources

def 初始化():
    with importlib.resources.open_text("chinese_characters_words.数据", "字典.json") as 文件:
        return json_load(文件)

原始数据 = None

# API
def 查单字(字):
    global 原始数据
    if 原始数据 == None:
        原始数据 = 初始化()
    for 字数据 in 原始数据:
        if 字 == 字数据['word']:
            信息 = {}
            信息['字'] = 字数据['word']
            信息['旧体'] = 字数据['oldword'] # 大多与现在相同
            信息['笔画数'] = 字数据['strokes']
            信息['拼音'] = 字数据['pinyin']
            信息['部首'] = 字数据['radicals']
            信息['释义'] = 字数据['explanation']
            信息['其他'] = 字数据['more']
            return 信息
