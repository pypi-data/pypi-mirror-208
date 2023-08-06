import json
import logging
import time

import config
import makepath

from nacos import NacosClient

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s [%(pathname)s:%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)

namespace_id = '8217d979-ffae-4b4e-ac66-1b7d5962f078'
service_name = 'monitor'
group_name = 'public'

nc = NacosClient(**config.NACOS_CONFIG)

# config test
# res = nc.config.get(group_name, 'BASE-CONFIG', namespace_id=namespace_id)
# res = nc.config.get_history_previous(group_name, 'BASE-CONFIG', 184, namespace_id=namespace_id)
# res = nc.config.get_history(group_name, 'BASE-CONFIG', 299, namespace_id=namespace_id)
# res = nc.config.get_history_list(group_name, 'BASE-CONFIG', namespace_id=namespace_id)
# res = nc.config.create(
#     group_name, 'testCase', 
#     content="{\n    \"test\": \"1111\"\n}", 
#     namespace_id=namespace_id, 
#     config_tags="test,test1", app_name='TEST')
# res = nc.config.delete(group_name, 'testCase', namespace_id=namespace_id)

# service_test
# res = nc.service.get(service_name, namespace_id=namespace_id, group_name=group_name)
# res = nc.service.get_by_namespace(namespace_id, group_name=group_name, service_name=service_name)
res = nc.service.query('{}', namespace_id=namespace_id, group_name=group_name)
print(res)