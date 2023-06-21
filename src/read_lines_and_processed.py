try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import asyncio
    import datetime
    from aiohttp import ClientSession
    from typing import Dict, Any, List
    import json
    from src.functions import returnDataInDictOrArray, formatDate
except Exception as e:
    print(f"Error importing libraries {e}")

API_HOST_SERVERLESS = os.environ.get('API_HOST_SERVERLESS')
API_HOST_DB_RELATIONAL = os.environ.get('API_HOST_DB_RELATIONAL')


class ReadLinesAndProcessed(object):
    def __init__(self) -> None:
        self.__dataToSave: Dict[str, Any] = {}

    async def __put(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.put(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def __post(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.post(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def __saveData(self, ):
        try:
            self.__dataToSave['startPeriod'] = formatDate(self.__dataToSave['startPeriod'])
            self.__dataToSave['endPeriod'] = formatDate(self.__dataToSave['endPeriod'])
            async with ClientSession() as session:
                response, statusCode = await self.__put(
                    session,
                    f"{API_HOST_SERVERLESS}/lanc-contabeis-financial",
                    data=json.loads(json.dumps(self.__dataToSave)),
                    headers={}
                )
                if statusCode >= 400:
                    raise Exception(statusCode, response)
                print('Salvo no banco de dados')

                await self.__saveDataApiRelational()

                return response
        except Exception as e:
            print('Error ao salvar dado dynamodb')
            print(e)

    async def __saveDataApiRelational(self):
        try:
            urlS3 = f"https://autmais-ecd-de-para-accounting-plan.s3.us-east-2.amazonaws.com/{self.__dataToSave['url']}"
            async with ClientSession() as session:

                response, statusCode = await self.__post(
                    session,
                    f"{API_HOST_DB_RELATIONAL}/lanc_contabil_financial",
                    data={
                        "nameCompanie": self.__dataToSave['nameCompanie'],
                        "startPeriod": self.__dataToSave['startPeriod'],
                        "endPeriod": self.__dataToSave['endPeriod'],
                        "urlFile": urlS3,
                        "typeLog": "success",
                        "messageLog": "SUCCESS",
                        "messageLogToShowUser": "Sucesso ao processar",
                        "messageError": ""
                    },
                    headers={"TENANT": self.__dataToSave['tenant']}
                )
                if statusCode >= 400:
                    raise Exception(statusCode, response)
                print('Salvo no banco de dados relacional')

                return response
        except Exception as e:
            print('Error ao salvar dado banco relacional')
            print(e)

    def __getTenant(self, key: str):
        try:
            return key.split('/')[0]
        except Exception:
            return ''

    def __getId(self, key: str):
        try:
            return key.split('/')[1].split('.')[0]
        except Exception:
            return key

    async def __readLinesAndProcessed(self, dataFile: List[Any], key: str):
        self.__dataToSave['url'] = key
        self.__dataToSave['id'] = self.__getId(key)
        self.__dataToSave['tenant'] = self.__getTenant(key)
        dateTimeNow = datetime.datetime.now()
        miliSecondsThreeChars = dateTimeNow.strftime('%f')[0:3]
        self.__dataToSave['updatedAt'] = f"{dateTimeNow.strftime('%Y-%m-%dT%H:%M:%S')}.{miliSecondsThreeChars}Z"
        self.__dataToSave['startPeriod'] = ''
        self.__dataToSave['endPeriod'] = ''
        self.__dataToSave['lancs'] = []

        isFileCorrect = False
        nameSheetLineBefore = ''
        bankAndAccount = ''
        nameCompanie = ''

        for _, data in enumerate(dataFile):
            try:
                nameSheet: str = returnDataInDictOrArray(data, [0])
                field6: str = returnDataInDictOrArray(data, [6])
                field7: str = returnDataInDictOrArray(data, [7])

                if nameSheetLineBefore != nameSheet:
                    isFileCorrect = False

                if str(type(field6)).count('str') > 0 and field6.count('380 - EXTRATO FINANCEIRO') > 0:
                    isFileCorrect = True

                if isFileCorrect is True:
                    if str(type(field6)).count('str') > 0 and field6.count('CONTA:') > 0:
                        bankAndAccount = field7

                    if str(type(field6)).count('str') > 0 and field6.count('NOME FILIAL') > 0:
                        nameCompanie = field7
                        self.__dataToSave['nameCompanie'] = nameCompanie

                    paymentDate = returnDataInDictOrArray(data, [3])
                    nameProvider = returnDataInDictOrArray(data, [6])
                    nameClient = returnDataInDictOrArray(data, [7])
                    amountReceived = returnDataInDictOrArray(data, [13])
                    amountPaid = returnDataInDictOrArray(data, [14])

                    if str(type(paymentDate)).count('datetime') > 0 and (amountPaid > 0 or amountReceived > 0):
                        if self.__dataToSave['startPeriod'] == '':
                            self.__dataToSave['startPeriod'] = paymentDate
                        if self.__dataToSave['endPeriod'] == '':
                            self.__dataToSave['endPeriod'] = paymentDate
                        if self.__dataToSave['startPeriod'] > paymentDate:
                            self.__dataToSave['startPeriod'] = paymentDate
                        if self.__dataToSave['endPeriod'] < paymentDate:
                            self.__dataToSave['endPeriod'] = paymentDate

                        dataProcessed = {
                            "bankAndAccount": bankAndAccount,
                            "nameCompanie": nameCompanie,
                            "dueDate": formatDate(returnDataInDictOrArray(data, [1]), '%d/%m/%Y'),
                            "paymentDate": formatDate(paymentDate, '%d/%m/%Y'),
                            "accountPlan": returnDataInDictOrArray(data, [5]),
                            "nameProvider": nameProvider,
                            "nameClient": nameClient,
                            "nameProviderClient": nameProvider if nameProvider != "" else nameClient,
                            "historic": returnDataInDictOrArray(data, [8]),
                            "document": returnDataInDictOrArray(data, [12]),
                            "amountReceived": amountReceived,
                            "amountPaid": amountPaid,
                            "amountMoviment": amountReceived if amountReceived > 0 else amountPaid * -1,
                            "accountDebit": '',
                            "accountCredit": ''
                        }
                        self.__dataToSave['lancs'].append(dataProcessed.copy())
                        dataProcessed.clear()

                nameSheetLineBefore = nameSheet
            except Exception as e:
                print('Error ao processar arquivo TXT')
                print(e)

        await self.__saveData()

    def executeJobMainAsync(self, f: List[Any], key: str):
        try:
            asyncio.run(self.__readLinesAndProcessed(f, key))
        except Exception:
            pass
