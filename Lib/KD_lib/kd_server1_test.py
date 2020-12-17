# -*- coding: utf-8 -*-
from kd_handler import KDHandler

import Common.config as config
import numpy as np

hander = KDHandler(address=config.server1_address, idx_port=config.mpc_idx_port, grad_port=config.mpc_grad_port,
                   role=True, num_workers=config.num_workers, f=config.f)

hander.init_sru_aby()
hander.init_kd_aby()
idx = np.random.randint(2, size=30)
print(idx)
rst = hander.computation_idx(data_in=idx.tolist())
print(rst)

########################################################################################################################

grad = np.random.randint(100, size=60)
print(grad)
rst = hander.computation_grad(data_in=grad)
print(rst)

hander.shutdown_sru_aby()
hander.shutdown_kd_aby()
