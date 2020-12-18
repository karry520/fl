from Common.Server.fl_grpc_server import FlGrpcServer
from Common.Grpc.fl_grpc_pb2 import GradResponse_int32

import Common.config as config

data_cache = []
sign_cache = []

complicate = False


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
        rst = super().process(dict_data=data_dict, handler=self.handler.computation)
        return GradResponse_int32(grad_upd=rst)

    def DataTrans_int32(self, request, context):
        global sign_cache, data_cache

        data_cache = request.data_ori
        sign_cache = [int(data_cache[i] > 0) - int(data_cache[i] < 0) for i in range(len(data_cache))]
        while len(data_cache) == 0:
            pass

        return data_cache


if __name__ == "__main__":
    gradient_handler = AvgGradientHandler(num_workers=config.num_workers)

    clear_server = ClearDenseServer(address=config.server1_address, port=config.port1, config=config,
                                    handler=gradient_handler)
    clear_server.start()
