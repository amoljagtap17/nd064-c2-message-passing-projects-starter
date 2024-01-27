import logging
from typing import Dict, List

from app import db
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from geoalchemy2.functions import ST_AsText, ST_Point

from kafka import KafkaConsumer

from flask import g
import json

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("locations-api")

class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location
    
    @staticmethod
    def retrieve_all() -> List[Location]:
        return db.session.query(Location).all()

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        kafka_data = json.dumps(location).encode()
        kafka_producer = g.kafka_producer
        kafka_producer.send("locations", kafka_data)
        kafka_producer.flush()
    
    @staticmethod
    def execute_locations_consumer(location: Dict) -> Location:
        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
        db.session.add(new_location)
        db.session.commit()

        return new_location
    

class KafkaService:
    @staticmethod
    def run_locations_consumer(topic_name, kafka_server):
        locations_consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_server)

        for location in locations_consumer:
            payload = json.loads(location.value)

            print("location payload :: " + str(payload))

            LocationService.execute_locations_consumer(payload)
