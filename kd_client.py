from Common.Node.workerbase import WorkerBase
from Common.Utils.edcode import encode, decode
from Common.Grpc.fl_grpc_pb2 import IdxRequest_uint32, GradRequest_int32

import numpy as np

import torch
from torch import nn

import Common.config as config

from Common.Model.LeNet import LeNet
from Common.Utils.data_loader import load_data_fashion_mnist
from Common.Utils.set_log import setup_logging

import grpc
from Common.Grpc.fl_grpc_pb2_grpc import FL_GrpcStub

import argparse


class KDClient(WorkerBase):
    def __init__(self, client_id, model, loss_func, train_iter, test_iter, config, optimizer, stub1, stub2):
        super(KDClient, self).__init__(model=model, loss_func=loss_func, train_iter=train_iter,
                                       test_iter=test_iter, config=config, optimizer=optimizer)
        self.client_id = client_id
        self.stub1 = stub1
        self.stub2 = stub2

    def update(self):
        rst_idx1_upd, rst_idx2_upd = self.update_idx()
        dc_idx_upd1 = decode(rst_idx1_upd)
        dc_idx_upd2 = decode(rst_idx2_upd)

        idx_upd = np.array(np.logical_xor(dc_idx_upd1[:self._grad_len], dc_idx_upd2[:self._grad_len]), dtype='int')

        rst_grad1_upd, rst_grad2_upd = self.update_grad(idx_upd=idx_upd)

        new_gradients = np.array(np.array(rst_grad1_upd) + np.array(rst_grad2_upd), dtype='float')
        new_gradients = new_gradients / self.config.gradient_frac

        idx_upd = np.nonzero(idx_upd.tolist())[0]

        gradients_upd = np.array(super().get_gradients())
        gradients_upd[idx_upd] = new_gradients.tolist()
        super().set_gradients(gradients_upd.tolist())
        print("update once!")

    def update_idx(self):
        grad_abs = np.abs(super().get_gradients())
        index = np.argpartition(grad_abs, self.config.topk)[0 - self.config.topk:]
        grad_idx = np.zeros(self._grad_len, dtype='int').tolist()

        for idx in index:
            grad_idx[idx] = 1

        share_idx1 = np.random.randint(2, size=self._grad_len).tolist()
        share_idx2 = np.array(np.logical_xor(grad_idx, share_idx1), dtype='int').tolist()

        idx_upd_res1 = self.stub1.UpdateIdx_uint32.future(
            IdxRequest_uint32(id=self.client_id, idx_ori=encode(share_idx1)))
        idx_upd_res2 = self.stub2.UpdateIdx_uint32(IdxRequest_uint32(id=self.client_id, idx_ori=encode(share_idx2)))
        print("update index")
        return idx_upd_res1.result().idx_upd, idx_upd_res2.idx_upd

    def update_grad(self, idx_upd):
        idx_upd = np.nonzero(idx_upd)[0]
        grad_top = np.array(self._gradients)[idx_upd]

        grad_top = np.array(grad_top * self.config.gradient_frac, dtype='int')
        print(grad_top)
        share_grad1 = np.random.randint(1000, size=len(idx_upd))
        share_grad2 = grad_top - share_grad1

        grad_upd_res1 = self.stub1.UpdateGrad_int32.future(
            GradRequest_int32(id=self.client_id, grad_ori=share_grad1.tolist()))
        grad_upd_res2 = self.stub2.UpdateGrad_int32(GradRequest_int32(id=self.client_id, grad_ori=share_grad2.tolist()))
        print("update grad")
        return grad_upd_res1.result().grad_upd, grad_upd_res2.grad_upd


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='clear_dense_client')
    parser.add_argument('-i', type=int, help="client's id")
    parser.add_argument('-t', type=int, default=10, help="train times locally")

    args = parser.parse_args()

    yaml_path = 'Log/log.yaml'
    setup_logging(default_path=yaml_path)

    model = LeNet()
    batch_size = 512
    train_iter, test_iter = load_data_fashion_mnist(batch_size=batch_size, root='Data/FashionMNIST')
    lr = 0.001
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_func = nn.CrossEntropyLoss()

    target1 = config.server1_address + ":" + str(config.port1)
    target2 = config.server2_address + ":" + str(config.port2)

    with grpc.insecure_channel(target1) as channel1:
        with grpc.insecure_channel(target2) as channel2:
            print("connect success!")

            stub1 = FL_GrpcStub(channel1)
            stub2 = FL_GrpcStub(channel2)

            client = KDClient(client_id=args.i, model=model, loss_func=loss_func, train_iter=train_iter,
                              test_iter=test_iter, config=config, optimizer=optimizer, stub1=stub1, stub2=stub2)

            client.fl_train(times=args.t)
            client.write_acc_record(fpath="Eva/kd_acc.txt", info="kd_worker")
