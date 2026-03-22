import { useState, useEffect, useRef } from "react";

/**
 * Returns `true` when no update has been signalled within `thresholdMs`.
 * Each time `lastUpdated` changes, staleness resets to `false`.
 */
export function useStale(lastUpdated: Date, timeout: number = 60_000): boolean {
  const [isStale, setIsStale] = useState(false);
  const lastUpdatedTimeRef = useRef<number | null>(null);

  useEffect(() => {
    lastUpdatedTimeRef.current = new Date(lastUpdated).getTime();
    setIsStale(false);
  }, [lastUpdated]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (lastUpdatedTimeRef.current !== null) {
        setIsStale(Date.now() - lastUpdatedTimeRef.current > timeout);
      }
    }, 1_000);

    return () => clearInterval(interval);
  }, [lastUpdated]);

  return isStale;
}
