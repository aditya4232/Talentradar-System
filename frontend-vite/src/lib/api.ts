/**
 * TalentRadar Backend API Service
 * Connects the hr-talent-lens frontend to the FastAPI backend
 */

const API_BASE = "http://localhost:8000/api/v1";

export type BackendCandidate = {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  profile_url: string | null;
  source: string | null;
  current_title: string | null;
  company: string | null;
  location: string | null;
  experience_years: number | null;
  skills: string[];
  summary: string | null;
  talent_score: number | null;
  freshness_score: number | null;
  last_updated: string | null;
  created_at: string | null;
};

// Fetch candidates from backend
export async function fetchCandidates(): Promise<BackendCandidate[]> {
  try {
    const res = await fetch(`${API_BASE}/candidates`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("[API] Failed to fetch candidates:", err);
    return [];
  }
}

// Upload JD PDF
export async function uploadJDFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/jd/upload`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Parse JD from text
export async function parseJDText(text: string) {
  const res = await fetch(`${API_BASE}/jd/parse-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Scrape a URL
export async function scrapeUrl(url: string) {
  const res = await fetch(`${API_BASE}/scraper/scrape-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Start scraper
export async function startScraper() {
  const res = await fetch(`${API_BASE}/scraper/run`, { method: "POST" });
  return res.json();
}

// Stop scraper
export async function stopScraper() {
  const res = await fetch(`${API_BASE}/scraper/stop`, { method: "POST" });
  return res.json();
}

// AI Consult
export async function aiConsult(query: string, candidates: any[] = []) {
  const res = await fetch(`${API_BASE}/ai/consult`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, candidates: candidates.slice(0, 15) }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
