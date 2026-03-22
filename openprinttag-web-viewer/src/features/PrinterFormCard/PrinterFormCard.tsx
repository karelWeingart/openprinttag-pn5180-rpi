import { PrinterDto } from "../../types";
import { FormMode, usePrinterFormCard } from "./usePrinterFormCard";

export interface PrinterFormCardProps {
  mode: FormMode;
  printer?: PrinterDto;
  onSave?: (printer: PrinterDto) => void;
  onCancel?: () => void;
  show: boolean;
}

export function PrinterFormCard({ mode, printer, onSave, onCancel, show }: PrinterFormCardProps) {
  const {
    formData,
    isReadOnly,
    title,
    isValid,
    handleChange,
    handleSave,
    handleCancel,
  } = usePrinterFormCard({ mode, printer, onSave, onCancel });

  if (!show) return null;

  return (
    <>
      <div className="modal-backdrop fade show" onClick={handleCancel}></div>
      <div className="modal fade show d-block" tabIndex={-1} role="dialog">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{title}</h5>
              <button type="button" className="btn-close" aria-label="Close" onClick={handleCancel}></button>
            </div>
            <div className="modal-body">
              <div className="mb-3">
                <label htmlFor="printerName" className="form-label">Name *</label>
                <input
                  type="text"
                  className="form-control form-control-sm"
                  id="printerName"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  disabled={isReadOnly}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="printerIp" className="form-label">IP Address</label>
                <input
                  type="text"
                  className="form-control form-control-sm"
                  id="printerIp"
                  value={formData.ip ?? ''}
                  onChange={(e) => handleChange('ip', e.target.value)}
                  disabled={isReadOnly}
                  placeholder="e.g. 192.168.1.100"
                />
              </div>
              <div className="mb-3">
                <label htmlFor="printerToken" className="form-label">API Token</label>
                <input
                  type="password"
                  className="form-control form-control-sm"
                  id="printerToken"
                  value={formData.token ?? ''}
                  onChange={(e) => handleChange('token', e.target.value)}
                  disabled={isReadOnly}
                />
              </div>
              { isReadOnly && <div className="mb-3">
                <label htmlFor="printerStatus" className="form-label">Status</label>
                <input
                  type="text"
                  className="form-control form-control-sm"
                  id="printerStatus"
                  value={formData.status ?? ''}
                  disabled={isReadOnly}
                />
              </div>}
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleCancel}
              >
                Cancel
              </button>
              {!isReadOnly && (
                <button
                  type="button"
                  className="btn btn-success btn-sm"
                  onClick={handleSave}
                  disabled={!isValid}
                >
                  {mode === 'create' ? 'Create' : 'Save'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
