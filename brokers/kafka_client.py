from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
from settings import logger


class AsyncKafkaClient:
    def __init__(self, broker: str = "localhost:9094", topic: str = "courses"):
        self.broker = broker
        self.topic = topic
        self.producer = None
        self.consumer = None

    async def start(self):
        # Initialize the producer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        # Stop the producer and consumer
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()

    async def send_message(self, message: dict):
        # Send a message to the Kafka topic
        if self.producer:
            await self.producer.send(self.topic, message)
            #  logger.info("Sent message to kafka")

    async def consume_messages(self):
        # Consume messages from the Kafka topic
        logger.info("Get message from kafka")
        return await self.consumer.getone().value


kafka_client = AsyncKafkaClient()
