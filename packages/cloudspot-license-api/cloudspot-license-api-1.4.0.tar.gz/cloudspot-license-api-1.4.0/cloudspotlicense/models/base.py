
#==============[HELPER FUNCTIONS]=================#


def get_index_with_value(list, attribute, value):

    for index, obj in enumerate(list):
        if hasattr(obj, attribute):
            if getattr(obj, attribute) == value:
                return index
    
    return None

def get_object_with_value(list, attribute, value):

    for index, obj in enumerate(list):
        if hasattr(obj, attribute):
            if getattr(obj, attribute) == value:
                return obj
    
    return None

def format_key(string):
    return (string[0].upper() + string[1:]).replace('_', '@')



#==============[BASE MODELS]=================#

class BaseModel:

    def __init__(self):

        self.has_error = False
        self.error = None

    def parse(self, json):
        for key, value in json.items():
            attrVal = getattr(self, key)

            if isinstance(attrVal, BaseModel):
                setattr(self, key, attrVal.parse(value))
            else:
                setattr(self, key, value)

        return self
    
    def get_json(self):

        dikt = {}
        for k, v in self.__dict__.items():
            if v:
                if isinstance(v, BaseModel):
                    json = v.get_json()
                    if json: dikt[k] = json
                else:
                    dikt[k] = v

        return dikt if len(dikt) > 0 else None
    
    def parse_error(self, json):
        from .errors import Error
        
        self.has_error = True
        self.error = Error().parse(json)

        return self


class ObjectListModel(BaseModel):

    def __init__(self, list=[], listObject=None):
        super().__init__()

        self.list = list
        self.listObject = listObject
        self.has_error = False
        self.error = None

    def add(self, item):
        self.list.append(item)
        return self.list
    
    def remove(self, item):
        self.list.remove(item)
        return self.list

    def get_item_index(self, attribute, value):
        index = get_index_with_value(self.list, attribute, value)
        return index
    
    def get_item_object(self, attribute, value):
        object = get_object_with_value(self.list, attribute, value)
        return object
    
    def parse(self, json):

        if isinstance(json, dict):
            itemObj = self.listObject().parse(json)
            self.add(itemObj)
        elif isinstance(json, list):
            for item in json:
                itemObj = self.listObject().parse(item)
                self.add(itemObj)

        return self
    
    def get_json(self):
        list = []

        for item in self.list:
            list.append(item.get_json())
        
        return list if len(list) > 0 else None

    def items(self):
        return self.list