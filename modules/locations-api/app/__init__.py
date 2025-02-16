from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

from kafka import KafkaProducer
from threading import Thread

db = SQLAlchemy()

TOPIC_NAME = 'locations'
KAFKA_SERVER = 'kafka-service:9094'

def create_app(env=None):
    from app.config import config_by_name
    from app.routes import register_routes
    from app.udaconnect.services import KafkaService

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or "test"])
    api = Api(app, title="Locations API", version="0.1.0")

    CORS(app)  # Set CORS for development

    register_routes(api, app)
    db.init_app(app)

    @app.route("/health")
    def health():
        return jsonify("healthy")
    
    @app.before_request
    def before_request():
        # Set up a Kafka producer
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        # Setting Kafka to g enables us to use this
        # in other parts of our application
        g.kafka_producer = producer

    # Run Kafka consumer in a separate thread
    consumer_thread = Thread(target=KafkaService.run_locations_consumer, args=(app.app_context(),), daemon=True)
    consumer_thread.start()

    return app
    