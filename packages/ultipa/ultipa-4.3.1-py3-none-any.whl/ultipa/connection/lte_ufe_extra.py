from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList


class LteUfeExtra(ConnectionBase):

	def lte(self, request: ULTIPA_REQUEST.LTE,
			requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.lte(ULTIPA_REQUEST.LteUfe(property='name',type=ULTIPA.DBType.DBNODE))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.lteNode or CommandList.lteEdge
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(request.schemaName.toString)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res

	def ufe(self, request: ULTIPA_REQUEST.UFE,
			requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.ufe(ULTIPA_REQUEST.LteUfe(property='name',type=ULTIPA.DBType.DBEDGE))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.ufeNode or CommandList.ufeEdge
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(request.schemaName.toString)
		res = self.uqlSingle(uqlMaker=uqlMaker)
		return res
