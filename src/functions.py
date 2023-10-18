try:
    import unzip_requirements
except ImportError:
    pass

try:
    import unicodedata
    import logging
    import re
    import datetime
    import pandas
    import numpy
    from typing import Any, List
    from validate_docbr import CNPJ, CPF
except Exception as e:
    print("Error importing libraries", e)

logger = logging.getLogger(__name__)


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


def treatDecimalFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', row='main', positionInFileEnd=0):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :param row: este serve pra caso não seja um pagamento que esteja na linha principal (que não tem cabeçalho, então pegar apenas pelo número do campo). O valor 'main' quer dizer que tá numa linha que pode ter cabeçalho
    :return: retorna um campo como decimal
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            if row == 'main':
                return treatDecimalField(data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)])
            else:
                return treatDecimalField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd))
        except Exception:
            try:
                return treatDecimalField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd))
            except Exception:
                return float(0)
    else:
        try:
            return treatDecimalField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd))
        except Exception:
            return float(0)


def treatDateField(valorCampo, formatoData=1):
    """
    :param valorCampo: Informar o campo string que será transformado para DATA
    :param formatoData: 1 = 'DD/MM/YYYY' ; 2 = 'YYYY-MM-DD' ; 3 = 'YYYY/MM/DD' ; 4 = 'DDMMYYYY'
    :return: retorna como uma data. Caso não seja uma data válida irá retornar None
    """
    if str(type(valorCampo)).find('datetime.date') >= 0:
        return valorCampo

    if str(type(valorCampo)).find('datetime.datetime') >= 0:
        return valorCampo.date()

    # if isinstance(valorCampo, datetime.datetime):
    #     return valorCampo.date()

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
        return datetime.datetime.strptime(valorCampo[:lengthField], formatoDataStr)
    except ValueError:
        return None


def treatDateFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', formatoData=1, row='main', positionInFileEnd=0):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :param formatoData: 1 = 'DD/MM/YYYY' ; 2 = 'YYYY-MM-DD (opcional)
    :param row: este serve pra caso não seja um pagamento que esteja na linha principal (que não tem cabeçalho, então pegar apenas pelo número do campo). O valor 'main' quer dizer que tá numa linha que pode ter cabeçalho
    :return: retorna um campo como decimal
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            if row == 'main':
                return treatDateField(data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)], formatoData)
            else:
                return treatDateField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), formatoData)
        except Exception:
            try:
                return treatDateField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), formatoData)
            except Exception:
                return None
    else:
        try:
            return treatDateField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), formatoData)
        except Exception:
            return None


def treatTextField(value: str):
    value = str(value)
    try:
        return minimalizeSpaces(removeCharSpecials(value.strip().upper()))
    except Exception:
        return ""


def treatTextFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', positionInFileEnd=0, keepTextOriginal=True):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :return: retorna um campo como texto, retirando acentos, espaços excessivos, etc
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            value = data[searchPositionFieldForName(
                fieldsHeader, nameFieldHeader)]
            return treatTextField(value) if keepTextOriginal is True else value
        except Exception:
            try:
                value = analyzeIfFieldHasPositionInFileEnd(
                    data, numberOfField, positionInFileEnd)
                return treatTextField(value) if keepTextOriginal is True else value
            except Exception:
                return ""
    else:
        try:
            value = analyzeIfFieldHasPositionInFileEnd(
                data, numberOfField, positionInFileEnd)
            return treatTextField(value) if keepTextOriginal is True else value
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


def formatDate(valueDate: datetime.date, format='%Y-%m-%d'):
    try:
        if str(type(valueDate)).find('datetime') >= 0:
            return valueDate.strftime(format)
    except Exception:
        return valueDate
    return valueDate


def removeAnArrayFromWithinAnother(arraySet=[]):
    newArray = []
    try:
        for array in arraySet:
            if array is None:
                continue
            for vector in array:
                if len(vector) == 0:
                    continue
                newArray.append(vector)
    except Exception:
        pass
    return newArray


def returnBankForNumber(numberBank):
    numberBankOriginal = numberBank
    numberBank = treatNumberField(numberBank, True)
    nameBank = ""
    if numberBank == 1:
        nameBank = 'BRASIL'
    elif numberBank == 3:
        nameBank = 'AMAZONIA'
    elif numberBank == 237:
        nameBank = 'BRADESCO'
    elif numberBank == 104:
        nameBank = 'CEF'
    elif numberBank == 756:
        nameBank = 'SICOOB'
    elif numberBank == 748:
        nameBank = 'SICRED'
    elif numberBank == 33:
        nameBank = 'SANTANDER'
    elif numberBank == 341:
        nameBank = 'ITAU'
    elif numberBank == 743:
        nameBank = 'SEMEAR'
    elif numberBank == 422:
        nameBank = 'SAFRA'
    elif numberBank == 637:
        nameBank = 'SOFISA'
    elif numberBank == 4:
        nameBank = 'NORDESTE'
    elif numberBank == 218:
        nameBank = 'BS2'
    elif numberBank == 634:
        nameBank = 'TRIANGULO'
    elif numberBank == 41:
        nameBank = 'BANRISUL'
    elif numberBank == 70:
        nameBank = 'BRB'
    elif numberBank == 82:
        nameBank = 'TOPAZIO'
    elif numberBank == 260:
        nameBank = 'NUBANK'
    elif numberBank == 336:
        nameBank = 'C6'
    else:
        nameBank = str(numberBankOriginal)

    return nameBank


def returnBankForName(nameBank):
    nameBank = str(nameBank)
    if nameBank.count('BRASIL') > 0:
        nameBank = 'BRASIL'
    elif nameBank.count('BRADESCO') > 0:
        nameBank = 'BRADESCO'
    elif (nameBank.count('CAIXA') > 0 and (nameBank.count('ECON') > 0 or nameBank.count('AG.') > 0 or nameBank.count('FEDERAL') > 0)) or nameBank.count('CEF') > 0:
        nameBank = 'CEF'
    elif nameBank.count('SICOOB') > 0:
        nameBank = 'SICOOB'
    elif nameBank.count('SICRED') > 0:
        nameBank = 'SICRED'
    elif nameBank.count('SANTANDER') > 0:
        nameBank = 'SANTANDER'
    elif nameBank.count('ITAU') > 0:
        nameBank = 'ITAU'
    elif nameBank.count('SAFRA') > 0:
        nameBank = 'SAFRA'
    elif nameBank.count('DINHEIRO') > 0:
        nameBank = 'DINHEIRO'
    else:
        nameBank = nameBank

    return nameBank


def validateCPF(value):
    cpf = CPF()
    return cpf.validate(value)


def validateCNPJ(value):
    cnpj = CNPJ()
    return cnpj.validate(value)


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
    elif typeData.count('numpy') > 0 and typeData.count('datetime') > 0:
        newData = numpy.datetime_as_string(data, unit='D')
        newData = treatDateField(newData, 2)
        newData = newData.strftime("%d/%m/%Y") if newData is not None else data
    else:
        newData = data

    return newData


def readExcelPandas(filePath: str, nameSheetToFilter=''):
    listOfDataAllRows = []
    dataOfRow = []

    try:
        try:
            sheetNames = pandas.ExcelFile(filePath).sheet_names
        except Exception:
            try:
                sheetNames = pandas.ExcelFile(
                    filePath, engine='xlrd').sheet_names
            except Exception:
                sheetNames = pandas.ExcelFile(
                    filePath, engine='openpyxl').sheet_names

        for sheet in sheetNames:
            try:
                if nameSheetToFilter == '' or sheet == nameSheetToFilter:
                    try:
                        dataFrame = pandas.read_excel(
                            filePath, sheet_name=sheet, header=None)
                    except Exception:
                        try:
                            dataFrame = pandas.read_excel(
                                filePath, sheet_name=sheet, header=None, engine='xlrd')
                        except Exception:
                            dataFrame = pandas.read_excel(
                                filePath, sheet_name=sheet, header=None, engine='openpyxl')

                    dataFrameDropNa = dataFrame.dropna(how='all')
                    dataFrameFillNa = dataFrameDropNa.fillna('')
                    dataFrameToRecords = dataFrameFillNa.to_records(
                        index=False)
                    for dataRow in dataFrameToRecords:
                        dataOfRow.append(sheet)
                        for data in dataRow:
                            newData = identifiesAndTransformTypeDataOfSeriesPandas(
                                data)
                            dataOfRow.append(newData)

                        listOfDataAllRows.append(dataOfRow.copy())
                        dataOfRow.clear()
            except Exception as e:
                logger.exception(e)

    except Exception as e:
        logger.exception(e)

    return listOfDataAllRows
