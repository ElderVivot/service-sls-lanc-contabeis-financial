try:
    import unzip_requirements
except ImportError:
    pass

try:
    from typing import Dict, Any, List
    from src.functions import returnDataInDictOrArray, treatTextField, minimalizeSpaces, \
        treatNumberField, treatTextFieldInVector, treatDecimalFieldInVector, treatDateField, treatDateFieldInVector
except Exception as e:
    print(f"Error importing libraries {e}")


dataDefaultAboutColumns = {
    "paymentDate": "",
    "nameProviderClient": "",
    "nameProvider": "",
    "nameClient": "",
    "document": "",
    "bank": "",
    "amountPaid": 0.0,
    "amountReceived": 0.0,
    "amountPaidOrReceived": 0.0,
    "amountOriginal": 0.0,
    "amountInterest": 0.0,
    "amountFine": 0.0,
    "amountDiscount": 0.0,
    "amountRate": 0.0,
    "account": "",
    "cgceProviderClient": "",
    "dueDate": "",
    "issueDate": "",
    "historic": "",
    "category": "",
    "accountPlan": "",
    "companyBranch": "",
    "typeMoviment": "",
}


def getListColumnsThatHaveValue(listOfColumnsThatHaveValue: List[str], data: Dict[str, Any]):
    for key, value in data.items():
        try:
            if listOfColumnsThatHaveValue.count(key) > 0:
                continue
            else:
                if value != dataDefaultAboutColumns[key]:
                    listOfColumnsThatHaveValue.append(key)
        except Exception:
            pass
    return listOfColumnsThatHaveValue
