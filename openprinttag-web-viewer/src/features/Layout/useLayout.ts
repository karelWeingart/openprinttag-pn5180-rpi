import { useState } from "react";

export function useLayout() {
  const [style, setStyle] = useState("dark-mode");

  return {
    style,
    setStyle,
  };
}