try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import asyncio
    import datetime
    import logging
    from typing import Dict, Any, List
    from src.functions import returnDataInDictOrArray, removeAnArrayFromWithinAnother
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

    def __mountHistoric(self, lanc: Dict[str, Any]):
        if lanc["historic"]:
            return lanc["historic"]
        if lanc["document"] != "" and lanc["nameProviderClient"] != "":
            return f"NF/DOC {lanc['document']} - {lanc['nameProviderClient']}"
        if lanc["document"] == "" and lanc["nameProviderClient"] != "":
            return lanc["nameProviderClient"]
        return ""

    async def __readLinesAndProcessed(self, dataFile: List[Any], key: str, saveDatabase=True):
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

        try:
            getLayout = GetLayout()
            settingsLayout = await getLayout.getDataCompanieXSettingLayout(self.__dataToSave["idCompanie"])
            settingsLayout = returnDataInDictOrArray(settingsLayout, ["Item"], None)
            if settingsLayout is None:
                print("Nao existe layout pra essa empresa")
                return None
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

                    analyzeSetting = analyzeSettingFields(layoutData["fields"], dataSetting)
                    fields = analyzeSetting["fieldsValidated"]
                    dataSetting = analyzeSetting["dataSetting"]

                    dataSetting["validationsLineToPrint"] = returnDataInDictOrArray(layoutData, ["validationLineToPrint"], [])
                    dataSetting["linesOfFile"] = returnDataInDictOrArray(layoutData, ["linesOfFile"], [])

                    bankAndAccountCorrelation = returnDataInDictOrArray(layout, ["bankAndAccountCorrelation"])
                    validateIfDataIsThisCompanie = returnDataInDictOrArray(layout, ["validateIfDataIsThisCompanie"])

                    for numberLine, data in enumerate(dataFile):
                        # print(numberLine, '----', data)
                        try:
                            posionsOfHeaderTemp = identifiesTheHeader(data, layoutData)
                            if posionsOfHeaderTemp is not None and len(posionsOfHeaderTemp) > 0:
                                if len(posionsOfHeaderTemp.items()) > 0:
                                    posionsOfHeader = posionsOfHeaderTemp
                                    continue

                            # quando as informações complementares estão uma linha abaixo da principal então lê ela primeiro e atualiza os campos notMain
                            nextData = returnDataInDictOrArray(dataFile, [numberLine + 1])
                            valuesOfLine = treatDataLayout(nextData, fields, posionsOfHeader, dataSetting, True, layoutData["fileType"])
                            dataSetting = updateFieldsNotMain(valuesOfLine, fields, dataSetting)

                            valuesOfLine = treatDataLayout(data, fields, posionsOfHeader, dataSetting, False, layoutData["fileType"])
                            dataSetting = updateFieldsNotMain(valuesOfLine, fields, dataSetting)
                            valuesOfLine = groupsRowData(valuesOfLine, dataSetting)

                            valuesOfLine = correlationBankAndAccountBetweenSettingsAndClient(valuesOfLine, bankAndAccountCorrelation)

                            valuesOfLine["cgceProviderClient"] = validateIfCnpjOrCpfIsValid(valuesOfLine, dataSetting)

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
                                valuesOfLine["historic"] = self.__mountHistoric(valuesOfLine)
                                self.__dataToSave["listOfColumnsThatHaveValue"] = getListColumnsThatHaveValue(self.__dataToSave["listOfColumnsThatHaveValue"], valuesOfLine)
                                # print(valuesOfLine)
                                lancsThisLayout.append(valuesOfLine.copy())

                        except Exception as e:
                            print(f"Error to process line {numberLine}")
                            logger.exception(e)

                    lancsThisLayout = checkIfItIsDuplicatedFields(lancsThisLayout, dataSetting)
                    lancsThisLayout = handleLayoutIsPartidaMultipla(lancsThisLayout, dataSetting)
                    # lancsThisLayout = self.sumAmountPaidPerLote(lancsThisLayout)
                    self.__dataToSave["lancs"].append(lancsThisLayout.copy())

                except Exception as e:
                    logger.exception(e)

            self.__dataToSave["lancs"] = removeAnArrayFromWithinAnother(self.__dataToSave["lancs"])

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

                self.__dataToSave["startPeriod"] = formatDate(self.__dataToSave["startPeriod"])
                self.__dataToSave["endPeriod"] = formatDate(self.__dataToSave["endPeriod"])
                jsonData = json.dumps(self.__dataToSave, indent=4)
                with open("data/_dataToSave.json", "w") as outfile:
                    outfile.write(jsonData)
        except Exception as e:
            self.__dataToSave["typeLog"] = "error"
            self.__dataToSave["messageLog"] = str(e)
            self.__dataToSave["messageLogToShowUser"] = "Erro ao processar, entre em contato com suporte"
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

    def executeJobMainAsync(self, f: List[Any], key: str, saveDatabase=True):
        try:
            asyncio.run(self.__readLinesAndProcessed(f, key, saveDatabase))
        except Exception as e:
            logger.exception(e)
