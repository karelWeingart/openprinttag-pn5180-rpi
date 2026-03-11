import { useContext, useRef } from "react";
import { useStale } from "../../hooks/useStale";
import { LastMqttMessageContext } from "../../context/MqttMessageContext";

export function usePN5180Status() {
  const lastMessage = useContext(LastMqttMessageContext);
  const isStale = useStale(lastMessage ? lastMessage.receivedAt : new Date(0));
  const animationKeyRef = useRef(0);
  const lastReadWriteMessageRef = useRef<string | null>(null);

  let healthColor = "#FF0000"; // Default to red for stale or unknown state

  if (lastMessage?.payload.event_type === "searching_read") {
    healthColor = "#FFFFFF"; // White for searching
    animationKeyRef.current += 1; // Trigger animation on searching_read
  } else if (lastMessage?.payload.event_type === "searching_write" || lastMessage?.payload.event_type === "success_written") {
    healthColor = "#FFFFFF"; // White for writing or success
    animationKeyRef.current += 1; // Trigger animation on searching_write or success_written
  }

  if (lastMessage?.payload.event_type === "success_read") {
    lastReadWriteMessageRef.current = lastMessage.payload.tag?.material_name ? lastMessage.payload.tag.material_name + " Filament" : "Unknown Filament";
  }

  if (lastMessage?.payload.event_type === "success_write") {
    lastReadWriteMessageRef.current = ".bin file written!";
  }

  if (lastMessage?.payload.event_type === "error") {
    lastReadWriteMessageRef.current = lastMessage.payload.error?.error ?? "Unknown error";
  }

  return { isStale, animationKey: animationKeyRef.current, healthColor, lastReadWriteMessage: lastReadWriteMessageRef.current };
}
