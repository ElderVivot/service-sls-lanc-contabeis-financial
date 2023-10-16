try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, treatTextField, treatDecimalField
except Exception as e:
    print(f"Error importing libraries {e}")


def bankAndAccountInTheCorrelation(bank, account: Dict[str, Any], bankAndAccountCorrelation: Dict[str, Any]):
    # :valuesOfLine é o banco que vem lá do financeiro do cliente já passado pelo treatDataLayout
    # :bankAndAccountCorrelation recebe as configurações do de-para dos bancos
    if bankAndAccountCorrelation is None:
        return True

    for correlation in bankAndAccountCorrelation:
        correlationBankNew = returnDataInDictOrArray(correlation, ['bankNew']).replace('-', '')
        correlationAccountNew = str(returnDataInDictOrArray(correlation, ['accountNew'])).replace('-', '')
        correlationAccountNew = "" if correlationAccountNew == "0" else correlationAccountNew

        if bank == correlationBankNew and account == correlationAccountNew:
            return True


def isValidDataThisCompanie(valuesOfLine, validateIfDataIsThisCompanie, bankAndAccountCorrelation):
    """
    :param valuesOfLine: valores normais da linha onde a verificação será será feita
    :parm validateIfDataIsThisCompanie: configurações do IntegrattionCompanies onde tem as verificações pra ver é uma linha válida ou não
    """
    if validateIfDataIsThisCompanie is None or len(validateIfDataIsThisCompanie) == 0:
        return True

    countValidationsOK = 0
    countValidationsConfigured = 0

    for key, validation in enumerate(validateIfDataIsThisCompanie):
        nameField = returnDataInDictOrArray(validation, ['nameField'])
        typeValidation = returnDataInDictOrArray(validation, ['typeValidation'])
        valueValidation = treatTextField(returnDataInDictOrArray(validation, ['valueValidation']))
        valueValidation = treatDecimalField(valueValidation) if nameField.find('amount') >= 0 else valueValidation
        nextValidationOrAnd = returnDataInDictOrArray(validation, ['nextValidationOrAnd'], 'and')

        valueFieldData = returnDataInDictOrArray(valuesOfLine, [nameField])

        if nextValidationOrAnd == 'and' or key == len(validateIfDataIsThisCompanie) - 1:
            countValidationsConfigured += 1

        if typeValidation == "banksInTheCorrelation":
            bank = returnDataInDictOrArray(valuesOfLine, ['bank'])
            account = returnDataInDictOrArray(valuesOfLine, ['account'])
            bankAndAccountInCorrelation = bankAndAccountInTheCorrelation(bank, account, bankAndAccountCorrelation)
            if bankAndAccountInCorrelation is True:
                countValidationsOK += 1
        elif typeValidation == "isLessThan" and valueFieldData < valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isLessThanOrEqual" and valueFieldData <= valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isBiggerThan" and valueFieldData > valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isBiggerThanOrEqual" and valueFieldData >= valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isEqual" and valueFieldData == valueValidation:
            countValidationsOK += 1
        elif typeValidation == "isDate" and str(type(valueFieldData)).count('datetime.date') > 0:
            countValidationsOK += 1
        elif typeValidation == "isDifferent" and valueFieldData != valueValidation:
            countValidationsOK += 1
        elif typeValidation == "contains" and valueFieldData.find(valueValidation) >= 0:
            countValidationsOK += 1
        elif typeValidation == "notContains" and valueFieldData.find(valueValidation) < 0:
            countValidationsOK += 1
        elif typeValidation == "isEmpty" and valueFieldData == "":
            countValidationsOK += 1
        elif typeValidation == "isNotEmpty" and valueFieldData != "":
            countValidationsOK += 1

    if countValidationsOK >= countValidationsConfigured:
        return True
