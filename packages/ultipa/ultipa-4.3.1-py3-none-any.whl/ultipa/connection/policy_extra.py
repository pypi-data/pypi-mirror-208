from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA_RESPONSE, ULTIPA
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.errors import ParameterException
from ultipa.utils.ResposeFormat import ResponseKeyFormat

JSONSTRING_KEYS = ["graphPrivileges", "systemPrivileges", "policies", "policy", "privilege"]
formatdata = ['graph_privileges']


class PolicyExtra(ConnectionBase):

	def showPolicy(self,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListPolicy:
		'''
		:EXP: conn.listPolicy()
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.showPolicy, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker,
								 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS, dataFormat=formatdata))
		return res

	def showPrivilege(self,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListPrivilege:
		'''
		:EXP: conn.listPolicy()
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.showPrivilege, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker,
								 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS))
		return res

	def getPolicy(self, request: ULTIPA_REQUEST.GetPolicy,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponsePolicy:
		'''
		:param requestConfig:
		:EXP: conn.getPolicy(ULTIPA_REQUEST.Policy(name='sales',privileges=['QUERY']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.getPolicy, commonParams=requestConfig)
		uqlMaker.setCommandParams(request.name)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker,
								 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS, dataFormat=formatdata))
		if isinstance(res.data, list) and len(res.data) > 0:
			res.data = res.data[0]
		return res

	def createPolicy(self, request: ULTIPA_REQUEST.CreatePolicy,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.createPolicy(ULTIPA_REQUEST.Policy(name='sales',privileges=['QUERY']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.createPolicy, commonParams=requestConfig)
		paramsP = [request.name]
		if request.graph_privileges:
			paramsP.append(request.graph_privileges)
		else:
			paramsP.append({})
		if request.system_privileges:
			paramsP.append(request.system_privileges)
		else:
			paramsP.append([])
		if request.policies:
			paramsP.append(request.policies)
		else:
			paramsP.append([])
		uqlMaker.setCommandParams(paramsP)
		# uqlMaker.addParam('name',request.name)
		# uqlMaker.addParam('system_privileges',request.system_privileges)
		# uqlMaker.addParam('graph_privileges',request.graph_privileges)
		# uqlMaker.addParam('policies',request.policies)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def alterPolicy(self, request: ULTIPA_REQUEST.AlterPolicy,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.alterPolicy(ULTIPA_REQUEST.AlterPolicy(name='sales', privileges=['QUERY','DELETE']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.alterPolicy, commonParams=requestConfig)
		uqlMaker.setCommandParams(request.name)
		params = {}
		if request.system_privileges is not None:
			params.update({"system_privileges": request.system_privileges})
		if request.graph_privileges is not None:
			params.update({"graph_privileges": request.graph_privileges})
		if request.policies is not None:
			params.update({"policies": request.policies})
		uqlMaker.addParam('set', params, notQuotes=True)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def dropPolicy(self, request: ULTIPA_REQUEST.DropPolicy,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.dropPolicy(ULTIPA_REQUEST.DropPolicy(name='sales'))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.dropPolicy, commonParams=requestConfig)
		uqlMaker.setCommandParams(request.name)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def grantPolicy(self, request: ULTIPA_REQUEST.GrantPolicy,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.grant(ULTIPA_REQUEST.GrantRevoke(username='sales', privileges=['QUERY']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.grant, commonParams=requestConfig)
		if request.username:
			uqlMaker.setCommandParams(request.username)
		else:
			raise ParameterException(err='username is a required parameter')

		paramsDict = {}
		if request.graph_privileges:
			paramsDict.setdefault('graph_privileges', request.graph_privileges)

		if request.system_privileges:
			paramsDict.setdefault('system_privileges', request.system_privileges)

		if request.policies:
			paramsDict.setdefault('policies', request.policies)
		uqlMaker.addParam('params', paramsDict, notQuotes=True)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def revokePolicy(self, request: ULTIPA_REQUEST.RevokePolicy,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.revoke(ULTIPA_REQUEST.GrantRevoke(username='sales', privileges=['QUERY']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.revoke, commonParams=requestConfig)
		if request.username:
			uqlMaker.setCommandParams(request.username)
		else:
			raise ParameterException(err='username is a required parameter')

		paramsDict = {}
		if request.graph_privileges:
			paramsDict.setdefault('graph_privileges', request.graph_privileges)

		if request.system_privileges:
			paramsDict.setdefault('system_privileges', request.system_privileges)

		if request.policies:
			paramsDict.setdefault('policies', request.policies)
		uqlMaker.addParam('params', paramsDict, notQuotes=True)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res
