export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ProductCandidate = {
  title: string;
  price: number;
  url: string;
  rating?: number | null;
  review_count?: number | null;
  pros: string[];
  cons: string[];
};

export type DecisionLogEntry = {
  node: string;
  decision: string;
  reasoning: string;
  confidence?: string;
  trade_offs?: string;
};

export type SearchResult = {
  session_id: string;
  query: {
    raw_query: string;
    product_type: string;
    budget_max: number;
    must_haves: string[];
    nice_to_haves: string[];
    sites_to_search: string[];
  };
  candidates: ProductCandidate[];
  decision_log: DecisionLogEntry[];
  final_recommendation?: ProductCandidate | null;
  runner_up?: ProductCandidate | null;
  synthesis_notes?: string | null;
  confidence?: "high" | "medium" | "low" | null;
  status: string;
  error?: string | null;
};

export type SessionSummary = {
  id: string;
  query: string;
  status: string;
  recommendation?: string | null;
  confidence?: string | null;
  candidates_found: number;
  created_at: string;
};

export async function runSearch(query: string): Promise<SearchResult> {
  const response = await fetch(`${API_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Search failed with HTTP ${response.status}`);
  }

  return response.json();
}

export async function getSessions(): Promise<SessionSummary[]> {
  const response = await fetch(`${API_URL}/sessions`, { cache: "no-store" });
  if (!response.ok) {
    return [];
  }
  return response.json();
}
