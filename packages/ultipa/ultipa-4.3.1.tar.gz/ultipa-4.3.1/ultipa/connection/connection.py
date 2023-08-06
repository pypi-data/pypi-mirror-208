from ultipa.connection.connection_base import ParameterException
from ultipa.connection.user_extra import UserExtra
from ultipa.connection.property_extra import PropertyExtra
from ultipa.connection.node_extra import NodeExtra
from ultipa.connection.edge_extra import EdgeExtra
from ultipa.connection.lte_ufe_extra import LteUfeExtra
from ultipa.connection.index_extra import IndexExtra
from ultipa.connection.policy_extra import PolicyExtra
# from ultipa.connection.algo.degrees_extra import DegreesExtra
# from ultipa.connection.algo.community_extra import CommunityExtra
# from ultipa.connection.algo.embedding_extra import EmbeddingExtra
from ultipa.connection.algo.algo_extra import AlgoExtra
from ultipa.connection.task_extra import TaskExtra
from ultipa.connection.export_extra import ExportExtra
from ultipa.connection.graph_extra import GraphExtra
from ultipa.connection.download_extra import DownloadExtra
from ultipa.connection.truncate_extra import TruncateExtra
from ultipa.connection.schema_extra import SchemaExtra
from ultipa.connection.backup_data_extra import BackupDataExtra
from ultipa.types.types import UltipaConfig
from ultipa.utils.logger import LoggerConfig


class Connection(DownloadExtra, UserExtra, PropertyExtra, NodeExtra, EdgeExtra, LteUfeExtra, IndexExtra, PolicyExtra,
				 TaskExtra, ExportExtra, GraphExtra,AlgoExtra, SchemaExtra, TruncateExtra,BackupDataExtra):

	def RunHeartBeat(self, time: int):
		self.keepConnectionAlive(time)

	def StopHeartBeat(self):
		self.stopConnectionAlive()

	@staticmethod
	def NewConnection(defaultConfig: UltipaConfig = UltipaConfig()):
		conn = None
		if not defaultConfig.hosts:
			raise ParameterException(err="hosts is a required parameter")
		if not defaultConfig.username:
			raise ParameterException(err="username is a required parameter")
		if not defaultConfig.password:
			raise ParameterException(err="password is a required parameter")
		for host in defaultConfig.hosts:
			conn = Connection(host=host, defaultConfig=defaultConfig, crtFilePath=defaultConfig.crtFilePath)
			testRes = conn.test()
			if testRes.status.code == 0:
				if defaultConfig.heartBeat > 0:
					conn.RunHeartBeat(defaultConfig.heartBeat)
				return conn
		return conn

	@staticmethod
	def GetConnection(defaultConfig: UltipaConfig = UltipaConfig()):
		if defaultConfig.uqlLoggerConfig is not None:
			defaultConfig.uqlLoggerConfig.getlogger().warning("The GetConnection method will be removed in a later version. we recommend using NewConnection instead")
		else:
			log = LoggerConfig(name="GetConnection warn", fileName=None,isWriteToFile=False,isStream=True)
			log.getlogger().warning("The GetConnection method will be removed in a later version. we recommend using NewConnection instead")
		return Connection.NewConnection(defaultConfig)

	def __del__(self):
		self.StopHeartBeat()
