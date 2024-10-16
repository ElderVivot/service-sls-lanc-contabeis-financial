from typing import Dict, Any
from src.functions import treatTextField


def mountHistoric(lanc: Dict[str, Any], historicComposition: str):
    textsToSearch = {
        'NF_DOC': 'document',
        'NOME_CLIENTE_FORNECEDOR': 'nameProviderClient',
        'HISTORICO': 'historic',
        'CATEGORIA': 'category',
        'PLANO_CONTAS': 'accountPlan',
        'TIPO_MOVIMENTO': 'typeMoviment',
        'FILIAL_EMPRESA': 'companyBranch',
        'NUMERO_PARCELA': 'parcelNumber'
    }

    if historicComposition != "":
        historicCompositionSplit = historicComposition.split('[')
        newHistoric = ''
        for historicC in historicCompositionSplit:
            findHistoricToSearch = False
            for text, field in textsToSearch.items():
                posColchete = historicC.find(']')
                if historicC.find(text) >= 0:
                    findHistoricToSearch = True
                    valueField = lanc[field]
                    if valueField != '' and text in ('NF_DOC'):  # and treatNumberField(valueField, isInt=True) > 0:
                        newHistoric = newHistoric + historicC.replace(text, valueField)
                    elif valueField != '' and text not in ('NF_DOC'):
                        newHistoric = newHistoric + historicC.replace(text, valueField)
                    else:
                        newHistoric = newHistoric + historicC[posColchete:]
                    newHistoric = newHistoric.replace(']', '')
                    break
            if findHistoricToSearch is False:
                newHistoric = newHistoric + historicC
        return treatTextField(newHistoric)
    else:
        lanc['historic'] = treatTextField(lanc['historic'])
        if lanc["historic"] != "":
            return lanc["historic"]
        if lanc["document"] != "" and lanc["nameProviderClient"] != "":
            return f"NF/DOC {lanc['document']} - {lanc['nameProviderClient']}"
        if lanc["document"] == "" and lanc["nameProviderClient"] != "":
            return lanc["nameProviderClient"]
        return ""
