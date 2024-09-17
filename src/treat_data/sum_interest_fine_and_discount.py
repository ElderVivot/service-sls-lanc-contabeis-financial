try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def sumInterestFineAndDiscount(valuesOfLine: Dict[str, Any], dataSetting: Dict[str, Any]):
    amountPaid = returnDataInDictOrArray(valuesOfLine, ["amountPaid"], 0.0)
    amountReceived = returnDataInDictOrArray(valuesOfLine, ["amountReceived"], 0.0)
    amountInterest = returnDataInDictOrArray(valuesOfLine, ["amountInterest"], 0.0)
    amountFine = returnDataInDictOrArray(valuesOfLine, ["amountFine"], 0.0)
    amountDiscount = returnDataInDictOrArray(valuesOfLine, ["amountDiscount"], 0.0)
    amountRate = returnDataInDictOrArray(valuesOfLine, ["amountRate"], 0.0)
    amountMoviment = returnDataInDictOrArray(valuesOfLine, ["amountMoviment"], 0.0)

    if dataSetting['sumInterestFineAndDiscount'] is True:
        if amountMoviment != 0:
            valuesOfLine['amountOriginal'] = amountMoviment if amountMoviment > 0 else (amountMoviment * -1)
            valuesOfLine['amountMoviment'] = amountMoviment + amountInterest + amountFine - amountDiscount - amountRate
        else:
            if amountPaid > 0:
                valuesOfLine['amountOriginal'] = amountPaid if amountPaid > 0 else (amountPaid * -1)
                valuesOfLine['amountPaid'] = amountPaid + amountInterest + amountFine - amountDiscount - amountRate
            else:
                valuesOfLine['amountOriginal'] = amountReceived if amountReceived > 0 else (amountReceived * -1)
                valuesOfLine['amountReceived'] = amountReceived + amountInterest + amountFine - amountDiscount - amountRate

    return valuesOfLine
