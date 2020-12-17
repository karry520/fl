from Common.Server.fl_grpc_server import FlGrpcServer
from Common.Grpc.fl_grpc_pb2 import GradResponse_int32, IdxResponse_uint32
from Common.Grpc.fl_grpc_pb2_grpc import add_FL_GrpcServicer_to_server
from Common.Utils.edcode import decode, encode

from concurrent import futures

import grpc
import time


class KDServer(FlGrpcServer):
    def __init__(self, address, port, config, handler):
        super(KDServer, self).__init__(config=config)
        self.address = address
        self.port = port
        self.config = config
        self.handler = handler

    def UpdateIdx_uint32(self, request, context):
        data_dict = {request.id: decode(request.idx_ori)}
        print("have received idx:", data_dict.keys())
        rst = super().process(dict_data=data_dict, handler=self.handler.computation_idx)
        return IdxResponse_uint32(idx_upd=encode(rst))

    def UpdateGrad_int32(self, request, context):
        data_dict = {request.id: request.grad_ori}
        print("have received grad:", data_dict.keys())
        rst = super().process(dict_data=data_dict, handler=self.handler.computation_grad)
        return GradResponse_int32(grad_upd=rst)

    def start(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_FL_GrpcServicer_to_server(self, server)

        target = self.address + ":" + str(self.port)
        server.add_insecure_port(target)
        server.start()

        try:
            while True:
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            self.handler.shutdown_sru_aby()
            self.handler.shutdown_kd_aby()
            server.stop(0)
