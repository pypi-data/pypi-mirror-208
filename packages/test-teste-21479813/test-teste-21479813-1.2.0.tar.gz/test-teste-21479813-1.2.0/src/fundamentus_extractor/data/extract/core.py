import pandas as pd
from . import Title, helpers


def get_detail_data(ticker: str) -> None:
    soup_data = helpers.get_html(
        f"https://fundamentus.com.br/detalhes.php?papel={ticker}"
    )
    tables = soup_data.find_all("table")

    out = {}
    for table in tables:
        trs = table.find_all("tr")

        titles = []
        for row_number in range(len(trs)):
            tr = helpers.fix_tr(trs[row_number])
            tds = tr.find_all("td")

            last_label = None
            pos = 1
            for td in tds:
                if "class" not in td.attrs:
                    continue

                classes = td.attrs["class"]
                spans = td.find_all("span")

                if "label" in classes:
                    spans = [span for span in spans if "txt" in span.attrs["class"]]

                    if len(spans) == 1:
                        last_label = spans[0].text

                    pos += 1

                elif "data" in classes:
                    if len(spans) == 1:
                        if last_label == None:
                            raise Exception("Data without label")

                        possibles = [
                            title
                            for title in titles
                            if pos <= title.col2 and pos >= title.col1
                        ]

                        if len(possibles) == 0:
                            out[last_label] = spans[0].text

                        else:
                            max_title = max(possibles, key=lambda x: x.row)
                            subtitle = max_title.find_subtitle(pos)
                            if subtitle == None:
                                out[max_title.text][last_label] = spans[0].text
                            else:
                                out[max_title.text][subtitle.text][last_label] = spans[
                                    0
                                ].text

                        last_label = None

                    pos += 1

                elif "nivel1" in classes:
                    colspan = int(td.attrs["colspan"])

                    if len(spans) == 1:
                        titles.append(
                            Title(spans[0].text, pos, pos + colspan - 1, row_number)
                        )
                        out[spans[0].text] = {}

                    pos += colspan

                elif "nivel2" in classes:
                    colspan = int(td.attrs["colspan"])

                    if len(spans) == 1:
                        possibles = [
                            title
                            for title in titles
                            if pos <= title.col2 and pos >= title.col1
                        ]

                        if len(possibles) == 0:
                            raise Exception("Subtitle without title")

                        max_title = max(possibles, key=lambda x: x.row)

                        max_title.subtitles.append(
                            Title(spans[0].text, pos, pos + colspan - 1, row_number)
                        )

                        out[max_title.text][spans[0].text] = {}

                    pos += colspan

    return out


def get_result_shares():
    soup_data = helpers.get_html("https://www.fundamentus.com.br/resultado.php")

    table = soup_data.find_all("table")[0]

    df = pd.read_html(str(table), decimal=",", thousands='.')[0]

    dict_list = df.to_dict(orient="records")
    
    return dict_list


def get_detail_data_list(list_ativos):
    dict_list = []

    for ativo in list_ativos:
        my_dict = get_detail_data(ativo)
        dict_list.append(my_dict)

    return dict_list
