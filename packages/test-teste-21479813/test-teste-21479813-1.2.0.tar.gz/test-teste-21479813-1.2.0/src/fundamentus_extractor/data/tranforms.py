from typing import List, Dict
import re

def cast_values(records: List[Dict])-> List[Dict]:
    """
    Faz o cast dos valores de todas as colunas do dataframe para float ou inteiro,
    dependendo do padrão encontrado na string.

    Args:
        df (pd.DataFrame): O dataframe a ser modificado.

    Returns:
        None: Esta função não retorna nada, ela modifica o dataframe diretamente.
    """
    if(isinstance(records, list)):
        for record in records:
            cast_values(record)
        
    elif(not isinstance(records, dict)):
        return None

    else:
        for key in records:
            value = records[key]

            if(isinstance(records[key], (dict, list))):
                cast_values(value)

            else:
                if(isinstance(value, (int, float))):
                    continue
                
                value = str(value)
                value = value.strip()
                value = value.replace(".", "")
                value = value.replace(",", ".")
                
                if re.match(r'^-?\d+\.\d+%?$', value):
                    if '%' in value:
                        records[key] = round(float(value[:-1]) / 100, 10)
                    else:
                        records[key] = round(float(value), 10)

                elif re.match(r'^-?\d+$', value):
                    records[key] = int(value)
                
                elif(isinstance(records[key], str)):
                    records[key] = value.strip()

    return records

def remove_columns(records: List[Dict]) -> List[Dict]:
    if(isinstance(records, list)):
        for record in records:
            remove_columns(record)
        
    elif(not isinstance(records, dict)):
        return None
    
    else:
        remove = []
        for key in records:
            if(str(key) == "" or re.search(r"^-\d+$", str(key))):
                remove.append(key)

            elif(isinstance(records[key], (dict, list))):
                remove_columns(records[key])
        
        for key in remove:
            del records[key]

    return records

def transform(records):
    records = cast_values(records)
    records = remove_columns(records)

    return records