try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    from aiohttp import ClientSession
    from typing import Dict
    from dotenv import load_dotenv
except Exception as e:
    print(f"Error importing libraries {e}")

load_dotenv()

API_HOST_SERVERLESS_COMPANIE_X_SETTING_LAYOUT = os.environ.get('API_HOST_SERVERLESS_COMPANIE_X_SETTING_LAYOUT')
API_HOST_SERVERLESS_SETTING_LAYOUT_FINANCIAL = os.environ.get('API_HOST_SERVERLESS_SETTING_LAYOUT_FINANCIAL')


class GetLayout(object):
    def __init__(self) -> None:
        pass

    async def __get(self, session: ClientSession, url: str, headers: Dict[str, str]):
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def getDataCompanieXSettingLayout(self, id: str):
        try:
            async with ClientSession() as session:
                response, statusCode = await self.__get(
                    session,
                    f"{API_HOST_SERVERLESS_COMPANIE_X_SETTING_LAYOUT}/companie-x-setting-layout/{id}",
                    headers={}
                )
                if statusCode >= 400:
                    raise Exception(statusCode, response)

                return response
        except Exception as e:
            print('Error ao buscar dado companie-x-setting-layout no dynamodb')
            print(e)

    async def getDataSettingLayout(self, id: str):
        try:
            async with ClientSession() as session:
                response, statusCode = await self.__get(
                    session,
                    f"{API_HOST_SERVERLESS_SETTING_LAYOUT_FINANCIAL}/setting-layout-financial/{id}",
                    headers={}
                )
                if statusCode >= 400:
                    raise Exception(statusCode, response)

                return response
        except Exception as e:
            print('Error ao buscar dado setting-layout-financial no dynamodb')
            print(e)
