import { useCurrentFilamentBadge } from "./useCurrentFilamentBadge";


export function CurrentFilamentBadge() {
  const { filament, filamentUsage } = useCurrentFilamentBadge();
  
  return (
    <>
      <div key={`material-${filament?.event_id}`} className="text-start badge bg-secondary col me-1" title="Filament loaded in printer">
        <span className="pe-2">{filament?.material}</span>
      </div>
      <div key={`usage-${filament?.event_id}`} className="text-start badge bg-secondary col-md-2 me-2" title="Filament usage">
        <span className="pe-2">{filamentUsage}g</span>
      </div>
    </>
  );
}