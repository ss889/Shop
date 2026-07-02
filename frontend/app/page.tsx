"use client";

import { ExternalLink, History, Search, ShieldCheck } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { DecisionLogEntry, ProductCandidate, SearchResult, SessionSummary, getSessions, runSearch } from "../lib/api";

const examples = [
  "wireless earbuds under $100 with good bass",
  "noise-cancelling headphones under $200",
  "4k monitor under $350 for coding",
];

const statusSteps = [
  "Planning your search...",
  "Browsing BestBuy and Walmart...",
  "Extracting product data...",
  "Reviewing against requirements...",
  "Ranking candidates...",
  "Synthesizing recommendation...",
];

function confidenceClass(confidence?: string | null) {
  if (confidence === "high") return "badge badgeHigh";
  if (confidence === "medium") return "badge badgeMedium";
  return "badge badgeLow";
}

function ProductCard({
  product,
  label,
  notes,
  confidence,
}: {
  product: ProductCandidate;
  label: string;
  notes?: string | null;
  confidence?: string | null;
}) {
  const site = useMemo(() => {
    try {
      return new URL(product.url).hostname.replace("www.", "");
    } catch {
      return "product page";
    }
  }, [product.url]);

  return (
    <article className="productCard">
      <div className="productHeader">
        <span className="eyebrow">{label}</span>
        {confidence ? <span className={confidenceClass(confidence)}>{confidence}</span> : null}
      </div>
      <h2>{product.title}</h2>
      <div className="metrics">
        <span>${product.price.toFixed(2)}</span>
        <span>{product.rating ? `${product.rating}/5` : "rating unavailable"}</span>
        <span>{product.review_count ? `${product.review_count} reviews` : "reviews unavailable"}</span>
      </div>
      {notes ? <p>{notes}</p> : null}
      <div className="chips">
        {product.pros.slice(0, 3).map((pro) => (
          <span key={pro}>{pro}</span>
        ))}
      </div>
      <a href={product.url} target="_blank" rel="noreferrer" className="linkButton">
        View on {site}
        <ExternalLink size={16} />
      </a>
    </article>
  );
}

function DecisionLog({ entries }: { entries: DecisionLogEntry[] }) {
  return (
    <div className="logList">
      {entries.map((entry, index) => (
        <div className="logItem" key={`${entry.node}-${index}`}>
          <span className="nodeBadge">{entry.node}</span>
          <div>
            <strong>{entry.decision}</strong>
            <p>{entry.reasoning}</p>
            {entry.trade_offs ? <p className="muted">Trade-offs: {entry.trade_offs}</p> : null}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  const [query, setQuery] = useState(examples[0]);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLog, setShowLog] = useState(true);
  const [step, setStep] = useState(0);

  useEffect(() => {
    getSessions().then(setSessions);
  }, []);

  useEffect(() => {
    if (!loading) return;
    const timer = window.setInterval(() => {
      setStep((current) => Math.min(current + 1, statusSteps.length - 1));
    }, 2000);
    return () => window.clearInterval(timer);
  }, [loading]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setStep(0);

    try {
      const nextResult = await runSearch(query);
      setResult(nextResult);
      if (nextResult.error) setError(nextResult.error);
      setSessions(await getSessions());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="appShell">
      <aside className="leftPanel">
        <div className="brand">
          <ShieldCheck size={28} />
          <div>
            <h1>Shopping Agent</h1>
            <p>Multi-agent product search with enforced autonomy boundaries</p>
          </div>
        </div>

        <form onSubmit={submit} className="searchForm">
          <label htmlFor="query">Product search</label>
          <textarea
            id="query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            rows={4}
          />
          <button disabled={loading || !query.trim()} type="submit">
            <Search size={18} />
            {loading ? "Searching" : "Search"}
          </button>
        </form>

        <div className="exampleList">
          {examples.map((example) => (
            <button key={example} type="button" onClick={() => setQuery(example)}>
              {example}
            </button>
          ))}
        </div>

        <section className="sessions">
          <div className="sectionTitle">
            <History size={18} />
            <h2>Recent Sessions</h2>
          </div>
          {sessions.length === 0 ? <p className="muted">No sessions yet.</p> : null}
          {sessions.map((session) => (
            <div className="sessionRow" key={session.id}>
              <strong>{session.query}</strong>
              <span>{session.status}{session.recommendation ? ` - ${session.recommendation}` : ""}</span>
            </div>
          ))}
        </section>
      </aside>

      <section className="rightPanel">
        {loading ? (
          <div className="statePanel">
            <span className="spinner" />
            <h2>{statusSteps[step]}</h2>
            <p>Each node writes to the decision log before the graph moves forward.</p>
          </div>
        ) : null}

        {!loading && error ? (
          <div className="statePanel errorPanel">
            <h2>{error}</h2>
            <p>The agent stops honestly when no candidates survive the filters.</p>
          </div>
        ) : null}

        {!loading && !error && !result ? (
          <div className="statePanel">
            <h2>Ready to compare products</h2>
            <p>Run a search to see recommendations and the node-by-node decision trail.</p>
          </div>
        ) : null}

        {!loading && result?.final_recommendation ? (
          <div className="results">
            <ProductCard
              product={result.final_recommendation}
              label="Recommendation"
              notes={result.synthesis_notes}
              confidence={result.confidence}
            />
            {result.runner_up ? (
              <ProductCard product={result.runner_up} label="Runner-up" />
            ) : null}
            <button className="toggleLog" type="button" onClick={() => setShowLog(!showLog)}>
              {showLog ? "Hide Decision Log" : "View Decision Log"}
            </button>
            {showLog ? <DecisionLog entries={result.decision_log} /> : null}
          </div>
        ) : null}
      </section>
    </main>
  );
}
