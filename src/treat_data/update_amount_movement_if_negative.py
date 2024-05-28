try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, returnBankForName, returnBankForNumber
except Exception as e:
    print(f"Error importing libraries {e}")


def updateAmountMovementIfNegative(valuesOfLine: Dict[str, Any]):
    # :valuesOfLine é o banco que vem lá do financeiro do cliente já passado pelo treatDataLayout

    amountPaidOrReceived = returnDataInDictOrArray(valuesOfLine, ['amountPaidOrReceived'], 0)

    typeMoviment = returnDataInDictOrArray(valuesOfLine, ['typeMoviment'], None)
    if typeMoviment is not None:
        typeMoviment = typeMoviment[:3]
        if typeMoviment in ('D', 'DEB', 'SAI', 'PAG'):
            if amountPaidOrReceived > 0:
                valuesOfLine['amountPaidOrReceived'] = amountPaidOrReceived * -1
    return valuesOfLine
