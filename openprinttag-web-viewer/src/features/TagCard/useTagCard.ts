import { useState, useEffect } from "react";

export interface TagData {
  tag_uid: string;
  material_type: string | null;
  name: string | null;
  manufacturer: string | null;
  color: string | null;
}

export interface TagCardState {
  tagData: TagData | null;
  loading: boolean;
  error: string | null;
}

export function useTagCard(tagUid: string): TagCardState {
  const [tagData, setTagData] = useState<TagData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    setLoading(true);
    fetch(`/tags/${tagUid}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setTagData(data as TagData))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [tagUid]);

  return { tagData, loading, error };
}