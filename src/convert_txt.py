try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import io
    # import pdftotext
except Exception as e:
    print(f"Error importing libraries {e}")


class ConvertTxt(object):
    def __init__(self) -> None:
        self.__folderTmp = '/tmp'

    def __fileByteToPdf(self, fileBytesIO: io.FileIO):
        with open(f'{self.__folderTmp}/out.pdf', 'wb') as f:
            f.write(fileBytesIO.getvalue())

    def pdfToText(self, fileBytesIO: io.FileIO):
        self.__fileByteToPdf(fileBytesIO)

        os.system(f"pdftotext {self.__folderTmp}/out.pdf {self.__folderTmp}/out.txt -layout")

        with open(f'{self.__folderTmp}/out.txt', 'rb') as f:
            data = f.read()
            data = data.decode()
            return data
