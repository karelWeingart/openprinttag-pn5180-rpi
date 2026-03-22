import { useEffect,  useState } from "react";

const WEB_API_URL =
  process.env.REACT_APP_WEB_API_URL ?? "";


export interface CurrentFilamentBadgeData {
  material: string;
  manufacturer?: string;
  event_id: number;
}

export interface FilamentUsageData {
  used_weight_g: number;
}

export function useCurrentFilamentBadge() {

  const [filament, setFilament] = useState<CurrentFilamentBadgeData | null>(null);
  const [filamentUsage, setFilamentUsage] = useState<number | null>(null);

  useEffect(() => {
    const fetchFilament = () => {
      fetch(`/events/latest/success_read`)
        .then(response => response.json())
        .then(data => {
          if (data && data.tag_data) {
            console.log("Fetched filament data:", data.tag_data);
            const tagData = JSON.parse(data.tag_data);
            setFilament({
              material: `${tagData.material_type ?? ""} ${tagData.material_name ?? ""}`.trim(),
              manufacturer: tagData.manufacturer,
              event_id: data.id,
            });
          }
        })
        .catch(error => {
          console.error("Error fetching filament data:", error);
        });
    };

    fetchFilament();
    const interval = setInterval(fetchFilament, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!filament) return;
    
    const fetchUsage = () => {
      fetch(`/events/${filament.event_id}/filament`)
        .then(response => response.json())
        .then(data => {
          if (data && typeof data.filament_usage === "number") {
            setFilamentUsage(Math.round(data.filament_usage));
          }
        })
        .catch(error => {
          console.error("Error fetching filament usage data:", error);
        });
    };

    fetchUsage();
    const interval = setInterval(fetchUsage, 5000);

    return () => clearInterval(interval);
  }, [filament?.event_id]);


  return { filament, filamentUsage };
}