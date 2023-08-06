# nacos-client-py
## 安装
```
pip install nacos-client-py
```
## 使用说明
## 配置项
```json

# nacos 服务配置
SERVER_ADDRESSES = ""
NAMESPACE = ""
USERNAME = ""
PASSWORD = ""

# 服务名
SERVICE_NAME = ""
# 服务端口
SERVICE_PORT = 8080

```
### 服务注册
```
import config
from nacos_client import NacosClient, get_local_ip

nc = NacosClient(config.SERVER_ADDRESSES, config.NAMESPACE, config.USERNAME, config.PASSWORD)

# 服务注册
nc.register(config.SERVICE_NAME, get_local_ip(), config.SERVICE_PORT)

# 开启调试模式
nc.set_debugging()
```
### 服务调用
```
import config
from nacos_client import NacosClient

nc = NacosClient(config.SERVER_ADDRESSES, config.NAMESPACE, config.USERNAME, config.PASSWORD)


@nc.request(service='test-service', path='/test', method='GET')
def test_get():
    pass


@nc.request(service='test-service', path='/test', method='POST')
def test_post():
    pass


# 服务调用 参数传递遵循requests参数规范。
try:
    # get请求参数使用params键传递
    response = test_get(params={'test': 'test'})

    # post表单
    response = test_post(data={'test': 'test'}, headers={'Token': 'test'})

    # post json
    response = test_post(json={'test': 'test'}, timeout=5)

    print(response.json())

except Exception as e:
    print(str(e))
```
