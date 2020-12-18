# from Common.Handler.handler import Handler
# from Common.Grpc.fl_grpc_pb2 import DataRequest_int32

import numpy as np

import cppimport
import cppimport.import_hook
import SKRUM as m


class SkrumHandler():

    def __init__(self, address, port, role, f, num_workers):
        super(SkrumHandler, self).__init__()
        self.address = address
        self.port = port
        self.role = role
        self.f = f
        self.num_workers = num_workers

    def computation_dis(self, data_in):
        data = np.array(data_in).reshape((self.num_workers, -1))

        length = data.shape[1]
        num_dis = 0

        sub = []
        sub_sqrt = []
        for i in range(self.num_workers - 1):
            for j in range(i + 1, self.num_workers):
                tmp = data[i, :] - data[j, :]
                sub += tmp.tolist()
                sub_sqrt += (tmp ** 2).tolist()
                num_dis += 1

        sign_bit = [int(sub[i] > 0) for i in range(len(sub))]
        sub = np.abs(sub, dtype='int16').tolist()

        rst = []
        in_d = m.VectoruInt32(sub)
        in_sign = m.VectoruInt32(sign_bit)
        rst += m.skrum_mul(self.role, in_d, in_sign, length, num_dis)


        if (self.role != True):

            s1_data = np.array(rst).reshape((3, -1))
            s1_sub = s1_data[0, :] ** 2
            s12_mul = s1_data[1, :]
            s12_sign = s1_data[2, :]

            dis = np.array(sub_sqrt) + s1_sub + s12_mul * (2 - s12_sign * 4)
            dis = dis.reshape((num_dis, -1)).sum(axis=1)
            # score
            score_table = np.zeros((self.num_workers, self.num_workers), dtype='int')
            idx = 0
            for i in range(self.num_workers - 1):
                for j in range(i + 1, self.num_workers):
                    score_table[i][j] = dis[idx]
                    score_table[j][i] = dis[idx]
                    idx += 1

            grad_score = []
            upd_grad_table = []

            for i in range(self.num_workers):
                upd_grad_table += [np.argpartition(score_table[i, :], self.f + 1)[:self.f + 1].tolist()]
                grad_score += [score_table[i, :][np.argpartition(score_table[i, :], self.f + 1)[:self.f + 1]].sum(axis=0)]

            update_idx = np.argmin(grad_score)

            upd_set = upd_grad_table[update_idx]
            sec_vec = np.zeros(self.num_workers, dtype='int')
            for i in upd_set:
                sec_vec[i] = 1
            

        return rst

    def computation(self, in_data):
        pass

    def init_skrum_aby(self):
        m.init_skrum_aby(self.address, self.port, self.role)

    def shutdown_skrum_aby(self):
        m.shutdown_skrum_aby()


