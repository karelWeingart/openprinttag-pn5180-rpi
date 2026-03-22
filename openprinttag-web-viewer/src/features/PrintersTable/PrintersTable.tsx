import { Pagination } from "../../components/Pagination";
import { PrinterFormCard } from "../PrinterFormCard";
import { usePrintersTable } from "./usePrintersTable";

export function PrintersTable() {
  const {
    pagination,
    printers,
    formMode,
    selectedPrinter,
    onPageChange,
    onAdd,
    onEdit,
    onView,
    onSave,
    onCancel,
    onDelete,
    onEnable,
  } = usePrintersTable();

  return (
    <div>
      <div className="d-flex justify-content-between align-items-end mt-3">
        <button
          type="button"
          className="btn btn-sm lh-base btn-outline-success"
          onClick={onAdd}
        >
          Add Printer
        </button>
        <Pagination tableName="Printers" pagination={pagination} onPageChange={onPageChange} />
      </div>

      <PrinterFormCard
        mode={formMode ?? 'create'}
        printer={selectedPrinter}
        onSave={onSave}
        onCancel={onCancel}
        show={formMode !== null}
      />

      <table className="table mt-3">
        <thead>
          <tr>
            <th>Name</th>
            <th>IP</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {printers.length === 0 && (
            <tr>
              <td colSpan={4} className="text-muted text-center">No printers configured</td>
            </tr>
          )}
          {printers.map((printer) => (
            <tr key={printer.id}>
              <td>{printer.name}</td>
              <td>{printer.ip ?? '-'}</td>
              <td>{printer.status ?? '-'}</td>
              <td>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary me-1"
                  onClick={() => onView(printer)}
                >
                  View
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-primary me-1"
                  onClick={() => onEdit(printer)}
                >
                  Edit
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-danger me-1"
                  onClick={() => onDelete(printer.id)}
                >
                  Delete
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-success me-1"
                  onClick={() => onEnable(printer.id)}
                >
                  Enable
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}