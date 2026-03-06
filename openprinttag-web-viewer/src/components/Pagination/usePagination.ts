import { PaginationInfo } from "../../types";

export interface PaginationComponentProps {
  tableName: string;
  pagination: PaginationInfo;
  onPageChange: (page: number) => void;
}

export interface PageItem {
  page: number;
  isActive: boolean;
}

export function usePagination(pagination: PaginationInfo) {
  const { page, total_pages } = pagination;

  const hasPrevious = page > 1;
  const hasNext = page < total_pages;

  const pages: PageItem[] = [];
  for (let i = 1; i <= total_pages; i++) {
    pages.push({ page: i, isActive: i === page });
  }

  return { pages, hasPrevious, hasNext };
}