interface TabProps {
  title: string;
  isActive: boolean;
  onClick: () => void;
}

export function Tab({ title, isActive, onClick }: TabProps) {
  return (
    <li className="nav-item">
      <a
        className={`nav-link ${isActive ? "active text-black" : "text-secondary"}`}
        aria-current={isActive ? "page" : undefined}
        href="#"
        onClick={(e) => { e.preventDefault(); onClick(); }}
        style={{
          border: "none",
          borderBottom: isActive ? "2px solid var(--bs-success)" : "2px solid transparent",
          borderRadius: 0,
        }}
      >
        {title}
      </a>
    </li>
  );
}