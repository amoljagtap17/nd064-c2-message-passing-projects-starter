import os

from app import create_app
from app.udaconnect.services import KafkaService

TOPIC_NAME = 'locations'
KAFKA_SERVER = 'kafka-service:9094'

app = create_app(os.getenv("FLASK_ENV") or "test")

if __name__ == "__main__":
    app.run(debug=True)
    KafkaService.run_locations_consumer(TOPIC_NAME, KAFKA_SERVER)
