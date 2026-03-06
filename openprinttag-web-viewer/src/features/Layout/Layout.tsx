import { ReactNode } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./Layout.css";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return <div className="fluid-container">{children}</div>;
}
