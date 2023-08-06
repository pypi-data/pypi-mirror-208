import json
from typing import List

class BaseModel:
    def toJSON(self, pretty=False):
        try:
            if pretty:
                return json.dumps(self, default=lambda o: o.__dict__,
                                  sort_keys=True, indent=4, ensure_ascii=False)
            else:

                return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, ensure_ascii=False)

        except Exception as e:
            return self

    def toDict(self):
        return json.loads(self.toJSON())

    def __str__(self):
        return str(self.__dict__)

class Any(BaseModel):
    def __str__(self):
        return  str(self.__dict__)
    pass

def convertToAnyObject(dict1: dict):
    obj = Any()
    for k in dict1.keys():
        v = dict1[k]
        if isinstance(v, list):
            for i, n in enumerate(v):
                if isinstance(n, dict):
                    v[i] = convertToAnyObject(n)
        obj.__setattr__(k, v)
    return obj

def convertToListAnyObject(list1: List[dict]):
    if not list1 and isinstance(list1,list):
        return list1
    if not list1:
        return
    newList = []
    for dict1 in list1:
        newList.append(convertToAnyObject(dict1))
    return newList

def convertAlgoList2AnyObject(list1: List[dict]):
    if not list1 and isinstance(list1,list):
        return list1
    if not list1:
        return
    newList = []
    for dict1 in list1:
        if not dict1.get("write_to_stats_parameters"):
            dict1.update({"write_to_stats_parameters":None})
        if not dict1.get("write_to_db_parameters"):
            dict1.update({"write_to_db_parameters":None})
        if not dict1.get("write_to_file_parameters"):
            dict1.update({"write_to_file_parameters":None})
        newList.append(convertToAnyObject(dict1))
    return newList

def convertTableToListAnyObject(list1: List[dict],headers):
    if not list1 and isinstance(list1,list):
        return list1
    if not list1:
        return list1
    if not headers:
        return list1

    newList = []
    for data in list1:
        dic = {}
        for index,header in enumerate(headers):
            dic.update({header.get("property_name"):data[index]})
        newList.append(convertToAnyObject(dic))

    return newList

def convertTableToDict(table_rows,headers):
    newList = []
    for data in table_rows:
        dic = {}
        for index,header in enumerate(headers):
            dic.update({header.get("property_name"):data[index]})
        newList.append(dic)
    return newList
