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
    amountMoviment = returnDataInDictOrArray(valuesOfLine, ["amountMoviment"], 0.0)

    if dataSetting['sumInterestFineAndDiscount'] is True:
        if amountMoviment != 0:
            valuesOfLine['amountMoviment'] = amountMoviment + amountInterest + amountFine - amountDiscount
        else:
            if amountPaid > 0 and amountMoviment == 0:
                valuesOfLine['amountPaid'] = amountPaid + amountInterest + amountFine - amountDiscount
            else:
                valuesOfLine['amountReceived'] = amountReceived + amountInterest + amountFine - amountDiscount

    return valuesOfLine
