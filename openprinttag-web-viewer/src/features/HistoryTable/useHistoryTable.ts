import { useContext, useEffect, useState } from "react";
import { PaginationInfo } from "../../types";
import { MqttMessageContext } from "../../context/MqttMessageContext";

export interface EventItem {
  id: number;
  event_type: string;
  timestamp: string;
  tag_uid: string | null;
  success: boolean;
}

interface EventListResponse {
  events: EventItem[];
  total: number;
  total_pages: number;
  page: number;
  page_size: number;
}

export interface HistoryTableState {
  events: EventItem[];
  pagination: PaginationInfo | null;
  loading: boolean;
  error: string | null;
  setPage: (page: number) => void;
  toggleRow: (id: number) => void;
  isExpanded: (id: number) => boolean;
}

export function useHistoryTable(): HistoryTableState {
  const [page, setPage] = useState(1);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const mqttMessageCount = useContext(MqttMessageContext);

  const toggleRow = (id: number) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const isExpanded = (id: number) => expandedId === id;

  useEffect(() => {
    setLoading(true);
    fetch(`/events?page=${page}&page_size=10`)
      .then((res) => {  
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<EventListResponse>;
      })
      .then((data) => {
        setEvents(data.events);
        setPagination({
          total: data.total,
          total_pages: data.total_pages,
          page: data.page,
          page_size: data.page_size,
        });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [page, mqttMessageCount]);

  return { events, pagination, loading, error, setPage, toggleRow, isExpanded };
}
