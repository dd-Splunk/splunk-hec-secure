from __future__ import annotations

import datetime
import logging
import zlib
from http import HTTPStatus
from typing import Generator, Literal

import lz4.frame
import requests
from minio import Minio
from splunklib import setup_logging

# To see debug and above level logs
setup_logging(logging.DEBUG)

# Define typing hints

Proto = Literal["http", "https"]
Url = str


class Archive:
    def __init__(
        self,
        host: str = None,
        port: int = None,
        access_key: str = None,
        secret_key: str = None,
        ddaa_bucket: str = None,
        ssl_verify: bool = None,
    ):
        self.log = logging.getLogger("S3")
        self.log.setLevel(logging.INFO)

        self.host = host if host is not None else "localhost"
        self.port = port if port is not None else 9000
        self.access_key = access_key if access_key is not None else "admin"
        self.secret_key = secret_key if secret_key is not None else "?"
        self.ddaa_bucket = ddaa_bucket if ddaa_bucket is not None else "ddaa-bucket"
        self.ssl_verify = ssl_verify if ssl_verify is not None else False

        self.client = Minio(
            endpoint=f"{self.host}:{self.port}",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,
            cert_check=self.ssl_verify,
        )

    def __repr__(self) -> str:
        cls = self.__class__
        return f"{cls.__name__}: {self.host} {self.access_key} \
{self.secret_key} {self.ddaa_bucket}"

    def bucket_prefix(self, thisday: datetime, sourcetype: str = None) -> str:
        """_summary_

        Args:
            thisday (datetime): _description_
            sourcetype (str, optional): _description_. Defaults to None.

        Returns:
            str: _description_
        """
        prefix = f"year={thisday.year:0{4}}"
        prefix += f"/month={thisday.month:0{2}}"
        prefix += f"/day={thisday.day:0{2}}/"

        if sourcetype is not None:
            prefix += f"sourcetype={sourcetype}/"

        self.log.debug(f"Bucket prefix {prefix}")

        return prefix

    # Supported decompressors
    def gunzip(compressed_content):
        # Decode .gz
        # https://stackoverflow.com/questions/1838699/how-can-i-decompress-a-gzip-stream-with-zlib
        lines = zlib.decompress(compressed_content, 15 + 32)
        return lines

    def lz4(compressed_content):
        lines = lz4.frame.decompress(compressed_content)
        return lines

    def zstd(compressed_content):
        lines = ""
        return lines

    def none(content):
        return content

    # Dict with supported compression algs and the corresponding decompression function
    supported_compression = {
        "gz": gunzip,
        "lz4": lz4,
        "zst": zstd,
        "json": none,
        "ndjson": none,
        "log": none,
    }

    # Wrapper to call the relevant decompressor based on its name
    def decompress(self, alg: str, text: str):
        # return self.supported_compression.get(alg)(text)
        return self.supported_compression[alg](text)

    def list_objects(
        self, thisday: datetime, sourcetype: str = None, recurse: bool = None
    ) -> Generator:
        """
        Recurse by default in case sourcetype is ommitted here
        but present in the archived object

        Args:
            thisday (datetime): Specific date to retrieve
            sourcetype (str, optional): Optional sourcetype to get Defaults to None.
            recurse (bool, optional): Optional look for deepest file. Defaults to None.

        Returns:
            _type_: _description_

        Yields:
            Generator: _description_
        """

        recurse = recurse if recurse is not None else True

        objects = self.client.list_objects(
            bucket_name=self.ddaa_bucket,
            prefix=self.bucket_prefix(thisday, sourcetype),
            recursive=recurse,
        )
        return objects

    def get_lines(self, object_name: str) -> bytes:
        """Read log lines from object.

        Returns:
            _type_: log lines
        """

        # object is an urlib3.response.BaseHTTPResponse
        # https://urllib3.readthedocs.io/en/stable/reference/urllib3.response.html
        object = self.client.get_object(
            bucket_name=self.ddaa_bucket, object_name=object_name
        )

        splits = object_name.split(".")
        compression = splits[-1]
        format = splits[-2]
        """Format exemples:

            log: raw logs
            2022-08-01 15:29:17,000 -0700 INFO event - 1
            2022-08-02 15:29:18,000 -0700 INFO event - 2

            json: single line
            [{"time":123456789,"event":"2022-01-01 12:00:00, 000 -0700 INFO event - 1",
            "host":"some-host","source":"/some/folder/sample.log","sourcetype":"some-sourcetype"},
            {"time":123456789,"event":"2022-01-02 12:00:00, 000 -0700 INFO event - 2",
            "host":"some-host","source":"/some/folder/sample.log","sourcetype":"some-sourcetype"}]

            ndjson: new line demlimited json
            {"time":123456789,"event":"2022-01-01 12:00:00, 000 -0700 INFO event - 1",
            "host":"some-host","source":"/some/folder/sample.log","sourcetype":"some-sourcetype"}
            {"time":123456789,"event":"2022-01-02 12:00:00, 000 -0700 INFO event - 2",
            "host":"some-host","source":"/some/folder/sample.log","sourcetype":"some-sourcetype"}

        """

        lines = self.decompress(compression, object.read(decode_content=True))

        # If needed convert to multilines (ndjson) format
        # Must become a distinct function wrapper
        #
        if format.lower() == "json":
            delim = "\n"
            lines = delim.join(map(str, lines))

        return lines

    @property
    def url(self) -> Url:
        return f"https://{self.host}:{self.port}"

    @property
    def check_connectivity(self) -> bool:
        requests.packages.urllib3.disable_warnings()
        self.log.info(f"Checking Archive Server {self.url} reachability.")
        minio_reachable = False
        try:
            response = requests.post(
                url=self.url,
                headers=dict(),
                data=dict(),
                verify=False,
            )
            minio_reachable = True
            self.log.debug(f"Status: {response.status_code}")

        except Exception:
            self.log.warning(f"Archive host {self.url} not reachable!")

        return minio_reachable

    @property
    def check_ddaa_bucket(self) -> bool:
        self.log.info(f"Checking availability of {self.ddaa_bucket} in archive")

        buckets = self.client.list_buckets()
        ddaa_bucket_exists = self.ddaa_bucket in buckets

        return ddaa_bucket_exists


class Destination:
    def __init__(
        self,
        host: str = None,
        port: int = None,
        token: str = None,
        proto: Proto = None,
        ssl_verify: bool = None,
    ):
        self.log = logging.getLogger("HEC")
        self.log.setLevel(logging.INFO)

        self.host = host if host is not None else "localhost"
        self.port = port if port is not None else 8088

        self.token = token if token is not None else "aa-bb"
        self.proto = proto if proto is not None else "https"
        self.ssl_verify = ssl_verify if ssl_verify is not None else False

    def __repr__(self) -> str:
        cls = self.__class__
        return f"{cls.__name__}: {self.host} {self.token}"

    @property
    def url(self) -> Url:
        return f"{self.proto}://{self.host}:{self.port}/services/collector/event"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": "Splunk " + self.token,
            "Content-Type": "application/json",
        }

    @property
    def check_connectivity(self) -> bool:
        requests.packages.urllib3.disable_warnings()
        self.log.info("Checking HEC Server URI reachability.")
        hec_reachable = False
        # acceptable_status_codes = [400, 401, 403]
        # heath_warning_status_codes = [500, 503]
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=dict(),
                verify=False,
            )
            hec_reachable = True
            self.log.debug(f"Status: {response.status_code}")

        except Exception:
            self.log.error(f"Splunk Server {self.host} is unreachable.")

        return hec_reachable

    def sendMultiLines(self, payload: str) -> HTTPStatus:
        requests.packages.urllib3.disable_warnings()
        status = HTTPStatus.SERVICE_UNAVAILABLE
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=payload,
                verify=self.ssl_verify,
            )
            status = response.status_code
            self.log.debug(f"Status: {response.status_code}")
        except Exception:
            logging.error(f"Connection to {self.host} refused!")

        return status


if __name__ == "__main__":
    from config import destination

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    payload = """{"time":1701388800,"event":"Current Time = 01:00:00\\n",
    "host":"uf1","source":"/opt/splunkforwarder/etc/apps/normal/bin/heure.py",
    "sourcetype":"heure","index":"cust1","fields":{"cust":"customer-normal"}}\n
    {"time":1701388800,"event":"Current Time = 01:00:00\\n","host":"uf0",
    "source":"/opt/splunkforwarder/etc/apps/unlimited-speed/bin/heure.py",
    "sourcetype":"heure","index":"cust0","fields":{"cust":"customer-unlimited"}}\n"""
    status = destination.sendMultiLines(payload)
    logging.debug(f"Archive sent status: {status}")
