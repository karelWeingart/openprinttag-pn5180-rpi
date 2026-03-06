interface HealthIndicatorProps {
  color: string;
}

export function HealthIndicator({ color }: HealthIndicatorProps) {
  return (
    <span
      style={{
        display: "inline-block",
        width: 12,
        height: 12,
        borderRadius: "50%",
        backgroundColor: color,
        animation: "fadeOut 1.5s ease-in-out forwards",
      }}
    >
      <style>{`
        @keyframes fadeOut {
          0% { opacity: 1; transform: scale(1); }
          100% { opacity: 0; transform: scale(0); }
        }
      `}</style>
    </span>
  );
}