import { useContext, useRef } from "react";
import { useStale } from "../../hooks/useStale";
import { LastMqttMessageContext } from "../../context/MqttMessageContext";

export function usePN5180NotificationBadge() {
  const lastMessage = useContext(LastMqttMessageContext);
  const messageAnimationKeyRef = useRef(0);
  const lastReadWriteMessageRef = useRef<string | null>(null);

  if (lastMessage?.payload.event_type === "success_read") {
    const newMessage = lastMessage.payload.tag?.material_name ? lastMessage.payload.tag.material_name + " Filament" : "Unknown Filament";
    if (newMessage !== lastReadWriteMessageRef.current) {
      lastReadWriteMessageRef.current = newMessage;
      messageAnimationKeyRef.current += 1;
    }
  }

  if (lastMessage?.payload.event_type === "success_write") {
    if (lastReadWriteMessageRef.current !== ".bin file written!") {
      lastReadWriteMessageRef.current = ".bin file written!";
      messageAnimationKeyRef.current += 1;
    }
  }

  if (lastMessage?.payload.event_type === "error") {
    const errorMsg = lastMessage.payload.error?.error ?? "Unknown error";
    if (lastReadWriteMessageRef.current !== errorMsg) {
      lastReadWriteMessageRef.current = errorMsg;
      messageAnimationKeyRef.current += 1;
    }
  }

  return { 
    messageAnimationKey: messageAnimationKeyRef.current,
    lastReadWriteMessage: lastReadWriteMessageRef.current 
  };
}
