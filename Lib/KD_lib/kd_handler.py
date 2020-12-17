from Common.Handler.handler import Handler
import Common.config as config
import numpy as np

import cppimport
import cppimport.import_hook
import Lib.KD_lib.KD as m


class KDHandler(Handler):

    def __init__(self, address, idx_port, grad_port, role, num_workers, f):
        super(KDHandler, self).__init__()
        self.address = address
        self.idx_port = idx_port
        self.grad_port = grad_port
        self.role = role
        self.num_workers = num_workers
        self.f = f

    def computation_idx(self, data_in):
        length = int(len(data_in) / self.num_workers)
        rst = []

        it_times = int(length / config.idx_max_length)
        residue_length = int(length % config.idx_max_length)

        array_idx = np.array(data_in).reshape((self.num_workers, -1))
        if it_times != 0:
            for i in range(it_times):
                in_idx = array_idx[:, config.idx_max_length * i:config.idx_max_length * (i + 1)].flatten().tolist()
                in_idx = m.VectoruInt(in_idx)
                rst += m.kd_sru(self.role, in_idx, self.num_workers, config.idx_max_length, self.f)

        in_idx = array_idx[:, -residue_length:].flatten().tolist()
        in_idx = m.VectoruInt(in_idx)
        rst += m.kd_sru(self.role, in_idx, self.num_workers, residue_length, self.f)

        return rst

    def computation_grad(self, data_in):
        length = int(len(data_in) / self.num_workers)
        rst = []
        grad = np.array(data_in) + config.grad_shift

        frac_grad = np.array(grad) * 0.2
        frac_grad = np.array(frac_grad, dtype='int16')

        in_grad = m.VectoruInt32(grad.tolist())
        in_fgrad = m.VectoruInt32(frac_grad.tolist())
        rst += m.kd_top(self.role, in_grad, in_fgrad, length, self.num_workers, self.f)
        rst = (np.array(rst) - (2 * self.f * config.grad_shift)) / (2 * self.f)
        rst = [int(rst[i]) for i in range(len(rst))]

        return rst

    def init_sru_aby(self):
        m.init_sru_aby(self.address, self.idx_port, self.role)

    def shutdown_sru_aby(self):
        m.shutdown_sru_aby()

    def init_kd_aby(self):
        m.init_kd_aby(self.address, self.grad_port, self.role)

    def shutdown_kd_aby(self):
        m.shutdown_kd_aby()
