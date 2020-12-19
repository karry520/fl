from Common.Handler.handler import Handler

import numpy as np

import cppimport
import cppimport.import_hook
import Lib.Skrum_lib.SKRUM as m


class SkrumHandler(Handler):

    def __init__(self, address, port, role, f, num_workers):
        super(SkrumHandler, self).__init__()
        self.address = address
        self.port = port
        self.role = role
        self.f = f
        self.num_workers = num_workers

    def computation_dis(self, data_in):
        grad_ori_data = np.array(data_in, dtype='int16').reshape((self.num_workers, -1))
        length = grad_ori_data.shape[1]
        print("length:", length)
        num_sub = 0

        sub = []
        sub_sqrt = []
        for i in range(self.num_workers - 1):
            for j in range(i + 1, self.num_workers):
                tmp = grad_ori_data[i, :] - grad_ori_data[j, :]
                sub += tmp.tolist()
                sub_sqrt += (tmp ** 2).tolist()
                num_sub += 1

        sign_bit = [int(sub[i] > 0) for i in range(len(sub))]
        sub = np.abs(sub, dtype='int16').tolist()

        mul_rst = []
        in_d = m.VectoruInt32(sub)
        in_sign = m.VectoruInt32(sign_bit)
        print(len(in_d))
        print(len(in_sign))
        mul_rst += m.skrum_mul(self.role, in_d, in_sign, length, num_sub)

        data_trans = [int(0) for i in range(self.num_workers)]
        s1_grad = []
        s2_grad = []
        print("mul_rst,", len(mul_rst))
        # print("mul_rst,", mul_rst)
        if self.role != True:

            s1_data = np.array(mul_rst).reshape((3, -1))
            s1_sub_sqrt = s1_data[0, :] ** 2
            s12_mul = s1_data[1, :]
            s12_sign = s1_data[2, :]

            distance = np.array(sub_sqrt) + s1_sub_sqrt + s12_mul * (2 - s12_sign * 4)
            distance = distance.reshape((num_sub, -1)).sum(axis=1)
            # score
            score_table = np.zeros((self.num_workers, self.num_workers), dtype='int')
            idx = 0
            for i in range(self.num_workers - 1):
                for j in range(i + 1, self.num_workers):
                    score_table[i][j] = distance[idx]
                    score_table[j][i] = distance[idx]
                    idx += 1

            grad_score = []
            upd_grad_table = []

            for i in range(self.num_workers):
                upd_grad_table += [np.argpartition(score_table[i, :], self.f + 1)[:self.f + 1].tolist()]
                grad_score += [
                    score_table[i, :][np.argpartition(score_table[i, :], self.f + 1)[:self.f + 1]].sum(axis=0)]

            update_idx = np.argmin(grad_score)

            upd_set = upd_grad_table[update_idx]
            sec_vec2 = np.zeros((self.num_workers, 1), dtype='int')
            for i in upd_set:
                sec_vec2[i][0] = 1

            s2_grad = np.array((grad_ori_data * sec_vec2 / (self.f + 1)).sum(axis=0), dtype='int16').tolist()
            print("s2_grad length:", len(s2_grad))
            data_trans = sec_vec2.flatten().tolist()

        if self.role:
            print(len(data_trans))
            print("s1:updated grad and select vec", data_trans)
        else:
            print(len(data_trans))
            print("s2:updated grad and select vec", data_trans)

        trs_length = len(data_trans)
        upd_grad_cpp = m.VectoruInt32(data_trans)
        rst_from_s2 = []
        rst_from_s2 += m.skrum_secp(self.role, upd_grad_cpp, trs_length)

        if self.role != True:
            print("s2_grad:", s2_grad[20:30])
            return s2_grad
        else:

            sec_vec1 = np.array(rst_from_s2).reshape((self.num_workers, 1))

            s1_grad = np.array((grad_ori_data * sec_vec1 / (self.f + 1)).sum(axis=0), dtype='int16').tolist()

            print("s1_grad length:", len(s1_grad))
            print("s1_grad:", s1_grad[20:30])
            return s1_grad

    def init_skrum_aby(self):
        m.init_skrum_aby(self.address, self.port, self.role)

    def shutdown_skrum_aby(self):
        m.shutdown_skrum_aby()
