# layout implemented to client ccaf1052-cc6f-4 - pdf_email_nutronordeste

try:
    import unzip_requirements
except ImportError:
    pass

try:
    import datetime
    import logging
    from typing import Dict, Any
    from src.functions import treatDateField, treatTextField, returnDataInDictOrArray, minimalizeSpaces, \
        treatDecimalField, formatDate, treatNumberField
    from src.save_data import SaveData
    from src.custom_layouts.update_values_fields_to_save import updateValuesFieldsToSave
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)


class L00001PdfEmailNutronordeste(object):
    def __init__(self, dataToSave: Dict[str, Any], dataTxt) -> None:
        self.__dataToSave = dataToSave
        self.__dataTxt = dataTxt

    def __updateDateStartAndDateEnd(self, dateMovement: datetime.datetime):
        if self.__dataToSave['startPeriod'] == '':
            self.__dataToSave['startPeriod'] = dateMovement
        if self.__dataToSave['startPeriod'] > dateMovement:
            self.__dataToSave['startPeriod'] = dateMovement

        if self.__dataToSave['endPeriod'] == '':
            self.__dataToSave['endPeriod'] = dateMovement
        if self.__dataToSave['endPeriod'] < dateMovement:
            self.__dataToSave['endPeriod'] = dateMovement

    def __setDefaultValuesOfLine(self):
        return {
            "paymentDate": None,
            "document": "",
            "nameProvider": '',
            "issueDate": None,
            "dueDate": None,
            "amountPaid": 0,
            "amountOriginal": 0,
            "amountInterest": 0,
            "amountDiscount": 0,
            "historic": '',
            "ledgerAccount": ''
        }

    async def processAsync(self):
        valuesOfLine = self.__setDefaultValuesOfLine()
        alreadyArrivedLinesToProcess = False

        try:
            for idxLine, line in enumerate(self.__dataTxt):
                dataValue = line
                dataValueLineBefore = returnDataInDictOrArray(self.__dataTxt, [idxLine - 1])
                dataValueLineNext = returnDataInDictOrArray(self.__dataTxt, [idxLine + 1])
                try:
                    dataValueSplitSpace = dataValue.split(' ')

                    field01 = returnDataInDictOrArray(dataValueSplitSpace, [0])

                    alreadyFindDateInThisLine = False

                    if (dataValue.find('VALOR PAGO') >= 0 or dataValue.find('BAIXADO') >= 0) or dataValue.find('TOTAL DO DIA') >= 0:
                        continue

                    if field01.find('DIA.') >= 0:
                        alreadyArrivedLinesToProcess = True
                        valuesOfLine = self.__setDefaultValuesOfLine()
                        continue

                    if alreadyArrivedLinesToProcess is False:
                        continue

                    if dataValue.find('OBSERVACAO') >= 0 and valuesOfLine['amountPaid'] > 0 and valuesOfLine['paymentDate'] is not None:
                        valuesOfLine['historic'] = valuesOfLine['historic'] + ' ' + dataValue
                        # print(idxLine, dataValue, valuesOfLine, sep=' | ')

                        if dataValueLineNext.find('OBSERVACAO') < 0:
                            valuesOfLine['nameProvider'] = treatTextField(valuesOfLine['nameProvider'])
                            self.__updateDateStartAndDateEnd(valuesOfLine['paymentDate'])
                            valuesOfLine['historic'] = treatTextField(valuesOfLine['historic'].replace('OBSERVACAO:', ''))
                            valuesOfLine = updateValuesFieldsToSave(valuesOfLine)

                            self.__dataToSave['lancs'].append(valuesOfLine.copy())

                            valuesOfLine = self.__setDefaultValuesOfLine()

                    if dataValue.find('OBSERVACAO') >= 0:
                        continue

                    idxFindAmountOriginal = -1
                    for idx, value in enumerate(dataValueSplitSpace):
                        alreadyGetThisValue = False
                        beforeValue = returnDataInDictOrArray(dataValueSplitSpace, [idx - 1])

                        # document
                        if idx == 1 and valuesOfLine['document'] == '':
                            valuesOfLine['document'] = treatNumberField(value)
                            alreadyGetThisValue = True

                        if alreadyFindDateInThisLine is False and treatDateField(value) is not None:
                            alreadyFindDateInThisLine = True

                        if treatDateField(value) is not None:
                            valuesOfLine['paymentDate'] = treatDateField(value)
                            alreadyGetThisValue = True

                        # nameProvider
                        if idx >= 4 and valuesOfLine['paymentDate'] is None and alreadyFindDateInThisLine is False and alreadyGetThisValue is False and value not in ('D'):
                            valuesOfLine['nameProvider'] = valuesOfLine['nameProvider'] + ' ' + value
                            alreadyGetThisValue = True

                        # amountOriginal
                        if treatTextField(valuesOfLine['nameProvider']) != '' and value.count(',') == 1 and treatDecimalField(value) > 0 and alreadyGetThisValue is False:
                            valuesOfLine['amountOriginal'] = treatDecimalField(value)

                            idxFindAmountOriginal = idx

                            valuesOfLine['amountInterest'] = treatDecimalField(returnDataInDictOrArray(dataValueSplitSpace, [idxFindAmountOriginal + 1]))
                            valuesOfLine['amountDiscount'] = treatDecimalField(returnDataInDictOrArray(dataValueSplitSpace, [idxFindAmountOriginal + 2]))
                            valuesOfLine['amountPaid'] = treatDecimalField(returnDataInDictOrArray(dataValueSplitSpace, [idxFindAmountOriginal + 3]))

                            alreadyGetThisValue = True
                            break

                except Exception as e:
                    print('erro ao processar linha ', idxLine + 1)
                    logger.exception(e)

        except Exception as e:
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao processar, entre em contato com suporte'
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

        return self.__dataToSave
