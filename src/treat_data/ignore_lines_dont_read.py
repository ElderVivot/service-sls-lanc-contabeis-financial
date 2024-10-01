try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any, List
    from src.functions import returnDataInDictOrArray, treatTextField
except Exception as e:
    print(f"Error importing libraries {e}")


def ignoreLinesDontRead(valuesOfFile: List[Dict[str, Any]], dataSetting: Dict[str, Any]):
    valuesOfFileNew = []

    for key, currentLine in enumerate(valuesOfFile):
        try:
            textCurrentLine = treatTextField(currentLine)
            ignoreThisLine = False
            for lineIgnore in dataSetting['linesToIgnore']:
                textLineIgnore = treatTextField(lineIgnore)
                if textLineIgnore == '__EM_BRANCO__' and textCurrentLine == '':
                    ignoreThisLine = True
                    break
                if textCurrentLine.find(textLineIgnore) >= 0:
                    ignoreThisLine = True
                    break
            if ignoreThisLine is False:
                valuesOfFileNew.append(currentLine)
        except Exception:
            pass

    return valuesOfFileNew
