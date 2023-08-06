import bs4
from typing import List
from urllib.request import urlopen, Request


def find_occurrences(string: str, sub_string: str) -> List[int]:
    occurrences = []
    sub_str_len = len(sub_string)

    for i in range(len(string) - sub_str_len + 1):
        if string[i : i + sub_str_len] == sub_string:
            occurrences.append(i)

    return occurrences


def fix_tr(tr: bs4.element.Tag) -> bs4.BeautifulSoup:
    tr_string = str(tr)

    if tr_string.count("<tr>") > 1:
        trs_pos = find_occurrences(str(tr_string), "<tr>")
        tr_string = tr_string[0 : trs_pos[1]]
        tr_string += "</tr>"

        tr = bs4.BeautifulSoup(tr_string, "html.parser")

    return tr


def get_html(url: str) -> bs4.BeautifulSoup:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    client = urlopen(req)
    html_data = client.read()
    client.close()
    return bs4.BeautifulSoup(html_data, "html.parser")
