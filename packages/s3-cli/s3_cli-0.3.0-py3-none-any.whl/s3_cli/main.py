import os
from io import BytesIO
import gzip
import boto3
import botocore


class S3:
    class DoesNotExist(Exception):
        pass

    def __init__(self, bucket):
        self.client = boto3.client("s3")
        self.resource = boto3.resource("s3")
        self.bucket = bucket

    def put(self, file, key):
        self.client.put_object(Bucket=self.bucket, Key=key, Body=file)

    def get(self, key):
        try:
            content = self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
        except self.client.exceptions.NoSuchKey:
            raise self.DoesNotExist()
        return BytesIO(content)

    def delete(self, key):
        self.resource.Object(self.bucket, key).delete()

    def new(self, key, content):
        file = self.resource.Object(self.bucket, key)
        file.put(Body=content)

    def key_exists(self, key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e
        return True

    def list(self, path):
        objects = self.resource.Bucket(name=self.bucket).objects.filter(Prefix=path, Marker=path)
        return [o.key for o in objects]

    def download(self, from_location, to_location):
        self.client.download_file(self.bucket, from_location, to_location)

    def stream(self, filename, out_dir, file):
        print("start stream for file: ", f"{out_dir}/{filename}")
        output = BytesIO()
        file.to_excel(output, index=False, engine='xlsxwriter')
        self.put(file=output.getvalue(), key=f"{out_dir}/{filename}")
        print("finish stream")


class LocalFS:
    class DoesNotExist(Exception):
        pass

    def __init__(self, bucket="/Users/nsalgado/work/scripts/lambdas/multicare/"):
        self.bucket = bucket

    def put(self, file, key):
        with open(os.path.join(self.bucket, key), "wb") as f:
            f.write(file.getbuffer())

    def get(self, key):
        print(os.path.join(self.bucket, key))
        with open(os.path.join(self.bucket, key), "rb") as f:
            return BytesIO(f.read())

    def key_exists(self, key):
        return os.path.exists(os.path.join(self.bucket, key))

    def delete(self, key):
        raise NotImplementedError

    def new(self, key, content):
        raise NotImplementedError

    def stream(self, filename, out_dir, file):
        file.to_excel(os.path.join(out_dir, filename), index=False)
