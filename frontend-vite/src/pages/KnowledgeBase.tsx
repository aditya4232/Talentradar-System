import { useState, useEffect } from "react";
import { Database, FileText, TrendingUp, RefreshCw, MapPin, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

interface KnowledgeData {
  total_candidates: number;
  total_jds: number;
  avg_score: number;
  avg_experience: number;
  top_skills: [string, number][];
  top_locations: [string, number][];
  source_distribution: [string, number][];
  recent_jds: {
    id: number;
    title: string;
    company: string;
    required_skills: string[];
    domain: string | null;
    created_at: string | null;
  }[];
}

const KnowledgeBase = () => {
  const [data, setData] = useState<KnowledgeData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/knowledge`);
      setData(res.data);
    } catch {
      console.warn("Failed to load knowledge base");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Knowledge Base</h1>
          <p className="text-sm text-muted-foreground">AI-built hiring intelligence from real scraped data</p>
        </div>
        <Button className="gap-2" variant="outline" onClick={loadData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat-card">
          <Database className="w-5 h-5 text-primary mb-2" />
          <p className="text-2xl font-bold text-foreground">{data?.total_candidates ?? 0}</p>
          <p className="text-xs text-muted-foreground">Candidates in DB</p>
        </div>
        <div className="stat-card">
          <FileText className="w-5 h-5 text-primary mb-2" />
          <p className="text-2xl font-bold text-foreground">{data?.total_jds ?? 0}</p>
          <p className="text-xs text-muted-foreground">Job Descriptions</p>
        </div>
        <div className="stat-card">
          <TrendingUp className="w-5 h-5 text-primary mb-2" />
          <p className="text-2xl font-bold text-foreground">{data?.avg_score ?? 0}%</p>
          <p className="text-xs text-muted-foreground">Avg Talent Score</p>
        </div>
        <div className="stat-card">
          <Briefcase className="w-5 h-5 text-primary mb-2" />
          <p className="text-2xl font-bold text-foreground">{data?.avg_experience ?? 0} yrs</p>
          <p className="text-xs text-muted-foreground">Avg Experience</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Skills */}
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-primary" /> Top Skills in Pipeline
          </h2>
          {data?.top_skills && data.top_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {data.top_skills.map(([skill, count]) => (
                <Badge key={skill} variant="outline" className="text-xs gap-1.5 px-2.5 py-1">
                  {skill} <span className="text-muted-foreground font-mono">({count})</span>
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No data yet. Scrape candidates to populate.</p>
          )}
        </div>

        {/* Top Locations */}
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-primary" /> Top Locations
          </h2>
          {data?.top_locations && data.top_locations.length > 0 ? (
            <div className="space-y-2">
              {data.top_locations.map(([loc, count]) => (
                <div key={loc} className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">{loc}</span>
                  <Badge variant="secondary" className="text-[10px]">{count}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No data yet.</p>
          )}
        </div>

        {/* Source Distribution */}
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <Database className="w-4 h-4 text-primary" /> Source Distribution
          </h2>
          {data?.source_distribution && data.source_distribution.length > 0 ? (
            <div className="space-y-2">
              {data.source_distribution.map(([src, count]) => (
                <div key={src} className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">{src}</span>
                  <span className="text-sm font-semibold text-foreground">{count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No data yet.</p>
          )}
        </div>

        {/* Recent JDs */}
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" /> Recent Job Descriptions
          </h2>
          {data?.recent_jds && data.recent_jds.length > 0 ? (
            <div className="space-y-3">
              {data.recent_jds.map((jd) => (
                <div key={jd.id} className="p-3 rounded-lg bg-secondary/30 border border-border/30">
                  <p className="text-sm font-medium text-foreground">{jd.title}</p>
                  <p className="text-[10px] text-muted-foreground">{jd.company} {jd.domain ? `• ${jd.domain}` : ""}</p>
                  {jd.required_skills.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {jd.required_skills.slice(0, 5).map((s) => (
                        <Badge key={s} variant="secondary" className="text-[9px] px-1 py-0">{s}</Badge>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No JDs uploaded yet. Use Job Input to add one.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
