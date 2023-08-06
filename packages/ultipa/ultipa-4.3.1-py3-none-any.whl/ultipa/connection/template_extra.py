from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList
import json
from typing import List


class TemplateExtra(ConnectionBase):
	def template(self, request: ULTIPA_REQUEST.Template,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		'''
		:EXP: conn.searchNode(ULTIPA_REQUEST.SearchMate(id='1',select=['name']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.isKhopTemplate and CommandList.khop or CommandList.template
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig, commandP=request.alias)
		uqlMaker.addTemplateParams(request.items)
		uqlMaker.addParam("limit", request.limit)
		uqlMaker.addParam("order_by", request.order_by)
		uqlMaker.addParam("return", request._return)
		if request.select:
			uqlMaker.addParam("select", request.select)
		res = self.uqlSingle(uqlMaker)
		if res.status.code != ULTIPA.Code.SUCCESS:
			return res
		return res
