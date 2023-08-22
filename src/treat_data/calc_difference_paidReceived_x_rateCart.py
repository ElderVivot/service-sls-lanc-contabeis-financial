try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def calcDifferencePaidReceivedXAmountOriginalAsRateCard(valuesOfLine: Dict[str, Any], dataSetting: Dict[str, Any]):
    amountReceived = returnDataInDictOrArray(valuesOfLine, ["amountReceived"], 0.0)
    amountOriginal = returnDataInDictOrArray(valuesOfLine, ["amountOriginal"], 0.0)

    if dataSetting['calcDifferencePaidOriginalAsRateCard'] is True:
        if amountReceived != 0:  # apenas pros recebimento que tem o desconto da taxa de cartao
            if amountReceived < amountOriginal:  # o valor que recebe é menor que o valor original, pq tem o desconto da taxa
                valuesOfLine['amountRate'] = amountOriginal - amountReceived

    return valuesOfLine
