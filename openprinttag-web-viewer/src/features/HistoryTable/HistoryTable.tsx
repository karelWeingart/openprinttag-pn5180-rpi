import { Pagination } from "../../components/Pagination";
import { EventRow } from "./EventRow";
import { useHistoryTable, HistoryTableState } from "./useHistoryTable";

export function HistoryTable() {
  const { events, pagination, loading, error, setPage, toggleRow, isExpanded }: HistoryTableState = useHistoryTable();
  
  if (loading) return <p>Loading events…</p>;
  if (error) return <p className="text-danger">Error: {error}</p>;

  return (
    <div>
      <Pagination tableName="history" pagination={pagination!} onPageChange={setPage} />
      <table className="table">
        <thead>
          <tr>
            <th scope="col" style={{ width: "2rem" }}></th>
            <th scope="col">Tag ID</th>
            <th scope="col">Timestamp</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        <tbody>
          {events.map((evt) => (
            <EventRow
              key={evt.id}
              event={evt}
              isExpanded={isExpanded(evt.id)}
              onToggle={() => toggleRow(evt.id)}
            />
          ))}
          {events.length === 0 && (
            <tr>
              <td colSpan={5} className="text-center">
                No events found
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}