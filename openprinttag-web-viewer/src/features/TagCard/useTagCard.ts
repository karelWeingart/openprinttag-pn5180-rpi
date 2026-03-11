import { useState, useEffect } from "react";
import { TagData } from "../../types";

export interface TagCardState {
  tagData: TagData | null;
  loading: boolean;
  error: string | null;
}

export function useTagCard(tagUid: string | null, eventId: number | null, tag: TagData | null): TagCardState {
  const [tagData, setTagData] = useState<TagData | null>(tag);
  const [loading, setLoading] = useState(!tag);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (tag || !tagUid || !eventId) return;
    setLoading(true);
    fetch(`/tags/${tagUid}/event/${eventId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setTagData(data as TagData))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [tagUid, eventId]);

  return { tagData, loading, error };
}