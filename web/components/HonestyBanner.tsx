import styles from "./chrome.module.css";

/** A persistent, prominent honesty notice. Never hidden by the redesign. */
export function HonestyBanner() {
  return (
    <div className={styles.banner} role="note">
      <div className="container">
        <strong>Portfolio demonstration — not legal advice, not a compliance product.</strong>{" "}
        Every figure, date, checksum, and verdict below comes from a deterministic engine; the UI
        only displays it. No system is &quot;compliant&quot; or &quot;certified&quot; by this tool.
      </div>
    </div>
  );
}
