"""
syntax = "proto3";

service Weather {
  rpc GetWeather (City) returns (Report);
}

message City {
  string name = 1;
}

message Report {
  double temperature = 1;
  string description = 2;
}

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. weather.proto
"""
服务端
import grpc
from concurrent import futures
import weather_pb2, weather_pb2_grpc

class WeatherServicer(weather_pb2_grpc.WeatherServicer):
    def GetWeather(self, request, context):
        city = request.name
        return weather_pb2.Report(
            temperature=20.5,
            description=f"Sunny day in {city}"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weather_pb2_grpc.add_WeatherServicer_to_server(WeatherServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server running on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

客户端
import grpc
import weather_pb2, weather_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = weather_pb2_grpc.WeatherStub(channel)

    response = stub.GetWeather(weather_pb2.City(name="Beijing"))
    print(f"Temperature: {response.temperature}, Description: {response.description}")

if __name__ == "__main__":
    run()



启动服务端：

python server.py


启动客户端：

python client.py


输出：

Temperature: 20.5, Description: Sunny day in Beijing