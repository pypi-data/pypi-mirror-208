from nacos.api.base import BaseNacosAPI

from .models import ServiceInfoModel, ServiceListModel


class NacosService(BaseNacosAPI):

    def get(self,
            service_name: str,
            *,
            namespace_id: str = 'public',
            group_name: str = 'DEFAULT_GROUP'):
        """查询某个具体服务的详情信息

        Parameters
        ----------
        service_name
            服务名
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'

        Example
        ----------
            from nacos.client import NacosClient

            client = NacosClient('server_addresses', 'namespace', 'username', 'password')
            response = client.service.get('service_name')
        """

        params = {
            'serviceName': f'{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name
        }
        res = self._get('/nacos/v1/ns/service', params=params)
        return ServiceInfoModel.parse_raw(res.content)

    def get_by_namespace(self,
                         namespace_id,
                         *,
                         service_name: str = None,
                         group_name: str = None,
                         has_ip_count: bool = True,
                         with_instances: bool = False,
                         page: int = 1,
                         page_size: int = 20):
        """ 查询指定命名空间下的服务列表

        Parameters
        ----------
        namespace_id
            命名空间
        service_name, optional
            服务名, by default None
        group_name, optional
            分组名, by default None
        has_ip_count, optional
            是否包含ip统计, by default True
        with_instances, optional
            是否返回示例列表, by default False
        page, optional
            当前页, by default 1
        page_size, optional
            页条目数, by default 20

        """
        data = {
            'namespaceId': namespace_id,
            'serviceNameParam': service_name,
            'groupNameParam': group_name,
            'withInstances': with_instances,
            'hasIpCount': has_ip_count,
            'pageNo': page,
            'pageSize': page_size
        }
        return self._get('/nacos/v1/ns/catalog/services', params=data)

    def query(self,
              selector: str,
              *,
              namespace_id: str = 'public',
              group_name: str = 'DEFAULT_GROUP',
              page: int = 1,
              page_size: int = 20):
        """查询符合条件的服务列表

        Parameters
        ----------
        selector
            访问策略
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        page, optional
            当前页, by default 1
        page_size, optional
            页条目数, by default 20

        Returns
        -------
            _description_
        """

        params = {
            'selector': selector,
            'namespaceId': namespace_id,
            'groupName': group_name,
            'pageNo': page,
            'pageSize': page_size}
        res = self._get('/nacos/v2/ns/service/list', params=params)
        return ServiceListModel.parse_raw(res.content)

    def create(self,
               service_name: str,
               *,
               namespace_id: str = 'public',
               group_name: str = 'DEFAULT_GROUP',
               metadata: str = '{}',
               protect_threshold: float = 0,
               ephemeral: bool = False,
               selector: str = ''):
        """注册实例

        Parameters
        ----------
        service_name
            服务名
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        metadata, optional
            实例元数据, by default "{}"
        ephemeral, optional
            是否为临时实例, by default False
        protect_threshold, optional
            保护阈值, by default 0
        selector, optional
            访问策略, by default ''
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name,
            'selector': selector,
            'protectThreshold': protect_threshold,
            'metadata': metadata,
            'ephemeral': ephemeral
        }
        return self._post('/nacos/v2/ns/service', data=data)

    def update(self,
               service_name: str,
               *,
               namespace_id: str = 'public',
               group_name: str = 'DEFAULT_GROUP',
               metadata: str = "{}",
               protect_threshold: float = 0,
               selector: str = ''):
        """更新指定服务
        服务不存在时会报错

        Parameters
        ----------
        service_name
            服务名
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        metadata, optional
            实例元数据, by default "{}"
        protect_threshold, optional
            保护阈值, by default 0
        selector, optional
            访问策略, by default ''
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name,
            'metadata': metadata,
            'protectThreshold': protect_threshold,
            'selector': selector
        }
        return self._post('/nacos/v2/ns/service', data=data)

    def delete(self,
               service_name: str,
               *,
               namespace_id: str = 'public',
               group_name: str = 'DEFAULT_GROUP'):
        """删除指定服务
        服务不存在时会报错，且服务还存在实例时会删除失败

        Parameters
        ----------
        service_name
            服务名
        namespace_id, optional
            命名空间Id, by default 'public'
        group_name, optional
            分组名, by default 'DEFAULT_GROUP'
        """

        data = {
            'serviceName': f'{group_name}@@{service_name}',
            'namespaceId': namespace_id,
            'groupName': group_name,
        }
        return self._delete('/nacos/v2/ns/service', data=data)
