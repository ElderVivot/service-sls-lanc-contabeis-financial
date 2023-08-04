try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def considerAmountPaidOrAmountReceived(valuesOfLine: Dict[str, Any], dataSetting: Dict[str, Any]):
    for nameField, valueField in valuesOfLine.items():
        if returnDataInDictOrArray(dataSetting['fieldsThatMultiplePerLessOne'], [nameField], False) is True:
            valuesOfLine[nameField] = valueField * (-1) if valueField < 0 else valueField

    return valuesOfLine
