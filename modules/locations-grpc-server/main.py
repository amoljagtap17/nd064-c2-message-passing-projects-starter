import time
from concurrent import futures

import grpc
import location_pb2
import location_pb2_grpc

import json
from kafka import KafkaProducer

TOPIC_NAME = 'locations'
KAFKA_SERVER = 'kafka-service:9094'

kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):
        print("Received location message!")

        payload = {
            "id": request.id,
            "person_id": request.person_id,
            "longitude": request.longitude,
            "latitude": request.latitude,
            "creation_time": request.creation_time,
        }

        print(payload)

        kafka_data = json.dumps(payload).encode()
        kafka_producer.send(TOPIC_NAME, kafka_data)
        kafka_producer.flush()

        return location_pb2.LocationMessage(**payload)

# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

print("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)