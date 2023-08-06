from nacos.api.base import BaseNacosAPI
from nacos.api.models import InstanceListModel, InstanceModel, InstanceSendHeartBeatModel


class NacosInstance(BaseNacosAPI):

    def get(self,
            service_name: str,
            ip: str,
            port: int,
            *,
            namespace_id: str = 'public',
            group_name: str = 'DEFAULT_GROUP',
            cluster_name: str = 'DEFAULT'):
        """查询某个具体实例的详情信息

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        cluster_name, optional
            集群名称, by default 'DEFAULT'

        Example
        ----------
            from nacos.client import NacosClient

            client = NacosClient('server_addresses', 'namespace', 'username', 'password')
            response = client.instance.get('service_name', '127.0.0.1', 8000)
        """

        params = {
            'serviceName': f'{group_name}@@{service_name}',
            'ip': ip,
            'port': port,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'clusterName': cluster_name
        }
        res = self._get('/nacos/v2/ns/instance', params=params)
        return InstanceModel.parse_raw(res.content)

    def query(self,
              service_name: str,
              *,
              ip: str = '',
              port: int = 0,
              namespace_id: str = 'public',
              group_name: str = 'DEFAULT_GROUP',
              cluster_name: str = 'DEFAULT',
              healthy_only: bool = False,
              app: str = ''):
        """查询指定服务下的实例详情信息列表

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        cluster_name, optional
            集群名称, by default 'DEFAULT'
        healthy_only, optional
            是否只获取健康实例, by default False
        app, optional
            应用名, by default ''

        Returns
        -------
            InstanceListModel
        """

        params = {
            'serviceName': f'{group_name}@@{service_name}',
            'ip': ip,
            'port': port,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'clusterName': cluster_name,
            'healthyOnly': healthy_only,
            'app': app
        }
        res = self._get('/nacos/v2/ns/instance/list', params=params)
        return InstanceListModel.parse_raw(res.content)

    def create(self,
               service_name: str,
               ip: str,
               port: int,
               *,
               namespace_id: str = 'public',
               group_name: str = 'DEFAULT_GROUP',
               cluster_name: str = 'DEFAULT',
               healthy: bool = True,
               weight: float = 1.0,
               enabled: bool = True,
               metadata: str = '{}',
               ephemeral: bool = False):
        """注册实例

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        cluster_name, optional
            集群名称, by default 'DEFAULT'
        healthy, optional
            是否只查找健康实例, by default True
        weight, optional
            实例权重, by default 1.0
        enabled, optional
            是否可用, by default True
        metadata, optional
            实例元数据, by default "{}"
        ephemeral, optional
            是否为临时实例, by default False
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'ip': ip,
            'port': port,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'clusterName': cluster_name,
            'healthy': healthy,
            'weight': weight,
            'enabled': enabled,
            'metadata': metadata,
            'ephemeral': ephemeral
        }
        return self._post('/nacos/v2/ns/instance', data=data)

    def update(self,
               service_name: str,
               ip: str,
               port: int,
               *,
               namespace_id: str = 'public',
               group_name: str = 'DEFAULT_GROUP',
               cluster_name: str = 'DEFAULT',
               healthy: bool = True,
               weight: float = 1.0,
               enabled: bool = True,
               metadata: str = "{}",
               ephemeral: bool = False):
        """修改指定实例

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        cluster_name, optional
            集群名称, by default 'DEFAULT'
        healthy, optional
            是否只查找健康实例, by default True
        weight, optional
            实例权重, by default 1.0
        enabled, optional
            是否可用, by default True
        metadata, optional
            实例元数据, by default "{}"
        ephemeral, optional
            是否为临时实例, by default False
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'ip': ip,
            'port': port,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'clusterName': cluster_name,
            'healthy': healthy,
            'weight': weight,
            'enabled': enabled,
            'metadata': metadata,
            'ephemeral': ephemeral
        }
        return self._put('/nacos/v2/ns/instance', data=data)

    def update_health(self,
                      service_name: str,
                      ip: str,
                      port: int,
                      healthy: bool,
                      *,
                      namespace_id: str = 'public',
                      group_name: str = 'DEFAULT_GROUP',
                      cluster_name: str = 'DEFAULT'):
        """更新实例的健康状态

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        healthy
            是否健康
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        cluster_name, optional
            集群名称, by default 'DEFAULT'
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'ip': ip,
            'port': port,
            'healthy': healthy,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'clusterName': cluster_name
        }
        return self._put('/nacos/v2/ns/health/instance', data=data)

    def delete(self,
               service_name: str,
               ip: str,
               port: int,
               *,
               namespace_id: str = 'public',
               group_name: str = 'DEFAULT_GROUP',
               cluster_name: str = 'DEFAULT',
               healthy: bool = True,
               weight: float = 1.0,
               enabled: bool = True,
               metadata: str = "{}",
               ephemeral: bool = False):
        """注销指定实例

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        cluster_name, optional
            集群名称, by default 'DEFAULT'
        healthy, optional
            是否只查找健康实例, by default True
        weight, optional
            实例权重, by default 1.0
        enabled, optional
            是否可用, by default True
        metadata, optional
            实例元数据, by default "{}"
        ephemeral, optional
            是否为临时实例, by default False
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'ip': ip,
            'port': port,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'clusterName': cluster_name,
            'healthy': healthy,
            'weight': weight,
            'enabled': enabled,
            'metadata': metadata,
            'ephemeral': ephemeral
        }
        return self._delete('/nacos/v2/ns/instance', data=data)

    def batch_update_metadata(self,
                              service_name: str,
                              metadata: str,
                              *,
                              namespace_id: str = 'public',
                              consistency_type: str = '',
                              instances: str = '[]',
                              group_name: str = 'DEFAULT_GROUP'):
        """批量更新实例的元数据

        Parameters
        ----------
        service_name
            服务名
        metadata
            实例元数据
        namespace_id, optional
            命名空间Id, by default 'public'
        consistency_type, optional
            持久化类型, by default ''
        instances, optional
            需要更新的实例列表, by default '[]'
            通过ip+port+ephemeral+cluster定位到某一实例,为空则表示更新指定服务下所有实例的元数据
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        """
        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name,
            'metadata': metadata,
            'consistencyType': consistency_type,
            'instances': instances
        }
        return self._put('/nacos/v2/ns/instance/metadata/batch', data=data)

    def batch_delete_metadata(self,
                              service_name: str,
                              metadata: str,
                              *,
                              namespace_id: str = 'public',
                              consistency_type: str = '',
                              instances: str = '[]',
                              group_name: str = 'DEFAULT_GROUP'):
        """批量删除实例的元数据

        Parameters
        ----------
        service_name
            服务名
        metadata
            实例元数据
        namespace_id, optional
            命名空间Id, by default 'public'
        consistency_type, optional
            持久化类型, by default ''
        instances, optional
            需要更新的实例列表, by default '[]'
            通过ip+port+ephemeral+cluster定位到某一实例,为空则表示更新指定服务下所有实例的元数据
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        """
        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name,
            'metadata': metadata,
            'consistencyType': consistency_type,
            'instances': instances
        }
        return self._delete('/nacos/v2/ns/instance/metadata/batch', data=data)

    def send_heartbeat(self,
                       service_name: str,
                       ip: str,
                       port: int,
                       beat: str,
                       *,
                       namespace_id: str = 'public',
                       group_name: str = 'DEFAULT_GROUP',
                       ephemeral: bool = False):
        """发送心跳

        Parameters
        ----------
        service_name
            服务名
        ip
            IP地址
        port
            端口号
        beat
            心跳信息
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        ephemeral, optional
            是否为临时实例, by default False
        """
        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name,
            'ip': ip,
            'port': port,
            'beat': beat,
            'ephemeral': ephemeral
        }
        res = self._put('/nacos/v1/ns/instance/beat', data=data)
        return InstanceSendHeartBeatModel.parse_raw(res.content)
