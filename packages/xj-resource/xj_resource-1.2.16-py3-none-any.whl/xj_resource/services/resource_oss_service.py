# encoding: utf-8
"""
@project: djangoModel->resource_oss_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/11/27 15:47
"""

# 获取授权策略：
# auth = oss2.Auth('LTAI5t5onsy3ZdzvgwJw3va8', 'DoSjbOVo4Hy6PiGwzEDojuB0paYK2D')
# bucket = oss2.Bucket(auth, 'http://oss-cn-beijing.aliyuncs.com', 'sunkaiyan')
# result = bucket.get_bucket_policy()
# policy_json = json.loads(result.policy)
# print("Get policy text: ", policy_json)

from aliyunsdkcore.client import AcsClient
from aliyunsdksts.request.v20150401.AssumeRoleRequest import AssumeRoleRequest

# 构建一个阿里云客户端，用于发起请求。
# 设置调用者（RAM用户或RAM角色）的AccessKey ID和AccessKey Secret。
client = AcsClient('LTAI5tJ3dWCHKsgvDMoNwp1f', 'RHgKlgTBOHq23B3cXmQu7JvV7ukjFR', 'cn-beijing')

# 构建请求。
request = AssumeRoleRequest()
request.set_accept_format('json')

# 设置参数。
request.set_RoleArn("acs:ram::1653068078015058:role/oss-service")
request.set_RoleSessionName("hhoss")

# 发起请求，并得到响应。
response = client.do_action_with_exception(request)
# python2:  print(response)
print(str(response, encoding='utf-8'))
