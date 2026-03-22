import { HealthIndicator } from "../../components/HealthIndicator/HealthIndicator";
import { usePrinterIndicatorBadge } from "./usePrinterIndicatorBadge";

export function PrinterIndicatorBadge() {
  const { healthStatus, animationKey } = usePrinterIndicatorBadge();

  return (
    <div className={`col-md-1 badge rounded health-indicator-badge bg-secondary`} title="Printer status">
      { healthStatus === "ok" && <HealthIndicator key={animationKey} color="#FFFFFF" /> }
      { healthStatus === "error" && <i className="bi bi-x-lg text-white"></i> }
    </div>
  )
}