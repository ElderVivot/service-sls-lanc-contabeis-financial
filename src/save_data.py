try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    from aiohttp import ClientSession
    from typing import Dict, Any, List
    import json
    from src.functions import formatDate
except Exception as e:
    print(f"Error importing libraries {e}")

API_HOST_SERVERLESS = os.environ.get('API_HOST_SERVERLESS')
API_HOST_DB_RELATIONAL = os.environ.get('API_HOST_DB_RELATIONAL')


class SaveData(object):
    def __init__(self, dataToSave: Dict[str, Any]) -> None:
        self.__dataToSave = dataToSave

    async def __put(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.put(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def __post(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.post(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def saveData(self, ):
        print(self.__dataToSave)
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

                response, statusCode = await self.__put(
                    session,
                    f"{API_HOST_DB_RELATIONAL}/lanc_contabil_financial/{self.__dataToSave['id']}",
                    data={
                        "idLancContabilFinancial": self.__dataToSave['id'],
                        "idCompanie": self.__dataToSave['idCompanie'],
                        "startPeriod": "2023-05-01",
                        "endPeriod": "2023-05-31",
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
