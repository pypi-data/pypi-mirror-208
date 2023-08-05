import json

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


# 腾讯云的cos操作工具类

class Cos(object):
    def __init__(self, cos_secret_id, cos_secret_key, region, bucket, domain):
        # 1. 设置用户属性, 包括 secret_id, secret_key, region 等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
        secret_id = cos_secret_id  # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
        secret_key = cos_secret_key  # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
        region = region  # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
        # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
        token = None  # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
        scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        self.client = CosS3Client(config)
        self.bucket = bucket
        self.domain = domain

    # 图片高级压缩
    def save_with_imageMogr2format(self, imge_file_key, imge_data, process_rules,
                                   mid_bucket, mid_region,
                                   to_overwrite=True):
        """
        图片高级压缩
        1.将图片存入到临时的bucket中，这个bucket有图片处理的功能
        2.使用临时bucket的图片处理功能，将图片转换成指定的格式
        3.将转换后的图片存入到正式的bucket中
        :param imge_file_key: 图片文件key
        :param imge_data: 图片文件流
        :param process_rules: 图片处理规则  [{"fileid": "test.avif", "rule": "imageMogr2/format/avif"}]
        :param mid_bucket: 临时bucket
        :param mid_region: 临时bucket的region
        :param to_overwrite: 是否覆盖
        :return:
        """

        file_keys = [imge_file_key]
        for process_rule in process_rules:
            # 获取imge_file_key的父级目录 例如：test/1.jpg  -> test/ ,imge_file_key= test/1.jpg ,dir_key=test/
            dir_key = imge_file_key[0:imge_file_key.rfind('/') + 1]
            file_keys.append(dir_key+process_rule.get('fileid'))

        if not to_overwrite:
            for process_file_key in file_keys:
                if self.exist(process_file_key):
                    raise Exception(f'file:{process_file_key} is exists')

        # 保存文件到临时bucket
        rules = {"is_pic_info": 1, "rules": process_rules}
        kwargs = {
            "PicOperations": json.dumps(rules)
        }
        resp_up_convert = self.simple_upload_file(imge_data, imge_file_key, mid_bucket, **kwargs)

        result_files = []
        # 复制文件到正式bucket
        for file_key in file_keys:
            resp = self.copy_object(file_key, file_key, mid_bucket, mid_region)
            result_files.append(self.domain + '/' + file_key)
            # print(json.dumps(resp, indent=4, ensure_ascii=False))
            # 删除临时bucket的文件
            self.delete_object(file_key, mid_bucket)

        return result_files

    def delete_object(self, key, bucket=None):
        if not bucket:
            bucket = self.bucket
        response = self.client.delete_object(
            Bucket=bucket,
            Key=key
        )
        return response

    # 判断文件是否存在
    def exist(self, key, bucket=None):
        if not bucket:
            bucket = self.bucket
        response = self.client.object_exists(
            Bucket=bucket,
            Key=key)
        # print(response)
        return response

    #### 文件流简单上传（不支持超过5G的文件，推荐使用下方高级上传接口）
    # 强烈建议您以二进制模式(binary mode)打开文件,否则可能会导致错误
    def upload_file_from_local_file(self, local_file_path, key,**kwargs):
        with open(local_file_path, 'rb') as fp:
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=fp,
                Key=key,
                StorageClass='STANDARD',
                EnableMD5=False,
                **kwargs
            )
        # print(response['ETag'])
        url = self.domain + '/' + key
        resp = {
            "url": url,
            "key": key,
            "response": response
        }
        return resp

    def simple_upload_file(self, file_data, key,bucket=None,domain=None, **kwargs):
        """
        简单上传
        :param file_data: 文件流、字节流
        :param key:
        :param kwargs:
        :return:
        """
        if not bucket:
            bucket = self.bucket
        if not domain:
            domain = self.domain
        response = self.client.put_object(
            Bucket=bucket,
            Body=file_data,
            Key=key,
            EnableMD5=False,
            **kwargs
        )
        url = domain + '/' + key

        resp = {
            "url": url,
            "key": key,
            "response": response
        }
        return resp

    def upload_file_from_url(self, url, key, **kwargs):
        import requests
        stream = requests.get(url)
        return self.simple_upload_file(stream, key, **kwargs)

    #### 高级上传接口（推荐）
    # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    def advance_upload_file(self, local_file_path, key, part_size=1, max_thread=10, enable_md5=False):
        response = self.client.upload_file(
            Bucket=self.bucket,
            LocalFilePath=local_file_path,
            Key=key,
            PartSize=part_size,
            MAXThread=max_thread,
            EnableMD5=enable_md5
        )
        # print(response['ETag'])
        url = self.domain + '/' + key
        return url

    def copy_object(self, source_object_key,target_key,source_bucket, source_region):
        response = self.client.copy(
            Bucket=self.bucket,
            Key=target_key,
            CopySource={
                'Bucket': source_bucket,
                'Key': source_object_key,
                'Region': source_region
            }
        )
        return response

if __name__ == '__main__':
    cos_secret_id = "xxx"
    cos_secret_key = "xxx"
    region = "ap-shanghai"
    bucket = "xxx"
    domain = "xxx"

    Cos1 = Cos(cos_secret_id, cos_secret_key, region, bucket, domain)
    kwargs = {}
    Cos1.simple_upload_file("file_data", "key", **kwargs)

