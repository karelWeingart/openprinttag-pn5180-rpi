"""General MQTT subscriber with callback support."""
import logging
from typing import Callable

import paho.mqtt.client as mqtt


class MQTTSubscriber:
    """MQTT subscriber that routes messages to registered callbacks."""

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        keepalive: int = 60
    ):
        """Initialize MQTT subscriber.
        
        Args:
            broker: MQTT broker address.
            port: MQTT broker port.
            keepalive: Connection keepalive in seconds.
        """
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self._client: mqtt.Client | None = None
        self._callbacks: dict[str, Callable[[bytes], None]] = {}

    def _on_message(self, _client, _userdata, msg) -> None:
        """Internal message handler - routes to registered callbacks."""
        topic = msg.topic
        if topic in self._callbacks:
            try:
                self._callbacks[topic](msg.payload)
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Error in callback for topic %s: %s", topic, e)

    def subscribe(self, topic: str, callback: Callable[[bytes], None]) -> None:
        """Subscribe to a topic with a callback.
        
        Args:
            topic: MQTT topic to subscribe to.
            callback: Function to call with message payload bytes.
        """
        self._callbacks[topic] = callback
        if self._client:
            self._client.subscribe(topic)

    def connect(self) -> bool:
        """Connect to the MQTT broker and start the message loop.
        
        Returns:
            True if connection succeeded, False otherwise.
        """
        try:
            self._client = mqtt.Client()
            self._client.on_message = self._on_message
            self._client.connect(self.broker, self.port, self.keepalive)
            
            # Subscribe to all registered topics
            for topic in self._callbacks:
                self._client.subscribe(topic)
            
            self._client.loop_start()
            logging.info("Connected to MQTT broker: %s:%d", self.broker, self.port)
            return True
        except (OSError, ConnectionRefusedError) as e:
            logging.error("Failed to connect to MQTT broker: %s", e)
            self._client = None
            return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None

    @property
    def connected(self) -> bool:
        """Check if connected to broker."""
        return self._client is not None
