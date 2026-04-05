import re


def expand_variables(items: list[dict], settings: dict[str, str]) -> list[dict]:
    """データ内の$name形式の変数をsettingsの値で展開する。

    $$name と書くことでエスケープし、展開後にリテラルの $name として残す。
    settingsに定義がない $name は展開せず元の文字列を保持する。
    """
    if not settings:
        return items
    return [_expand_item(item, settings) for item in items]


def expand_dict(d: dict, settings: dict[str, str]) -> dict:
    """dict内の$name形式の変数をsettingsの値で展開する。"""
    if not settings:
        return d
    return {k: expand_value(v, settings) for k, v in d.items()}


def expand_value(value, settings: dict[str, str]):
    """値の$name形式の変数をsettingsの値で展開する。

    str, dictは再帰的に展開する。それ以外の型はそのまま返す。
    """
    if isinstance(value, str):
        # 1. $$name → プレースホルダに退避（展開を回避）
        # 2. $name → settingsの値で展開
        # 3. プレースホルダ → $name に復元
        result = re.sub(r'\$\$(\w+)', lambda m: f'\x00{m.group(1)}\x00', value)
        result = re.sub(r'\$(\w+)', lambda m: settings.get(m.group(1), m.group(0)), result)
        result = re.sub(r'\x00(\w+)\x00', lambda m: f'${m.group(1)}', result)
        return result
    if isinstance(value, dict):
        return {k: expand_value(v, settings) for k, v in value.items()}
    return value


def _expand_item(item: dict, settings: dict[str, str]) -> dict:
    return {k: expand_value(v, settings) for k, v in item.items()}
