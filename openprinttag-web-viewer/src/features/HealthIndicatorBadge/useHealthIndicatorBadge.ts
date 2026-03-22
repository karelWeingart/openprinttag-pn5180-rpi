import { LastMqttMessageContext } from "../../context/MqttMessageContext";
import { useContext, useRef, useEffect } from "react";
import { useStale } from "../../hooks/useStale";

export function useHealthIndicatorBadge() {
  const lastMessage = useContext(LastMqttMessageContext);
  const pn5180statusRef = useRef<string>("searching_read");
  const animationKeyRef = useRef<number>(0);
  const isStale = useStale(lastMessage ? lastMessage.receivedAt : new Date(0), 10_000);

  useEffect (() =>{
    if (
      lastMessage?.payload.event_type === "searching_read" ||
      lastMessage?.payload.event_type === "searching_write"
    ) {
      pn5180statusRef.current = lastMessage?.payload.event_type;
      animationKeyRef.current += 1;
    }
  }, [lastMessage]);


  return {
    isStale: isStale,
    pn5180Status: pn5180statusRef.current,
    animationKey: animationKeyRef.current,
  };
}