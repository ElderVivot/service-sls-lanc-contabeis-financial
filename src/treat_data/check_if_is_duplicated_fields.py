try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any, List
    from src.functions import returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def checkIfItIsDuplicatedFields(valuesOfFile: List[Dict[str, Any]], dataSetting: Dict[str, Any]):
    if len(dataSetting['considerToCheckIfItIsDuplicatedFields']) > 0:
        newValuesOfFile = []
        arrayFieldToCheckDuplicate: List[Any] = []
        for valuesOfLine in valuesOfFile:
            valuesOfLine['fieldToCheckDuplicate'] = ''

            for field in valuesOfLine.items():
                nameField = field[0]
                valueField = field[1]

                fieldToCheck = returnDataInDictOrArray(dataSetting['considerToCheckIfItIsDuplicatedFields'], [nameField], False)
                if fieldToCheck is True:
                    valuesOfLine['fieldToCheckDuplicate'] += str(valueField)

            if arrayFieldToCheckDuplicate.count(valuesOfLine['fieldToCheckDuplicate']) == 0:
                arrayFieldToCheckDuplicate.append(valuesOfLine['fieldToCheckDuplicate'])
                newValuesOfFile.append(valuesOfLine.copy())

        return newValuesOfFile
    else:
        return valuesOfFile
