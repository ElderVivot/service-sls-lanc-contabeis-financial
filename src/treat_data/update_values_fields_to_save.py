try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import formatDate, returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def updateValuesFieldsToSave(valuesOfLine: Dict[str, Any]):
    amountPaid = returnDataInDictOrArray(valuesOfLine, ['amountPaid'], 0.0)
    amountPaid = amountPaid * -1 if amountPaid < 0 else amountPaid
    amountReceived = returnDataInDictOrArray(valuesOfLine, ['amountReceived'], 0.0)
    amountPaidOrReceived = returnDataInDictOrArray(valuesOfLine, ['amountPaidOrReceived'], 0.0)
    if amountPaidOrReceived != 0:
        valuesOfLine['amountMoviment'] = amountPaidOrReceived
    else:
        valuesOfLine['amountMoviment'] = amountReceived if amountReceived > 0 else amountPaid * -1

    valuesOfLine['paymentDate'] = formatDate(returnDataInDictOrArray(valuesOfLine, ['paymentDate']), '%d/%m/%Y')
    valuesOfLine['dueDate'] = formatDate(returnDataInDictOrArray(valuesOfLine, ['dueDate']), '%d/%m/%Y')

    nameProvider = returnDataInDictOrArray(valuesOfLine, ['nameProvider'])
    nameClient = returnDataInDictOrArray(valuesOfLine, ['nameClient'])
    nameProviderClient = returnDataInDictOrArray(valuesOfLine, ['nameProviderClient'])
    if nameProviderClient == '':
        valuesOfLine['nameProviderClient'] = nameProvider if nameProvider != "" else nameClient

    valuesOfLine['accountDebit'] = valuesOfLine['ledgerAccount'] if amountReceived > 0 else ''
    valuesOfLine['accountCredit'] = valuesOfLine['ledgerAccount'] if amountPaid > 0 else ''

    return valuesOfLine
