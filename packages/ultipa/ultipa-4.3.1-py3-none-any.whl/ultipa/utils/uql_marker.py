import json
import re
from typing import List
from ultipa.utils import errors
from ultipa.utils.ufilter.new_ufilter import UltipaFilter, Filter
from ultipa.utils.ufilter.ufilter import FilterBase


# from ultipa.types.types_request import TemplateBaseItem

class CommandList:
    ab = "ab"
    khop = "khop"
    nodes = "find().nodes"
    edges = "find().edges"
    deleteNodes = "delete().nodes"
    deleteEdges = "delete().edges"
    updateNodes = "update().nodes"
    updateEdges = "update().edges"
    template = "t"
    autoNet = "autoNet"
    autoNetByPart = "autoNetByPart"
    nodeSpread = "spread"
    insert = "insert"
    upsert = "upsert"
    showProperty = "show().property"
    showNodeProperty = "show().node_property"
    showEdgeProperty = "show().edge_property"
    createNodeProperty = "create().node_property"
    createEdgeProperty = "create().edge_property"
    dropNodeProperty = "drop().node_property"
    dropEdgeProperty = "drop().edge_property"
    alterNodeProperty = "alter().node_property"
    alterEdgeProperty = "alter().edge_property"
    showSchema = "show().schema"
    showNodeSchema = "show().node_schema"
    showEdgeSchema = "show().edge_schema"
    createNodeSchema = "create().node_schema"
    createEdgeSchema = "create().edge_schema"
    alterNodeSchema = "alter().node_schema"
    alterEdgeSchema = "alter().edge_schema"
    dropNodeSchema = "drop().node_schema"
    dropEdgeSchema = "drop().edge_schema"
    lteNode = "LTE().node_property"
    lteEdge = "LTE().edge_property"
    ufeNode = "UFE().node_property"
    ufeEdge = "UFE().edge_property"
    createNodeIndex = "create().node_index"
    createEdgeIndex = "create().edge_index"
    createNodeFulltext = "create().node_fulltext"
    createEdgeFulltext = "create().edge_fulltext"
    showIndex = "show().index"
    showNodeIndex = "show().node_index"
    showEdgeIndex = "show().edge_index"
    showFulltext = "show().fulltext"
    showNodeFulltext = "show().node_fulltext"
    showEdgeFulltext = "show().edge_fulltext"
    dropNodeIndex = "drop().node_index"
    dropEdgeIndex = "drop().edge_index"
    dropNodeFulltext = "drop().node_fulltext"
    dropEdgeFulltext = "drop().edge_fulltext"
    stat = "stats"
    algo = "algo"
    algo_dv = "algo_dv"
    showPrivilege = "show().privilege"
    grant = "grant().user"
    revoke = "revoke().user"
    showAlgo = "show().algo"
    showGraph = "show().graph"
    createGraph = "create().graph"
    dropGraph = "drop().graph"
    alterGraph = "alter().graph"
    truncate = "truncate"
    compact = "compact"
    showUser = "show().user"
    getUser = "show().user"
    getSelfInfo = "show().self"
    createUser = "create().user"
    alterUser = "alter().user"
    dropUser = "drop().user"
    createPolicy = "create().policy"
    alterPolicy = "alter().policy"
    dropPolicy = "drop().policy"
    showPolicy = "show().policy"
    getPolicy = "show().policy"
    showTask = "show().task"
    clearTask = "clear().task"
    pauseTask = "pause().task"
    resumeTask = "resume().task"
    stopTask = "stop().task"
    top = "top"
    kill = "kill"
    mount = "mount().graph"
    unmount = "unmount().graph"

def _replace(value:str):
    template = re.compile(r"\'?\"?(point\([^)]*\))\'?\"?")
    matches = re.search(template, value)
    if matches:
        return re.sub(r"\'?\"?(point\([^)]*\))\'?\"?",matches.group(1),value)
    return value

class UQLMAKER:
    def __init__(self, command: CommandList, commandP: any = None, commonParams=None):
        self._command = command
        self._commandP = commandP
        self.commonParams = commonParams
        self._params: List[object] = []
        self.templateParams: List[object] = []

    @staticmethod
    def PointFunction(latitude: float, longitude: float):
        return "point({latitude:%s, longitude:%s})" % (latitude,longitude)

    @staticmethod
    def PointString(latitude: float, longitude: float):
        return f"POINT({latitude} {longitude})"

    def setCommandParams(self, commandP: any):
        if commandP:
            if not isinstance(commandP, list):
                self._commandP = [commandP]
            else:
                self._commandP = commandP
            newcommandP = []
            for comm in self._commandP:
                if isinstance(comm, list) or isinstance(comm, dict) or isinstance(comm, int):
                    newcommandP.append(str(comm))
                    continue
                if isinstance(comm, Filter):
                    if isinstance(comm, str):
                        continue
                    newcommandP.append("{%s}" % (comm.builder()))
                    continue
                if not comm:
                    newcommandP.append(comm)
                    continue
                if comm.startswith('{'):
                    newcommandP.append(comm)
                    continue
                if comm.startswith('@'):
                    newcommandP.append(comm)
                else:
                    newcommandP.append(json.dumps(comm, ensure_ascii=False))

            commandP = ','.join(newcommandP)
        else:
            return
        if type(commandP) == object:
            commandP = json.dumps(commandP, ensure_ascii=False)
        if isinstance(commandP, Filter):
            commandP = commandP.builder()
        # 将 commandp 变成带有双引号的
        # if type(commandP) == str and len(commandP) > 0 :
        #     commandP = json.dumps(commandP)
        self._commandP = commandP

    def addTemplateParams(self, templateParams: List[object]):
        self.templateParams = templateParams

    def addParam(self, key: str, value: any, required: bool = True, notQuotes=False):
        try:
            if notQuotes:
                self._params.append({"key": key, "value": value})
                return
            _notStringify = False
            if type(value) == bool:
                if value:
                    required = False
                value = ""
            if required:
                if isinstance(value, list) or value or value == 0:
                    pass
                else:
                    return
            if "filter" == key:
                self.addParam("node_filter", value)
                self.addParam("edge_filter", value)
                return

            if key in ["filter", "node_filter", "edge_filter"]:
                _notStringify = True
                if isinstance(value, FilterBase):
                    value = value.builder()

            if key == 'return':
                if type(value) == list:
                    value = ','.join([i.toString for i in value])
                elif type(value) == str:
                    self._params.append({"key": key, "value": value})
                    return
                else:
                    value = value.toString
                self._params.append({"key": key, "value": value})
                return
            if key in ['into', 'as']:
                self._params.append({"key": key, "value": value})
                return

            # if key in ["select", "select_node_properties", "select_edge_properties", "srcs",
            #            "dests", "return"]:
            #     _notStringify=True
            #     if value:
            #         value = ','.join(map(str,value))

            if key in ['graph_privileges']:
                if isinstance(value, list):
                    value = [{v.toDict().get('name'): v.toDict().get('values')} for v in value]
                else:
                    value = [{value.toDict().get('name'): value.toDict().get('values')}]

            # 判断value 是否为对象 或者 为 str -> select('name')
            # 将 value 变成双引号
            if type(value) == object or type(value) == dict or (
                    type(value) == str and len(value) > 0 and not _notStringify):
                value = json.dumps(value,ensure_ascii=False)
            if isinstance(value,list):
                value =[i for i in value]
            # value = re.sub("(point\([^)]*\))",value,value)

            if value == [] or value == None:
                return
            self._params.append({"key": key, "value": value})
        except Exception as e:
            raise errors.ParameterException(e)

    def toString(self):
        uql = ""
        str_return = ""
        if self._commandP:
            self._commandP = self._commandP
            uql += "{}({})".format(self._command, self._commandP)
        else:
            uql += "{}({})".format(self._command, '')
        if len(self.templateParams) > 0:
            for tp in self.templateParams:
                filterString = ''
                if tp.filter:
                    if isinstance(tp.filter, FilterBase):
                        tp.filter = tp.filter.builder()
                    filterString = tp.filter
                node_filter_str = ''
                if tp.__dict__.get('node_fitler'):
                    if isinstance(tp.node_fitler, FilterBase):
                        tp.node_fitler = tp.node_fitler.builder()
                    node_filter_str = f'.nf{tp.node_fitler}'
                step = tp.__dict__.get('steps')
                stepStr = ''
                if step:
                    stepStr = f'[{":".join(step)}]'
                uql += f'.{tp.name}({tp.alias or ""}{filterString or ""}){node_filter_str}{stepStr}'
        if len(self._params) > 0:
            ps = []
            for p in self._params:
                value = p["value"]
                if p['key'] in ["return", "limit", "as"]:
                    fstr = "{} {}".format(p['key'], value)
                    str_return += fstr + " "
                    continue

                if p['key'] in ["select_node_properties", "select_edge_properties", "srcs",
                                "dests", "return"]:
                    fstr = "{}({})".format(p["key"], value)
                    # fstr = fstr.replace('"' or "'", '')
                else:
                    fstr = "{}({})".format(p["key"], value)
                fstr = _replace(fstr)
                ps.append(fstr)
            if len(ps) > 0:
                uql += "." + ".".join(ps)
        uql += " " + str_return
        return uql.strip()


class UQLParmas():
    def __init__(self):
        self.commands = []
        self.commandParam = {}
        self.params = {}
        self.paramsOriginal = {}

    def getFirstCommands(self):
        if len(self.commands)>0:
            return self.commands[0]
        return None

    def getSecondCommands(self):
        if len(self.commands)>1:
            return self.commands[1]
        return None

    def getCommands(self,index):
        if len(self.commands)>index:
            return self.commands[index]
        return None

    def getCommandsParam(self,index):
        if len(self.commands) > index:
            return self.commandParam.get(self.commands[index])
        return None



class UQL:

    @staticmethod
    def uqlObjectExample(uqlStr):
        ret = UQLParmas()
        ret.uql = uqlStr
        return ret

    @staticmethod
    def parse(uqlStr):
        commandReg = '([a-zA-Z]*)\(([^\(|^\)]*)\)'
        matchAll = re.findall(commandReg, uqlStr)
        result = UQL.uqlObjectExample(uqlStr)
        # index = 0
        for i,m in enumerate(matchAll):
            name, value = m
            result.commands.append(name)
            if isinstance(value,str):
                value = value.replace("\"","").replace("'","")
            result.commandParam.update({name:value})
            # if index == 0:
            #     result.command = name
            #     result.commandParam = value
            # else:
            #     value = value.replace("'" or '"', '')
            #     result.params[name] = value
            #     result.paramsOriginal[name] = value
            # index += 1
        return result

    # @staticmethod
    # def parse(uqlStr):
    #     # regList=['([a-zA-Z]*)\(([^\(|^\)]*)\)','^exec task\s(\d+)?\s+(.*)']
    #     regList=['(.*\(\)\.?.*)?(\(.*)','^exec task\s(\d+)?\s+(.*)']
    #     for commandReg in regList:
    #         matchAll = re.findall(commandReg, uqlStr)
    #         result = UQL.uqlObjectExample(uqlStr)
    #         index = 0
    #         if matchAll:
    #             for m in matchAll:
    #                 name, value = m
    #                 if not name:
    #                     return UQL.parsegeneral(uqlStr)
    #                 if index == 0:
    #                     result.command = name
    #                     result.commandParam = value
    #                 else:
    #                     value = value.replace("'" or '"', '')
    #                     result.params[name] = value
    #                     result.paramsOriginal[name] = value
    #                 index += 1
    #             return result
    #         continue

    # @staticmethod
    # def parse(uqlStr):
    #     # regList=['([a-zA-Z]*)\(([^\(|^\)]*)\)','^exec task\s(\d+)?\s+(.*)']
    #     regList=['(.*\(\)\.?.*)?(\(.*)','^exec task\s(\d+)?\s+(.*)']
    #     for commandReg in regList:
    #         matchAll = re.findall(commandReg, uqlStr)
    #         result = UQL.uqlObjectExample(uqlStr)
    #         index = 0
    #         if matchAll:
    #             for m in matchAll:
    #                 name, value = m
    #                 if not name:
    #                     return UQL.parsegeneral(uqlStr)
    #                 if index == 0:
    #                     result.command = name
    #                     result.commandParam = value
    #                 else:
    #                     value = value.replace("'" or '"', '')
    #                     result.params[name] = value
    #                     result.paramsOriginal[name] = value
    #                 index += 1
    #             return result
    #         continue

    # @staticmethod
    # def parsegeneral(uqlStr):
    #     regList=['([a-zA-Z]*)\(([^\(|^\)]*)\)','^exec task\s(\d+)?\s+(.*)']
    #     # regList=['(.*\(\)\.?.*)?(\(.*)','^exec task\s(\d+)?\s+(.*)']
    #     for commandReg in regList:
    #         matchAll = re.findall(commandReg, uqlStr)
    #         result = UQL.uqlObjectExample(uqlStr)
    #         index = 0
    #         if matchAll:
    #             for m in matchAll:
    #                 name, value = m
    #                 if index == 0:
    #                     result.command = name
    #                     result.commandParam = value
    #                 else:
    #                     value = value.replace("'" or '"', '')
    #                     result.params[name] = value
    #                     result.paramsOriginal[name] = value
    #                 index += 1
    #             return result
    #         continue

    @staticmethod
    def parse_globle(uqlStr):
        # regList=['([a-zA-Z]*)\(([^\(|^\)]*)\)','^exec task\s(\d+)?\s+(.*)']
        reg = '(.*\(\)\.[A-Za-z]+\(?)'
        matchAll = re.findall(reg, uqlStr)
        result = UQL.uqlObjectExample(uqlStr)
        index = 0
        if matchAll:
            for value in matchAll:
                result.commands.append(value.strip("("))
                index += 1
            return result

