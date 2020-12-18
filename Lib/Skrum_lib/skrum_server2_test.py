# -*- coding: utf-8 -*-
from skrum_handler import SkrumHandler

import config
import numpy as np

hander = SkrumHandler(address=config.server1_address, port=config.mpc_idx_port, role=False, f=config.f,
                      num_workers=config.num_workers)

hander.init_skrum_aby()

idx = [6, 6, 6, 5, 0, 0, 1, 1, 0, 6, 6, 6, 5, 0, 0, 1, 1, 2, 1, 5]

print("idx:", idx)
rst = hander.computation_dis(data_in=idx)
print("rst:", rst)

hander.shutdown_skrum_aby()
