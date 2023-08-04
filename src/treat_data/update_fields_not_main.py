try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any
    from src.functions import returnDataInDictOrArray
except Exception as e:
    print(f"Error importing libraries {e}")


def getPositionFieldByNameField(settingFields, nameFieldSearch):
    for positionFieldInVector, settingField in enumerate(settingFields):
        nameField = returnDataInDictOrArray(settingField, ['nameField', 'value'])
        if nameField == nameFieldSearch:
            return positionFieldInVector


def updateFieldsNotMain(data: Dict[str, Any], settingFields: Dict[str, Any], dataSetting: Dict[str, Any]):
    # :data é os dados com informações dos campos daquela linha
    # :settingFields é o vetor de configuração de cada campo que fica no 'fields'
    row = returnDataInDictOrArray(data, ['row'])

    if row == 'not_main':
        for nameField, valueField in data.items():

            # pega a posição do campo do vetor do fields da tabela IntegrattionLayouts
            positionFieldInVector = getPositionFieldByNameField(settingFields, nameField)
            if positionFieldInVector is not None:
                lineThatTheDataIs = returnDataInDictOrArray(settingFields[positionFieldInVector], ['lineThatTheDataIs'], None)
            else:
                lineThatTheDataIs = None

            # faz validação dos campos pra ver se devem ser atualizados as informações ou não
            if lineThatTheDataIs is not None:
                dataSetting['fieldsRowNotMain'][nameField] = valueField

    return dataSetting
