import time
from v1.models import User, Vpn, Vpc
from HCC.settings import keystoneUrl, novaUrl, neutronUrl, glanceUrl, aliyun_instance_parameters
import requests
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest, StartInstanceRequest, StopInstanceRequest, \
    RebootInstanceRequest, ModifyInstanceAttributeRequest, DeleteInstanceRequest, CreateInstanceRequest, \
    AllocatePublicIpAddressRequest, DescribeAvailableResourceRequest, DescribeInstanceTypesRequest, \
    DescribeImagesRequest
from aliyunsdkecs.request.v20140526 import DescribeKeyPairsRequest, ImportKeyPairRequest, DeleteKeyPairsRequest
from aliyunsdkecs.request.v20140526 import DescribeSecurityGroupsRequest, CreateSecurityGroupRequest, \
    AuthorizeSecurityGroupRequest
from aliyunsdkvpc.request.v20160428 import CreateVpcRequest, DeleteVpcRequest, CreateVSwitchRequest, \
    DeleteVSwitchRequest, DescribeVSwitchAttributesRequest, DescribeVSwitchesRequest, \
    CreateRouteEntryRequest, DescribeRouteTableListRequest


class Result:
    def __init__(self):
        self.code = None
        self.data = None
        self.msg = None

    def set_code(self, code):
        self.code = code
        if code == 200:
            self.msg = "OK"
        elif code == 201:
            self.msg = "Created"
        elif code == 202:
            self.msg = "Accepted"
        elif code == 204:
            self.msg = "No Content"
        elif code == 400:
            self.msg = "Bad Request"
        elif code == 401:
            self.msg = "Unauthorized"
        elif code == 403:
            self.msg = "Forbidden"
        elif code == 404:
            self.msg = "Not Found"
        elif code == 405:
            self.msg = "Method Not Allowed"
        elif code == 409:
            self.msg = "Conflict"
        elif code == 500:
            self.msg = "Internal Server Error"
        else:
            self.code = 403
            self.msg = "Forbidden"

    def set_result(self, code, data):
        self.code = code
        self.data = data
        self.set_code(code)

    def get_dict(self):
        return remove_null_value(self.__dict__)


class Identity:
    def __init__(self):
        self.methods = None
        self.token = None
        self.password = None

    def set_token_id(self, token_id):
        self.methods = ["token"]
        self.token = {
            "id": token_id
        }

    def set_identity(self, identity):
        if identity['methods'] == ['password']:
            self.methods = ["password"]
            self.password = identity['password']
        elif identity['methods'] == ['token']:
            self.methods = ["token"]
            self.token = identity['token']

    def get_dict(self):
        return remove_null_value(self.__dict__)


class Auth:
    def __init__(self):
        self.identity = None
        self.scope = None

    def set_unscoped(self, identity):
        self.identity = identity.get_dict()

    def set_scoped(self, identity, scope):
        self.identity = identity.get_dict()
        self.scope = scope

    def get_dict(self):
        return remove_null_value(self.__dict__)


def remove_null_value(src):
    for key in list(src.keys()):
        if not src.get(key):
            del src[key]
    return src


def get_openstack_token(auth):
    url = keystoneUrl + "auth/tokens"
    body = {
        "auth": auth.get_dict()
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/101.0.4951.54 Safari/537.36 ",
    }
    res = requests.post(url, data=json.dumps(body), headers=headers)
    return res


def verify_token(token):
    identity = Identity()
    identity.set_token_id(token)
    auth = Auth()
    auth.set_unscoped(identity)
    res = get_openstack_token(auth)
    return res


def verify_access_key(access_key, cloud_id):
    if cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeInstancesRequest.DescribeInstancesRequest()
            client.do_action_with_exception(req)
            return True
        except (KeyError, ClientException, ServerException):
            return False
    else:
        return False


def get_project_id(token):
    code = 200
    project_id = ""
    url = keystoneUrl + "auth/projects"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/101.0.4951.54 Safari/537.36 ",
        "X-Auth-Token": token
    }
    res = requests.get(url, headers=headers)
    payload = json.loads(res.text)
    if "projects" in payload:
        project_id = payload["projects"][0]["id"]
    else:
        code = res.status_code
    return code, project_id


def update_password(user_id, user):
    url = keystoneUrl + "users/" + user_id + "/password"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/101.0.4951.54 Safari/537.36 ",
    }
    res = requests.post(url, data=json.dumps(user), headers=headers)
    if res.status_code == 204:
        return 200
    elif res.status_code == 401:
        return 400
    else:
        return res.status_code


def get_access_key(token, user_name, cloud_id):
    access_keys = json.loads(User.objects.filter(userName=user_name).first().accessKeys)
    if cloud_id == "openstack":
        access_key = token
    else:
        access_key = access_keys.get(cloud_id)
    return access_key


def get_instance_list(access_key, cloud_id):
    code = 200
    instances = []
    if cloud_id == "openstack":
        url = novaUrl + "servers/detail"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "servers" in payload:
            src_instances = json.loads(res.text)["servers"]
            for src_instance in src_instances:
                addresses = []
                if "addresses" in src_instance:
                    addresses = list(src_instance["addresses"].values())[0]
                ip_addresses = {
                    "private": [],
                    "public": []
                }
                for address in addresses:
                    if address["OS-EXT-IPS:type"] == "fixed":
                        ip_addresses["private"].append(address["addr"])
                    elif address["OS-EXT-IPS:type"] == "floating":
                        ip_addresses["public"].append(address["addr"])
                if src_instance["OS-EXT-STS:vm_state"] == "building":
                    status = "building"
                elif src_instance["OS-EXT-STS:task_state"] == "powering-on":
                    status = "starting"
                elif src_instance["OS-EXT-STS:task_state"] == "powering-off":
                    status = "stopping"
                elif src_instance["OS-EXT-STS:vm_state"] == "active":
                    status = "running"
                elif src_instance["OS-EXT-STS:vm_state"] == "stopped":
                    status = "stopped"
                else:
                    status = "error"
                instance = {
                    "cloud_id": "openstack",
                    "instance_name": src_instance["name"],
                    "instance_id": src_instance["id"],
                    "addresses": ip_addresses,
                    "status": status,
                    "availability_zone": src_instance["OS-EXT-AZ:availability_zone"]
                }
                instances.append(instance)
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeInstancesRequest.DescribeInstancesRequest()
            res = client.do_action_with_exception(req)
            src_instances = json.loads(res)["Instances"]["Instance"]
            for src_instance in src_instances:
                ip_addresses = {
                    "private": src_instance["VpcAttributes"]["PrivateIpAddress"]["IpAddress"],
                    "public": src_instance["PublicIpAddress"]["IpAddress"]
                }
                if src_instance["Status"] == "Pending":
                    status = "building"
                elif src_instance["Status"] == "Starting":
                    status = "starting"
                elif src_instance["Status"] == "Stopping":
                    status = "stopping"
                elif src_instance["Status"] == "Running":
                    status = "running"
                elif src_instance["Status"] == "Stopped":
                    status = "stopped"
                else:
                    status = "error"
                instance = {
                    "cloud_id": "aliyun",
                    "instance_name": src_instance["InstanceName"],
                    "instance_id": src_instance["InstanceId"],
                    "addresses": ip_addresses,
                    "status": status,
                    "availability_zone": src_instance["ZoneId"]
                }
                instances.append(instance)
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, instances


def create_instance(access_key, cloud_id, src_instance):
    code = 200
    instance = {}
    if cloud_id == "openstack":
        url = novaUrl + "servers"
        data = {
            "server": src_instance
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if "server" in payload:
            instance_id = payload["server"]["id"]
            code, external_network_list = get_external_network_list(access_key)
            external_network_id = external_network_list[0]["id"]
            port_list = []
            while not port_list:
                code, port_list = get_port_list(access_key, cloud_id, instance_id)
            port_id = port_list[0]["id"]
            url = neutronUrl + "floatingips"
            data = {
                "floatingip": {
                    "floating_network_id": external_network_id,
                    "port_id": port_id
                }
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/101.0.4951.54 Safari/537.36 ",
                "X-Auth-Token": access_key
            }
            requests.post(url, data=json.dumps(data), headers=headers)
            time.sleep(5)
            code, instance = get_instance_details(access_key, cloud_id, instance_id)
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = CreateInstanceRequest.CreateInstanceRequest()
            req.set_InstanceChargeType(src_instance.get("InstanceChargeType"))
            req.set_ZoneId(src_instance.get("ZoneId"))
            req.set_InstanceType(src_instance.get("InstanceType"))
            req.set_ImageId(src_instance.get("ImageId"))
            req.set_SystemDiskSize(src_instance["SystemDisk"].get("Size"))
            req.set_SystemDiskCategory(src_instance["SystemDisk"].get("Category"))
            req.set_VSwitchId(src_instance.get("VSwitchId"))
            req.set_SecurityGroupId(src_instance.get("SecurityGroupId"))
            req.set_InternetMaxBandwidthOut(src_instance.get("InternetMaxBandwidthOut"))
            req.set_InstanceName(src_instance.get("InstanceName"))
            if src_instance.get("PrivateIpAddress"):
                req.set_Password(src_instance.get("PrivateIpAddress"))
            if src_instance.get("InstanceChargeType") == "PrePaid":
                req.set_Period(src_instance.get("Period"))
            if src_instance.get("Password"):
                req.set_Password(src_instance.get("Password"))
            elif src_instance.get("KeyPairName"):
                req.set_KeyPairName(src_instance.get("KeyPairName"))
            if src_instance.get("Description"):
                req.set_Description(src_instance.get("Description"))
            res = client.do_action_with_exception(req)
            instance_id = json.loads(res).get("InstanceId")
            #
            new_req = AllocatePublicIpAddressRequest.AllocatePublicIpAddressRequest()
            new_req.set_InstanceId(instance_id)
            new_res = client.do_action_with_exception(new_req)
            #
            time.sleep(3)
            start_instance(access_key, cloud_id, instance_id)
            instance = {
                "InstanceId": instance_id,
                "PublicIpAddress": json.loads(new_res).get("IpAddress")
            }
        except (KeyError, ClientException):
            code = 400
        except ServerException as result:
            code = result.get_http_status()
    return code, instance


def create_instance_parameters(access_key, cloud_id):
    params = {}
    if cloud_id == "openstack":
        params = {
            "availability_zones": [],
            "images": [],
            "flavors": [],
            "networks": [],
            "security_groups": [],
            "key_pairs": [],
        }
        code, availability_zone_list = get_zone_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_zone in availability_zone_list:
            if src_zone["zoneState"]["available"]:
                zone = {
                    "name": src_zone.get("zoneName"),
                }
                params["availability_zones"].append(zone)
        code, image_list = get_image_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_image in image_list:
            image = {
                "name": src_image.get("name"),
                "id": src_image.get("id")
            }
            params["images"].append(image)
        code, flavor_list = get_flavor_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_flavor in flavor_list:
            flavor = {
                "name": src_flavor.get("name"),
                "id": src_flavor.get("id"),
                "vcpus": src_flavor.get("vcpus"),
                "ram": src_flavor.get("ram"),
                "disk": src_flavor.get("disk"),
            }
            params["flavors"].append(flavor)
        code, vpc_list = get_vpc_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_vpc in vpc_list:
            if not src_vpc.get("router:external"):
                vpc = {
                    "name": src_vpc.get("name"),
                    "id": src_vpc.get("id")
                }
                params["networks"].append(vpc)
        code, security_group_list = get_security_group_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_security_group in security_group_list:
            security_group = {
                "name": src_security_group.get("security_group_name"),
                "id": src_security_group.get("security_group_id")
            }
            params["security_groups"].append(security_group)
        code, key_pair_list = get_key_pair_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_key_pair in key_pair_list:
            key_pair = {
                "name": src_key_pair.get("key_pair_name")
            }
            params["key_pairs"].append(key_pair)
    elif cloud_id == "aliyun":
        params = {
            "images": [],
            "instanceTypes": [],
            "vSwitchs": [],
            "securityGroups": [],
            "keyPairs": [],
        }
        code, image_list = get_image_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_image in image_list:
            image = {
                "name": src_image.get("OSName"),
                "id": src_image.get("ImageId")
            }
            params["images"].append(image)
        code, flavor_list = get_flavor_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_flavor in flavor_list:
            flavor = {
                "id": src_flavor.get("InstanceTypeId"),
                "vcpus": src_flavor.get("CpuCoreCount"),
                "ram": src_flavor.get("MemorySize"),
            }
            params["instanceTypes"].append(flavor)
        code, subnet_list = get_subnet_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_subnet in subnet_list:
            if src_subnet.get("Status") == "Available":
                subnet = {
                    "vpcId": src_subnet.get("VpcId"),
                    "vSwitchName": src_subnet.get("VSwitchName"),
                    "vSwitchId": src_subnet.get("VSwitchId"),
                    "zoneId": src_subnet.get("ZoneId"),
                    "cidrBlock": src_subnet.get("CidrBlock"),
                }
                params["vSwitchs"].append(subnet)
        code, security_group_list = get_security_group_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_security_group in security_group_list:
            security_group = {
                "vpcId": src_security_group.get("vpc_id"),
                "name": src_security_group.get("security_group_name"),
                "id": src_security_group.get("security_group_id")
            }
            params["securityGroups"].append(security_group)
        code, key_pair_list = get_key_pair_list(access_key, cloud_id)
        if code != 200:
            return code, {}
        for src_key_pair in key_pair_list:
            key_pair = {
                "name": src_key_pair.get("key_pair_name")
            }
            params["keyPairs"].append(key_pair)
    return 200, params


def get_image_list(access_key, cloud_id):
    code = 200
    images = []
    if cloud_id == "openstack":
        url = glanceUrl + "images"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "images" in payload:
            images = payload["images"]
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeImagesRequest.DescribeImagesRequest()
            req.set_ImageOwnerAlias("system")
            res = client.do_action_with_exception(req)
            images = json.loads(res)["Images"]["Image"]
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, images


def get_flavor_list(access_key, cloud_id):
    code = 200
    flavors = []
    if cloud_id == "openstack":
        url = novaUrl + "flavors/detail"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "flavors" in payload:
            flavors = payload["flavors"]
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeInstanceTypesRequest.DescribeInstanceTypesRequest()
            req.set_InstanceTypeFamily(aliyun_instance_parameters.get("InstanceTypeFamily"))
            res = client.do_action_with_exception(req)
            flavors = json.loads(res)["InstanceTypes"]["InstanceType"]
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, flavors


def get_zone_list(access_key, cloud_id):
    code = 200
    zones = []
    if cloud_id == "openstack":
        url = novaUrl + "os-availability-zone"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "availabilityZoneInfo" in payload:
            zones = payload["availabilityZoneInfo"]
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeAvailableResourceRequest.DescribeAvailableResourceRequest()
            req.set_DestinationResource("Zone")
            res = client.do_action_with_exception(req)
            zones = json.loads(res)["AvailableZones"]["AvailableZone"]
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, zones


def get_instance_details(access_key, cloud_id, instance_id):
    code = 200
    instance = {}
    if cloud_id == "openstack":
        url = novaUrl + "servers/" + instance_id
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        instance = json.loads(res.text).get("server")
        if instance:
            if instance["OS-EXT-STS:vm_state"] == "building":
                instance["status"] = "building"
            elif instance["OS-EXT-STS:task_state"] == "powering-on":
                instance["status"] = "starting"
            elif instance["OS-EXT-STS:task_state"] == "powering-off":
                instance["status"] = "stopping"
            elif instance["OS-EXT-STS:vm_state"] == "active":
                instance["status"] = "running"
            elif instance["OS-EXT-STS:vm_state"] == "stopped":
                instance["status"] = "stopped"
            else:
                instance["status"] = "error"
            url = novaUrl + "flavors/" + instance["flavor"]["id"]
            res = requests.get(url, headers=headers)
            instance["flavor"] = json.loads(res.text).get("flavor")
            url = novaUrl + "images/" + instance["image"]["id"]
            res = requests.get(url, headers=headers)
            instance["image"] = json.loads(res.text).get("image")
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeInstancesRequest.DescribeInstancesRequest()
            req.set_InstanceIds([instance_id])
            res = client.do_action_with_exception(req)
            instance = json.loads(res)["Instances"]["Instance"][0]
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, instance


def update_instance(access_key, cloud_id, instance_id, instance):
    if cloud_id == "openstack":
        url = novaUrl + "servers/" + instance_id
        data = {
            "server": instance
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.put(url, data=json.dumps(data), headers=headers)
        return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = ModifyInstanceAttributeRequest.ModifyInstanceAttributeRequest()
            req.set_InstanceId(instance_id)
            req.set_InstanceName(instance.get("name"))
            client.do_action_with_exception(req)
            return 200
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def delete_instance(access_key, cloud_id, instance_id):
    if cloud_id == "openstack":
        url = novaUrl + "servers/" + instance_id
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.delete(url, headers=headers)
        return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DeleteInstanceRequest.DeleteInstanceRequest()
            req.set_InstanceId(instance_id)
            req.set_Force(True)
            client.do_action_with_exception(req)
            return 204
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def start_instance(access_key, cloud_id, instance_id):
    if cloud_id == "openstack":
        url = novaUrl + "servers/" + instance_id + "/action"
        data = {
            "os-start": None
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = StartInstanceRequest.StartInstanceRequest()
            req.set_InstanceId(instance_id)
            client.do_action_with_exception(req)
            return 202
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def stop_instance(access_key, cloud_id, instance_id, stop):
    if cloud_id == "openstack":
        url = novaUrl + "servers/" + instance_id + "/action"
        data = {
            "os-stop": None
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = StopInstanceRequest.StopInstanceRequest()
            req.set_InstanceId(instance_id)
            req.set_ForceStop(stop.get("force"))
            req.set_StoppedMode(stop.get("mode"))
            client.do_action_with_exception(req)
            return 202
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def reboot_instance(access_key, cloud_id, instance_id, reboot):
    if cloud_id == "openstack":
        url = novaUrl + "servers/" + instance_id + "/action"
        data = {
            "reboot": {
                "type": "HARD" if reboot.get("force") else "SOFT"
            }
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = RebootInstanceRequest.RebootInstanceRequest()
            req.set_InstanceId(instance_id)
            req.set_ForceStop(reboot.get("force"))
            client.do_action_with_exception(req)
            return 202
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def get_key_pair_list(access_key, cloud_id):
    code = 200
    key_pairs = []
    if cloud_id == "openstack":
        url = novaUrl + "os-keypairs"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "keypairs" in payload:
            src_key_pairs = payload["keypairs"]
            for src_key_pair in src_key_pairs:
                url = novaUrl + "os-keypairs/" + src_key_pair["keypair"]["name"]
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/101.0.4951.54 Safari/537.36 ",
                    "X-Auth-Token": access_key
                }
                res = requests.get(url, headers=headers)
                key_pair_detailed = json.loads(res.text)["keypair"]
                key_pair = {
                    "cloud_id": "openstack",
                    "key_pair_name": key_pair_detailed["name"],
                    "key_pair_fingerprint": key_pair_detailed["fingerprint"],
                    "created_time": key_pair_detailed["created_at"]
                }
                key_pairs.append(key_pair)
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeKeyPairsRequest.DescribeKeyPairsRequest()
            res = client.do_action_with_exception(req)
            src_key_pairs = json.loads(res)["KeyPairs"]["KeyPair"]
            for src_key_pair in src_key_pairs:
                key_pair = {
                    "cloud_id": "aliyun",
                    "key_pair_name": src_key_pair["KeyPairName"],
                    "key_pair_fingerprint": ":".join(src_key_pair["KeyPairFingerPrint"][i:i + 2]
                                                     for i in range(0, len(src_key_pair["KeyPairFingerPrint"]), 2)),
                    "created_time": src_key_pair["CreationTime"]
                }
                key_pairs.append(key_pair)
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, key_pairs


def import_key_pair(access_key, cloud_id, src_key_pair):
    code = 200
    key_pair = {}
    if cloud_id == "openstack":
        url = novaUrl + "os-keypairs"
        data = {
            "keypair": {
                "name": src_key_pair.get("name"),
                "public_key": src_key_pair.get("publicKey")
            }
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if payload.get("keypair"):
            key_pair = payload["keypair"]
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = ImportKeyPairRequest.ImportKeyPairRequest()
            req.set_PublicKeyBody(src_key_pair.get("publicKey"))
            req.set_KeyPairName(src_key_pair.get("name"))
            res = client.do_action_with_exception(req)
            key_pair = json.loads(res)
            if key_pair.get("RequestId"):
                key_pair.pop("RequestId")
        except (KeyError, ClientException):
            code = 400
        except ServerException as result:
            code = result.get_http_status()
    return code, key_pair


def remove_key_pair(access_key, cloud_id, key_pair_name):
    if cloud_id == "openstack":
        url = novaUrl + "os-keypairs/" + key_pair_name
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.delete(url, headers=headers)
        if res.status_code == 202:
            return 204
        else:
            return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DeleteKeyPairsRequest.DeleteKeyPairsRequest()
            req.set_KeyPairNames([key_pair_name])
            client.do_action_with_exception(req)
            return 204
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def get_vpc_list(access_key, cloud_id):
    code = 200
    vpcs = []
    if cloud_id == "openstack":
        url = neutronUrl + "networks"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "networks" in payload:
            vpcs = payload["networks"]
        else:
            code = res.status_code
    return code, vpcs


def create_vpc(access_key, cloud_id, src_vpc):
    code = 200
    vpc = {}
    if cloud_id == "openstack":
        url = neutronUrl + "networks"
        data = {
            "network": src_vpc
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if "network" in payload:
            vpc = payload["network"]
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = CreateVpcRequest.CreateVpcRequest()
            req.set_VpcName(src_vpc.get("name"))
            req.set_CidrBlock(src_vpc.get("cidr"))
            res = client.do_action_with_exception(req)
            vpc = json.loads(res)
        except (KeyError, ClientException):
            code = 400
        except ServerException as result:
            code = result.get_http_status()
    return code, vpc


def delete_vpc(access_key, cloud_id, vpc_id):
    if cloud_id == "openstack":
        url = neutronUrl + "networks/" + vpc_id
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.delete(url, headers=headers)
        return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DeleteVpcRequest.DeleteVpcRequest()
            req.set_VpcId(vpc_id)
            client.do_action_with_exception(req)
            return 204
        except (KeyError, ClientException):
            return 403
        except ServerException as result:
            return result.get_http_status()


def get_port_list(access_key, cloud_id, device_id):
    code = 200
    ports = []
    if cloud_id == "openstack":
        url = neutronUrl + "ports"
        params = {
            "device_id": device_id
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, params=params, headers=headers)
        payload = json.loads(res.text)
        if "ports" in payload:
            ports = payload["ports"]
        else:
            code = res.status_code
    return code, ports


def get_subnet_list(access_key, cloud_id):
    code = 200
    subnets = []
    if cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeVSwitchesRequest.DescribeVSwitchesRequest()
            res = client.do_action_with_exception(req)
            subnets = json.loads(res)["VSwitches"]["VSwitch"]
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, subnets


def create_subnet(access_key, cloud_id, src_subnet):
    code = 200
    subnet = {}
    if cloud_id == "openstack":
        url = neutronUrl + "subnets"
        data = {
            "subnet": src_subnet
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if payload.get("subnet"):
            subnet = payload["subnet"]
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = CreateVSwitchRequest.CreateVSwitchRequest()
            req.set_VpcId(src_subnet.get("VpcId"))
            req.set_VSwitchName(src_subnet.get("VSwitchName"))
            req.set_ZoneId(src_subnet.get("ZoneId"))
            req.set_CidrBlock(src_subnet.get("CidrBlock"))
            req.set_Description(src_subnet.get("Description"))
            res = client.do_action_with_exception(req)
            subnet = json.loads(res)
            if subnet.get("RequestId"):
                subnet.pop("RequestId")
        except (KeyError, ClientException):
            code = 400
        except ServerException as result:
            code = result.get_http_status()
    return code, subnet


def get_subnet_details(access_key, cloud_id, subnet_id):
    code = 200
    subnet = {}
    if cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeVSwitchAttributesRequest.DescribeVSwitchAttributesRequest()
            req.set_VSwitchId(subnet_id)
            res = client.do_action_with_exception(req)
            subnet = json.loads(res)
            if subnet.get("RequestId"):
                subnet.pop("RequestId")
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, subnet


def update_subnet(access_key, cloud_id, subnet_id, subnet):
    if cloud_id == "openstack":
        url = neutronUrl + "subnets/" + subnet_id
        data = {
            "subnet": subnet
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.put(url, data=json.dumps(data), headers=headers)
        return res.status_code


def get_external_network_list(token):
    code = 200
    networks = []
    url = neutronUrl + "networks"
    params = {
        "router:external": True
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/101.0.4951.54 Safari/537.36 ",
        "X-Auth-Token": token
    }
    res = requests.get(url, params=params, headers=headers)
    payload = json.loads(res.text)
    if payload.get("networks"):
        networks = payload["networks"]
    else:
        code = res.status_code
    return code, networks


def operate_router_interface(token, router_id, device, device_id, action):
    url = neutronUrl + "routers/" + router_id + "/" + action + "_router_interface"
    data = {
        device + "_id": device_id
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/101.0.4951.54 Safari/537.36 ",
        "X-Auth-Token": token
    }
    res = requests.put(url, data=json.dumps(data), headers=headers)
    return res.status_code


def get_router_list(access_key, cloud_id):
    code = 200
    routers = []
    if cloud_id == "openstack":
        url = neutronUrl + "routers"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "routers" in payload:
            router_list = payload.get("routers")
            for src_router in router_list:
                router = {
                    "id": src_router.get("id"),
                    "cloud_id": "openstack"
                }
                routers.append(router)
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeRouteTableListRequest.DescribeRouteTableListRequest()
            res = client.do_action_with_exception(req)
            router_list = json.loads(res)["RouterTableList"]["RouterTableListType"]
            for src_router in router_list:
                router = {
                    "id": src_router.get("RouteTableId"),
                    "cloud_id": "aliyun"
                }
                routers.append(router)
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, routers


def create_router(access_key, cloud_id, src_router):
    code = 200
    router = {}
    if cloud_id == "openstack":
        url = neutronUrl + "routers"
        code, external_network_list = get_external_network_list(access_key)
        if code != 200:
            return code, {}
        external_network_id = external_network_list[0]["id"]
        data = {
            "router": {
                "name": src_router.get("name"),
                "external_gateway_info": {
                    "network_id": external_network_id
                }
            }
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if payload.get("router"):
            router_id = payload["router"]["id"]
            code = operate_router_interface(access_key, router_id, "subnet", src_router.get("subnet_id"), "add")
            router = payload["router"]
        else:
            code = res.status_code
    return code, router


def get_router_details(access_key, cloud_id, router_id):
    code = 200
    router = {}
    if cloud_id == "openstack":
        url = neutronUrl + "routers/" + router_id
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "router" in payload:
            router = payload["router"]
        else:
            code = res.status_code
    return code, router


def delete_router(access_key, cloud_id, router_id):
    if cloud_id == "openstack":
        code, port_list = get_port_list(access_key, cloud_id, router_id)
        for port in port_list:
            operate_router_interface(access_key, router_id, "port", port.get("id"), "remove")
        code, router = get_router_details(access_key, cloud_id, router_id)
        operate_routes(access_key, cloud_id, router_id, router.get("routes"), "remove")
        url = neutronUrl + "routers/" + router_id
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.delete(url, headers=headers)
        return res.status_code


def operate_routes(access_key, cloud_id, router_id, routes, action):
    if cloud_id == "openstack":
        url = neutronUrl + "routers/" + router_id + "/" + action + "_extraroutes"
        data = {
            "router": {
                "routes": routes
            }
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.put(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if "router" in payload:
            return 200
        else:
            return res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            if action == "add":
                req = CreateRouteEntryRequest.CreateRouteEntryRequest()
                req.set_DestinationCidrBlock(routes.get("DestinationCidrBlock"))
                req.set_RouteTableId(router_id)
                req.set_NextHopId(routes.get("NextHopId"))
                client.do_action_with_exception(req)
                return 200
            elif action == "remove":
                return 400
            else:
                return 400
        except (KeyError, ClientException):
            return 400
        except ServerException as result:
            return result.get_http_status()


def update_port(access_key, cloud_id, port_id, port):
    if cloud_id == "openstack":
        url = neutronUrl + "ports/" + port_id
        data = {
            "port": port
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.put(url, data=json.dumps(data), headers=headers)
        payload = json.loads(res.text)
        if "port" in payload:
            return 200
        else:
            return res.status_code


def get_security_group_list(access_key, cloud_id):
    code = 200
    security_groups = []
    if cloud_id == "openstack":
        url = neutronUrl + "security-groups"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/101.0.4951.54 Safari/537.36 ",
            "X-Auth-Token": access_key
        }
        res = requests.get(url, headers=headers)
        payload = json.loads(res.text)
        if "security_groups" in payload:
            src_security_groups = payload["security_groups"]
            for src_security_group in src_security_groups:
                security_group = {
                    "cloud_id": "openstack",
                    "security_group_id": src_security_group["id"],
                    "security_group_name": src_security_group["name"],
                }
                security_groups.append(security_group)
        else:
            code = res.status_code
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = DescribeSecurityGroupsRequest.DescribeSecurityGroupsRequest()
            res = client.do_action_with_exception(req)
            src_security_groups = json.loads(res)["SecurityGroups"]["SecurityGroup"]
            for src_security_group in src_security_groups:
                security_group = {
                    "cloud_id": "aliyun",
                    "security_group_id": src_security_group["SecurityGroupId"],
                    "security_group_name": src_security_group["SecurityGroupName"],
                    "vpc_id": src_security_group["VpcId"],
                }
                security_groups.append(security_group)
        except (KeyError, ClientException):
            code = 403
        except ServerException as result:
            code = result.get_http_status()
    return code, security_groups


def create_security_group(access_key, cloud_id, src_security_group):
    code = 200
    security_group = {}
    if cloud_id == "openstack":
        code = 403
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            req = CreateSecurityGroupRequest.CreateSecurityGroupRequest()
            req.set_VpcId(src_security_group["VpcId"])
            req.set_SecurityGroupName(src_security_group["SecurityGroupName"])
            res = client.do_action_with_exception(req)
            security_group = json.loads(res)
            if security_group.get("RequestId"):
                security_group.pop("RequestId")
        except (KeyError, ClientException):
            code = 400
        except ServerException as result:
            code = result.get_http_status()
    return code, security_group


def add_security_group_rule(access_key, cloud_id, security_group_id, rule):
    if cloud_id == "openstack":
        return 403
    elif cloud_id == "aliyun":
        try:
            client = AcsClient(
                access_key["access_key"]["id"],
                access_key["access_key"]["secret"],
                access_key["region_id"]
            )
            if rule.get("Direction") == "In":
                req = AuthorizeSecurityGroupRequest.AuthorizeSecurityGroupRequest()
                req.set_SecurityGroupId(security_group_id)
                req.set_IpProtocol(rule.get("IpProtocol"))
                req.set_PortRange(rule.get("PortRange"))
                req.set_SourceCidrIp(rule.get("SourceCidrIp"))
                if "Description" in rule:
                    req.set_Description(rule.get("Description"))
                client.do_action_with_exception(req)
            return 200
        except (KeyError, ClientException):
            return 400
        except ServerException as result:
            return result.get_http_status()
