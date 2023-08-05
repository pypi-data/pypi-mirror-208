from crawlutils.num_utils import defaultIfNumber


def get_td(td_list, *text_in):
    for i in td_list:
        valid = True
        for text in text_in:
            if text not in i.text.replace(" ", ""):
                valid = False
                break
        if valid:
            return i
    return "-"


def get_td_text(td_list, *text_in):
    for i in td_list:
        valid = True
        for text in text_in:
            if text not in i.text.replace(" ", ""):
                valid = False
                break
        if valid:
            return i.findNext('td').text.strip()
    return "-"


def find_tr_has_text(text, trlist):
    target_tr = None
    for tr in trlist:
        if text in tr.text.replace(' ', ''):
            target_tr = tr
            break
    return target_tr


def defaultNumberInTR(text, tr3, unit_multiplier, default="-"):
    np_tr = find_tr_has_text(text, tr3)
    np = defaultIfNumber(np_tr.findAll('td')[1].text, unit_multiplier, default=default)
    return np