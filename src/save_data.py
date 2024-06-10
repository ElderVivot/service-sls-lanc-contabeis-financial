try:
    import unzip_requirements
except ImportError:
    pass

try:
    import uuid
    import os
    import gzip
    import base64
    from aiohttp import ClientSession
    from typing import Dict, Any, List
    import json
    from src.functions import formatDate
except Exception as e:
    print(f"Error importing libraries {e}")

API_HOST_SERVERLESS = os.environ.get('API_HOST_SERVERLESS')
API_HOST_DB_RELATIONAL = os.environ.get('API_HOST_DB_RELATIONAL')


class SaveData(object):
    def __init__(self, dataToSave: Dict[str, Any], zipData=False) -> None:
        self.__dataToSave = dataToSave
        self.__zipData = zipData

    async def __put(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.put(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def __post(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.post(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def saveData(self, ):
        try:
            self.__dataToSave['startPeriod'] = formatDate(self.__dataToSave['startPeriod'])
            self.__dataToSave['endPeriod'] = formatDate(self.__dataToSave['endPeriod'])

            lenghtData = len(self.__dataToSave['lancs'])
            lancsOriginal = self.__dataToSave['lancs']
            qtdTimesSplit = int(lenghtData / 5000) + 1
            loopProcessing = 0
            messageLogOriginal = self.__dataToSave['messageLogToShowUser']
            urlFile = self.__dataToSave['url'].split('/')[-1]

            async with ClientSession() as session:
                for idx in range(0, lenghtData, 5000):
                    loopProcessing += 1
                    if idx > 0:
                        self.__dataToSave['id'] = str(uuid.uuid4())
                        self.__dataToSave['lancs'] = lancsOriginal[idx: idx + 5000]
                    else:
                        self.__dataToSave['lancs'] = lancsOriginal[0: idx + 5000]
                    dataJson = json.dumps(self.__dataToSave)
                    dataBytes = bytes(dataJson, 'utf-8')
                    dataCompress = gzip.compress(dataBytes)
                    dataEncoded = base64.b64encode(dataCompress)

                    response, statusCode = await self.__put(
                        session,
                        f"{API_HOST_SERVERLESS}/lanc-contabeis-financial-zip",
                        data=json.loads(json.dumps({"data": dataEncoded.decode()})),
                        headers={}
                    )
                    if statusCode >= 400:
                        raise Exception(statusCode, response)
                    print('Salvo no banco de dados')

                    if qtdTimesSplit > 1:
                        self.__dataToSave['messageLogToShowUser'] = f"{messageLogOriginal}. Parte {loopProcessing} de {qtdTimesSplit} do arquivo {urlFile[0:7]}"

                    if idx > 0:
                        await self.__saveDataApiRelational('post')
                    else:
                        result = await self.__saveDataApiRelational('put')
                        self.__dataToSave["idUser"] = result['idUser']
                        self.__dataToSave["nameFinancial"] = result['nameFinancial']

                return response
        except Exception as e:
            print('Error ao salvar dado dynamodb')
            print(e)
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao salvar resultado do processamento'

            await self.__saveDataApiRelational('put')

    async def __saveDataApiRelational(self, typeSave):
        try:
            urlS3 = f"https://cont-financial-files.s3.us-east-2.amazonaws.com/{self.__dataToSave['url']}"
            async with ClientSession() as session:
                if typeSave == 'put':
                    response, statusCode = await self.__put(
                        session,
                        f"{API_HOST_DB_RELATIONAL}/lanc_contabil_financial/{self.__dataToSave['id']}",
                        data={
                            "idLancContabilFinancial": self.__dataToSave['id'],
                            "idCompanie": self.__dataToSave['idCompanie'],
                            "startPeriod": self.__dataToSave['startPeriod'],
                            "endPeriod": self.__dataToSave['endPeriod'],
                            "urlFile": urlS3,
                            "typeLog": self.__dataToSave['typeLog'],
                            "messageLog": self.__dataToSave['messageLog'],
                            "messageLogToShowUser": self.__dataToSave['messageLogToShowUser'],
                            "messageError": ""
                        },
                        headers={"TENANT": self.__dataToSave['tenant']}
                    )
                    if statusCode >= 400:
                        raise Exception(statusCode, response)
                    print('Salvo no banco de dados relacional')

                    return response
                else:
                    response, statusCode = await self.__post(
                        session,
                        f"{API_HOST_DB_RELATIONAL}/lanc_contabil_financial",
                        data={
                            "idLancContabilFinancial": self.__dataToSave['id'],
                            "idCompanie": self.__dataToSave['idCompanie'],
                            "startPeriod": self.__dataToSave['startPeriod'],
                            "endPeriod": self.__dataToSave['endPeriod'],
                            "urlFile": urlS3,
                            "idUser": self.__dataToSave['idUser'],
                            "typeLog": self.__dataToSave['typeLog'],
                            "nameFinancial": self.__dataToSave["nameFinancial"],
                            "messageLog": self.__dataToSave['messageLog'],
                            "messageLogToShowUser": self.__dataToSave['messageLogToShowUser'],
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
