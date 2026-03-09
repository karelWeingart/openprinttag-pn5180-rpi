import { TagData } from "../../types";
import { useTagCard } from "./useTagCard";

export function TagCard({ tagUid, eventId, tag }: { tagUid?: string; eventId?: number; tag?: TagData }) {

  const { tagData, loading, error } = useTagCard(tagUid ?? null, eventId ?? null, tag ?? null);
  
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="card-title">Name: {tagData?.material_name ?? "Unknown"}</h5>
        <p className="card-text mb-1">Material: {tagData?.material_type ?? "Unknown"}</p>
        <p className="card-text mb-1">Manufacturer: {tagData?.manufacturer ?? "Unknown"}</p>
        <p className="card-text mb-2">Color: <span className="badge rounded-pill ms-1 ps-2 pe-2" style={{ backgroundColor: tagData?.primary_color_hex ?? "transparent" }}>{tagData?.primary_color_hex ?? "Unknown"}</span></p>
      </div>
    </div>
  );
}