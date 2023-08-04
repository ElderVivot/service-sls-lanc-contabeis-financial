try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, treatTextField
except Exception as e:
    print(f"Error importing libraries {e}")


def identifiesTheHeader(data: Dict[str, Any], settingLayout: Dict[str, Any]):
    # :data são os valores de cada "linha" dos arquivos processados
    # :settingLayout é a configuração do layout que está no banco de dados

    posionsOfHeader = {}
    header = returnDataInDictOrArray(settingLayout, ['header'])  # pega as configurações só do cabeçalho
    dataManipulate = []

    # se não tiver cabeçalho já retorna em branco
    if len(header) == 0:
        return None

    for field in data:
        dataManipulate.append(treatTextField(field))

    countNumberHeader = 0
    for field in header:
        nameColumn = treatTextField(returnDataInDictOrArray(field, ['nameColumn']))
        nameColumn = None if nameColumn == "" else nameColumn

        if dataManipulate.count(nameColumn) > 0 and nameColumn is not None:
            countNumberHeader += 1

    if countNumberHeader == len(header):
        for keyField, nameColumn in enumerate(dataManipulate):
            if nameColumn != "":
                posionsOfHeader[nameColumn] = keyField

    return posionsOfHeader
