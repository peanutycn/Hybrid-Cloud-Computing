## 混合云计算平台

本系统为本人在本科期间的毕业设计《基于OpenStack和混合云框架的跨云虚拟网络协同设计与实现》中实现的混合云计算平台管理系统，为实现混合云的一种轻量级方案，功能尚未完全，仅为Demo。

## 前端

前端服务器采用Linux系统，示例中采用Ubuntu 20.04 LTS，并部署到阿里云服务器上。

前端项目源代码为`front_end`，项目打包文件为该目录下`/dist`。

示例中`index.html`置于`/opt/cloud/dist/`路径下。

前端需安装nginx和配置ssl证书，此处不再赘述。

如下配置nginx服务器配置文件`cloud.conf`：

```
server{

	server_name cloud.peanuty.cn;
	charset utf-8;

	listen 443 ssl;
	ssl_certificate   /usr/local/nginx/cert.d/peanuty.cn.pem;
    ssl_certificate_key  /usr/local/nginx/cert.d/peanuty.cn.key;
    ssl_dhparam /usr/local/nginx/cert.d/dhparam.pem;
    
	proxy_connect_timeout    300s;
    proxy_read_timeout       300s;
    proxy_send_timeout       300s;
	
	location /{
		alias /opt/cloud/dist/;
		index  index.html index.htm;
	}

    location /api/ {
        proxy_pass http://controller:8000/;
    }

    error_page  404  /index.html;
    location = /index.html{
        root /opt/cloud/dist;
    }

}

server{
    if ($host = cloud.peanuty.cn) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name cloud.peanuty.cn;
    return 404;
    
}
```

其中由于Vue项目History模式，且项目采用https，直接刷新会导致404，故将404页面指向`index.html`，这样直接刷新除了在浏览器F12控制台会显示404外无大影响。

`/api/`反向代理地址为实际后端地址，如果如图使用controller主机名需要在`/etc/hosts`添加一条host。

## 后端

后端服务器采用Linux系统，示例中采用Ubuntu 20.04 LTS，为本地云主机。

后端需额外配置OpenStack环境。

后端项目源代码为`back_end`，将源代码部署到后端服务器上。

**后文指令均切换到指定后端目录下**。

### Django

安装python3、Django及相应python包

```bash
sudo apt install python3-pip libmysqlclient-dev wireguard
pip3 install django -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install mysqlclient -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install aliyun-python-sdk-core -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install aliyun-python-sdk-ecs -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install aliyun-python-sdk-vpc -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install paramiko -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

配置项目`HCC/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'HCC',
        'USER': 'HCC',
        'PASSWORD': '$password$',
        'HOST': 'controller',
        'PORT': '3306',
    }
}

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://cloud.peanuty.cn"]
keystoneUrl = "http://controller:5000/v3/"
novaUrl = "http://controller:8774/v2.1/"
neutronUrl = "http://controller:9696/v2.0/"
glanceUrl = "http://controller:9292/v2/"
openstack_vpn = {
    "default_password": "ubuntu",
    "availability_zone": "high-performance",
    "imageRef": "137100c7-f701-4624-9b2c-a975b78c4ead",
    "flavorRef": "c469cda0-f613-4c82-9079-b6b70e0fb9c8",
}
aliyun_vpn = {
    "default_password": "Default0",
    "ImageId": "ubuntu_20_04_x64_20G_alibase_20220428.vhd",
    "InstanceType": "ecs.s6-c1m1.small",
    "SystemDisk": {
        "Size": "20",
        "Category": "cloud_efficiency"
    },
}
aliyun_instance_parameters = {
    "InstanceTypeFamily": "ecs.s6"
}

```

修改`DATABASES`信息，修改`CSRF_TRUSTED_ORIGINS`为前端项目地址；

`keystoneUrl`等为OpenStack各API地址；

`openstack_vpn`为系统设置的作为OpenStack网络VPN的实例默认设置，`aliyun_vpn`亦同，根据实际情况进行修改；

其中OpenStack的镜像需要管理员手动使用`guestfish`进行修改，修改`/etc/cloud/cloud.conf`和`/etc/ssh/sshd_config`以及`/etc/shadow`文件，设置ssh密钥登陆，并设置root登录和默认密码，或者采用启动虚拟机时添加脚本的方式。

`aliyun_instance_parameters`中`InstanceTypeFamily`为返回给前端创建实例的实例规格族参数，详情可查看[阿里云相关页面](https://help.aliyun.com/document_detail/25378.htm)。

### 数据库

后端需安装mariaDB。

```bash
sudo apt install mariadb-server python3-pymysql
```

根据提示设置mariaDB的root密码。

```
mysql_secure_installation
```

登录mariaDB并创建HCC数据库（数据库名称可自定义，需与前文对应），创建HCC用户并授权访问HCC数据库，其中$password$更改为自设定的密码。

```bash
sudo mysql
MariaDB [(none)]> CREATE DATABASE HCC;
GRANT ALL PRIVILEGES ON HCC.* TO 'HCC'@'localhost' IDENTIFIED BY '$password$';
GRANT ALL PRIVILEGES ON HCC.* TO 'HCC'@'%' IDENTIFIED BY '$password$';
```

<kbd>ctrl</kbd>+<kbd>d</kbd>或输入`exit;`退出。

使用`manage.py`自动生成数据库表：

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 运行

采用`manage.py runserver`运行，可使用screen后台运行。

```bash
python3 manage.py runserver controller:8000
```

## 需改进和完善功能

### 实例

实例的更多操作如元数据定义、与安全组交互、接口管理等。

作为VPN的实例应该锁定等。

### VPC

创建VPC时前后端对参数需要进行验证、子VPC详细信息页面、子VPC的子网管理操作等。

VPC删除时嵌套删除子VPC及其一系列涉及的资源。

### 路由

创建路由、各云路由详细界面、路由表。

### 安全组

创建安全组、安全组详细界面、管理安全组规则。
