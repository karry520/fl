from Common.Server.fl_grpc_server import FlGrpcServer
from Common.Grpc.fl_grpc_pb2 import GradResponse_int32, IdxResponse_uint32
from Common.Grpc.fl_grpc_pb2_grpc import add_FL_GrpcServicer_to_server
from Common.Utils.edcode import decode, encode

from concurrent import futures

import grpc
import time
from Lib.KD_lib.kd_handler import KDHandler
import Common.config as config
import argparse


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='clear_dense_server')
    parser.add_argument('-r', type=int, default=0, help="server's role")
    args = parser.parse_args()

    address = config.server1_address
    port = config.port1
    role = True
    if args.r == 1:
        role = False
        address = config.server2_address
        port = config.port2

    kd_handler = KDHandler(address=config.server1_address, idx_port=config.mpc_idx_port, grad_port=config.mpc_grad_port,
                           role=role, num_workers=config.num_workers, f=config.f)
    kd_server = KDServer(address=address, port=port, config=config, handler=kd_handler)

    kd_handler.init_sru_aby()
    kd_handler.init_kd_aby()
    kd_server.start()
