import { HealthIndicator } from "../../components/HealthIndicator/HealthIndicator";
import { usePN5180NotificationBadge } from "./usePN5180NotificationBadge";
import "./PN5180NotificationBadge.css";

export function PN5180NotificationBadge() {
  const { messageAnimationKey, lastReadWriteMessage } = usePN5180NotificationBadge();
  
  return (
    <div 
      key={messageAnimationKey}
      className="col rounded badge border pn5180-notification-badge bg-success">
      <span className="ms-2 ps-2">{lastReadWriteMessage}</span>        
    </div>
  );
}