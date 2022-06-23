from django.db import models


# Create your models here.
class User(models.Model):
    userName = models.CharField(max_length=16, verbose_name="用户名", db_column='user_name')
    accessKeys = models.CharField(max_length=1024, db_column='access_keys', default="{}")

    class Meta:
        db_table = 'tb_user'


class Vpn(models.Model):
    instanceId = models.CharField(max_length=36, db_column='instance_id')
    vpcId = models.CharField(max_length=36, db_column='vpc_id')
    cloudId = models.CharField(max_length=16, db_column='cloud_id')

    class Meta:
        db_table = 'tb_vpn'


class Vpc(models.Model):
    userName = models.CharField(max_length=16, db_column='user_name')
    vpcName = models.CharField(max_length=128, db_column='vpc_name')
    vpcId = models.CharField(max_length=36, db_column='vpc_id')
    cidr = models.CharField(max_length=18, db_column='cidr')
    subVpc = models.CharField(max_length=4096, db_column='sub_vpc')

    class Meta:
        db_table = 'tb_vpc'
