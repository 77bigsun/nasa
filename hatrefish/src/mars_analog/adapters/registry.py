"""變數資料來源的註冊表：(body, variable, source) -> loader。換資料只要新增 adapter、改 features.yaml。"""
_REGISTRY = {}


def register(body: str, variable: str, source: str):
    def deco(fn):
        _REGISTRY[(body, variable, source)] = fn
        return fn
    return deco


def get_loader(body: str, variable: str, source: str):
    return _REGISTRY[(body, variable, source)]


def registered():
    return sorted(_REGISTRY)
