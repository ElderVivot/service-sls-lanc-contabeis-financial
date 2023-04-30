try:
    import unzip_requirements
except ImportError:
    pass

try:
    import io
    from src.functions import removeCharSpecials
except Exception as e:
    print("Error importing libraries", e)


def readLinesAndProcessed(f: io.TextIOWrapper):
    dataToSave = {}
    lastI150File = False

    while line := f.readline():
        lineFormated = removeCharSpecials(line)
        lineSplit = lineFormated.split('|')

        identificador = lineSplit[1]

        if identificador == '0000':
            dataToSave['startPeriod'] = lineSplit[3]
            dataToSave['endPeriod'] = lineSplit[4]
            dataToSave['nameCompanie'] = lineSplit[5]
            dataToSave['federalRegistration'] = lineSplit[6]
        elif identificador == 'I150':
            competenceEndI150 = lineSplit[3]
            if competenceEndI150 == dataToSave['endPeriod']:
                lastI150File = True
            else:
                continue
        elif identificador == 'I155' and lastI150File is True:
            print(lineFormated)
        elif identificador == 'I200':
            print('terminou processar todos registros')
            break
        elif identificador == '9999':
            print('arquivo sem reg de I200, processou inteiro')
            break
        else:
            continue
