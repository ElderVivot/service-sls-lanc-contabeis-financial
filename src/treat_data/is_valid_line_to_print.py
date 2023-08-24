try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, treatTextField, treatDecimalField
except Exception as e:
    print(f"Error importing libraries {e}")


def isValidLineToPrint(data: Dict[str, Any], dataSetting: Dict[str, Any]):
    countValidationsOK = 0
    countValidationsConfigured = 0
    for key, validation in enumerate(dataSetting['validationsLineToPrint']):
        nextValidationOrAnd = returnDataInDictOrArray(validation, ['nextValidationOrAnd'], 'and')

        if nextValidationOrAnd == 'and' or key == len(dataSetting['validationsLineToPrint']) - 1:
            countValidationsConfigured += 1

        nameField: str = returnDataInDictOrArray(validation, ['nameField'])
        typeValidation = returnDataInDictOrArray(validation, ['typeValidation'])
        valueValidation = treatTextField(returnDataInDictOrArray(validation, ['valueValidation']))
        valueValidation = treatDecimalField(valueValidation) if nameField.find('amount') >= 0 else valueValidation

        valueFieldData: str = returnDataInDictOrArray(data, [nameField])

        if typeValidation == "isLessThan" and valueFieldData < valueValidation:
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

    paymentDate = returnDataInDictOrArray(data, ['paymentDate'], None)
    amountPaid = returnDataInDictOrArray(data, ['amountPaid'], 0.0)
    amountReceived = returnDataInDictOrArray(data, ['amountReceived'])
    amountPaidOrReceived = returnDataInDictOrArray(data, ['amountPaidOrReceived'], 0.0)

    existSomeAmount = False
    if amountPaid != 0 or amountReceived != 0 or amountPaidOrReceived != 0:
        existSomeAmount = True

    # paymentDate is obrigatory and existSomeAmount too, to exist data of payment
    if countValidationsOK >= countValidationsConfigured and str(type(paymentDate)).count('datetime.date') > 0 and paymentDate is not None and existSomeAmount is True:
        return True
