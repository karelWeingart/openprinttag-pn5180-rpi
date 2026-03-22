import { DivContainer } from "../../components/DivContainer/DivContainer";
import { CurrentFilamentBadge } from "../CurrentFilamentBadge/CurrentFilamentBadge";
import { HealthIndicatorBadge } from "../HealthIndicatorBadge/HealthIndicatorBadge";
import { PN5180NotificationBadge } from "../PN5180NotificationBadge/PN5180NotificationBadge";
import { PrinterIndicatorBadge } from "../PrinterIndicatorBadge/PrinterIndicatorBadge";
interface NavigationProps {
  appName: string;
  version: string;
}

export function Navigation({ appName, version }: NavigationProps) {

  return (
    <nav className="mb-5 navbar navbar-expand-lg navbar-light bg-light d-flex justify-content-between pe-3 ps-3 text-secondary">
      <a className="navbar-brand border-2 border-bottom text-success" href="#">
        {appName}        
      </a>
      <DivContainer classes="w-25">
        <DivContainer classes="row mb-1">
          <HealthIndicatorBadge />
          <PN5180NotificationBadge />
        </DivContainer>
        <DivContainer classes="row">
          <CurrentFilamentBadge />
          <PrinterIndicatorBadge />
        </DivContainer>
      </DivContainer>
    </nav>)
}