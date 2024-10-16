# layout implemented to client ccaf1052-cc6f-4 - pdf_email_nutronordeste

try:
    import unzip_requirements
except ImportError:
    pass

try:
    import datetime
    import logging
    import fitz
    from typing import Dict, Any
    from src.custom_layouts.update_values_fields_to_save import updateValuesFieldsToSave
    from src.functions import treatDateField, treatTextField, returnDataInDictOrArray, minimalizeSpaces, \
        treatDecimalField, formatDate, treatNumberField
    from src.save_data import SaveData
    from src.treat_data.check_columns_that_have_value import getListColumnsThatHaveValue
    from src.custom_layouts.mount_historic import mountHistoric
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)


class L00002PdfOminieExtratoConciliado(object):
    def __init__(self, dataToSave: Dict[str, Any], dataDoc, historicComposition='') -> None:
        self.__dataToSave = dataToSave
        self.__dataDoc = dataDoc
        self.__historicComposition = historicComposition

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
            "amountPaidOrReceived": 0,
            "amountOriginal": 0,
            "amountInterest": 0,
            "amountDiscount": 0,
            "historic": '',
            "ledgerAccount": '',
            'category': ''
        }

    async def processAsync(self):
        valuesOfLine = self.__setDefaultValuesOfLine()
        alreadyArrivedLinesValidToProcess = False

        yearStr = ''
        balanceInitial = None
        account = ''
        bankName = ''

        try:
            with fitz.open(stream=self.__dataDoc, filetype='pdf') as doc:
                for numberPage, page in enumerate(doc):
                    dataPage = page.get_text("blocks", sort=True)
                    dataPage.sort(key=lambda x: x[-2])
                    for numberLine, dataLine in enumerate(dataPage):
                        # if numberPage == 0:
                        #     print(print(dataLine))
                        try:
                            valuesOfLine = self.__setDefaultValuesOfLine()

                            dataValue = treatTextField(dataLine[4], optionRemove=2)
                            dataValueSplitEnter = dataValue.split('\n')

                            dataValueWithoutEnter = dataValue.replace('\n', '').replace('\r', '')
                            dataValueSplitSpace = dataValueWithoutEnter.split(' ')

                            field01 = returnDataInDictOrArray(dataValueSplitEnter, [0])
                            field02 = returnDataInDictOrArray(dataValueSplitEnter, [1])
                            field03 = returnDataInDictOrArray(dataValueSplitEnter, [2])
                            field04 = returnDataInDictOrArray(dataValueSplitEnter, [3])
                            fieldLast01 = returnDataInDictOrArray(dataValueSplitEnter, [-1])
                            fieldLast02 = returnDataInDictOrArray(dataValueSplitEnter, [-2])
                            fieldLast03 = returnDataInDictOrArray(dataValueSplitEnter, [-3])

                            # field01FirstSpace = returnDataInDictOrArray(dataValueSplitSpace, [0])

                            if dataValue.find('SALDO ANTERIOR') >= 0:
                                if balanceInitial is None:
                                    balanceInitial = dataValueSplitSpace[-1]
                                    balanceInitial = treatDecimalField(balanceInitial)
                                    self.__dataToSave['balanceInitial'] = balanceInitial

                            if dataValue.find('PERIODO DE') >= 0 and yearStr == '':
                                positionFind = dataValue.find('PERIODO DE')
                                lenght = len('PERIODO DE')
                                positionStart = positionFind + lenght
                                yearStr = minimalizeSpaces(treatTextField(dataValue[positionStart:]))
                                yearStr = treatNumberField(yearStr.split('/')[2].split(' ')[0])
                                continue

                            if dataValue.find('CONTA:') >= 0 and account == '':
                                positionFindAccount = dataValue.find('CONTA:')
                                lenghtAccount = len('CONTA:')
                                positionStartAccount = positionFindAccount + lenghtAccount
                                positionEnd = dataValue.find('LIMITE')
                                account = treatNumberField(dataValue[positionStartAccount:positionEnd])

                            if dataValue.find('EXTRATO DE') >= 0 and bankName == '':
                                positionFind = dataValue.find('EXTRATO DE')
                                lenght_ = len('EXTRATO DE')
                                positionStart = positionFind + lenght_
                                bankName = treatTextField(dataValue[positionStart:])

                            if dataValue.find('DATA') >= 0 and dataValue.find('CATEGORIA') >= 0 and dataValue.find('VALOR') >= 0:
                                alreadyArrivedLinesValidToProcess = True
                                valuesOfLine = self.__setDefaultValuesOfLine()
                                continue

                            if alreadyArrivedLinesValidToProcess is False:
                                continue

                            dateMovementTemp = treatDateField(f'{field02}/{yearStr}')
                            if dateMovementTemp is not None:
                                valuesOfLine['paymentDate'] = dateMovementTemp

                            valuesOfLine['amountPaidOrReceived'] = treatDecimalField(fieldLast02)
                            valuesOfLine['nameProviderClient'] = field03
                            valuesOfLine['category'] = fieldLast03
                            if field04 == fieldLast03:
                                valuesOfLine['document'] = ''
                            else:
                                valuesOfLine['document'] = field04

                            if valuesOfLine['paymentDate'] is not None and valuesOfLine['nameProviderClient'] != '' and valuesOfLine['amountPaidOrReceived'] != 0:
                                self.__updateDateStartAndDateEnd(valuesOfLine['paymentDate'])
                                valuesOfLine['bank'] = bankName
                                if bankName.find(account) < 0:
                                    valuesOfLine['account'] = account
                                valuesOfLine = updateValuesFieldsToSave(valuesOfLine)
                                valuesOfLine["historic"] = treatTextField(mountHistoric(valuesOfLine, self.__historicComposition))
                                self.__dataToSave['lancs'].append(valuesOfLine.copy())
                                self.__dataToSave["listOfColumnsThatHaveValue"] = getListColumnsThatHaveValue(self.__dataToSave["listOfColumnsThatHaveValue"], valuesOfLine)

                        except Exception as e:
                            print('erro ao processar linha ', numberLine)
                            logger.exception(e)

        except Exception as e:
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao processar, entre em contato com suporte'
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

        return self.__dataToSave
