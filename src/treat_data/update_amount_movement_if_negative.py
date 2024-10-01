try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, returnBankForName, returnBankForNumber
except Exception as e:
    print(f"Error importing libraries {e}")


def updateAmountMovementIfNegative(valuesOfLine: Dict[str, Any], existTypeMovimentAsProventoFolha=False):
    # :valuesOfLine é o banco que vem lá do financeiro do cliente já passado pelo treatDataLayout

    amountPaidOrReceived = returnDataInDictOrArray(valuesOfLine, ['amountPaidOrReceived'], 0)

    typeMoviment = returnDataInDictOrArray(valuesOfLine, ['typeMoviment'], None)
    if typeMoviment is not None:
        typeMoviment = typeMoviment[:3]
        if existTypeMovimentAsProventoFolha is True:
            if typeMoviment == 'P':
                valuesOfLine['typeMoviment'] = 'PROVENTOS'
            elif typeMoviment == 'D':
                valuesOfLine['typeMoviment'] = 'DESCONTOS'
                typeMoviment = 'DESCONTOS'
            elif typeMoviment == 'I':
                valuesOfLine['typeMoviment'] = 'INFORMATIVA'
            elif typeMoviment == 'ID':
                valuesOfLine['typeMoviment'] = 'INFORMATIVA DEDUTORA'

        if typeMoviment in ('D', 'DEB', 'SAI', 'PAG', 'PRO', 'P', 'I'):
            if amountPaidOrReceived > 0:
                valuesOfLine['amountPaidOrReceived'] = amountPaidOrReceived * -1
    return valuesOfLine
