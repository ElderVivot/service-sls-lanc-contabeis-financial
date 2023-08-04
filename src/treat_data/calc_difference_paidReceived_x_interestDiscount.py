try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def calcDifferencePaidReceivedXAmountOriginalAsInterestDiscount(valuesOfLine: Dict[str, Any], dataSetting: Dict[str, Any]):
    amountPaid = returnDataInDictOrArray(valuesOfLine, ["amountPaid"], 0.0)
    amountReceived = returnDataInDictOrArray(valuesOfLine, ["amountReceived"], 0.0)
    amountOriginal = returnDataInDictOrArray(valuesOfLine, ["amountOriginal"], 0.0)

    if dataSetting['calcDifferencePaidOriginalAsInterestDiscount'] is True:
        if amountPaid != 0:
            if amountPaid > amountOriginal:
                valuesOfLine['amountInterest'] = amountPaid - amountOriginal
            if amountPaid < amountOriginal:
                valuesOfLine['amountDiscount'] = amountOriginal - amountPaid
        if amountReceived != 0:
            if amountReceived > amountOriginal:
                valuesOfLine['amountInterest'] = amountReceived - amountOriginal
            if amountReceived < amountOriginal:
                valuesOfLine['amountDiscount'] = amountOriginal - amountReceived

    return valuesOfLine
