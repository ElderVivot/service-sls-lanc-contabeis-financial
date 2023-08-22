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
    valuesOfLine['issueDate'] = formatDate(returnDataInDictOrArray(valuesOfLine, ['issueDate']), '%d/%m/%Y')

    nameProvider = returnDataInDictOrArray(valuesOfLine, ['nameProvider'])
    nameClient = returnDataInDictOrArray(valuesOfLine, ['nameClient'])
    nameProviderClient = returnDataInDictOrArray(valuesOfLine, ['nameProviderClient'])
    if nameProviderClient == '':
        valuesOfLine['nameProviderClient'] = nameProvider if nameProvider != "" else nameClient

    valuesOfLine['accountDebit'] = valuesOfLine['ledgerAccount'] if amountReceived > 0 else ''
    valuesOfLine['accountCredit'] = valuesOfLine['ledgerAccount'] if amountPaid > 0 else ''

    # fields that can null
    valuesOfLine['document'] = returnDataInDictOrArray(valuesOfLine, ['document'])
    valuesOfLine['nameProvider'] = returnDataInDictOrArray(valuesOfLine, ['nameProvider'])
    valuesOfLine['nameClient'] = returnDataInDictOrArray(valuesOfLine, ['nameClient'])
    valuesOfLine['nameProviderClient'] = returnDataInDictOrArray(valuesOfLine, ['nameProviderClient'])
    valuesOfLine['cgceProviderClient'] = returnDataInDictOrArray(valuesOfLine, ['cgceProviderClient'])
    valuesOfLine['bank'] = returnDataInDictOrArray(valuesOfLine, ['bank'])
    valuesOfLine['account'] = returnDataInDictOrArray(valuesOfLine, ['account'])
    valuesOfLine['amountOriginal'] = returnDataInDictOrArray(valuesOfLine, ['amountOriginal'], 0.0)
    valuesOfLine['amountInterest'] = returnDataInDictOrArray(valuesOfLine, ['amountInterest'], 0.0)
    valuesOfLine['amountFine'] = returnDataInDictOrArray(valuesOfLine, ['amountFine'], 0.0)
    valuesOfLine['amountDiscount'] = returnDataInDictOrArray(valuesOfLine, ['amountDiscount'], 0.0)
    valuesOfLine['amountRate'] = returnDataInDictOrArray(valuesOfLine, ['amountRate'], 0.0)
    valuesOfLine['historic'] = returnDataInDictOrArray(valuesOfLine, ['historic'])
    valuesOfLine['category'] = returnDataInDictOrArray(valuesOfLine, ['category'])
    valuesOfLine['accountPlan'] = returnDataInDictOrArray(valuesOfLine, ['accountPlan'])
    valuesOfLine['parcelNumber'] = returnDataInDictOrArray(valuesOfLine, ['parcelNumber'])
    valuesOfLine['companyBranch'] = returnDataInDictOrArray(valuesOfLine, ['companyBranch'])
    valuesOfLine['typeMoviment'] = returnDataInDictOrArray(valuesOfLine, ['typeMoviment'])

    return valuesOfLine
