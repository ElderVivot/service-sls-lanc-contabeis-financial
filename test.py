from src.functions import readExcelPandas, readCsv, readPdf
from src.read_lines_and_processed import ReadLinesAndProcessed
from dotenv import load_dotenv
import io
import pandas
import xlrd
import pandas as pd
import tabula
load_dotenv()

pathFile = 'data/t23.pdf'
extension = pathFile.split('.')[1].lower()
file = open(pathFile, 'rb')
fileContent = file.read()
fileBytesIO = io.BytesIO(fileContent)
ReadLinesAndProcessed().executeJobMainAsync(fileBytesIO, '42d48d08-2dfa-4/67ca0f71-013b-4d45-9928-d0225a46ecd2/ABC', False, extension)


# tabula.convert_into(pathFile, output_path='data/t23.tsv', stream=True, pages='all', output_format='tsv')
# print(data)
# 4904e452-9b2c-4/ed5792c9-d944-4dff-bbf1-b4a97af1409f -> ultra
# 97338620-6e04-4/8ecc4b70-3470-4fb9-90a6-2d6f126bf0fd/ABC -> wise contabilidade
# d4192c40-c6e3-4/19814551-87fb-41ad-99b9-e71ee79ac824/ABC -> joze
# 42d48d08-2dfa-4/b1112c3d-1f1b-49ef-a2d6-5923c1544ee5/ABC -> teste
# ffa680d3-3b4e-4/34e021e4-4aa8-4a76-b8cb-159243195509/ABC -> gestao bc -> t12.csv
# ffa680d3-3b4e-4/fe22b819-9b43-4038-a237-6a87c037d952/ABC -> t14.xlsx
# 42d48d08-2dfa-4/67ca0f71-013b-4d45-9928-d0225a46ecd2/ABC -> t10.xlsx


# r = pandas.read_excel(pathFile, engine='xlrd')
# print(r)

# bytesIORead = fileBytesIO.read()
# bytesIODecode = bytesIORead.decode('UTF-8', errors='ignore')
