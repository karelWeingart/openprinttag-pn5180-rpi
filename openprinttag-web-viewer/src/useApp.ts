import { useEffect, useState } from "react";
import { useMqttConnection, useMqttMessages } from "./hooks/useMqtt";
import { Pn5180Event } from "./context/MqttMessageContext";
import { MqttMessage } from "./hooks/useMqttMessages";

export interface AppState {
  msgCount: number;
  lastMessage: MqttMessage<Pn5180Event> | null;
}

export function useApp(): AppState {
  const connection = useMqttConnection();
  const { lastMessage } = useMqttMessages<Pn5180Event>(connection, "openprinttag/webapi/events");
  const [msgCount, setMsgCount] = useState(0);

  useEffect(() => {
    if (lastMessage?.payload.event_type !== "searching_read" && lastMessage?.payload.event_type !== "searching_write") {
      setMsgCount((c) => c + 1);
    }
  }, [lastMessage]);

  return { msgCount, lastMessage };
}
