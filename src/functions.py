try:
    import unzip_requirements
except ImportError:
    pass

try:
    import io
    import fitz
    # import tabula
    import unicodedata
    import logging
    import re
    import datetime
    import pandas
    import numpy
    import csv
    from typing import Any, List
    from bs4 import BeautifulSoup
    from validate_docbr import CNPJ, CPF
except Exception as e:
    print("Error importing libraries", e)

logger = logging.getLogger(__name__)


def minimalizeSpaces(text: str, charsSpaceReplace='  '):
    _result = text
    while (charsSpaceReplace in _result):
        _result = _result.replace(charsSpaceReplace, charsSpaceReplace[:-1])
    _result = _result.strip()
    return _result


def removeCharSpecials(text: str):
    nfkd = unicodedata.normalize('NFKD', text).encode(
        'ASCII', 'ignore').decode('ASCII')
    textFormated = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    textFormated = textFormated.replace('\n', ' ').replace('\r', '')
    return re.sub('[^a-zA-Z0-9.!+:>;<=[\])|?$(/*,\-_ \\\]', '', textFormated)


def removeCharSpecials2(text: str):
    nfkd = unicodedata.normalize('NFKD', text).encode(
        'ASCII', 'ignore').decode('ASCII')
    textFormated = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub('[^a-zA-Z0-9.]!+:><=[)|?$(/*,\-_\n\r \\\]', '', textFormated)


def searchPositionFieldForName(header, nameField=''):
    nameField = treatTextField(nameField)
    try:
        position = header[nameField]
        return position
    except Exception:
        return None


def analyzeIfFieldHasPositionInFileEnd(data, positionInFile, positionInFileEnd):
    positionInFile = int(positionInFile)
    positionInFileEnd = int(positionInFileEnd)
    charToJoin = ''
    if str(type(data)).find('list') >= 0:
        charToJoin = ' '
    try:
        if positionInFileEnd == 0:
            return data[positionInFile]
        else:
            return charToJoin.join(data[positionInFile:positionInFileEnd])
    except Exception as e:
        # print(e, data, positionInFile, positionInFileEnd)
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


def treatDecimalFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', row='main', positionInFileEnd=0, fileType=''):
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
                if fileType == 'pdf':
                    positionFindText = searchPositionFieldForName(fieldsHeader, nameFieldHeader) - 10
                    positionFindTextEnd = -1
                    validGetPos = False
                    for keyHeader, posHeader in fieldsHeader.items():
                        if validGetPos is True:
                            positionFindTextEnd = posHeader
                            break
                        if keyHeader == nameFieldHeader:
                            validGetPos = True
                    value = data[positionFindText:positionFindTextEnd] if positionFindTextEnd != -1 else data[positionFindText:]
                    value = treatTextField(value).split(' ')[0]
                    return treatDecimalField(value)
                else:
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

    formatoDataStr = "%d/%m/%Y"
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


def treatDateFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', formatoData=1, row='main', positionInFileEnd=0, fileType=''):
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
                if fileType == 'pdf':
                    positionFindText = searchPositionFieldForName(fieldsHeader, nameFieldHeader) - 10
                    positionFindTextEnd = -1
                    validGetPos = False
                    for keyHeader, posHeader in fieldsHeader.items():
                        if validGetPos is True:
                            positionFindTextEnd = posHeader
                            break
                        if keyHeader == nameFieldHeader:
                            validGetPos = True
                    value = data[positionFindText:positionFindTextEnd] if positionFindTextEnd != -1 else data[positionFindText:]
                    value = treatTextField(value).split(' ')[0]
                    return treatDateField(value, formatoData)
                else:
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


def treatTextField(value: str, minimalizeSpace=True, optionRemove=1):
    value = str(value)
    try:
        if optionRemove == 1:
            value = removeCharSpecials(value.upper())
        else:
            value = removeCharSpecials2(value.upper())
        value = value.replace('−', '-')
        if minimalizeSpace is True:
            value = minimalizeSpaces(value.strip())
        return value
    except Exception:
        return ""


def treatTextFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', positionInFileEnd=0, keepTextOriginal=True, fileType=''):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :return: retorna um campo como texto, retirando acentos, espaços excessivos, etc
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            if fileType == 'pdf':
                positionFindText = searchPositionFieldForName(fieldsHeader, nameFieldHeader) - 10
                positionFindTextEnd = -1
                validGetPos = False
                for keyHeader, posHeader in fieldsHeader.items():
                    if validGetPos is True:
                        positionFindTextEnd = posHeader
                        break
                    if keyHeader == nameFieldHeader:
                        validGetPos = True
                value = data[positionFindText:positionFindTextEnd] if positionFindTextEnd != -1 else data[positionFindText:]
            else:
                value = data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)]
            return treatTextField(value) if keepTextOriginal is True else value
        except Exception:
            try:
                value = analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd)
                return treatTextField(value) if keepTextOriginal is True else value
            except Exception:
                return ""
    else:
        try:
            value = analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd)
            return treatTextField(value) if keepTextOriginal is True else value
        except Exception:
            return ""


def treatNumberField(value, isInt=False, replaceHifen=True):
    if type(value) == int or str(type(value)).find('numpy.int') >= 0:
        return value
    try:
        value = re.sub("[^0-9-]", '', value)
        if replaceHifen is True:
            value = value.replace('-', '')
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
    print('---', typeData)

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


def roundValueDataPage(dataPage):
    newDataPage = []
    dataPage.sort(key=lambda x: (x[1], x[0]))
    for numberLine, dataLine in enumerate(dataPage):
        nextLine = returnDataInDictOrArray(dataPage, [numberLine + 1])

        # update yLine because round not exact
        yThisLine = dataLine[1]
        yNextLine = returnDataInDictOrArray(nextLine, [1], 0)
        if yThisLine + 1 == yNextLine:
            yThisLine += 1

        # update yLine when is equal nextYLine, because date is first line in process
        dataNextLine = returnDataInDictOrArray(nextLine, [4], '')
        dataNextLineField01 = minimalizeSpaces(returnDataInDictOrArray(dataNextLine.split('\n'), [0]))
        if yThisLine == yNextLine and dataNextLineField01.count('/') == 2:
            yThisLine += 1

        tupleResult = (round(dataLine[0]), yThisLine, round(dataLine[2]), round(dataLine[3]), dataLine[4], dataLine[5], dataLine[6])
        newDataPage.append(tupleResult)
    newDataPage.sort(key=lambda x: (x[1], x[0]))
    return newDataPage


def readExcelPandas(filePath: str, nameSheetToFilter=''):
    listOfDataAllRows = []
    dataOfRow = []

    try:
        try:
            sheetNames = pandas.ExcelFile(filePath).sheet_names
        except Exception:
            try:
                sheetNames = pandas.ExcelFile(filePath, engine='xlrd').sheet_names
            except Exception:
                try:
                    sheetNames = pandas.ExcelFile(filePath, engine='openpyxl').sheet_names
                except Exception as e:
                    logger.error(e)
                    sheetNames = []

        for sheet in sheetNames:
            try:
                if nameSheetToFilter == '' or sheet == nameSheetToFilter:
                    try:
                        dataFrame = pandas.read_excel(filePath, sheet_name=sheet, header=None)
                    except Exception:
                        try:
                            dataFrame = pandas.read_excel(filePath, sheet_name=sheet, header=None, engine='xlrd')
                        except Exception:
                            try:
                                dataFrame = pandas.read_excel(filePath, sheet_name=sheet, header=None, engine='openpyxl')
                            except Exception as e:
                                logger.error(e)
                                return []

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
                logger.exception(e)

    except Exception as e:
        logger.exception(e)

    return listOfDataAllRows


def readCsv(filePath, splitField=';'):
    listOfDataAllRows = []
    dataOfRow = []

    try:
        try:
            dataFrame = pandas.read_csv(filePath, sep=splitField, encoding='utf-8', on_bad_lines='skip')
        except Exception:
            dataFrame = pandas.read_csv(filePath, sep=splitField, encoding='cp1252', on_bad_lines='skip')

        dataFrameDropNa = dataFrame.dropna(how='all')
        dataFrameFillNa = dataFrameDropNa.fillna('')
        dataFrameToRecords = dataFrameFillNa.to_records(index=False)
        for idx, dataRow in enumerate(dataFrameToRecords):
            dataOfRow.append('')
            for data in dataRow:
                newData = identifiesAndTransformTypeDataOfSeriesPandas(data)
                dataOfRow.append(newData)

            listOfDataAllRows.append(dataOfRow.copy())
            dataOfRow.clear()
    except Exception as e:
        logger.exception(e)

    return listOfDataAllRows


def readCsvAsTxt(fileBytesIO, splitField=';'):
    listOfDataAllRows = []

    bytesIORead = fileBytesIO.read()
    try:
        bytesIODecode = bytesIORead.decode('cp1252')
    except Exception:
        bytesIODecode = bytesIORead.decode('utf-8', errors='ignore')

    try:
        for line in bytesIODecode.split('\n'):
            lineFormated = line.replace('\r', '')
            lineFormated = treatTextField(lineFormated)
            lineFormated = f"{splitField}{lineFormated}"
            lineFormatedSplit = lineFormated.split(splitField)
            listOfDataAllRows.append(lineFormatedSplit.copy())

    except Exception as e:
        logger.exception(e)

    return listOfDataAllRows


def readXlsWithBeautifulSoup(fileBytesIO):
    listOfDataAllRows = []

    fileBytesSTR = fileBytesIO.getvalue()
    soup = BeautifulSoup(fileBytesSTR, 'xml')

    for sheet in soup.findAll('Worksheet'):
        for row in sheet.findAll('Row'):
            dataOfRow = []
            dataOfRow.append(sheet.attrs['ss:Name'])
            for cell in row.findAll('Cell'):
                if cell.Data:
                    dataOfRow.append(cell.Data.text)
                else:
                    dataOfRow.append('')
            listOfDataAllRows.append(dataOfRow)

    return listOfDataAllRows


def readXlsWithBeautifulSoupOption2(fileBytesIO):
    listOfDataAllRows = []
    dataOfRow = []

    fileBytesSTR = fileBytesIO.getvalue()
    soup = BeautifulSoup(fileBytesSTR, 'lxml')

    for row in soup.find_all('tr'):
        dataOfRow = []
        dataOfRow.append('')
        for cell in row.find_all(['td', 'th']):
            valueFieldSdval = cell.get('sdval')
            if valueFieldSdval is not None:
                valueField = valueFieldSdval
            else:
                valueField = cell.get_text()
            dataOfRow.append(valueField)
        listOfDataAllRows.append(dataOfRow)

    return listOfDataAllRows


def readTxt(fileBytesIO, minimalizeSpace=True, ignoreLineBlanks=False, dataAsByte=True, charsSpaceReplace='  '):
    newDataDoc = []

    if dataAsByte is True:
        bytesIORead = fileBytesIO.read()
        try:
            bytesIODecode = bytesIORead.decode('cp1252')
        except Exception:
            bytesIODecode = bytesIORead.decode('utf-8', errors='ignore')
    else:
        bytesIODecode = fileBytesIO

    numberLine = 0
    for line in bytesIODecode.split('\n'):
        try:
            dataValue = treatTextField(line, minimalizeSpace)
            if minimalizeSpace is True:
                dataValue = minimalizeSpaces(dataValue, charsSpaceReplace)
            if ignoreLineBlanks is True and treatTextField(dataValue) == "":
                continue
            numberLine += 1
            newDataDoc.append(dataValue)
        except Exception as e:
            print(e)

    return newDataDoc


def readPdf(fileBytesIO):
    dataLines = []
    with fitz.open(stream=fileBytesIO, filetype='pdf') as doc:

        for numberPage, page in enumerate(doc):
            dataPage = page.get_text("words", sort=True)

            newDataPage = []
            for numberLine, dataLine in enumerate(dataPage):
                tupleResult = (round(dataLine[0]), round(dataLine[1]), round(dataLine[2]), round(dataLine[3]), dataLine[4], dataLine[5], dataLine[6])
                newDataPage.append(tupleResult)

            # order by 3 times, because some number dont round correct
            newDataPage = roundValueDataPage(newDataPage)
            newDataPage = roundValueDataPage(newDataPage)
            newDataPage = roundValueDataPage(newDataPage)

            numberLineBefore = 0
            positionTextBefore = 0
            if numberPage >= 0:
                for data in newDataPage:
                    positionText = data[0]
                    numberLine = data[1]
                    valueField = ''
                    if numberLine == numberLineBefore:
                        for _ in range(positionTextBefore, positionText - len(data[4]), 1):
                            valueField += ' '
                        valueField += data[4]

                        dataLine += valueField
                    else:
                        numberLineBefore = 0
                        positionTextBefore = 0
                        dataLines.append(dataLine)
                        dataLine = ''

                        for _ in range(positionTextBefore, positionText - len(data[4]), 1):
                            valueField += ' '
                        valueField += data[4]

                        dataLine += valueField
                    numberLineBefore = numberLine
                    positionTextBefore = positionText

    return dataLines


def pdfToExcel(pdf_file_path, excel_file_path):
    pass
    # tables = tabula.read_pdf(pdf_file_path, pages='all')

    # # Write each table to a separate sheet in the Excel file
    # with pandas.ExcelWriter(excel_file_path) as writer:
    #     for i, table in enumerate(tables):
    #         table.to_excel(writer, sheet_name=f'Sheet{i+1}')
