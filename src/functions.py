try:
    import unzip_requirements
except ImportError:
    pass

try:
    import unicodedata
    import re
    import datetime
    import pandas
    from typing import Any, List
except Exception as e:
    print("Error importing libraries", e)


def minimalizeSpaces(text: str):
    _result = text
    while ("  " in _result):
        _result = _result.replace("  ", " ")
    _result = _result.strip()
    return _result


def removeCharSpecials(text: str):
    nfkd = unicodedata.normalize('NFKD', text).encode(
        'ASCII', 'ignore').decode('ASCII')
    textFormated = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub('[^a-zA-Z0-9.!+:><=[)|?$(/*,\-_ \\\]', '', textFormated)


def searchPositionFieldForName(header, nameField=''):
    nameField = treatTextField(nameField)
    try:
        return header[nameField]
    except Exception:
        return None


def analyzeIfFieldHasPositionInFileEnd(data, positionInFile, positionInFileEnd):
    positionInFile = positionInFile - 1

    try:
        if positionInFileEnd <= 0:
            return data[positionInFile]
        else:
            return ''.join(data[positionInFile:positionInFileEnd])
    except Exception:
        return ""


def returnDataInDictOrArray(data: Any, arrayStructureDataReturn: List[Any], valueDefault='') -> Any:
    """
    :data: vector, matrix ou dict with data -> example: {"name": "Obama", "adress": {"zipCode": "1234567"}}
    :arrayStructureDataReturn: array in order with position of vector/matriz or name property of dict to \
    return -> example: ['adress', 'zipCode'] -> return is '1234567'
    """
    try:
        dataAccumulated = ''
        for i in range(len(arrayStructureDataReturn)):
            if i == 0:
                dataAccumulated = data[arrayStructureDataReturn[i]]
            else:
                dataAccumulated = dataAccumulated[arrayStructureDataReturn[i]]
        return dataAccumulated
    except Exception:
        return valueDefault


def treatDecimalField(value, numberOfDecimalPlaces=2, decimalSeparator=','):
    if type(value) == float:
        return value
    try:
        value = str(value)
        value = re.sub('[^0-9.,-]', '', value)
        if decimalSeparator == '.' and value.find(',') >= 0 and value.find('.') >= 0:
            value = value.replace(',', '')
        elif value.find(',') >= 0 and value.find('.') >= 0:
            value = value.replace('.', '')

        if value.find(',') >= 0:
            value = value.replace(',', '.')

        if value.find('.') < 0:
            value = int(value)

        return float(value)
    except Exception:
        return float(0)


def treatDateField(valorCampo, formatoData=1):
    """
    :param valorCampo: Informar o campo string que será transformado para DATA
    :param formatoData: 1 = 'DD/MM/YYYY' ; 2 = 'YYYY-MM-DD' ; 3 = 'YYYY/MM/DD' ; 4 = 'DDMMYYYY'
    :return: retorna como uma data. Caso não seja uma data válida irá retornar None
    """
    if type(valorCampo) == 'datetime.date':
        return valorCampo

    valorCampo = str(valorCampo).strip()

    lengthField = 10  # tamanho padrão da data são 10 caracteres, só muda se não tiver os separados de dia, mês e ano

    if formatoData == 1:
        formatoDataStr = "%d/%m/%Y"
    elif formatoData == 2:
        formatoDataStr = "%Y-%m-%d"
    elif formatoData == 3:
        formatoDataStr = "%Y/%m/%d"
    elif formatoData == 4:
        formatoDataStr = "%d%m%Y"
        lengthField = 8
    elif formatoData == 5:
        formatoDataStr = "%d/%m/%Y"
        valorCampo = valorCampo[0:6] + '20' + valorCampo[6:]

    try:
        return datetime.datetime.strptime(valorCampo[:lengthField], formatoDataStr).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def treatTextField(value: str):
    try:
        return minimalizeSpaces(removeCharSpecials(value.strip().upper()))
    except Exception:
        return ""


def treatNumberField(value, isInt=False):
    if type(value) == int:
        return value
    try:
        value = re.sub("[^0-9]", '', value)
        if value == "":
            return 0
        else:
            if isInt is True:
                try:
                    return int(value)
                except Exception:
                    return 0
            return value
    except Exception:
        return 0


def treatNumberFieldInVector(data, numberOfField=-1, fieldsHeader=[], nameFieldHeader='', isInt=False, positionInFileEnd=0):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :return: retorna um campo apenas como número
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            return treatNumberField(data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)], isInt)
        except Exception:
            try:
                return treatNumberField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), isInt)
            except Exception:
                return 0
    else:
        try:
            return treatNumberField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), isInt)
        except Exception:
            return 0


def identifiesAndTransformTypeDataOfSeriesPandas(data):
    newData = ''
    typeData = str(type(data))

    if typeData.count('str') > 0:
        newData = treatTextField(data)
    elif typeData.count('int') > 0:
        newData = treatNumberField(data, isInt=True)
    elif typeData.count('float') > 0:
        newData = treatDecimalField(data)
    elif typeData.count('pandas') > 0 and typeData.count('timestamp') > 0:
        newData = data.strftime("%d/%m/%Y")
    else:
        newData = data

    return newData


def formatDate(valueDate: datetime.date, format='%Y-%m-%d'):
    try:
        if str(type(valueDate)).find('datetime') >= 0:
            return valueDate.strftime(format)
    except Exception:
        return valueDate
    return valueDate


def readExcelPandas(filePath: str, nameSheetToFilter=''):
    listOfDataAllRows = []
    dataOfRow = []

    try:
        sheetNames = pandas.ExcelFile(filePath).sheet_names

        for sheet in sheetNames:
            if nameSheetToFilter == '' or sheet == nameSheetToFilter:
                dataFrame = pandas.read_excel(filePath, sheet_name=sheet, header=None)
                dataFrameDropNa = dataFrame.dropna(how='all')
                dataFrameFillNa = dataFrameDropNa.fillna('')
                dataFrameToRecords = dataFrameFillNa.to_records(index=False)
                for dataRow in dataFrameToRecords:
                    dataOfRow.append(sheet)
                    for data in dataRow:
                        newData = identifiesAndTransformTypeDataOfSeriesPandas(data)
                        dataOfRow.append(newData)

                    listOfDataAllRows.append(dataOfRow.copy())
                    dataOfRow.clear()

    except Exception as e:
        print(e)

    return listOfDataAllRows
