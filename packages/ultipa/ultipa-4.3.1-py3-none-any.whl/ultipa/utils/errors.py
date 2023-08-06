'''
自定义错误异常
'''
class ParameterException(Exception):
    def __init__(self,err='Parameter error!'):
        Exception.__init__(self,err)


class ServerException(Exception):
    def __init__(self,err='Server connection failed!'):
        Exception.__init__(self,err)


class SerializeException(Exception):
    def __init__(self,err='Serialize failed!'):
        Exception.__init__(self,err)



class SettingException(Exception):
    def __init__(self,err='Setting error!'):
        Exception.__init__(self,err)


def checkError(error: str):
    if "large" in error:
        return "argument out of range"
    else:
        return error