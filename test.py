from src.functions import readExcelPandas, readCsv
from src.read_lines_and_processed import ReadLinesAndProcessed
from dotenv import load_dotenv
import io
import pandas
import xlrd
load_dotenv()

# dataFile = readExcelPandas('data/t12.csv')
# ReadLinesAndProcessed().executeJobMainAsync(dataFile, 'ffa680d3-3b4e-4/34e021e4-4aa8-4a76-b8cb-159243195509/ABC', False)

pathFile = 'data/t6.xls'
extension = pathFile.split('.')[1].lower()
file = open(pathFile, 'rb')
fileContent = file.read()
fileBytesIO = io.BytesIO(fileContent)
ReadLinesAndProcessed().executeJobMainAsync(fileBytesIO, '660cd413-018f-4/782e94aa-1f78-4347-a2fa-a3009c5c911a/ABC', False, extension)

# 4904e452-9b2c-4/ed5792c9-d944-4dff-bbf1-b4a97af1409f -> ultra
# 97338620-6e04-4/8ecc4b70-3470-4fb9-90a6-2d6f126bf0fd/ABC -> wise contabilidade
# d4192c40-c6e3-4/19814551-87fb-41ad-99b9-e71ee79ac824/ABC -> joze
# 42d48d08-2dfa-4/b1112c3d-1f1b-49ef-a2d6-5923c1544ee5/ABC -> teste
# ffa680d3-3b4e-4/34e021e4-4aa8-4a76-b8cb-159243195509/ABC -> gestao bc -> t12.csv

# book = xlrd.open_workbook(pathFile)
# print("The number of worksheets is {0}".format(book.nsheets))
# print("Worksheet name(s): {0}".format(book.sheet_names()))

# r = pandas.read_excel(pathFile, engine='xlrd')
# print(r)