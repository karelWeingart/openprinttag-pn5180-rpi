import { HealthIndicator } from "../../components/HealthIndicator/HealthIndicator";
import { useHealthIndicatorBadge } from "./useHealthIndicatorBadge";
import "./HealthIndicatorBadge.css";


export function HealthIndicatorBadge() {
  const { isStale,pn5180Status, animationKey } = useHealthIndicatorBadge();
  const bgClass = isStale ? "bg-danger" : pn5180Status === "searching_write" ? "bg-warning" : "bg-success";
  
  const helpText = isStale ? "No activity - reader may be disconnected" : 
    pn5180Status === "searching_write" 
    ? "Waiting for tag to write..." 
    : "Waiting for tag to read..."; 

  return (
    <div className={`col-md-1 badge rounded health-indicator-badge ${bgClass}`} title={helpText}>
      {!isStale && <HealthIndicator key={animationKey} color="#FFFFFF" />}
      {isStale && <i className="bi bi-x-lg text-white"></i>}
    </div>
  )
}