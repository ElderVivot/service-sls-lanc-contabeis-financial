try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, returnBankForName, returnBankForNumber
except Exception as e:
    print(f"Error importing libraries {e}")


def correlationBankAndAccountBetweenSettingsAndClient(valuesOfLine: Dict[str, Any], bankAndAccountCorrelation: Dict[str, Any]):
    # :valuesOfLine é o banco que vem lá do financeiro do cliente já passado pelo treatDataLayout
    # :bankAndAccountCorrelation recebe as configurações do de-para dos bancos

    bankFinancy = returnDataInDictOrArray(valuesOfLine, ['bank'])
    accountFinancy = returnDataInDictOrArray(valuesOfLine, ['account'])

    if bankAndAccountCorrelation is not None and len(bankAndAccountCorrelation) > 0:
        for correlation in bankAndAccountCorrelation:
            correlationBankFile = returnDataInDictOrArray(correlation, ['bankFile']).replace('-', '')
            correlationAccountFile = returnDataInDictOrArray(correlation, ['accountFile']).replace('-', '')
            correlationAccountFile = "" if correlationAccountFile == "0" else correlationAccountFile

            correlationBankNew = returnBankForNumber(returnDataInDictOrArray(correlation, ['bankNew']).replace('-', ''))
            correlationAccountNew = returnDataInDictOrArray(correlation, ['accountNew']).replace('-', '')
            correlationAccountNew = "" if correlationAccountNew == "0" else correlationAccountNew
            ledgerAccountNew = returnDataInDictOrArray(correlation, ['ledgerAccount'])

            if correlationAccountFile == "":
                if bankFinancy == correlationBankFile:
                    valuesOfLine['bank'] = correlationBankNew
                    valuesOfLine['account'] = correlationAccountNew
                    valuesOfLine['ledgerAccount'] = ledgerAccountNew
                    break

            if bankFinancy == correlationBankFile and accountFinancy == correlationAccountFile:
                valuesOfLine['bank'] = correlationBankNew
                valuesOfLine['account'] = correlationAccountNew
                valuesOfLine['ledgerAccount'] = ledgerAccountNew
                break

            valuesOfLine['bank'] = bankFinancy
            valuesOfLine['account'] = accountFinancy
            valuesOfLine['ledgerAccount'] = ''
    else:
        valuesOfLine['bank'] = bankFinancy
        valuesOfLine['account'] = accountFinancy
        valuesOfLine['ledgerAccount'] = ''

    valuesOfLine['bankAndAccount'] = f"{valuesOfLine['bank']}-{valuesOfLine['account']}"

    return valuesOfLine
