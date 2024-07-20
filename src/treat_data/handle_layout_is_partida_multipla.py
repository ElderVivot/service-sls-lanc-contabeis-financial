try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any, List
    from src.functions import returnDataInDictOrArray, treatTextField
except Exception as e:
    print(f"Error importing libraries {e}")


def handleLayoutIsPartidaMultipla(valuesOfFile: List[Dict[str, Any]], dataSetting: Dict[str, Any]):
    valuesOfFilePartidaMultipla = []
    existLancInLote = False

    for key, currentLine in enumerate(valuesOfFile):
        previousLine = returnDataInDictOrArray(valuesOfFile, [key - 1], {})
        numberLote = returnDataInDictOrArray(previousLine, ["numberLote"], 0)

        groupingFields = dataSetting['groupingFields']

        # se não houver campos agrupadores de informações cada registro será um lote sequencial
        if len(groupingFields) == 0:
            numberLote += 1
            currentLine['numberLote'] = numberLote
            valuesOfFilePartidaMultipla.append(currentLine)
            continue  # não tem pq processar as linhas abaixo pq o layout não tem campo agrupador

        lineValidGrouping = True

        currentField = ""
        for nameField, valueField in currentLine.items():
            if returnDataInDictOrArray(groupingFields, [nameField], False) is True:
                if valueField == '':
                    lineValidGrouping = False
                currentField = currentField + "-" + treatTextField(valueField)

        previousField = ""
        for nameField, valueField in previousLine.items():
            if returnDataInDictOrArray(groupingFields, [nameField], False) is True:
                if valueField == '':
                    lineValidGrouping = False
                previousField = previousField + "-" + treatTextField(valueField)

        if currentField == previousField and lineValidGrouping is True:
            existLancInLote = True
            currentLine['numberLote'] = numberLote
            valuesOfFilePartidaMultipla.append(currentLine)
        else:
            numberLote += 1
            currentLine['numberLote'] = numberLote
            valuesOfFilePartidaMultipla.append(currentLine)

    return valuesOfFilePartidaMultipla, existLancInLote
