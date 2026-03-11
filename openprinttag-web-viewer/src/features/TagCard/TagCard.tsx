import { TagData } from "../../types";
import { useTagCard } from "./useTagCard";

export function TagCard({ tagUid, eventId, tag }: { tagUid?: string; eventId?: number; tag?: TagData }) {

  const { tagData, loading, error } = useTagCard(tagUid ?? null, eventId ?? null, tag ?? null);
  
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="card mb-3">
      <div className="card-header">
        <p className="w-100 mb-0">{tagData?.material_name ?? "Unknown"}
          <span className="badge rounded-pill ms-2 ps-2 pe-2" style={{ backgroundColor: tagData?.primary_color_hex ?? "transparent" }}>
            {tagData?.material_type ?? "Unknown"} - {tagData?.manufacturer ?? "Unknown"}
          </span>          
        </p>        
      </div>
      <div className="card-body">
        <p className="text-secondary fst-italic">Tag UID: {tagData?.tag_uid ?? "Unknown"}</p>
      </div>
    </div>
  );
}