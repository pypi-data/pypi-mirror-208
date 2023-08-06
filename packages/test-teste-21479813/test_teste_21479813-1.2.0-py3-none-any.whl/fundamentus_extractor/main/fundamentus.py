from ..data import get_detail_data_list, get_result_shares, transform

from typing import List

def get_stock_summary(clean=True):
    dict_list = get_result_shares()

    if(clean == True):
        dict_list = transform(dict_list)

    return dict_list

def get_stock_tickers() -> List[str]:
    sumary = get_stock_summary()

    result = [record["Papel"] for record in sumary]

    return result


def get_indicators(shares_list, clean=True):
    dict_list = get_detail_data_list(shares_list)
    
    if(clean == True):
        dict_list = transform(dict_list)

    return dict_list
