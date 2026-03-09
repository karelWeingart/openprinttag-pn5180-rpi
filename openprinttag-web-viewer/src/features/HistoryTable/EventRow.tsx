import { TagCard } from "../TagCard";
import { TagData } from "../../types";
import { EventItem } from "./useHistoryTable";

interface EventRowProps {
  event: EventItem;
  isExpanded: boolean;
  onToggle: () => void;
}

export function EventRow({ event, isExpanded, onToggle }: EventRowProps) {
  return (
    <>
      <tr className={`${event.success ? "table-success" : "table-danger"}`}onClick={onToggle} style={{ cursor: "pointer" }}>
        <td><i className={`bi ${isExpanded ? "bi-chevron-down" : "bi-chevron-right"}`} /></td>
        <td>{event.tag_uid ?? "—"}</td>
        <td>{event.timestamp}</td>
        <td>
          {event.event_type == "success_write" && <i className="fs-5 text-dark bi bi-pencil-fill text-success"></i>}
          {event.event_type == "success_read" && <i className="fs-5 text-dark bi bi-book-fill text-success"></i>}
          {event.event_type == "error" && <i className="fs-5 text-dark bi bi-exclamation-triangle-fill text-danger"></i>}
        </td>  
      </tr>
      {isExpanded && (
        <tr className="table-secondary">
          <td></td>
          <td colSpan={1}>
            {event.tag_data ? (
              <span>
                <TagCard tag={JSON.parse(event.tag_data) as TagData} />
              </span>
            ) : (
              <em>No tag associated with this event</em>
            )}
          </td>
          <td colSpan={2}></td>
        </tr>
      )}
    </>
  );
}
