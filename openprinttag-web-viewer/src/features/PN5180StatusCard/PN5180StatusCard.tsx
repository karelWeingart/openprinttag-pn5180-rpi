import { HealthIndicator } from "../../components/HealthIndicator/HealthIndicator";
import { usePN5180Status } from "./usePN5180Status";

export function PN5180StatusCard() {
  const { isStale, animationKey, healthColor, lastReadWriteMessage } = usePN5180Status();
  
  return (
    <div className={`text-start w-25 badge ${isStale ? 'bg-danger' : 'bg-success'}`}>
        <span className="pe-2"><HealthIndicator key={animationKey} color={healthColor} /></span>
        {lastReadWriteMessage && <span className="pe-2 text-white">{lastReadWriteMessage}</span>}
    </div>
  );
}