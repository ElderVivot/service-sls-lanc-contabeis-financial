try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
except Exception as e:
    print(f"Error importing libraries {e}")


def groupsRowData(valuesOfLine: Dict[str, Any], dataSetting: Dict[str, Any]):
    for nameField, valueField in dataSetting['fieldsRowNotMain'].items():
        valuesOfLine[nameField] = valueField

    return valuesOfLine
