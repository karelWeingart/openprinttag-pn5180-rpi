import { useEffect, useState, useRef } from "react";
import mqtt, { MqttClient } from "mqtt";

const MQTT_BROKER =
  process.env.REACT_APP_MQTT_URL ?? `ws://${window.location.hostname}:9001`;

export interface MqttConnection {
  client: MqttClient | null;
  connected: boolean;
  error: string | null;
}

/**
 * Manages the MQTT WebSocket connection lifecycle.
 * Connects on mount, disconnects on unmount.
 */
export function useMqttConnection(): MqttConnection {
  const [connected, setConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const clientRef = useRef<MqttClient | null>(null);

  useEffect(() => {
      const mqttClient = mqtt.connect(MQTT_BROKER);
      clientRef.current = mqttClient;

      mqttClient.on("connect", () => {
        setConnected(true);
        setError(null);
      });

      mqttClient.on("error", (err) => {
        setError(err.message);
        setConnected(false);
      });

      mqttClient.on("close", () => {
        setError(null);
        setConnected(false)
      });

      return () => {mqttClient.end()}
    
    
  }, []);
  
  return { client: clientRef.current, connected, error };
}
