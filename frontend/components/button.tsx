import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className = "", variant = "primary", ...props }: ButtonProps) {
  const variantClass =
    variant === "primary"
      ? "border-transparent bg-accent text-white hover:brightness-95"
      : variant === "secondary"
        ? "border-border bg-panel text-foreground hover:bg-muted"
        : "border-transparent bg-transparent hover:bg-muted";

  return (
    <button
      className={[
        "inline-flex h-9 items-center justify-center gap-2 rounded-md border px-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50",
        variantClass,
        className
      ].join(" ")}
      {...props}
    />
  );
}
