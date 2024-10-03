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
    from typing import Dict, Any, List
    from src.custom_layouts.l_00001_pdf_email_nutronordeste import L00001PdfEmailNutronordeste
    from src.convert_txt import ConvertTxt
    from src.functions import formatDate, readTxt
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

            if self.__layout[0:6] == 'L00001':
                self.__dataToSave = await L00001PdfEmailNutronordeste(self.__dataToSave, dataFile).processAsync()

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
