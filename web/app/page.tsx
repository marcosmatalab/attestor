import Link from "next/link";
import { getDictionary } from "@/lib/i18n/dictionaries";

export default function HomePage() {
  const t = getDictionary("en");
  return (
    <main>
      <h1>{t.home.title}</h1>
      <p className="lede">{t.home.tagline}</p>
      <p className="lede">
        <strong>{t.home.deterministic}</strong> {t.home.noLlm}
      </p>
      <p>
        <Link href="/demo">
          <button type="button">{t.home.runDemo}</button>
        </Link>
      </p>
      <section className="grid" style={{ marginTop: "2rem" }}>
        {t.home.features.map((feature) => (
          <article className="card" key={feature.title}>
            <h2>{feature.title}</h2>
            <p style={{ margin: 0, color: "var(--muted)", fontSize: "0.9rem" }}>{feature.body}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
