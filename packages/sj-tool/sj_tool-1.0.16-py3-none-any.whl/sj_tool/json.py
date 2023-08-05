import json


def load(filename):
    """加载json文件"""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


def dump(obj, filename):
    """保存为json文件"""
    with open(filename, "w", encoding="utf-8") as f:
        return json.dump(obj, f, ensure_ascii=False)
