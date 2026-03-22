import { useEffect, useState } from "react";

const WEB_API_URL =
  process.env.REACT_APP_WEB_API_URL ?? "";

export function usePrinterIndicatorBadge() {
  const [healthStatus, setHealthStatus] = useState<"ok" |"error">("ok");
  const [animationKey, setAnimationKey] = useState<number>(0);

  useEffect(() => {
    const timer = setInterval(() => {
      fetch(`/printers/active/health`)
        .then(res => res.json())
        .then(data => {
          setHealthStatus(data.status);
          setAnimationKey(prev => prev + 1);
        })
        .catch(err => {
          console.error("Error fetching printer health:", err);
          setHealthStatus("error");
          setAnimationKey(prev => prev + 1);
        });
    }, 5000);

    return () => {
      clearInterval(timer);
    }
  }, [])
  
  return {
    healthStatus,
    animationKey
  }
}