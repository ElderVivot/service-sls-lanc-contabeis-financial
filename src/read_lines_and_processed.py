try:
    import unzip_requirements
except ImportError:
    pass

try:
    import io
    import os
    import asyncio
    import datetime
    from aiohttp import ClientSession
    from typing import Dict, Any, List
    import json
    from src.functions import removeCharSpecials, treatDecimalField, treatDateField
except Exception as e:
    print(f"Error importing libraries {e}")

API_HOST_DE_PARA_ACCOUNT_ECD = os.environ.get('API_HOST_DE_PARA_ACCOUNT_ECD')

dataToSave: Dict[str, Any] = {}
dataToSave['accountsDePara'] = []
accountsNameToCorrelation: Dict[str, str] = {}
accountsTypeToCorrelation: Dict[str, str] = {}  # sintetica S or analitica A


async def put(session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
    async with session.put(url, json=data, headers=headers) as response:
        data = await response.json()
        return data, response.status


async def saveData(data: Dict[str, Any]):
    try:
        async with ClientSession() as session:
            response, statusCode = await put(
                session,
                f"{API_HOST_DE_PARA_ACCOUNT_ECD}",
                data=json.loads(json.dumps(data)),
                headers={}
            )
            if statusCode >= 400:
                raise Exception(statusCode, response)
            print('Salvo no banco de dados')
            return response
    except Exception as e:
        print('Error ao salvar dado')
        print(e)


def getTenant(key: str):
    try:
        return key.split('/')[0]
    except Exception:
        return ''


def getDataFromIdentificador0000(lineSplit: List[str]):
    dataToSave['startPeriod'] = treatDateField(lineSplit[3], 4)
    dataToSave['endPeriod'] = treatDateField(lineSplit[4], 4)
    dataToSave['nameCompanie'] = lineSplit[5]
    dataToSave['federalRegistration'] = lineSplit[6]


def getNameAccount(lineSplit: List[str]):
    try:
        return accountsNameToCorrelation[f'{lineSplit[2]}']
    except Exception:
        return ''


def getTypeAccount(lineSplit: List[str]):
    try:
        return accountsTypeToCorrelation[f'{lineSplit[2]}']
    except Exception:
        return ''


def checkIfIsFileECD(lineSplit: List[str]):
    if len(lineSplit) < 2:
        return False
    if lineSplit[1] == '0000':
        field02 = lineSplit[2].upper()
        if field02 != 'LECD':
            return False
    return True


def getDataFromIdentificadorI155(lineSplit: List[str]):
    balanceAccount = treatDecimalField(lineSplit[8])
    typeAccount = getTypeAccount(lineSplit)

    if balanceAccount > 0 and typeAccount == 'A':
        dataToSave['accountsDePara'].append({
            "oldAccount": lineSplit[2],
            "newAccount": "",
            "nameAccount": getNameAccount(lineSplit),
            "balanceAccount": treatDecimalField(lineSplit[8]),
            "kindBalanceAccount": lineSplit[9]
        })


async def readLinesAndProcessed(f: io.TextIOWrapper, key: str):
    lastI150File = False
    isFileECD = False

    dataToSave['id'] = key.replace('/', '__')
    dataToSave['tenant'] = getTenant(key)
    dataToSave['updatedAt'] = datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S')

    while line := f.readline():
        try:
            lineFormated = removeCharSpecials(line)
            lineSplit = lineFormated.split('|')

            if isFileECD is False:
                isFileECD = checkIfIsFileECD(lineSplit)
                if isFileECD is False:
                    print('Arquivo não é ECD')
                    break

            identificador = lineSplit[1]

            if identificador == '0000':
                endPeriod = lineSplit[4]
                getDataFromIdentificador0000(lineSplit)
            elif identificador == 'I050':
                accountsNameToCorrelation[f'{lineSplit[6]}'] = lineSplit[8]
                accountsTypeToCorrelation[f'{lineSplit[6]}'] = lineSplit[4]
            elif identificador == 'I150':
                competenceEndI150 = lineSplit[3]
                if competenceEndI150 == endPeriod:
                    lastI150File = True
                else:
                    continue
            elif identificador == 'I155' and lastI150File is True:
                getDataFromIdentificadorI155(lineSplit)
            elif identificador == 'I200':
                print('Terminou de processar todos registros do TXT')
                break
            elif identificador == '9999':
                print('Arquivo sem reg de I200, processou completo TXT')
                break
            else:
                continue
        except Exception as e:
            print('Error ao processar arquivo TXT')
            print(e)

    await saveData(dataToSave)


def executeJobAsync(f: io.TextIOWrapper, key: str):
    try:
        asyncio.run(readLinesAndProcessed(f, key))
    except Exception:
        pass
