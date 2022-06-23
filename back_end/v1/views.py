from django.http import JsonResponse
from django.middleware.csrf import get_token
from HCC.settings import openstack_vpn, aliyun_vpn
from v1.utils import *
import uuid
import json
import paramiko
import os


# Create your views here.


def auth_csrf_func(req):
    result = Result()
    if req.method == "GET":
        # 获取csrf_token的值
        csrf_token = get_token(req)
        result.set_result(200, {'csrf_token': csrf_token})
    else:
        result.set_code(405)
    return JsonResponse(result.get_dict())


def auth_token_func(req):
    result = Result()
    headers = {}
    # 根据账号密码获取token
    if req.method == "POST":
        # 根据账号密码从openstack获取unscoped_token
        body = json.loads(req.body.decode('utf-8'))
        identity = Identity()
        identity.set_identity(body)
        auth = Auth()
        auth.set_unscoped(identity)
        res = get_openstack_token(auth)
        payload = json.loads(res.text)
        if "token" in payload:
            unscoped_token = res.headers["X-Subject-Token"]
            # 通过认证则先获取project_id
            code, project_id = get_project_id(unscoped_token)
            if code == 200:
                scope = {
                    "project": {
                        "id": project_id
                    }
                }
                # 获取到project_id后再获取scoped_token
                auth.set_scoped(identity, scope)
                res = get_openstack_token(auth)
                payload = json.loads(res.text)
                if "token" in payload:
                    headers = {
                        "token": res.headers["X-Subject-Token"]
                    }
                    result.set_result(200, json.loads(res.text))
                else:
                    result.set_code(res.status_code)
            else:
                result.set_code(code)
        else:  # 认证失败
            result.set_code(res.status_code)
    else:
        result.set_code(405)
    return JsonResponse(result.get_dict(), headers=headers)


def auth_password_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_id = payload["token"]["user"]["id"]
        # 更新密码
        if req.method == "POST":
            user = json.loads(req.body.decode('utf-8'))
            code = update_password(user_id, user)
            result.set_code(code)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def auth_access_keys_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        # 获取各云accessKey，并剔除accessKey Secret
        if req.method == "GET":
            if not User.objects.filter(userName=user_name):
                User.objects.create(userName=user_name)
            access_key = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
            if access_key.get("aliyun"):
                access_key["aliyun"]["access_key"].pop("secret")
            result.set_result(200, access_key)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_auth_access_keys_func(req, cloud_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        if req.method == "POST":
            access_key = json.loads(req.body.decode('utf-8'))
            if verify_access_key(access_key, cloud_id):
                access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
                if cloud_id == "aliyun":
                    access_keys["aliyun"] = access_key
                User.objects.filter(userName=user_name).update(accessKeys=json.dumps(access_keys))
                result.set_code(200)
            else:
                result.set_code(400)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def instances_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
        # 获取实例列表
        if req.method == "GET":
            instance_list = []
            code, instances = get_instance_list(token, "openstack")
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            instance_list.extend(instances)
            if access_keys.get("aliyun"):
                code, instances = get_instance_list(access_keys.get("aliyun"), "aliyun")
                if code != 200:
                    result.set_code(code)
                    return JsonResponse(result.get_dict())
                instance_list.extend(instances)
            result.set_result(200, instance_list)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_instances_func(req, cloud_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 创建实例
        if req.method == "POST":
            instance = json.loads(req.body.decode('utf-8')).get("instance")
            code, instance = create_instance(access_key, cloud_id, instance)
            result.set_code(code)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_instances_create_func(req, cloud_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 获取创建实例的参数
        if req.method == "GET":
            code, data = create_instance_parameters(access_key, cloud_id)
            if code == 200:
                result.set_result(code, data)
            else:
                result.set_code(code)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_instances_instance_func(req, cloud_id, instance_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 获取实例详细信息
        if req.method == "GET":
            code, data = get_instance_details(access_key, cloud_id, instance_id)
            result.set_result(code, data)
        # 更新实例信息
        elif req.method == "PUT":
            instance = json.loads(req.body.decode('utf-8'))
            code = update_instance(access_key, cloud_id, instance_id, instance.get("instance"))
            result.set_code(code)
        # 删除实例
        elif req.method == "DELETE":
            code = delete_instance(access_key, cloud_id, instance_id)
            result.set_code(code)
        else:
            result.set_code(403)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_instances_instance_action_func(req, cloud_id, instance_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 操作实例
        if req.method == "POST":
            operation = json.loads(req.body.decode('utf-8'))
            # 启动实例
            if "start" in operation:
                code = start_instance(access_key, cloud_id, instance_id)
            # 停止实例
            elif "stop" in operation:
                code = stop_instance(access_key, cloud_id, instance_id, operation["stop"])
            # 重启实例
            elif "reboot" in operation:
                code = reboot_instance(access_key, cloud_id, instance_id, operation["reboot"])
            else:
                code = 403
            result.set_code(code)
        else:
            result.set_code(403)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def key_pairs_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
        # 获取密钥对列表
        if req.method == "GET":
            key_pair_list = []
            code, key_pairs = get_key_pair_list(token, "openstack")
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            key_pair_list.extend(key_pairs)
            if access_keys.get("aliyun"):
                code, key_pairs = get_key_pair_list(access_keys.get("aliyun"), "aliyun")
                if code != 200:
                    result.set_code(code)
                    return JsonResponse(result.get_dict())
                key_pair_list.extend(key_pairs)
            result.set_result(200, key_pair_list)
        else:
            result.set_code(403)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_key_pairs_func(req, cloud_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 通过导入公钥创建密钥对，由于创建密钥对需要返回私钥并直接弹出下载比较麻烦
        if req.method == "POST":
            key_pair = json.loads(req.body.decode('utf-8')).get("key_pair")
            code, key_pair = import_key_pair(access_key, cloud_id, key_pair)
            result.set_code(code)
        else:
            result.set_code(403)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_key_pairs_key_pair_func(req, cloud_id, key_pair_name):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 删除密钥对
        if req.method == "DELETE":
            code = remove_key_pair(access_key, cloud_id, key_pair_name)
            result.set_code(code)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def vpcs_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        # 获取VPC列表
        if req.method == "GET":
            vpc_list = list(Vpc.objects.filter(userName=user_name).values())
            for vpc in vpc_list:
                vpc["subVpc"] = json.loads(vpc["subVpc"])
                vpc["subVpc"]["openstack"]["key_pair"].pop("private_key")
                vpc["subVpc"]["aliyun"]["key_pair"].pop("private_key")
            result.set_result(200, vpc_list)
        # 创建VPC
        elif req.method == "POST":
            aliyun_access_key = get_access_key(token, user_name, "aliyun")
            vpc = json.loads(req.body.decode('utf-8')).get("vpc")
            subnet = json.loads(req.body.decode('utf-8')).get("subnet")
            instance = json.loads(req.body.decode('utf-8')).get("instance")
            # openstack创建network
            openstack_params = {
                "name": vpc["name"],
            }
            code, openstack_network = create_vpc(token, "openstack", openstack_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # aliyun创建vpc
            aliyun_params = {
                "name": vpc["name"],
                "cidr": vpc["sub_vpc"]["aliyun"]["cidr"]
            }
            code, aliyun_vpc = create_vpc(aliyun_access_key, "aliyun", aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # openstack创建subnet
            openstack_params = {
                "network_id": openstack_network.get("id"),
                "name": subnet["openstack"]["name"],
                "cidr": subnet["openstack"]["cidr"],
                "ip_version": 4,
                "gateway_ip": subnet["openstack"]["gateway_ip"],
            }
            if subnet["openstack"].get("allocation_pools"):
                openstack_params["allocation_pools"] = subnet["openstack"].get("allocation_pools")
            if subnet["openstack"].get("dns_nameservers"):
                openstack_params["dns_nameservers"] = subnet["openstack"].get("dns_nameservers")
            code, openstack_subnet = create_subnet(token, "openstack", openstack_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # openstack创建router
            openstack_params = {
                "name": "",
                "subnet_id": openstack_subnet["id"]
            }
            code, openstack_router = create_router(token, "openstack", openstack_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # aliyun创建subnet，需要等待时间否则可能出错
            time.sleep(5)
            aliyun_params = {
                "VpcId": aliyun_vpc.get("VpcId"),
                "VSwitchName": subnet["aliyun"]["VSwitchName"],
                "ZoneId": subnet["aliyun"]["ZoneId"],
                "CidrBlock": subnet["aliyun"]["CidrBlock"],
                "Description": subnet["aliyun"]["Description"],
            }
            code, aliyun_subnet = create_subnet(aliyun_access_key, "aliyun", aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # aliyun创建sg
            aliyun_params = {
                "VpcId": aliyun_vpc.get("VpcId"),
                "SecurityGroupName": "sg_" + vpc["name"]
            }
            code, aliyun_security_group = create_security_group(aliyun_access_key, "aliyun", aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            aliyun_params = {
                "Direction": "In",
                "IpProtocol": "icmp",
                "PortRange": "-1/-1",
                "SourceCidrIp": "0.0.0.0/0"
            }
            code = add_security_group_rule(aliyun_access_key, "aliyun",
                                           aliyun_security_group["SecurityGroupId"], aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            aliyun_params = {
                "Direction": "In",
                "IpProtocol": "tcp",
                "PortRange": "22/22",
                "SourceCidrIp": "0.0.0.0/0"
            }
            code = add_security_group_rule(aliyun_access_key, "aliyun",
                                           aliyun_security_group["SecurityGroupId"], aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            aliyun_params = {
                "Direction": "In",
                "IpProtocol": "udp",
                "PortRange": "9473/9473",
                "SourceCidrIp": "0.0.0.0/0"
            }
            code = add_security_group_rule(aliyun_access_key, "aliyun",
                                           aliyun_security_group["SecurityGroupId"], aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # openstack创建实例
            openstack_params = {
                "name": "vpn_openstack_" + vpc["name"],
                "availability_zone": openstack_vpn["availability_zone"],
                "imageRef": openstack_vpn["imageRef"],
                "flavorRef": openstack_vpn["flavorRef"],
                "networks": [{
                    "uuid": openstack_network.get("id"),
                    "fixed_ip": instance["openstack"]["networks"]["fixed_ip"]
                }]
            }
            code, openstack_instance = create_instance(token, "openstack", openstack_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # aliyun创建实例
            aliyun_params = instance["aliyun"]
            aliyun_params["ZoneId"] = subnet["aliyun"]["ZoneId"]
            aliyun_params["VSwitchId"] = aliyun_subnet.get("VSwitchId")
            aliyun_params["SecurityGroupId"] = aliyun_security_group.get("SecurityGroupId")
            aliyun_params["InstanceName"] = "vpn_aliyun_" + vpc["name"]
            aliyun_params["Password"] = aliyun_vpn["default_password"]
            aliyun_params["ImageId"] = aliyun_vpn["ImageId"]
            aliyun_params["InstanceType"] = aliyun_vpn["InstanceType"]
            aliyun_params["SystemDisk"] = aliyun_vpn["SystemDisk"]
            code, aliyun_instance = create_instance(aliyun_access_key, "aliyun", aliyun_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # openstack整理数据
            openstack_address_list = openstack_instance["addresses"][vpc["name"]]
            openstack_floating_ip = ""
            openstack_fixed_ip = instance["openstack"]["networks"]["fixed_ip"]
            for address in openstack_address_list:
                if address["OS-EXT-IPS:type"] == "floating":
                    openstack_floating_ip = address["addr"]
            # openstack设置可用地址对
            code, port_list = get_port_list(token, "openstack", openstack_instance["id"])
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            openstack_params = {
                "allowed_address_pairs": [{
                    "ip_address": "0.0.0.0/0"
                }]
            }
            code = update_port(token, "openstack", port_list[0]["id"], openstack_params)
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # openstack设置路由
            openstack_params = [{
                "destination": vpc["cidr"],
                "nexthop": openstack_fixed_ip
            }]
            code = operate_routes(token, "openstack", openstack_router["id"], openstack_params, "add")
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            # aliyun设置路由
            code, aliyun_subnet = get_subnet_details(aliyun_access_key, "aliyun", aliyun_subnet["VSwitchId"])
            aliyun_params = {
                "DestinationCidrBlock": vpc["cidr"],
                "NextHopId": aliyun_instance["InstanceId"]
            }
            code = operate_routes(aliyun_access_key, "aliyun", aliyun_subnet["RouteTable"]["RouteTableId"],
                                  aliyun_params, "add")
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())

            openstack_private_key = os.popen("wg genkey").read().rstrip("\n")
            openstack_public_key = os.popen("echo " + openstack_private_key + " | wg pubkey").read().rstrip("\n")
            aliyun_private_key = os.popen("wg genkey").read().rstrip("\n")
            aliyun_public_key = os.popen("echo " + aliyun_private_key + " | wg pubkey").read().rstrip("\n")
            openstack_ip_address = "10.1.0.1/24"
            aliyun_ip_address = "10.1.0.2/24"
            openstack_remote_ips = "10.1.0.2/32, " + vpc["sub_vpc"]["aliyun"]["cidr"]
            aliyun_remote_ips = "10.1.0.1/32, " + vpc["sub_vpc"]["openstack"]["cidr"]
            openstack_endpoint = aliyun_instance["PublicIpAddress"] + ":9473"

            # 等待1min OpenStack实例初始化，否则无法连接
            time.sleep(60)
            while True:
                code, instance = get_instance_details(token, "openstack", openstack_instance["id"])
                if instance["status"] == "running":
                    break
                time.sleep(5)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接openstack实例
            client.connect(hostname=openstack_floating_ip, port=22,
                           username="root", password=openstack_vpn["default_password"])
            command = 'echo "\nnet.ipv4.ip_forward=1" >> /etc/sysctl.conf' \
                      " && sysctl -p" \
                      " && apt update" \
                      " && apt -y install wireguard" \
                      " && cd /etc/wireguard" \
                      " && cat > wg0.conf<<EOF \n" \
                      "[Interface]\n" \
                      "PrivateKey = " + openstack_private_key + "\n" \
                      "Address = " + openstack_ip_address + "\n" \
                      "ListenPort = 9473\n" \
                      "MTU = 1420\n" \
                      "PostUp   = iptables -A FORWARD -i %i -j ACCEPT; " \
                      "iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat " \
                      "-A POSTROUTING -o eth0 -j MASQUERADE\n" \
                      "PostDown = iptables -D FORWARD -i %i -j ACCEPT; " \
                      "iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat " \
                      "-D POSTROUTING -o eth0 -j MASQUERADE\n\n" \
                      "[peer]\n" \
                      "PublicKey = " + aliyun_public_key + "\n" \
                      "AllowedIPs = " + openstack_remote_ips + "\n" \
                      "Endpoint = " + openstack_endpoint + "\n" \
                      "PersistentKeepalive = 25\n" \
                      "EOF\n" \
                      "systemctl enable wg-quick@wg0" \
                      " && systemctl start wg-quick@wg0"
            stdin, stdout, stderr = client.exec_command(command)
            print(stderr.read().decode("utf-8"))
            client.close()

            while True:
                code, instance = get_instance_details(aliyun_access_key, "aliyun", aliyun_instance["InstanceId"])
                if instance["Status"] == "Running":
                    break
                time.sleep(5)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接aliyun实例
            client.connect(hostname=aliyun_instance["PublicIpAddress"], port=22,
                           username="root", password=aliyun_vpn["default_password"])
            command = 'echo "\nnet.ipv4.ip_forward=1" >> /etc/sysctl.conf' \
                      " && sysctl -p" \
                      " && apt update" \
                      " && apt -y install wireguard" \
                      " && cd /etc/wireguard" \
                      " && cat > wg0.conf<<EOF \n" \
                      "[Interface]\n" \
                      "PrivateKey = " + aliyun_private_key + "\n" \
                      "Address = " + aliyun_ip_address + "\n" \
                      "ListenPort = 9473\n" \
                      "MTU = 1420\n" \
                      "PostUp   = iptables -A FORWARD -i %i -j ACCEPT; " \
                      "iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat " \
                      "-A POSTROUTING -o eth0 -j MASQUERADE\n" \
                      "PostDown = iptables -D FORWARD -i %i -j ACCEPT; " \
                      "iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat " \
                      "-D POSTROUTING -o eth0 -j MASQUERADE\n\n" \
                      "[peer]\n" \
                      "PublicKey = " + openstack_public_key + "\n" \
                      "AllowedIPs = " + aliyun_remote_ips + "\n" \
                      "PersistentKeepalive = 25\n" \
                      "EOF\n" \
                      "systemctl enable wg-quick@wg0" \
                      " && systemctl start wg-quick@wg0"
            stdin, stdout, stderr = client.exec_command(command)
            print(stderr.read().decode("utf-8"))
            client.close()

            # 保存vpc至数据库
            openstack_sub_vpc = vpc["sub_vpc"]["openstack"]
            openstack_sub_vpc["key_pair"] = {
                "private_key": openstack_private_key,
                "public_key": openstack_public_key
            }
            openstack_sub_vpc["vpc_id"] = openstack_network.get("id")
            aliyun_sub_vpc = vpc["sub_vpc"]["aliyun"]
            aliyun_sub_vpc["key_pair"] = {
                "private_key": aliyun_private_key,
                "public_key": aliyun_public_key
            }
            aliyun_sub_vpc["vpc_id"] = aliyun_vpc.get("VpcId")
            sub_vpc = {
                "openstack": openstack_sub_vpc,
                "aliyun": aliyun_sub_vpc
            }
            vpc_id = uuid.uuid4()
            Vpc.objects.create(userName=user_name, vpcName=vpc["name"], vpcId=vpc_id, cidr=vpc["cidr"],
                               subVpc=json.dumps(sub_vpc))
            # 保存vpn至数据库
            Vpn.objects.create(instanceId=openstack_instance["id"], vpcId=vpc_id, cloudId="openstack")
            Vpn.objects.create(instanceId=aliyun_instance["InstanceId"], vpcId=vpc_id, cloudId="aliyun")
            result.set_code(200)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def vpcs_create_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
        # 获取创建vpc参数
        if req.method == "GET":
            if access_keys.get("aliyun"):
                data = {
                    "zones": []
                }
                code, zone_list = get_zone_list(access_keys.get("aliyun"), "aliyun")
                for src_zone in zone_list:
                    if src_zone["Status"] == "Available":
                        zone = {
                            "id": src_zone.get("ZoneId"),
                        }
                        data["zones"].append(zone)
                result.set_result(code, data)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def vpcs_vpc_func(req, vpc_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        # 获取vpc列表
        if req.method == "GET":
            vpc = Vpc.objects.filter(userName=user_name, vpcId=vpc_id).values().first()
            vpn_list = list(Vpn.objects.filter(vpcId=vpc_id).values())
            if vpc:
                vpc["subVpc"] = json.loads(vpc["subVpc"])
                vpc["subVpc"]["openstack"]["key_pair"].pop("private_key")
                vpc["subVpc"]["aliyun"]["key_pair"].pop("private_key")
                vpc["vpn"] = vpn_list
                result.set_result(200, vpc)
            else:
                result.set_code(404)
        # 编辑vpc
        elif req.method == "PUT":
            vpc_name = json.loads(req.body.decode('utf-8'))["vpc"]["name"]
            if Vpc.objects.filter(userName=user_name, vpcId=vpc_id).values().first() and vpc_name:
                Vpc.objects.filter(userName=user_name, vpcId=vpc_id).update(vpcName=vpc_name)
                result.set_code(200)
            else:
                result.set_code(404)
        # 删除vpc
        elif req.method == "DELETE":
            if Vpc.objects.filter(userName=user_name, vpcId=vpc_id).values().first():
                Vpn.objects.filter(vpcId=vpc_id).delete()
                Vpc.objects.filter(userName=user_name, vpcId=vpc_id).delete()
                result.set_code(204)
            else:
                result.set_code(404)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def routers_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
        # 获取路由/路由表列表
        if req.method == "GET":
            router_list = []
            code, routers = get_router_list(token, "openstack")
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            router_list.extend(routers)
            if access_keys.get("aliyun"):
                code, routers = get_router_list(access_keys.get("aliyun"), "aliyun")
                if code != 200:
                    result.set_code(code)
                    return JsonResponse(result.get_dict())
                router_list.extend(routers)
            result.set_result(200, router_list)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def cloud_routers_router_func(req, cloud_id, router_id):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_key = get_access_key(token, user_name, cloud_id)
        # 删除路由
        if req.method == "DELETE":
            code = delete_router(access_key, cloud_id, router_id)
            result.set_code(code)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())


def security_groups_func(req):
    result = Result()
    token = req.headers.get("token")
    res = verify_token(token)
    payload = json.loads(res.text)
    if "token" in payload:
        user_name = payload["token"]["user"]["name"]
        access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
        # 获取安全组列表
        if req.method == "GET":
            security_group_list = []
            code, security_groups = get_security_group_list(token, "openstack")
            if code != 200:
                result.set_code(code)
                return JsonResponse(result.get_dict())
            security_group_list.extend(security_groups)
            if access_keys.get("aliyun"):
                code, security_groups = get_security_group_list(access_keys.get("aliyun"), "aliyun")
                if code != 200:
                    result.set_code(code)
                    return JsonResponse(result.get_dict())
                security_group_list.extend(security_groups)
            result.set_result(200, security_group_list)
        else:
            result.set_code(405)
    else:
        result.set_code(401)
    return JsonResponse(result.get_dict())
