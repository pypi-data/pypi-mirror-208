# 字

字典数据是 [此库](https://github.com/pwxcoo/chinese-xinhua) 中的 `data/word.json`。

## 接口

### 查单字()

参数为单字字符串，如：

```
from chinese_characters_words import 字典
字典.查单字('好')
```

如果查不到，返回 None；否则信息如下：
```
{
  '字'
  '旧体'
  '笔画数'
  '拼音'
  '部首'
  '释义'
  '其他'
}
```
