import csv
import traceback
from io import BytesIO, StringIO
from typing import List, Optional
from urllib.parse import urlparse

import pandas as pd
from minio.api import Minio
from pydantic import BaseModel
from urllib3.response import HTTPResponse

from exodusutils.exceptions.exceptions import ExodusForbidden


class MinioURI(BaseModel):
    """
    The Minio URI.
    """

    bucket: str
    key: str

    @property
    def url(self) -> str:
        """
        Returns `"s3a://{bucket}/{object}"`.
        """
        return f"s3a://{self.bucket}/{self.key}"

    @classmethod
    def parse(cls, s: str):
        """
        Parses a string to a Minio compatible URI. The scheme could be either `s3`, `s3a`, or `s3n`.

        Parameters
        ----------
        s : str
            The string to parse.
        """
        parsed = urlparse(s)
        if parsed.scheme not in ["s3", "s3a", "s3n"]:
            raise ExodusForbidden(f"Invalid scheme: {parsed.scheme}")
        return cls(bucket=parsed.netloc, key=parsed.path.lstrip("/"))

    def put_df(self, minio: Minio, df: pd.DataFrame) -> str:
        """
        Stores the given Pandas DataFrame in Minio as a CSV object, and returns its URI as `str`.

        Parameters
        ----------
        minio : Minio
            The minio client
        df : pd.DataFrame
            The dataframe to store

        Returns
        -------
        str
            The URI for the stored dataframe, as a `str`.
        """
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        csv_buffer = BytesIO(csv_bytes)
        if not minio.bucket_exists(self.bucket):
            minio.make_bucket(self.bucket)
        minio.put_object(
            self.bucket,
            self.key,
            csv_buffer,
            length=len(csv_bytes),
            content_type="application/csv",
        )
        return self.url

    def get_df(self, minio: Minio, header: List[str]) -> Optional[pd.DataFrame]:
        """
        Returns a Pandas dataframe parsed from this Minio URI. Returns `None` on failure.

        Parameters
        ----------
        minio : Minio
            The Minio client.
        header : List[str]
            The header we want to parse the dataframe with.

        Returns
        -------
        Optional[pd.DataFrame]
            The parsed dataframe.

        """
        try:
            resp: HTTPResponse = minio.get_object(self.bucket, self.key)
            if not resp.data:
                # Should be inpossible
                raise ValueError
            return pd.DataFrame(pd.read_csv(BytesIO(resp.data), usecols=header))
        except Exception:
            traceback.print_exc()

    @classmethod
    def get_header(self, minio: Minio, uri: str) -> List[str]:
        """
        Returns the header of the Pandas dataframe parsed from the provided Minio URI.

        Parameters
        ----------
        minio : Minio
            The Minio client.
        uri : str
            The Minio URI.

        Returns
        -------
        header : List[str]
            The parsed header.
        """
        minio_uri = self.parse(uri)
        stuff = minio.get_object(minio_uri.bucket, minio_uri.key).data

        with StringIO(stuff.decode("utf-8-sig")) as f:
            rows = csv.reader(f, delimiter=",")
            header = next(rows)
            return header
