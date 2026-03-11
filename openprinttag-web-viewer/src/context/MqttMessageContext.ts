import { createContext } from "react";
import { MqttMessage } from "../hooks/useMqttMessages";

export interface Pn5180Event {
  event_type: string;
  tag?: TagDto;
  error?: ErrorDto;

}

interface ErrorDto {
  error: string;
  tag_uid?: string;
}

interface TagDto {
  tag_uid: string;
  material_type?: string;
  manufacturer?: string;
  primary_color_hex?: string;
  material_name?: string;
}

export const MqttMessageContext = createContext<number>(0);
export const LastMqttMessageContext = createContext<MqttMessage<Pn5180Event> | null>(null);