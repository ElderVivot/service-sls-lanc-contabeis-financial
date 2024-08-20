try:
    import unzip_requirements
except ImportError:
    pass

try:
    import asyncio
    import datetime
    import logging
    from operator import itemgetter
    from typing import Dict, Any, List
    from src.convert_txt import ConvertTxt
    from src.functions import readCsvAsTxt, readTxt, readExcelPandas, readPdf, returnDataInDictOrArray, removeAnArrayFromWithinAnother, \
        treatTextField, readXlsWithBeautifulSoup, treatNumberField
    from src.get_layout import GetLayout
    from src.save_data import SaveData
    from src.treat_data.analyze_setting_fields import analyzeSettingFields
    from src.treat_data.identifies_header import identifiesTheHeader
    from src.treat_data.treat_data_layout import treatDataLayout
    from src.treat_data.update_fields_not_main import updateFieldsNotMain
    from src.treat_data.group_row_data import groupsRowData
    from src.treat_data.correlation_bank_x_settings_client import correlationBankAndAccountBetweenSettingsAndClient
    from src.treat_data.sum_interest_fine_and_discount import sumInterestFineAndDiscount
    from src.treat_data.is_valid_line_to_print import isValidLineToPrint
    from src.treat_data.is_valid_data_this_companie import isValidDataThisCompanie
    from src.treat_data.update_values_fields_to_save import updateValuesFieldsToSave
    from src.treat_data.multiple_per_less_one_when_necessary import multiplePerLessOneWhenNecessary
    from src.treat_data.calc_difference_paidReceived_x_interestDiscount import calcDifferencePaidReceivedXAmountOriginalAsInterestDiscount
    from src.treat_data.calc_difference_paidReceived_x_rateCart import calcDifferencePaidReceivedXAmountOriginalAsRateCard
    from src.treat_data.validate_if_cnpj_or_cpf_is_valid import validateIfCnpjOrCpfIsValid
    from src.treat_data.check_if_is_duplicated_fields import checkIfItIsDuplicatedFields
    from src.treat_data.handle_layout_is_partida_multipla import handleLayoutIsPartidaMultipla
    from src.treat_data.check_columns_that_have_value import getListColumnsThatHaveValue
    from src.treat_data.update_amount_movement_if_negative import updateAmountMovementIfNegative
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)


class ReadLinesAndProcessed(object):
    def __init__(self) -> None:
        self.__dataToSave: Dict[str, Any] = {}

    def __getTenant(self, key: str):
        try:
            return key.split("/")[0]
        except Exception:
            return ""

    def __getIdCompanie(self, key: str):
        try:
            return key.split("/")[1]
        except Exception:
            return ""

    def __getId(self, key: str):
        try:
            return key.split("/")[2].split(".")[0]
        except Exception:
            return key

    def __generateDataSettingInitial(self):
        return {
            "fieldsRowNotMain": {},
            "groupingFields": {},
            "linesOfFile": [],
            "considerToCheckIfItIsDuplicatedFields": {},
            "fieldsThatMultiplePerLessOne": {},
            "validationsLineToPrint": [],
            "sumInterestFineAndDiscount": False,
            "calcDifferencePaidOriginalAsInterestDiscount": False,
            "validateIfCnpjOrCpfIsValid": False,
            "negativeIsAmountPaid": False,
            "positiveIsAmountReceived": False,
        }

    def __updateDateStartAndDateEnd(self, dateMovement: datetime.datetime):
        if dateMovement is not None:
            if self.__dataToSave["startPeriod"] == "":
                self.__dataToSave["startPeriod"] = dateMovement
            if self.__dataToSave["startPeriod"] > dateMovement:
                self.__dataToSave["startPeriod"] = dateMovement

            if self.__dataToSave["endPeriod"] == "":
                self.__dataToSave["endPeriod"] = dateMovement
            if self.__dataToSave["endPeriod"] < dateMovement:
                self.__dataToSave["endPeriod"] = dateMovement

    def __mountHistoric(self, lanc: Dict[str, Any], historicComposition: str):
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
                        if valueField != '' and text in ('NF_DOC') and treatNumberField(valueField, isInt=True) > 0:
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

    async def __readLinesAndProcessed(self, fileBytesIO: List[Any], key: str, saveDatabase=True, extension='xlsx', layoutFilter=''):
        self.__dataToSave["url"] = key
        self.__dataToSave["id"] = self.__getId(key)
        self.__dataToSave["tenant"] = self.__getTenant(key)
        self.__dataToSave["idCompanie"] = self.__getIdCompanie(key)
        dateTimeNow = datetime.datetime.now()
        miliSecondsThreeChars = dateTimeNow.strftime("%f")[0:3]
        self.__dataToSave["updatedAt"] = f"{dateTimeNow.strftime('%Y-%m-%dT%H:%M:%S')}.{miliSecondsThreeChars}Z"
        self.__dataToSave["startPeriod"] = ""
        self.__dataToSave["endPeriod"] = ""
        self.__dataToSave["lancs"]: List[Dict[str, Any]] = []
        self.__dataToSave["listOfColumnsThatHaveValue"]: List[str] = []
        numberLoteInitial = 0

        try:
            getLayout = GetLayout()
            settingsLayout = await getLayout.getDataCompanieXSettingLayout(self.__dataToSave["idCompanie"])
            settingsLayout = returnDataInDictOrArray(settingsLayout, ["Item"], None)
            if settingsLayout is None:
                raise Exception('DONT_EXIST_LAYOUT_THIS_COMPANIE')
            layouts = settingsLayout["layoutsFinancial"]

            for layout in layouts:
                lancsThisLayout: List[Dict[str, Any]] = []
                try:
                    dataSetting = self.__generateDataSettingInitial()
                    valuesOfLine: Dict[str, Any] = {}
                    posionsOfHeaderTemp: Dict[str, Any] = {}
                    posionsOfHeader: Dict[str, Any] = {}

                    layoutData = await getLayout.getDataSettingLayout(layout["idLayout"])
                    layoutData = returnDataInDictOrArray(layoutData, ["Item"], None)
                    if layoutData is None:
                        print(f"Layout com ID {layout['idLayout']} não encontrado")
                        raise Exception('LAYOUT_DELETED')

                    fileType = layoutData['fileType']
                    splitFile = layoutData['splitFile']

                    nameLayout = treatTextField(layoutData['system'])
                    if layoutFilter not in ('', 'all', 'ALL'):
                        if nameLayout.find(layoutFilter) < 0:
                            continue

                    analyzeSetting = analyzeSettingFields(layoutData["fields"], dataSetting)
                    fields = analyzeSetting["fieldsValidated"]
                    dataSetting = analyzeSetting["dataSetting"]

                    dataSetting["validationsLineToPrint"] = returnDataInDictOrArray(layoutData, ["validationLineToPrint"], [])
                    dataSetting["linesOfFile"] = returnDataInDictOrArray(layoutData, ["linesOfFile"], [])
                    historicComposition = treatTextField(returnDataInDictOrArray(layoutData, ["historicComposition"]))

                    bankAndAccountCorrelation = returnDataInDictOrArray(layout, ["bankAndAccountCorrelation"])
                    validateIfDataIsThisCompanie = returnDataInDictOrArray(layout, ["validateIfDataIsThisCompanie"])

                    if fileType == 'excel' and extension in ('xlsx', 'xltx', 'ods'):
                        dataFile = readExcelPandas(fileBytesIO)
                        if len(dataFile) == 0:
                            dataFile = readXlsWithBeautifulSoup(fileBytesIO)
                    elif fileType == 'excel' and extension in ('xls'):
                        dataFile = readExcelPandas(fileBytesIO)
                        if len(dataFile) == 0:
                            dataFile = readXlsWithBeautifulSoup(fileBytesIO)
                    elif fileType == 'csv' and extension in ('csv', 'txt'):
                        dataFile = readCsvAsTxt(fileBytesIO)
                    elif fileType == 'txt' and extension in ('txt', 'html'):
                        dataFile = readTxt(fileBytesIO, minimalizeSpace=False, ignoreLineBlanks=False)
                    elif fileType == 'pdf' and extension in ('pdf'):
                        dataFile = readPdf(fileBytesIO)
                    else:
                        dataFile = []

                    for numberLine, data in enumerate(dataFile):
                        # print(numberLine, '----', data)
                        try:
                            positionsOfHeaderTemp = identifiesTheHeader(data, layoutData, fileType)
                            if positionsOfHeaderTemp is not None and len(positionsOfHeaderTemp) > 0:
                                if len(positionsOfHeaderTemp.items()) > 0:
                                    posionsOfHeader = positionsOfHeaderTemp
                                    continue

                            # quando as informações complementares estão uma linha abaixo da principal então lê ela primeiro e atualiza os campos notMain
                            nextData = returnDataInDictOrArray(dataFile, [numberLine + 1])
                            valuesOfLine = treatDataLayout(nextData, fields, posionsOfHeader, dataSetting, True, layoutData["fileType"])
                            dataSetting = updateFieldsNotMain(valuesOfLine, fields, dataSetting)

                            valuesOfLine = treatDataLayout(data, fields, posionsOfHeader, dataSetting, False, layoutData["fileType"])
                            dataSetting = updateFieldsNotMain(valuesOfLine, fields, dataSetting)
                            valuesOfLine = groupsRowData(valuesOfLine, dataSetting)
                            valuesOfLine = updateAmountMovementIfNegative(valuesOfLine)
                            valuesOfLine = correlationBankAndAccountBetweenSettingsAndClient(valuesOfLine, bankAndAccountCorrelation)

                            valuesOfLine["cgceProviderClient"] = validateIfCnpjOrCpfIsValid(valuesOfLine, dataSetting)

                            # print(data, valuesOfLine)
                            isValid = isValidLineToPrint(valuesOfLine, dataSetting)
                            isValidDataCompanie = isValidDataThisCompanie(valuesOfLine, validateIfDataIsThisCompanie, bankAndAccountCorrelation)
                            if isValid is True and isValidDataCompanie is True:
                                self.__updateDateStartAndDateEnd(valuesOfLine["paymentDate"])
                                valuesOfLine = multiplePerLessOneWhenNecessary(valuesOfLine, dataSetting)
                                valuesOfLine = sumInterestFineAndDiscount(valuesOfLine, dataSetting)
                                valuesOfLine = calcDifferencePaidReceivedXAmountOriginalAsInterestDiscount(valuesOfLine, dataSetting)
                                valuesOfLine = calcDifferencePaidReceivedXAmountOriginalAsRateCard(valuesOfLine, dataSetting)
                                valuesOfLine = updateValuesFieldsToSave(valuesOfLine)
                                valuesOfLine["codeHistoric"] = ""
                                paymentDate = valuesOfLine["paymentDate"]
                                valuesOfLine["paymentDateAsDate"] = f'{paymentDate[6:]}{paymentDate[3:5]}{paymentDate[0:2]}'
                                valuesOfLine["historic"] = treatTextField(self.__mountHistoric(valuesOfLine, historicComposition))
                                self.__dataToSave["listOfColumnsThatHaveValue"] = getListColumnsThatHaveValue(self.__dataToSave["listOfColumnsThatHaveValue"], valuesOfLine)
                                # print(valuesOfLine)
                                lancsThisLayout.append(valuesOfLine.copy())

                        except Exception as e:
                            print(f"Error to process line {numberLine}")
                            logger.exception(e)

                    lancsThisLayout = checkIfItIsDuplicatedFields(lancsThisLayout, dataSetting)
                    resultProcessingPartidaMultipla = handleLayoutIsPartidaMultipla(lancsThisLayout, dataSetting, numberLoteInitial)
                    lancsThisLayout = resultProcessingPartidaMultipla[0]
                    if resultProcessingPartidaMultipla[1] is True:
                        self.__dataToSave["listOfColumnsThatHaveValue"].append('numberLote')
                    numberLoteInitial = returnDataInDictOrArray(lancsThisLayout, [-1, 'numberLote'], 0)
                    # lancsThisLayout = self.sumAmountPaidPerLote(lancsThisLayout)
                    self.__dataToSave["lancs"].append(lancsThisLayout.copy())

                except Exception as e:
                    logger.exception(e)

            self.__dataToSave["lancs"] = removeAnArrayFromWithinAnother(self.__dataToSave["lancs"])
            self.__dataToSave['lancs'] = sorted(self.__dataToSave['lancs'], key=itemgetter('paymentDateAsDate'))

            # print(dataSetting)
            # print('----------------------')
            # print(self.__dataToSave)
            self.__dataToSave["typeLog"] = "success"
            self.__dataToSave["messageLog"] = "SUCCESS"
            self.__dataToSave["messageLogToShowUser"] = "Sucesso ao processar"
            if len(self.__dataToSave["lancs"]) == 0:
                self.__dataToSave["typeLog"] = "success"
                self.__dataToSave["messageLog"] = "SUCCESS"
                self.__dataToSave["messageLogToShowUser"] = "Processou com sucesso, mas não encontrou nenhuma linha válida no arquivo pra lançamento contábil, revise o layout."
            if saveDatabase is True:
                saveData = SaveData(self.__dataToSave)
                await saveData.saveData()
            else:
                import json
                from src.functions import formatDate
                import base64
                import bz2
                import sys
                import gzip

                self.__dataToSave["startPeriod"] = formatDate(self.__dataToSave["startPeriod"])
                self.__dataToSave["endPeriod"] = formatDate(self.__dataToSave["endPeriod"])
                jsonData = json.dumps(self.__dataToSave, indent=4)

                dataBytes = bytes(json.dumps(self.__dataToSave), 'utf-8')
                dataEncoded = base64.b64encode(dataBytes)
                dataCompress = gzip.compress(dataBytes)
                dataCompressBZ2 = bz2.compress(dataBytes)
                print(sys.getsizeof(dataCompress), sys.getsizeof(dataEncoded), sys.getsizeof(dataBytes), sys.getsizeof(dataCompressBZ2), len(self.__dataToSave['lancs']))

                with open("data/_dataToSave.json", "w") as outfile:
                    outfile.write(jsonData)
        except Exception as e:
            self.__dataToSave["typeLog"] = "error"
            self.__dataToSave["messageLog"] = str(e)
            self.__dataToSave["messageLogToShowUser"] = "Erro ao processar, entre em contato com suporte"
            if str(e) == 'DONT_EXIST_LAYOUT_THIS_COMPANIE':
                self.__dataToSave["typeLog"] = "warning"
                self.__dataToSave["messageLogToShowUser"] = "Não existe layout configurado pra essa empresa. Acesse Cadastros >> Vincular Empresas nos Layouts e configure"
            if str(e) == 'LAYOUT_DELETED':
                self.__dataToSave["typeLog"] = "warning"
                self.__dataToSave["messageLogToShowUser"] = "O layout vinculado nesta empresa não existe mais, acesse Cadastros >> Vincular Empresas nos Layouts e atualize"
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

    def executeJobMainAsync(self, fileBytesIO: List[Any], key: str, saveDatabase=True, extension='xlsx', layoutFilter=''):
        try:
            asyncio.run(self.__readLinesAndProcessed(fileBytesIO, key, saveDatabase, extension, layoutFilter))
        except Exception as e:
            logger.exception(e)
