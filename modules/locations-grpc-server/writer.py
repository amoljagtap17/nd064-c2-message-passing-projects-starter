import grpc
import location_pb2
import location_pb2_grpc

"""
Sample implementation of a writer that can be used to write messages to gRPC.
"""

print("Sending sample location payload...")

channel = grpc.insecure_channel("localhost:5005")
stub = location_pb2_grpc.LocationServiceStub(channel)

# Update this with desired payload
location = location_pb2.LocationMessage(
    id=1,
    person_id=5,
    longitude="37.5536299999999983",
    latitude="-122.2908829999999938",
    creation_time='2024-01-29',
)

response = stub.Create(location)
