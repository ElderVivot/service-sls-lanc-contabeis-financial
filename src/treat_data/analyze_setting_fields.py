try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray, removeAnArrayFromWithinAnother
except Exception as e:
    print(f"Error importing libraries {e}")

# avalia quais configurações são importantes pro processamento de outros campos, tais como _groupingFields, etc
# além disso, ele reagrupa os fields pra trazer primeiro o que tem o atributo dataIsNotLineMain, pra depois trazer os  que não tem
# isto é necessário afim de que um campo numa linha not_main ele só seja preenchido se de fato ele tiver naquela linha


def analyzeSettingFields(settingFields: Dict[str, Any], dataSetting: Dict[str, Any]):
    fieldsHasDataIsNotLineMain = []
    fieldsDontHasDataIsNotLineMain = []

    for settingField in settingFields:
        nameField = returnDataInDictOrArray(settingField, ['nameField', 'value'])

        # --- este agrupamento é pra fazer a leitura de quando for um registro com vários débito pra vários créditos
        groupingField = returnDataInDictOrArray(settingField, ['groupingField'], False)
        if groupingField is True:
            dataSetting["groupingFields"][nameField] = True

        # --- este agrupamento é pra fazer a leitura de quando for um registro com vários débito pra vários créditos
        groupingLancsByField = returnDataInDictOrArray(settingField, ['groupingLancsByField'], False)
        if groupingLancsByField is True:
            dataSetting["groupingLancsByFields"][nameField] = True

        considerToCheckIfItIsDuplicatedFields = returnDataInDictOrArray(settingField, ['considerToCheckIfItIsDuplicated'], False)
        if considerToCheckIfItIsDuplicatedFields is True:
            dataSetting["considerToCheckIfItIsDuplicatedFields"][nameField] = True

        if nameField == "amountPaid" or nameField == "amountReceived":
            dataSetting["sumInterestFineAndDiscount"] = returnDataInDictOrArray(settingField, ['sumInterestFineAndDiscount'], False)
            dataSetting["calcDifferencePaidOriginalAsInterestDiscount"] = returnDataInDictOrArray(settingField, ['calcDifferencePaidOriginalAsInterestDiscount'], False)
            dataSetting["calcDifferencePaidOriginalAsRateCard"] = returnDataInDictOrArray(settingField, ['calcDifferencePaidOriginalAsRateCard'], False)

        if nameField == "cgceProviderClient":
            dataSetting["validateIfCnpjOrCpfIsValid"] = returnDataInDictOrArray(settingField, ['validateIfCnpjOrCpfIsValid'], False)

        dataSetting["fieldsThatMultiplePerLessOne"][nameField] = returnDataInDictOrArray(settingField, ['multiplePerLessOne'], False)
        dataSetting["negativeIsAmountPaid"] = returnDataInDictOrArray(settingField, ['negativeIsAmountPaid'], False)
        dataSetting["positiveIsAmountReceived"] = returnDataInDictOrArray(settingField, ['positiveIsAmountReceived'], False)

        # estas linhas abaixo faz com que os campos que não estão em linhas principais vão pro 'final' da configuração, visto que
        # os campos que não estão na principal não devem ser impressos em linhas que são a principal
        lineThatTheDataIs = returnDataInDictOrArray(settingField, ['lineThatTheDataIs'], '')
        if lineThatTheDataIs != "":
            fieldsHasDataIsNotLineMain.append(settingField)
        else:
            fieldsDontHasDataIsNotLineMain.append(settingField)

    return {
        "dataSetting": dataSetting,
        "fieldsValidated": removeAnArrayFromWithinAnother([fieldsHasDataIsNotLineMain, fieldsDontHasDataIsNotLineMain])
    }
