import { useState, useMemo, useCallback, useEffect } from "react";
import { Candidate, fetchCandidates, startScraper, getScraperStatus } from "@/api/candidates";
import CandidateTable from "@/components/CandidateTable";
import CandidateDetailModal from "@/components/CandidateDetailModal";
import FilterPanel, { Filters, defaultFilters } from "@/components/FilterPanel";
import ExportButtons from "@/components/ExportButtons";
import AgentStatusBar from "@/components/AgentStatusBar";
import AIRecommendations from "@/components/AIRecommendations";
import RadarInsights from "@/components/RadarInsights";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Zap, Users, Search, Radar, ArrowUpDown, RefreshCw } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

const TalentRadar = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"talentScore" | "experience" | "name">("talentScore");

  useEffect(() => {
    loadCandidates();
    checkStatus();
    const interval = setInterval(() => {
      checkStatus();
      // Reload candidates while scraping is active
      if (isRunning) loadCandidates();
    }, 5000);
    return () => clearInterval(interval);
  }, [isRunning]);

  const loadCandidates = async () => {
    try {
      const data = await fetchCandidates();
      setCandidates(data);
    } catch {
      console.warn("Failed to fetch candidates");
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    try {
      const status = await getScraperStatus();
      setIsRunning(status.active);
    } catch {
      // ignore
    }
  };

  const filtered = useMemo(() => {
    return candidates
      .filter((c) => (c.talent_score || 0) >= filters.minScore)
      .filter((c) => (c.experience_years || 0) >= filters.minExp && (c.experience_years || 0) <= filters.maxExp)
      .filter((c) => filters.location === "all" || (c.location || "").includes(filters.location))
      .filter((c) => filters.source === "all" || c.source === filters.source)
      .filter((c) => filters.skills.length === 0 || filters.skills.some((s) => (c.skills || []).includes(s)))
      .filter((c) => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
          c.name.toLowerCase().includes(q) ||
          (c.current_title || "").toLowerCase().includes(q) ||
          (c.skills || []).some((s) => s.toLowerCase().includes(q))
        );
      })
      .sort((a, b) => {
        if (sortBy === "talentScore") return (b.talent_score || 0) - (a.talent_score || 0);
        if (sortBy === "experience") return (b.experience_years || 0) - (a.experience_years || 0);
        return a.name.localeCompare(b.name);
      });
  }, [candidates, filters, search, sortBy]);

  const handleStartScan = async () => {
    try {
      setIsRunning(true);
      await startScraper();
      toast.success("Scraping agents activated!");
    } catch {
      toast.error("Failed to start scraper");
      setIsRunning(false);
    }
  };

  const handleComplete = useCallback(() => {
    setIsRunning(false);
    loadCandidates();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/15 flex items-center justify-center">
            <Radar className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Talent Radar</h1>
            <p className="text-sm text-muted-foreground">AI-powered candidate discovery & ranking</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" className="gap-2" onClick={loadCandidates}>
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <ExportButtons candidates={filtered} />
          <Button className="gap-2" onClick={handleStartScan} disabled={isRunning}>
            <Zap className="w-4 h-4" /> {isRunning ? "Scanning..." : "Start Scan"}
          </Button>
        </div>
      </div>

      {/* Agent Status */}
      <AgentStatusBar isRunning={isRunning} onComplete={handleComplete} />

      {/* AI Recommendations */}
      {filtered.length >= 3 && (
        <AIRecommendations candidates={filtered} onView={setSelectedCandidate} />
      )}

      {/* Insights */}
      {filtered.length > 0 && <RadarInsights candidates={filtered} />}

      {/* Filters */}
      <FilterPanel filters={filters} onChange={setFilters} />

      {/* Search & Sort bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Quick search candidates..."
            className="pl-9 h-9 text-sm bg-card"
          />
        </div>
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-3.5 h-3.5 text-muted-foreground" />
          <Select value={sortBy} onValueChange={(v) => setSortBy(v as typeof sortBy)}>
            <SelectTrigger className="h-9 text-xs w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="talentScore">Talent Score</SelectItem>
              <SelectItem value="experience">Experience</SelectItem>
              <SelectItem value="name">Name (A-Z)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Users className="w-4 h-4" />
          <span>{filtered.length} results</span>
          {(search || filters.minScore > 0) && <Badge variant="outline" className="text-[10px]">filtered</Badge>}
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="glass-card p-12 text-center">
          <RefreshCw className="w-8 h-8 text-muted-foreground mx-auto mb-3 animate-spin" />
          <p className="text-sm text-muted-foreground">Loading candidates...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Radar className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-50" />
          <p className="text-sm text-muted-foreground">
            {candidates.length === 0
              ? "No candidates yet. Start a scan to discover talent."
              : "No candidates match your criteria. Try adjusting filters."}
          </p>
        </div>
      ) : (
        <CandidateTable candidates={filtered} onViewCandidate={setSelectedCandidate} />
      )}

      <CandidateDetailModal
        candidate={selectedCandidate}
        open={!!selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
      />
    </div>
  );
};

export default TalentRadar;
