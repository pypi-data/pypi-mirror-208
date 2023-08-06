import json
import ast
import logging
from datetime import datetime
from http.client import HTTPException

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from confluent_kafka import Consumer, KafkaError
import certifi
import os
import threading
import jwt

class create_stream:
    def __init__(self, kafka_connection, mongo_connection=None, topicname="", timestamp_attr="timestamp"):
        self.topicname = topicname
        self.kafka_connection = kafka_connection
        self.mongo_connection = mongo_connection
        self.timestamp_attr = timestamp_attr
        self._stop_event = threading.Event()

    def is_epoch(self, timestamp):
        try:
            datetime.fromtimestamp(int(timestamp))
            return True
        except ValueError:
            return False

    def _run(self, token):
        mongo_client = MongoClient(self.mongo_connection['uri'], server_api=ServerApi('1'), tlsCAFile=certifi.where())
        mongo_db = mongo_client[self.mongo_connection['database']]
        raw_data_collection = mongo_db[self.mongo_connection['rawdata']]

        consumer = Consumer(self.kafka_connection)
        print(self.topicname)
        consumer.subscribe([self.topicname])

        while not self._stop_event.is_set():
            msg = consumer.poll(10.0)
            print("Poll executed")
            print(msg)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
            else:
                message_value = ast.literal_eval(msg.value().decode("utf-8"))
                print(message_value)

                # New lines added for validation
                if self.timestamp_attr not in message_value:
                    print(
                        f"Error: Message does not contain the required timestamp attribute '{self.timestamp_attr}'. Skipping message.")
                    continue

                if self.is_epoch(message_value.get(self.timestamp_attr)):
                    if self.is_epoch(message_value.get(self.timestamp_attr)):
                        message_value[self.timestamp_attr] = int(message_value[self.timestamp_attr])
                    else:
                        message_value[self.timestamp_attr] = datetime.now().timestamp()

                raw_data_collection.insert_one(message_value)
                print("Message received: {}".format(message_value))
        consumer.close()

    def start(self, token):
        # authenicate token
        mongo_client = MongoClient(self.mongo_connection['uri'], server_api=ServerApi('1'), tlsCAFile=certifi.where())
        mongo_db = mongo_client[self.mongo_connection['database']]
        mongo_db_featurizer = mongo_client['featurizer']
        users_collection = mongo_db_featurizer["users"]
        SECRET_KEY = "features"  # Change this to your desired secret key
        TOKEN_EXPIRATION = 3600  # Token expiration in seconds (1 hour)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("user_id")
            if user_id is None:
                print("User not found")
                return ("Invalid token")
            print(user_id)
            user = users_collection.find_one({"userid": user_id})
            if user is None:
                print("User not found")
                return ("Invalid token")
        except Exception as e:
            print(e)
            return ("Invalid token")


        if not hasattr(self, '_consumer_thread') or not self._consumer_thread.is_alive():
            self._stop_event.clear()
            self._consumer_thread = threading.Thread(target=self._run(self))
            self._consumer_thread.start()
            print('featurizerai: Started consumer thread.')
        else:
            print("Thread is already running. Cannot start it again.")

    def stop(self):
        if hasattr(self, '_consumer_thread') and self._consumer_thread.is_alive():
            self._stop_event.set()
            self._consumer_thread.join()
            print('featurizerai: Stopped consumer thread.')
        else:
            print("Thread is not running. Cannot stop it.")
