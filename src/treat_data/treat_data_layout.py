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
        positionInFile = int(returnDataInDictOrArray(validation, ['positionInFile'], -1))
        positionInFileEnd = returnDataInDictOrArray(validation, ['positionInFileEnd'], -1)
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
                    dataSetting: Dict[str, Any], readOnlyIfLineBelowTheMain=False, fileType='excel'):
    # o readOnlyIfLineBelowTheMain serve pra ler as linhas que estão uma abaixo da principal, pra poder agrupar com a linha anterior
    valuesOfLine: Dict[str, Any] = {}
    positionsOfHeaderCorrect = positionsOfHeader

    for settingField in settingFields:
        nameField: str = returnDataInDictOrArray(settingField, ['nameField', 'value'])

        positionInFile = int(returnDataInDictOrArray(settingField, ['positionInFile'], -1))
        positionInFile = positionInFile - 1 if fileType == 'txt' else positionInFile
        positionInFileEnd = returnDataInDictOrArray(settingField, ['positionInFileEnd'], -1)

        nameColumn = treatTextField(returnDataInDictOrArray(settingField, ['nameColumn']))
        nameColumn = None if nameColumn == "" else nameColumn

        # esta row é apenas pra identificar se a informação está na linha principal ou não, caso não esteja, vai guardar seu valor
        # na self._fieldsRowNotMain pra serem utilizados na linha principal depois
        lineThatTheDataIs = returnDataInDictOrArray(settingField, ['lineThatTheDataIs'], '')
        if lineThatTheDataIs != "":
            dataLine = identifiesTheLineThatTheDataIs(lineThatTheDataIs, data, dataSetting)
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
        if rowIsMain == "not_main" and isRowCorrect is False:
            continue

        if readOnlyIfLineBelowTheMain is True and (isRowCorrect is False or informationIsOnOneLineBelowTheMain is False):
            continue

        splitField = returnDataInDictOrArray(settingField, ['splitField'])
        positionFieldInTheSplit = treatNumberField(returnDataInDictOrArray(settingField, ['positionFieldInTheSplit'], 0), isInt=True)
        positionFieldInTheSplitEnd = treatNumberField(returnDataInDictOrArray(settingField, ['positionFieldInTheSplitEnd'], 0), isInt=True)  # o zero determina que não tem fim, é daquele campo pra frente

        valueField = treatTextFieldInVector(data, positionInFile, positionsOfHeaderCorrect, nameColumn, positionInFileEnd=positionInFileEnd)
        valueField = "" if positionInFile <= 0 and nameColumn is None else valueField

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
                valueField = treatDateFieldInVector(data, positionInFile, positionsOfHeaderCorrect, nameColumn, formatDate, rowIsMain, positionInFileEnd=positionInFileEnd)
                valueField = None if positionInFile <= 0 and nameColumn is None else valueField

        elif nameField.lower().find('amount') >= 0:
            if splitField != "":
                valueField = treatDecimalField(valueField)
            else:
                valueFieldOriginal = valueField
                valueField = treatDecimalFieldInVector(data, positionInFile, positionsOfHeaderCorrect, nameColumn, positionInFileEnd=positionInFileEnd)
                valueField = 0 if positionInFile <= 0 and nameColumn is None else round(valueField, 2)
                try:
                    if valueFieldOriginal[-1] == 'D':
                        valueField *= -1
                except Exception:
                    pass

        # else:

        valuesOfLine['row'] = rowIsMain
        valuesOfLine[nameField] = valueField

    return valuesOfLine
