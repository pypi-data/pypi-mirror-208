import json
import logging
import random
import signal
import sys
import threading
import time
from collections import defaultdict

from nacos import api
from nacos.client.base import BaseNacosClient

logger = logging.getLogger(__name__)


class NacosClient(BaseNacosClient):

    instance = api.NacosInstance()
    config = api.NacosConfig()
    service = api.NacosService()

    def __init__(self,
                 server_addresses: str,
                 username: str,
                 password: str,
                 namespace_id: str = None):
        super().__init__(server_addresses, username, password, namespace_id)

        self.service_dict = defaultdict(lambda: defaultdict(list))
        self.register_info = None

        if namespace_id:
            subscribe_thread = threading.Thread(target=self.subscribe_services)
            subscribe_thread.setDaemon(True)
            subscribe_thread.start()

    def get_random_instance(self, service_name, group_name='public', cluster_name="DEFAULT"):
        if not self.namespace_id:
            return None
        hosts = self.service_dict[f'{group_name}@@{service_name}'][cluster_name]
        if not hosts:
            # 获取instance list
            res = self.instance.query(service_name, group_name=group_name,
                                      cluster_name=cluster_name, namespace_id=self.namespace_id)
            hosts = [f'{host.ip}:{host.port}' for host in res.hosts if host.healthy and host.enabled]
            self.service_dict[f'{group_name}@@{service_name}'][cluster_name] = hosts
        return random.choice(hosts) if hosts else None

    def subscribe_services(self):
        while True:
            response = self.service.get_by_namespace(self.namespace_id, with_instances=True, page_size=999)
            for i in response.json():
                for cluster, item in i['clusterMap'].items():
                    self.service_dict[f'{i["groupName"]}@@{i["serviceName"]}'][cluster] = [
                        f"{j['ip']}:{j['port']}" for j in item['hosts'] if j['enabled']]

            time.sleep(5)

    def register(self,
                 service_name: str,
                 ip: str,
                 port: int,
                 *,
                 namespace_id: str = 'public',
                 group_name: str = 'public',
                 cluster_name: str = 'DEFAULT',
                 healthy: bool = True,
                 weight: float = 1.0,
                 enabled: bool = True,
                 metadata: str = '{}',
                 ephemeral: bool = True):
        """ 自动注册服务
        注册实例、发送心跳；服务终止时删除实例

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
            是否为临时实例, by default True
        """

        signal.signal(signal.SIGTERM, self.delete_instance)
        signal.signal(signal.SIGINT, self.delete_instance)

        self.register_info = locals()

        try:
            # 注册实例
            logger.info(
                f'[InstanceRegister] service_name: {service_name}, ip: {ip}, port: {port}, group_name: {group_name}, namespace_id: {namespace_id}')
            result = self.instance.create(service_name, ip, port, namespace_id=namespace_id, group_name=group_name,
                                          cluster_name=cluster_name, healthy=healthy, weight=weight, enabled=enabled, metadata=metadata, ephemeral=ephemeral)
            if result.content == b'ok':
                logger.info(
                    f'[InstanceRegister] register success! service_name: {service_name}, ip: {ip}, port: {port}, group_name: {group_name}, namespace_id: {namespace_id}')
                while True:
                    # 发送心跳
                    beat_data = {
                        "serviceName": f'{group_name}@@{service_name}',
                        "ip": ip,
                        "port": port,
                        "weight": weight,
                        "groupName": group_name,
                        "clusterName": cluster_name,
                        "ephemeral": ephemeral,
                        "metadata": json.loads(metadata)
                    }
                    logger.info(
                        f'[InstanceRegister] send heartbeat. service_name: {service_name}, ip: {ip}, port: {port}, group_name: {group_name}, namespace_id: {namespace_id}, beat: {beat_data}')
                    result = self.instance.send_heartbeat(service_name, ip, port, json.dumps(beat_data),
                                                          namespace_id=namespace_id, group_name=group_name, ephemeral=ephemeral)
                    if result.code != 10200:
                        logger.error(
                            f'[InstanceRegister] send heartbeat failed! service_name: {service_name}, ip: {ip}, port: {port}, group_name: {group_name}, namespace_id: {namespace_id}, beat: {beat_data}')
                        break
                    time.sleep(5)
            else:
                logger.error(
                    f'[InstanceRegister] register failed! service_name: {service_name}, ip: {ip}, port: {port}, group_name: {group_name}, namespace_id: {namespace_id}')
        except (KeyboardInterrupt, SystemExit, EOFError, OSError):
            pass
        except:
            logger.error(
                f'[InstanceRegister] register failed! service_name: {service_name}, ip: {ip}, port: {port}, group_name: {group_name}, namespace_id: {namespace_id}')

    def delete_instance(self, signum, frame):
        logger.info(f'[InstanceRegister] catch signal {signum}, frame: {frame}, delete instance!')
        if self.register_info:
            # 注销服务
            result = self.instance.delete(self.register_info['service_name'], self.register_info['ip'], self.register_info['port'], namespace_id=self.register_info['namespace_id'],
                                          group_name=self.register_info['group_name'], ephemeral=self.register_info['ephemeral'])
            if result.content == b'ok':
                logger.info(
                    f'[InstanceRegister] delete instance success! {self.register_info["service_name"]}, ip: {self.register_info["ip"]}, port: {self.register_info["port"]}, group_name: {self.register_info["group_name"]}, namespace_id: {self.register_info["namespace_id"]}')
        sys.exit(1)
