try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, treatNumberField, validateCPF, validateCNPJ
except Exception as e:
    print(f"Error importing libraries {e}")


def validateIfCnpjOrCpfIsValid(data: Dict[str, Any], dataSetting: Dict[str, Any]):
    cgce = treatNumberField(returnDataInDictOrArray(data, ['cgceProvider']))

    if cgce is None or cgce == 0:
        return ""

    if dataSetting['validateIfCnpjOrCpfIsValid'] is False:
        return cgce
    else:
        cgceValid = False
        if len(cgce) <= 11:
            cgceValid = validateCPF(cgce)
        else:
            cgceValid = validateCNPJ(cgce)
        return "" if cgceValid is False else cgce
