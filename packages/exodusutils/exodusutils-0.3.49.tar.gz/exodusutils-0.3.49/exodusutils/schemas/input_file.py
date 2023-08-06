from pandas import DataFrame, read_csv
from pydantic import BaseModel

from exodusutils.schemas.uri import BytesIO, Minio, MinioURI


class InputFile(BaseModel):
    """
    The path to a local file user wishes to use as a task's input.
    """

    path: str

    @property
    def uri(self) -> MinioURI:
        return MinioURI(bucket="tmp", key=self.path)

    def json(self) -> str:
        res = DataFrame(read_csv(self.path)).to_json(orient="records")
        if res is None:
            raise ValueError
        return res

    def upload(self, minio: Minio) -> str:
        if self.uri.bucket not in [b.name for b in minio.list_buckets()]:
            minio.make_bucket(self.uri.bucket)
        with open(self.path) as f:
            content = f.read().encode("UTF-8")
            minio.put_object(self.uri.bucket, self.path, BytesIO(content), len(content))
        return self.uri.url

    def delete(self, minio: Minio) -> None:
        minio.remove_object(self.uri.bucket, self.path)
