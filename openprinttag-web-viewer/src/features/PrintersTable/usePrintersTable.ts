import { useEffect, useState } from "react";
import { PaginationInfo, PrinterDto, PrinterDbDto } from "../../types";
import { FormMode } from "../PrinterFormCard";

const defaultPaginationInfo: PaginationInfo = {
  total: 0,
  total_pages: 0,
  page: 1,
  page_size: 10,
};

const WEB_API_URL =
  process.env.REACT_APP_WEB_API_URL ?? "";

export function usePrintersTable() {
  const [pagination, setPagination] = useState<PaginationInfo>(
    defaultPaginationInfo
  );
  const [page, setPage] = useState<number>(1);
  const [formMode, setFormMode] = useState<FormMode | null>(null);
  const [selectedPrinter, setSelectedPrinter] = useState<PrinterDbDto | undefined>();
  const [printers, setPrinters] = useState<PrinterDbDto[]>([]);
  const [updateTrigger, setUpdateTrigger] = useState<boolean>(false);

  useEffect(() => {
    fetch(`/printers?page=${page}&page_size=${pagination.page_size}`)
      .then((res) => res.json())
      .then((data) => {
        setPrinters(data.printers);
        setPagination({
          total: data.total,
          total_pages: data.total_pages,
          page: data.page,
          page_size: data.page_size,
        });
      })
      .catch((err) => {
        console.error("Failed to fetch printers:", err);
      });
  }, [page, updateTrigger]);

  const handleAdd = () => {
    setSelectedPrinter(undefined);
    setFormMode('create');
  };

  const handleEdit = (printer: PrinterDbDto) => {
    setSelectedPrinter(printer);
    setFormMode('edit');
  };

  const handleView = (printer: PrinterDbDto) => {
    setSelectedPrinter(printer);
    setFormMode('view');
  };

  const handleSave = async (printer: PrinterDto) => {
    await fetch(`/printers`, 
      { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(printer) 
      })
      .then((res) => {  
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
      })
      .then(() => {
        setFormMode(null);
        setUpdateTrigger(!updateTrigger);
      });
  };

  const handleEnable = async (printerId: number) => {
    await fetch(`/printers/active/${printerId}`,
      { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: "{}"
      }).then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
      })
      .then(() => {
        setUpdateTrigger(!updateTrigger);
      });
  };

  const handleDelete = async (printerId: number) => {
    await fetch(`/printers/${printerId}`, 
      { 
        method: 'DELETE'
      }).then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
      })
      .then(() => {
        setUpdateTrigger(!updateTrigger);
      });
  };

  const handleCancel = () => {
    setFormMode(null);
    setSelectedPrinter(undefined);
  };

  return {
    pagination,
    printers,
    formMode,
    selectedPrinter,
    onPageChange: setPage,
    onAdd: handleAdd,
    onEdit: handleEdit,
    onView: handleView,
    onSave: handleSave,
    onDelete: handleDelete,
    onEnable: handleEnable,
    onCancel: handleCancel,
  };
}