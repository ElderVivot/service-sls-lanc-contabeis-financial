try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import io
    import asyncio
    import datetime
    import logging
    from operator import itemgetter
    from typing import Dict, Any, List
    from src.get_layout import GetLayout
    from src.custom_layouts.l_00001_pdf_email_nutronordeste import L00001PdfEmailNutronordeste
    from src.custom_layouts.l_00002_pdf_omnie_extrato_conciliado import L00002PdfOminieExtratoConciliado
    from src.treat_data.check_columns_that_have_value import getListColumnsThatHaveValue
    from src.convert_txt import ConvertTxt
    from src.functions import removeAnArrayFromWithinAnother, readTxt, returnDataInDictOrArray, treatTextField, treatNumberField
    from src.save_data import SaveData
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)

API_HOST_SERVERLESS = os.environ.get('API_HOST_SERVERLESS')
API_HOST_DB_RELATIONAL = os.environ.get('API_HOST_DB_RELATIONAL')


class ReadLinesAndProcessedCustomLayouts(object):
    def __init__(self, fileData: io.FileIO, key: str, extension: str, layout='') -> None:
        self.__fileData = fileData
        self.__key = key
        self.__extension = extension
        self.__layout = layout

        self.__dataToSave: Dict[str, Any] = {}
        self.__dataToSave["url"] = key
        self.__dataToSave["id"] = self.__getId(key)
        self.__dataToSave["tenant"] = self.__getTenant(key)
        self.__dataToSave["idCompanie"] = self.__getIdCompanie(key)

        self.__historicComposition = ''

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
            "groupingLancsByFields": {},
            "linesOfFile": [],
            "considerToCheckIfItIsDuplicatedFields": {},
            "fieldsThatMultiplePerLessOne": {},
            "validationsLineToPrint": [],
            "linesToIgnore": [],
            "sumInterestFineAndDiscount": False,
            "calcDifferencePaidOriginalAsInterestDiscount": False,
            "validateIfCnpjOrCpfIsValid": False,
            "negativeIsAmountPaid": False,
            "positiveIsAmountReceived": False,
        }

    async def __getHistoricComposition(self):
        getLayout = GetLayout()
        settingsLayout = await getLayout.getDataCompanieXSettingLayout(self.__dataToSave["idCompanie"])
        settingsLayout = returnDataInDictOrArray(settingsLayout, ["Item"], None)
        if settingsLayout is None:
            raise Exception('DONT_EXIST_LAYOUT_THIS_COMPANIE')
        layouts = settingsLayout["layoutsFinancial"]

        for layout in layouts:
            try:
                layoutData = await getLayout.getDataSettingLayout(layout["idLayout"])
                layoutData = returnDataInDictOrArray(layoutData, ["Item"], None)
                if layoutData is None:
                    print(f"Layout com ID {layout['idLayout']} não encontrado")
                    raise Exception('LAYOUT_DELETED')

                nameLayout = treatTextField(layoutData['system'])
                if self.__layout not in ('', 'all', 'ALL') and nameLayout.find(self.__layout[0:6]) >= 0:
                    break

                self.__historicComposition = treatTextField(returnDataInDictOrArray(layoutData, ["historicComposition"]))

            except Exception:
                pass

    async def __readLinesAndProcessed(self):
        dateTimeNow = datetime.datetime.now()
        miliSecondsThreeChars = dateTimeNow.strftime("%f")[0:3]
        self.__dataToSave["updatedAt"] = f"{dateTimeNow.strftime('%Y-%m-%dT%H:%M:%S')}.{miliSecondsThreeChars}Z"
        self.__dataToSave["startPeriod"] = ""
        self.__dataToSave["endPeriod"] = ""
        self.__dataToSave["lancs"]: List[Dict[str, Any]] = []
        self.__dataToSave["listOfColumnsThatHaveValue"]: List[str] = []

        try:
            dataFile = []
            if self.__extension == 'pdf':
                convertTxt = ConvertTxt()
                pdfResult = convertTxt.pdfToText(self.__fileData)
                dataFile = readTxt(pdfResult, dataAsByte=False, minimalizeSpace=False)

            await self.__getHistoricComposition()

            if self.__layout[0:6] == 'L00001':
                self.__dataToSave = await L00001PdfEmailNutronordeste(self.__dataToSave, dataFile).processAsync()
            elif self.__layout[0:6] == 'L00002':
                self.__dataToSave = await L00002PdfOminieExtratoConciliado(self.__dataToSave, self.__fileData, self.__historicComposition).processAsync()

            # self.__dataToSave["lancs"] = removeAnArrayFromWithinAnother(self.__dataToSave["lancs"])
            self.__dataToSave['lancs'] = sorted(self.__dataToSave['lancs'], key=itemgetter('paymentDateAsDate'))

            if len(self.__dataToSave['lancs']) > 0:
                self.__dataToSave['typeLog'] = 'success'
                self.__dataToSave['messageLog'] = 'SUCCESS'
                self.__dataToSave['messageLogToShowUser'] = 'Sucesso ao processar'
            if len(self.__dataToSave['lancs']) == 0:
                self.__dataToSave['typeLog'] = 'success'
                self.__dataToSave['messageLog'] = 'SUCCESS'
                self.__dataToSave['messageLogToShowUser'] = 'Processou com sucesso, mas não encontrou nenhuma linha válida no arquivo pra lançamento contábil, revise o layout.'
            if self.__key != '':
                saveData = SaveData(self.__dataToSave)
                await saveData.saveData()
            if self.__key == '':
                saveData = SaveData(self.__dataToSave)
                await saveData.saveLocal()
        except Exception as e:
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao processar, entre em contato com suporte'
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

    def executeJobMainAsync(self):
        try:
            asyncio.run(self.__readLinesAndProcessed())
        except Exception as e:
            logger.exception(e)
