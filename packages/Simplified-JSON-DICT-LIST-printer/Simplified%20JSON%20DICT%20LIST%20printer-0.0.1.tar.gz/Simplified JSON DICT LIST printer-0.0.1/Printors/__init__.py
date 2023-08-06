import pprint
import inspect

def print_dict_as_table(targetDict:dict)->None:
    for key in targetDict:
        print(f"key={key} value={targetDict[key]}")

def print_list_as_table(targetList:list)->None:
    for index in range(len(targetList)):
        print(f"index={index} element={targetList[index]}")


def print_dict(targetDict:dict)->None:
    pprint.pprint(targetDict)

def print_list(targetList:list)->None:
    pprint.pprint(targetList)
    
# used for decorator
def called_from():
    frame_info = inspect.stack()[1]
    filename = frame_info.filename
    line_number = frame_info.lineno
    print(f"Called from {filename}:{line_number}")


if __name__ == "__main__":
    called_from()
    sample = {
        "key": "valueff"
    }
    print_dict_as_table(sample)

    sampleList = [1,"poggers",3,4]
    print_list_as_table(sampleList)
