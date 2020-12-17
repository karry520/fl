# Federated Learning

## 使用说明 
### Grpc已有配置
~~~
rpc UpdateIdx_uint32(IdxRequest_uint32) returns (IdxResponse_uint32){}
rpc UpdateGrad_int32(GradRequest_int32) returns (GradResponse_int32){}
rpc UpdateGrad_float(GradRequest_float) returns (GradResponse_float){}
rpc DataTrans_int32(DataRequest_int32) returns (DataResponse_int32){}
~~~

### 服务端
1. FlGrpcServer类已实现的方法（服务端的一般操作）
~~~
# 收集数据
def process(self, dict_data, handler)
# 启动服务
def start(self)
~~~
2. 定义自己的Server，继承FlGrpcServer，实现Grpc中定义的函数（数据类型）
~~~
from Common.Server.fl_grpc_server import FlGrpcServer

class yourServer(FLGrpcServer):
    # 实现上述Grpc中的方法
    def yourfunc(self, request, context):
        pass
~~~

3. 实现具体的hander(处理数据)
~~~
# 接口定义为
class YourHandler:
    def computation(self, data_in):
        return data_out
~~~

### 客户端
1. WorkerBase基类实现了单步训练的方法
2. 定义自己的Woker，继承WorkerBase类
~~~
from Common.Node.workerbase import WorkerBase

class YourWorker(WorkerBase):
    def update():
        gradients = super().get_gradients()
        
        # 定义上传/接收操作
        
        super().set_gradients()    
    
~~~