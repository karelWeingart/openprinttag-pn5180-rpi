import { useEffect, useState } from "react";
import { MqttConnection } from "./useMqttConnection";

export interface MqttMessage<T> {
  topic: string;
  payload: T;
  receivedAt: Date;
}

export interface UseMqttMessagesResult<T> {
  /** The most recent message received */
  lastMessage: MqttMessage<T> | null;
}

function parsePayload<T>(raw: Buffer): T {
  try {
    return JSON.parse(raw.toString()) as T;
  } catch {
    return raw.toString() as unknown as T;
  }
}

/**
 * Subscribes to an MQTT topic using an existing connection and
 * returns parsed, strongly-typed messages.
 *
 * @param connection  The connection from ``useMqttConnection()``
 * @param topic       MQTT topic to subscribe to
 */
export function useMqttMessages<T>(
  connection: MqttConnection,
  topic: string,
): UseMqttMessagesResult<T> {
  const [lastMessage, setLastMessage] = useState<MqttMessage<T> | null>(null);

  const { client } = connection;

  useEffect(() => {
    const handler = (_topic: string, payload: Buffer) => {
      if (_topic !== topic) return;

      const msg: MqttMessage<T> = {
        topic: _topic,
        payload: parsePayload(payload),
        receivedAt: new Date(),
      };
      setLastMessage(msg);
    };

    if (client) {
      client.subscribe(topic);
      client.on("message", handler);
    }

  return () => {
    if (client) {
      client.unsubscribe(topic);
      client.removeListener("message", handler);
    }
  };
  
  }, [client, topic]);

  return { lastMessage };
}
