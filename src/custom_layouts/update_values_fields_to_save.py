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

    paymentDate = returnDataInDictOrArray(valuesOfLine, ['paymentDate'])
    valuesOfLine['paymentDate'] = formatDate(paymentDate, '%d/%m/%Y')
    valuesOfLine['paymentDateAsDate'] = formatDate(paymentDate, '%Y%m%d')
    valuesOfLine['dueDate'] = formatDate(returnDataInDictOrArray(valuesOfLine, ['dueDate']), '%d/%m/%Y')
    valuesOfLine['issueDate'] = formatDate(returnDataInDictOrArray(valuesOfLine, ['issueDate']), '%d/%m/%Y')

    accountDebit = returnDataInDictOrArray(valuesOfLine, ['accountDebit'])
    accountCredit = returnDataInDictOrArray(valuesOfLine, ['accountCredit'])

    valuesOfLine['codeHistoric'] = returnDataInDictOrArray(valuesOfLine, ['codeHistoric'])
    valuesOfLine['typeLanc'] = returnDataInDictOrArray(valuesOfLine, ['typeLanc'])
    valuesOfLine['typeDocument'] = returnDataInDictOrArray(valuesOfLine, ['typeDocument'])
    valuesOfLine['codeParticipante'] = returnDataInDictOrArray(valuesOfLine, ['codeParticipante'])
    valuesOfLine['codeImovel'] = returnDataInDictOrArray(valuesOfLine, ['codeImovel'])

    nameProvider = returnDataInDictOrArray(valuesOfLine, ['nameProvider'])
    nameClient = returnDataInDictOrArray(valuesOfLine, ['nameClient'])
    nameProviderClient = returnDataInDictOrArray(valuesOfLine, ['nameProviderClient'])
    if nameProviderClient == '':
        valuesOfLine['nameProviderClient'] = nameProvider if nameProvider != "" else nameClient

    valuesOfLine['accountDebit'] = valuesOfLine['ledgerAccount'] if amountReceived > 0 else ''
    valuesOfLine['accountCredit'] = valuesOfLine['ledgerAccount'] if amountPaid > 0 else ''

    accountProviderClient = returnDataInDictOrArray(valuesOfLine, ['accountProviderClient'])
    accountProvider = returnDataInDictOrArray(valuesOfLine, ['accountProvider'])
    accountClient = returnDataInDictOrArray(valuesOfLine, ['accountClient'])
    if (amountPaidOrReceived < 0 or amountPaid != 0) and (accountProviderClient != '' or accountProvider != ''):
        valuesOfLine['accountDebit'] = accountProviderClient if accountProviderClient != '' else accountProvider
    if (amountPaidOrReceived > 0 or amountReceived != 0) and (accountProviderClient != '' or accountClient != ''):
        valuesOfLine['accountCredit'] = accountProviderClient if accountProviderClient != '' else accountClient

    valuesOfLine['accountDebit'] = accountDebit if accountDebit != '' else valuesOfLine['accountDebit']
    valuesOfLine['accountCredit'] = accountCredit if accountCredit != '' else valuesOfLine['accountCredit']

    # fields that can null
    valuesOfLine['document'] = returnDataInDictOrArray(valuesOfLine, ['document'])
    valuesOfLine['nameProvider'] = returnDataInDictOrArray(valuesOfLine, ['nameProvider'])
    valuesOfLine['nameClient'] = returnDataInDictOrArray(valuesOfLine, ['nameClient'])
    valuesOfLine['nameProviderClient'] = returnDataInDictOrArray(valuesOfLine, ['nameProviderClient'])
    valuesOfLine['cgceProviderClient'] = returnDataInDictOrArray(valuesOfLine, ['cgceProviderClient'])
    valuesOfLine['bank'] = returnDataInDictOrArray(valuesOfLine, ['bank'])
    valuesOfLine['account'] = returnDataInDictOrArray(valuesOfLine, ['account'])
    valuesOfLine['amountPaid'] = returnDataInDictOrArray(valuesOfLine, ['amountPaid'], 0.0)
    valuesOfLine['amountReceived'] = returnDataInDictOrArray(valuesOfLine, ['amountReceived'], 0.0)
    valuesOfLine['amountPaidOrReceived'] = returnDataInDictOrArray(valuesOfLine, ['amountPaidOrReceived'], 0.0)
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
