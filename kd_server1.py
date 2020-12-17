from Lib.KD_lib.kd_handler import KDHandler
from kd_server import KDServer
import Common.config as config

if __name__ == "__main__":
    kd_handler = KDHandler(address=config.server1_address, idx_port=config.mpc_idx_port, grad_port=config.mpc_grad_port,
                           role=True, num_workers=config.num_workers, f=config.f)
    kd_handler.init_sru_aby()
    kd_handler.init_kd_aby()

    kd_server = KDServer(address=config.server1_address, port=config.port1, config=config, handler=kd_handler)
    kd_server.start()
