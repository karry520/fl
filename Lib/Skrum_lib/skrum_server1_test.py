# -*- coding: utf-8 -*-
from skrum_handler import SkrumHandler

import config
import numpy as np

hander = SkrumHandler(address=config.server1_address, port=config.mpc_idx_port, role=True, f=config.f, num_workers=config.num_workers)

hander.init_skrum_aby()

idx = [4, 2, 3, 1, 1, 2, 3, 3, 5, 4, 2, 3, 1, 1, 2, 3, 3, 5, 2, 4]
print("idx:", idx)
rst = hander.computation_dis(data_in=idx)
print("rst:", rst)

hander.shutdown_skrum_aby()
