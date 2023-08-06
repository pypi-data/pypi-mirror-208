# -*- coding: utf-8 -*-
# @Time    : 2023/4/4 16:24
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : backup_data_extra.py
from ultipa.connection.connection_base import ConnectionBase
from ultipa.proto import ultipa_pb2
from ultipa.utils import UQLMAKER, CommandList
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils.errors import ParameterException
from ultipa.utils.format import FormatType
from ultipa.utils.ResposeFormat import ResponseKeyFormat

JSONSTRING_KEYS = ["graphPrivileges", "systemPrivileges", "policies", "policy", "privilege"]
formatdata = ['graph_privileges']


class BackupDataExtra(ConnectionBase):

	def backupData(self, backupPath: str,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		requestConfig.useMaster = True
		response = ULTIPA_RESPONSE.Response()
		clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster,
										isGlobal=True)
		request = ultipa_pb2.BackupRequest()
		request.backup_path = backupPath
		bakupRet = clientInfo.Controlsclient.Backup(request,metadata=clientInfo.metadata)
		status = FormatType.status(bakupRet.status)
		response.status = status
		if self.defaultConfig.responseWithRequestInfo:
			response.req = ULTIPA.ReturnReq(self.graphSetName, "backupData",
											requestConfig.useHost if requestConfig.useHost else self.host, requestConfig.retry,
											False)
		return response