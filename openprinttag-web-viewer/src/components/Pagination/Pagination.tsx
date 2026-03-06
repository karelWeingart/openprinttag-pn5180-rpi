import { usePagination, PaginationComponentProps } from "./usePagination";

export function Pagination({ tableName, pagination, onPageChange }: PaginationComponentProps) {
  const { pages, hasPrevious, hasNext } = usePagination(pagination);

  return (
    <nav aria-label={`Pagination for ${tableName}`}>
      <ul className="pagination mb-0 mt-3 float-end">
        <li className={`page-item ${!hasPrevious ? "disabled" : ""}`}>
          <a
            className={`page-link text-secondary`}
            href="#"
            onClick={(e) => { e.preventDefault(); if (hasPrevious) onPageChange(pagination.page - 1); }}
            style={{ border: "none", borderRadius: 0 }}
          >
            Previous
          </a>
        </li>
        {pages.map((item) => (
          <li key={item.page} className="page-item">
            <a
              className={`page-link ${item.isActive ? "text-black" : "text-secondary"}`}
              href="#"
              onClick={(e) => { e.preventDefault(); onPageChange(item.page); }}
              style={{
                border: "none",
                borderBottom: item.isActive ? "2px solid var(--bs-success)" : "none",
                borderRadius: 0,
              }}
            >
              {item.page}
            </a>
          </li>
        ))}
        <li className={`page-item ${!hasNext ? "disabled" : ""}`}>
          <a
            className={`page-link text-secondary`}
            href="#"
            onClick={(e) => { e.preventDefault(); if (hasNext) onPageChange(pagination.page + 1); }}
            style={{ border: "none", borderRadius: 0 }}
          >
            Next
          </a>
        </li>
      </ul>
    </nav>
  );
}