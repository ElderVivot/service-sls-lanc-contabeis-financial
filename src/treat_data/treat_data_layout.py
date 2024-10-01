try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, treatTextField, minimalizeSpaces, \
        treatNumberField, treatTextFieldInVector, treatDecimalFieldInVector, treatDateField, treatDateFieldInVector, treatDecimalField
except Exception as e:
    print(f"Error importing libraries {e}")


def identifiesTheLineThatTheDataIs(lineThatTheDataIs, data: Dict[str, Any], dataSetting: Dict[str, Any]):
    if len(lineThatTheDataIs) == 0:
        return {'isRowCorrect': False, 'informationIsOnOneLineBelowTheMain': False}

    line = None
    for lineOfFile in dataSetting['linesOfFile']:
        if lineOfFile['nameOfLine']['value'] == lineThatTheDataIs:
            line = lineOfFile
            break

    if line is None:
        return {'isRowCorrect': False, 'informationIsOnOneLineBelowTheMain': False}

    countValidationsOK = 0
    countValidationsConfigured = 0

    for key, validation in enumerate(line['validations']):
        positionInFile = treatNumberField(returnDataInDictOrArray(validation, ['positionInFile'], 0), isInt=True, replaceHifen=False)
        positionInFileEnd = treatNumberField(returnDataInDictOrArray(validation, ['positionInFileEnd'], 0), isInt=True, replaceHifen=False)
        typeValidation = returnDataInDictOrArray(validation, ['typeValidation'])
        valueValidation = treatTextField(returnDataInDictOrArray(validation, ['valueValidation']))
        nextValidationOrAnd = returnDataInDictOrArray(validation, ['nextValidationOrAnd'], 'and')
        valueFieldData = treatTextFieldInVector(data, positionInFile, positionInFileEnd=positionInFileEnd)

        if nextValidationOrAnd == 'and' or key == len(validation) - 1:
            countValidationsConfigured += 1

        if typeValidation == "isDate":
            valueFieldData = treatDateFieldInVector(data, positionInFile, positionInFileEnd=positionInFileEnd)
            if str(type(valueFieldData)).count("datetime.date") > 0:
                countValidationsOK += 1
        elif typeValidation == "isEqual" and valueValidation == valueFieldData:
            countValidationsOK += 1
        elif typeValidation == "contains" and valueFieldData.find(valueValidation) >= 0:
            countValidationsOK += 1
        elif typeValidation == "notContains" and valueFieldData.find(valueValidation) == -1:
            countValidationsOK += 1
        elif typeValidation == "isLessThan" and valueFieldData < valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isLessThanOrEqual" and valueFieldData <= valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isBiggerThan" and valueFieldData > valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isBiggerThanOrEqual" and valueFieldData >= valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isDifferent" and valueFieldData != valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isEmpty" and valueFieldData == "":
            countValidationsOK += 1
        elif typeValidation == "isNotEmpty" and valueFieldData != "":
            countValidationsOK += 1

    if countValidationsOK == countValidationsConfigured:
        return {'isRowCorrect': True, 'informationIsOnOneLineBelowTheMain': line['informationIsOnOneLineBelowTheMain']}
    else:
        return {'isRowCorrect': False, 'informationIsOnOneLineBelowTheMain': False}


def treatDataLayout(data: Dict[str, Any], settingFields: Dict[str, Any], positionsOfHeader,
                    dataSetting: Dict[str, Any], readOnlyIfLineBelowTheMain=False, fileType='excel', splitFilePDFBySpace=False,
                    charsToSplitBySpace='  '):
    # o readOnlyIfLineBelowTheMain serve pra ler as linhas que estão uma abaixo da principal, pra poder agrupar com a linha anterior
    valuesOfLine: Dict[str, Any] = {}
    positionsOfHeaderCorrect = positionsOfHeader

    for settingField in settingFields:
        nameField: str = returnDataInDictOrArray(settingField, ['nameField', 'value'])

        positionInFile = treatNumberField(returnDataInDictOrArray(settingField, ['positionInFile'], 0), isInt=True, replaceHifen=False)
        positionInFileEnd = treatNumberField(returnDataInDictOrArray(settingField, ['positionInFileEnd'], 0), isInt=True, replaceHifen=False)

        nameColumn = treatTextField(returnDataInDictOrArray(settingField, ['nameColumn']))
        nameColumn = None if nameColumn == "" else nameColumn

        positionStartFindWord = treatTextField(returnDataInDictOrArray(settingField, ['positionStartFindWord']))
        positionStartFindWord = 0 if positionStartFindWord == "" else data.find(positionStartFindWord) + len(positionStartFindWord)

        positionEndFindWord = treatTextField(returnDataInDictOrArray(settingField, ['positionEndFindWord']))
        positionEndFindWord = -1 if positionEndFindWord == "" else data.find(positionEndFindWord)

        dataToSearch = data
        if fileType in ('txt', 'pdf') and (positionStartFindWord > 0 or positionEndFindWord > 0):
            if positionEndFindWord == -1:
                dataToSearch = data[positionStartFindWord:]
            else:
                dataToSearch = data[positionStartFindWord:positionEndFindWord]

            if positionStartFindWord > 0:
                positionInFile = 1
            if positionEndFindWord > 0:
                positionInFileEnd = len(dataToSearch) + 1

        if fileType in ('txt', 'pdf'):
            dataToSearch = charsToSplitBySpace[:-1] + dataToSearch  # add a space blank because to return data begins 1

        if fileType in ('txt', 'pdf') and splitFilePDFBySpace is True:
            dataToSearch = dataToSearch.split(charsToSplitBySpace[:-1])

        if positionInFileEnd != 0:
            positionInFileEnd = positionInFileEnd + 1

        # esta row é apenas pra identificar se a informação está na linha principal ou não, caso não esteja, vai guardar seu valor
        # na self._fieldsRowNotMain pra serem utilizados na linha principal depois
        lineThatTheDataIs = returnDataInDictOrArray(settingField, ['lineThatTheDataIs'], '')
        if lineThatTheDataIs != "":
            dataLine = identifiesTheLineThatTheDataIs(lineThatTheDataIs, dataToSearch, dataSetting)
            isRowCorrect = dataLine['isRowCorrect']
            informationIsOnOneLineBelowTheMain = dataLine['informationIsOnOneLineBelowTheMain']
        else:
            isRowCorrect = False
            informationIsOnOneLineBelowTheMain = False

        rowIsMain = returnDataInDictOrArray(valuesOfLine, ['row'])
        if rowIsMain == "" or rowIsMain == "main":
            if isRowCorrect is True:
                rowIsMain = 'not_main'
                positionsOfHeaderCorrect = {}
            else:
                rowIsMain = 'main'

        # se não for a linha correta mas o campo seja referente a uma linha notMain então ignora, pois este campo não é válido nesta linha
        if isRowCorrect is False and lineThatTheDataIs != "":
            continue

        # se a linha for "not_main" mas o isRowCorrect não retornar resultado, então quer dizer que aquele campo não é daquela linha not_main. Pode ser de outra.
        # if rowIsMain == "not_main" and isRowCorrect is False:
        #     continue

        if readOnlyIfLineBelowTheMain is True and (isRowCorrect is False or informationIsOnOneLineBelowTheMain is False):
            continue

        splitField = returnDataInDictOrArray(settingField, ['splitField'])
        positionFieldInTheSplit = treatNumberField(returnDataInDictOrArray(settingField, ['positionFieldInTheSplit'], 0), isInt=True, replaceHifen=False)
        positionFieldInTheSplitEnd = treatNumberField(returnDataInDictOrArray(settingField, ['positionFieldInTheSplitEnd'], 0),
                                                      isInt=True, replaceHifen=False)  # o zero determina que não tem fim, é daquele campo pra frente

        getByNameTab = False
        if positionInFile == -10:
            positionInFile = 0
            getByNameTab = True
        valueField = treatTextFieldInVector(dataToSearch, positionInFile, positionsOfHeaderCorrect, nameColumn, positionInFileEnd=positionInFileEnd, fileType=fileType)
        valueField = "" if positionInFile == 0 and getByNameTab is False and nameColumn is None else valueField
        # if getByNameTab is True:
        #     print(valueField)

        if splitField != "":
            valueField = valueField.split(splitField)
            if len(valueField) >= positionFieldInTheSplit:
                if positionFieldInTheSplitEnd != 0:
                    valueField = ' '.join(valueField[positionFieldInTheSplit - 1:positionFieldInTheSplitEnd])
                else:
                    valueField = ' '.join(valueField[positionFieldInTheSplit - 1:])
            else:
                valueField = ""
            valueField = minimalizeSpaces(valueField)

        if nameField == "account":
            valueField = minimalizeSpaces(valueField.replace('-', ''))
            valueField = treatNumberField(valueField, True)
            valueField = "" if valueField == 0 else str(valueField)

        if nameField == "bank":
            valueField = minimalizeSpaces(valueField.replace('-', ''))

        if nameField.lower().find('date') >= 0:
            formatDate = returnDataInDictOrArray(settingField, ['formatDate'])
            if formatDate == 'dd/mm/aaaa':
                formatDate = 1
            elif formatDate == 'aaaa-mm-dd':
                formatDate = 2
            elif formatDate == 'dd/mm/aa':
                formatDate = 5
            else:
                formatDate = 1

            if splitField != "":
                valueField = treatDateField(valueField, formatDate)
            else:
                valueField = treatDateFieldInVector(dataToSearch, positionInFile, positionsOfHeaderCorrect, nameColumn, formatDate, rowIsMain, positionInFileEnd=positionInFileEnd, fileType=fileType)
                valueField = None if positionInFile == 0 and nameColumn is None else valueField

        elif nameField.lower().find('amount') >= 0:
            if splitField != "":
                valueField = treatDecimalField(valueField)
            else:
                valueFieldOriginal = valueField
                valueField = treatDecimalFieldInVector(dataToSearch, positionInFile, positionsOfHeaderCorrect, nameColumn, positionInFileEnd=positionInFileEnd, fileType=fileType)
                valueField = 0 if positionInFile == 0 and nameColumn is None else round(valueField, 2)
                try:
                    if valueFieldOriginal[-1] == 'D':
                        valueField *= -1
                except Exception:
                    pass

        # else:

        valuesOfLine['row'] = rowIsMain
        valuesOfLine[nameField] = valueField

    return valuesOfLine
