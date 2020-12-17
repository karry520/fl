import threading
import numpy as np
from Common.Grpc.fl_grpc_pb2_grpc import FL_GrpcServicer

con = threading.Condition()
num = 0

data_ori = {}
data_upd = []


class FlGrpcServer(FL_GrpcServicer):
    def __init__(self, config):
        super(FlGrpcServer, self).__init__()
        self.config = config

    def process(self, dict_data, handler):
        global num, data_ori, data_upd

        data_ori.update(dict_data)

        con.acquire()
        num += 1
        if num < self.config.num_workers:
            con.wait()
        else:
            rst = [data_ori[k] for k in sorted(data_ori.keys())]
            rst = np.array(rst).flatten()
            data_upd = handler(data_in=rst)
            data_ori = {}
            num = 0
            con.notifyAll()

        con.release()

        return data_upd
