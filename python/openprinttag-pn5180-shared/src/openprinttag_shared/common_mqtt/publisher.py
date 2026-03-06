"""General MQTT publisher with singleton connection management."""

import logging
from threading import Lock

import paho.mqtt.client as mqtt
from openprinttag_shared.common_mqtt.config import MQTT_BROKER, MQTT_PORT

class MQTTPublisher:
    """Singleton MQTT publisher — one connection per broker:port pair.

    Use ``MQTTPublisher.get_instance(broker, port)`` to obtain the shared instance.
    Call ``connect()`` once; subsequent ``get_instance()`` calls return the same
    connected client.
    """

    _instances: dict[tuple[str, int], "MQTTPublisher"] = {}
    _lock = Lock()

    def __init__(
        self, broker: str , port: int, keepalive: int = 60
    ) -> None:
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self._client: mqtt.Client | None = None

    @classmethod
    def get_instance(cls, broker: str = MQTT_BROKER, port: int = MQTT_PORT, keepalive: int = 60) -> "MQTTPublisher":
        """Return the shared publisher for *broker*:*port*, creating it if needed."""
        _key = (broker, port)
        with cls._lock:
            if _key not in cls._instances:
                _instance: "MQTTPublisher" = cls(broker, port, keepalive)
                _instance.connect()
                cls._instances[_key] = _instance
            return cls._instances[_key]

    def connect(self) -> bool:
        """Connect to the MQTT broker and start the network loop.

        Safe to call multiple times — returns True immediately if already connected.
        """
        if self._client is not None:
            return True
        try:
            self._client = mqtt.Client()
            self._client.connect(self.broker, self.port, self.keepalive)
            self._client.loop_start()
            logging.info("MQTT publisher connected to %s:%d", self.broker, self.port)
            return True
        except (OSError, ConnectionRefusedError) as e:
            logging.error("Failed to connect to MQTT broker: %s", e)
            self._client = None
            return False

    def publish(
        self, topic: str, payload: str | bytes, retain: bool = False, qos: int = 0
    ) -> bool:
        """Publish a message to an MQTT topic.

        Args:
            topic: MQTT topic to publish to.
            payload: Message payload (string or bytes).
            retain: Whether the broker should retain the message.
            qos: Quality of service level (0, 1, or 2).

        Returns:
            True if publish succeeded, False otherwise.
        """
        if not self._client:
            logging.error("Cannot publish: not connected to MQTT broker")
            return False
        try:
            result = self._client.publish(topic, payload, retain=retain, qos=qos)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logging.error("MQTT publish failed: %s", e)
            return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None
            key = (self.broker, self.port)
            with self._lock:
                self._instances.pop(key, None)

    @property
    def connected(self) -> bool:
        """Check if connected to broker."""
        return self._client is not None
