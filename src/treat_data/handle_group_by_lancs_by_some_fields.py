try:
    import unzip_requirements
except ImportError:
    pass

try:
    from operator import itemgetter
    from typing import Dict, Any, List
    from src.functions import returnDataInDictOrArray, treatTextField
except Exception as e:
    print(f"Error importing libraries {e}")


def handleGroupByLancsBySomeFields(valuesOfFile: List[Dict[str, Any]], dataSetting: Dict[str, Any]):
    groupingLancsByFields = dataSetting['groupingLancsByFields']
    if len(groupingLancsByFields.keys()) == 0:
        return valuesOfFile

    newDictFieldsToUseInGrouping = {}
    for key, valueField in groupingLancsByFields.items():
        if valueField is True:
            if key == 'paymentDate':
                newDictFieldsToUseInGrouping['paymentDateAsDate'] = True
            else:
                newDictFieldsToUseInGrouping[key] = True

    valuesOfFile = sorted(valuesOfFile, key=itemgetter(*newDictFieldsToUseInGrouping.keys()))

    valuesOfFileGroupingLancs = []

    for key, currentLine in enumerate(valuesOfFile):
        previousLine = returnDataInDictOrArray(valuesOfFile, [key - 1], {})

        currentField = ""
        for nameField, valueField in currentLine.items():
            if returnDataInDictOrArray(newDictFieldsToUseInGrouping, [nameField], False) is True:
                if valueField != '' and valueField is not None:
                    currentField = currentField + "-" + treatTextField(valueField)

        previousField = ""
        for nameField, valueField in previousLine.items():
            if returnDataInDictOrArray(newDictFieldsToUseInGrouping, [nameField], False) is True:
                if valueField != '' and valueField is not None:
                    previousField = previousField + "-" + treatTextField(valueField)

        if currentField == previousField:
            valuesOfFileGroupingLancs[-1]['amountMoviment'] += currentLine['amountMoviment']
            valuesOfFileGroupingLancs[-1]['amountPaid'] += currentLine['amountPaid']
            valuesOfFileGroupingLancs[-1]['amountReceived'] += currentLine['amountReceived']
            valuesOfFileGroupingLancs[-1]['amountPaidOrReceived'] += currentLine['amountPaidOrReceived']
            valuesOfFileGroupingLancs[-1]['amountOriginal'] += currentLine['amountOriginal']
            valuesOfFileGroupingLancs[-1]['amountInterest'] += currentLine['amountInterest']
            valuesOfFileGroupingLancs[-1]['amountFine'] += currentLine['amountFine']
            valuesOfFileGroupingLancs[-1]['amountDiscount'] += currentLine['amountDiscount']
            valuesOfFileGroupingLancs[-1]['amountRate'] += currentLine['amountRate']
        else:
            valuesOfFileGroupingLancs.append(currentLine.copy())

    return valuesOfFileGroupingLancs
