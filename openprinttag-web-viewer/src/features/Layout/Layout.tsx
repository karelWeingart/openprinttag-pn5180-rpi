import { ReactNode } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./Layout.css";
import { useTheme } from "../../context/ThemeContext";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { isDarkMode } = useTheme();
  return <div className={`fluid-container  ${isDarkMode ? "dark-mode" : ""}`}>{children}</div>;
}
