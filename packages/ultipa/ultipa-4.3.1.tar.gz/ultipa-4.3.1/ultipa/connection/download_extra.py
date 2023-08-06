from typing import List

from ultipa.connection.connection_base import ConnectionBase
from ultipa.proto import ultipa_pb2
from ultipa.types import ULTIPA_REQUEST, ULTIPA_RESPONSE, ULTIPA
from ultipa.utils.format import FormatType


class DownloadExtra(ConnectionBase):

	def _download(self, request: ULTIPA_REQUEST.Download,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> List[
		ULTIPA_RESPONSE.Response]:
		'''
		:param requestConfig:
		:param task_id:
		:param file_name:
		:EXP:
			with open('./XXXXX.csv', 'ab+') as f:
				for data_flow in ret:
					data = data_flow.chunk
					f.write(data)
		:return: stream
		'''
		downResponse = ULTIPA_RESPONSE.Response()
		try:
			clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster)
			res = clientInfo.Controlsclient.DownloadFileV2(
				ultipa_pb2.DownloadFileRequestV2(file_name=request.fileName, task_id=request.taskId),
				metadata=clientInfo.metadata)
			if request.savePath:
				with open(request.savePath, 'wb+') as f:
					for data_flow in res:
						status = FormatType.status(data_flow.status)
						downResponse.status = status
						if status.code != ULTIPA.Code.SUCCESS:
							yield downResponse
							break
						data = data_flow.chunk
						f.write(data)
				# downResponse.status = ULTIPA.Status(code=ULTIPA.Code.SUCCESS, message="")
				yield downResponse
			else:
				for data_flow in res:
					ultipa_response = ULTIPA_RESPONSE.Response()
					status = FormatType.status(data_flow.status)
					ultipa_response.status = status
					if status.code != ULTIPA.Code.SUCCESS:
						yield ultipa_response
						break
					ultipa_response.data = data_flow.chunk
					yield ultipa_response
		except Exception as e:
			downResponse.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=str(e._state.details))
			yield downResponse

	def download(self, request: ULTIPA_REQUEST.Download,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> List[
		ULTIPA_RESPONSE.Response]:
		return  list(self._download(request,requestConfig))