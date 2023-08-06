import os
import socket

import pandas as pd

from pyjava.api.mlsql import PythonContext
from pyjava.serializers import \
    ArrowStreamPandasSerializer


class DataServer(object):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port


class RayContext(object):

    def __init__(self, python_context: PythonContext):
        self.python_context = python_context
        self.servers = []
        for item in self.python_context.fetch_once_as_rows():
            self.servers.append(DataServer(item["host"], int(item["port"]), item["timezone"]))

    def data_servers(self):
        return self.servers

    def fetch_data_from_single_data_server(self, data_server: DataServer, timezone: str):
        out_ser = ArrowStreamPandasSerializer(timezone, True, True)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((data_server.host, data_server.port))
            buffer_size = int(os.environ.get("BUFFER_SIZE", 65536))
            infile = os.fdopen(os.dup(sock.fileno()), "rb", buffer_size)
            result = out_ser.load_stream(infile)
            for items in result:
                yield pd.DataFrame(items.to_pydict())
