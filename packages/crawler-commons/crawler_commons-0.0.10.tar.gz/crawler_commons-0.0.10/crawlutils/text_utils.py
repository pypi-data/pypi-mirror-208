import re


def make_text(t) -> str:
    return t.replace('\n', '').replace('\t', '').replace(' ', '').replace('\r', '').replace('\xa0', '')


def make_num(t) -> str:
    return t.replace('\n', '').replace('\t', '').replace(' ', '').replace('\r', '').replace('\xa0', '').replace(',', '')


def make_num_include_zo(txt):
    """
    ## 억원 이 생략된 억단위 금액을 숫자로 변환
    ## 1조 2,000 => 1_200_000_000_000
    :param txt:
    :return:
    """
    일조 = 1_000_000_000_000
    일억 = 100_000_000
    tkns = txt.split("조")
    zo_part = int(make_num(tkns[0])) * 일조 if len(tkns) > 1 else 0
    uk_part_txt = tkns[1] if len(tkns) > 1 else make_num(tkns[0])
    uk_part = int(make_num(uk_part_txt)) * 일억
    return zo_part + uk_part


def make_date(data):
    return data.replace('년', '-').replace('월', '-').replace('일', '').replace(' ', '').replace('.', '-')


def to_quarter_str(num):
    return f"{num // 100}.{(num % 100) // 3}"


def splitter(s):
    spl = s.split(" = ")
    if len(spl) <= 1:
        return None
    try:
        return int(spl[1])
    except ValueError:
        return None


def has_text_in_list(texts, str):
    for text in texts:
        if text in str:
            return True

    return False


def remove_strs(text, removes):
    tmp = text
    for remove in removes:
        tmp = tmp.replace(remove, '')

    return tmp


def trim_template(text):
    return re.sub(r"^\s*\|", "", text.strip(), 0, re.MULTILINE) + "\n\n"


def json_encode(dictionary):
    return dictionary.encode()
