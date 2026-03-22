export function DivContainer({ children, classes }: { children: React.ReactNode, classes?: string }) {
  return (
    <div className={classes}>
      {children}
    </div>
  );
}