import { useState, useEffect } from "react";
import { PrinterDto } from "../../types";

export type FormMode = 'create' | 'edit' | 'view';

export interface UsePrinterFormCardProps {
  mode: FormMode;
  printer?: PrinterDto;
  onSave?: (printer: PrinterDto) => void;
  onCancel?: () => void;
}

const emptyPrinter: PrinterDto = {
  name: '',
  status: null,
  ip: null,
  token: null,
};

export function usePrinterFormCard({ mode, printer, onSave, onCancel }: UsePrinterFormCardProps) {
  const [formData, setFormData] = useState<PrinterDto>(printer ?? emptyPrinter);

  useEffect(() => {
    setFormData(printer ?? emptyPrinter);
  }, [printer]);

  const isReadOnly = mode === 'view';
  const title = mode === 'create' ? 'Add Printer' : mode === 'edit' ? 'Edit Printer' : 'Printer Details';

  const handleChange = (field: keyof PrinterDto, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value || null }));
  };

  const handleSave = () => {
    if (onSave && formData.name.trim()) {
      onSave(formData);
    }
  };

  const handleCancel = () => {
    onCancel?.();
  };

  const isValid = formData.name.trim().length > 0;

  return {
    formData,
    isReadOnly,
    title,
    isValid,
    handleChange,
    handleSave,
    handleCancel,
  };
}
