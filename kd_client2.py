import torch
from torch import nn

import Common.config as config

from Common.Model.LeNet import LeNet
from Common.Utils.data_loader import load_data_fashion_mnist
from Common.Utils.set_log import setup_logging

import grpc
from Common.Grpc.fl_grpc_pb2_grpc import FL_GrpcStub

from kd_client import KDClient

if __name__ == '__main__':
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

            client = KDClient(client_id=2, model=model, loss_func=loss_func, train_iter=train_iter,
                              test_iter=test_iter, config=config, optimizer=optimizer, stub1=stub1, stub2=stub2)

            client.fl_train(times=10)
            client.write_acc_record(fpath="Eva/kd_acc.txt", info="kd_worker")
