import { createContext } from "react";
import { MqttMessage } from "../hooks/useMqttMessages";

export interface Pn5180Event {
  event_type: string;
  tag_uid?: string;
  error?: string;
  material_type?: string;
  manufacturer?: string;
  color?: string;
  name?: string;
}

export const MqttMessageContext = createContext<number>(0);
export const LastMqttMessageContext = createContext<MqttMessage<Pn5180Event> | null>(null);