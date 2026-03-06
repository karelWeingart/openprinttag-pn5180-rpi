import { PN5180StatusCard } from "../PN5180StatusCard/PN5180StatusCard";

interface NavigationProps {
  appName: string;
  version: string;
}

export function Navigation({ appName, version }: NavigationProps) {
  return (
    <nav className="mb-5 navbar navbar-expand-lg navbar-light bg-light d-flex justify-content-between pe-3 ps-3 text-secondary">
      <a className="navbar-brand border-2 border-bottom text-success" href="#">{appName}</a>
      <PN5180StatusCard />
    </nav>)
}