from Common.Server.fl_grpc_server import FlGrpcServer, add_FL_GrpcServicer_to_server
from Common.Grpc.fl_grpc_pb2 import GradResponse_int32
import argparse
import Common.config as config
from Lib.Skrum_lib.skrum_handler import SkrumHandler
from concurrent import futures

import grpc
import time


class SkrumServer(FlGrpcServer):
    def __init__(self, address, port, config, handler):
        super(SkrumServer, self).__init__(config=config)
        self.address = address
        self.port = port
        self.config = config
        self.handler = handler

    def UpdateGrad_int32(self, request, context):
        data_dict = {request.id: request.grad_ori}
        print("have received:", data_dict.keys())
        rst = super().process(dict_data=data_dict, handler=self.handler.computation_dis)
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
            self.handler.shutdown_skrum_aby()
            server.stop(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='skrum server')
    parser.add_argument('-r', type=int, default=0, help="server's role")
    args = parser.parse_args()

    address = config.server1_address
    port = config.port1
    role = True
    if args.r == 1:
        role = False
        address = config.server2_address
        port = config.port2

    skrum_handler = SkrumHandler(address=config.server1_address, port=config.mpc_grad_port,
                                 role=role, num_workers=config.num_workers, f=config.f)
    skrum_server = SkrumServer(address=address, port=port, config=config, handler=skrum_handler)

    skrum_handler.init_skrum_aby()
    skrum_server.start()
