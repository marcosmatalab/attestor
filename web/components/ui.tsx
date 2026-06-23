import type { ButtonHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";
import styles from "./ui.module.css";

export type Tone = "neutral" | "prohibited" | "high" | "limited" | "minimal" | "ok" | "warn";

export function Card({
  title,
  action,
  children,
}: {
  title?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className={styles.card}>
      {title && (
        <div className={styles.cardHead}>
          <h2 className={styles.cardTitle}>{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`${styles.badge} ${styles[`tone_${tone}`]}`}>{children}</span>;
}

export function Spinner({ label }: { label?: string }) {
  return (
    <span
      className={styles.spinner}
      role={label ? "status" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
    />
  );
}

export function Button({
  busy,
  children,
  disabled,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { busy?: boolean }) {
  return (
    <button
      className={styles.button}
      aria-busy={busy || undefined}
      disabled={busy || disabled}
      {...rest}
    >
      {busy && <Spinner />}
      {children}
    </button>
  );
}

export type CalloutTone = "note" | "caveat" | "error" | "muted";

export function Callout({
  tone = "note",
  role,
  children,
}: {
  tone?: CalloutTone;
  role?: string;
  children: ReactNode;
}) {
  return (
    <div className={`${styles.callout} ${styles[`callout_${tone}`]}`} role={role}>
      {children}
    </div>
  );
}

export function Field({
  label,
  htmlFor,
  children,
}: {
  label: ReactNode;
  htmlFor: string;
  children: ReactNode;
}) {
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={htmlFor}>
        {label}
      </label>
      {children}
    </div>
  );
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={styles.control} {...props} />;
}

export function Fieldset({ legend, children }: { legend: ReactNode; children: ReactNode }) {
  return (
    <fieldset className={styles.fieldset}>
      <legend className={styles.legend}>{legend}</legend>
      <div className={styles.checks}>{children}</div>
    </fieldset>
  );
}

export function Checkbox({
  label,
  checked,
  onChange,
}: {
  label: ReactNode;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className={styles.check}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}

export function TableWrap({ caption, children }: { caption?: ReactNode; children: ReactNode }) {
  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        {caption && <caption className={styles.caption}>{caption}</caption>}
        {children}
      </table>
    </div>
  );
}

export const cellDiverges = styles.diverges;

export function KeyValue({ children }: { children: ReactNode }) {
  return <dl className={styles.kv}>{children}</dl>;
}

export function KV({ k, children }: { k: ReactNode; children: ReactNode }) {
  return (
    <div className={styles.kvRow}>
      <dt className={styles.kvKey}>{k}</dt>
      <dd className={styles.kvVal}>{children}</dd>
    </div>
  );
}

export function Mono({ children }: { children: ReactNode }) {
  return <span className="mono">{children}</span>;
}

export function Skeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className={styles.skeleton} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <span key={i} className={styles.skelLine} />
      ))}
    </div>
  );
}
