import { useState, useMemo, useEffect } from "react";
import { Candidate, fetchCandidates } from "@/api/candidates";
import CandidateCard from "@/components/CandidateCard";
import CandidateDetailModal from "@/components/CandidateDetailModal";
import ExportButtons from "@/components/ExportButtons";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Users, LayoutGrid, List, Star, SlidersHorizontal, Play, Square, Timer, RefreshCw, Trash2 } from "lucide-react";
import CandidateTable from "@/components/CandidateTable";
import { startScraper, stopScraper, getScraperStatus, resetDatabase, ScraperStatus } from "@/api/candidates";
import { toast } from "sonner";
import ScraperMissionControl from "@/components/ScraperMissionControl";
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription, 
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle, 
  AlertDialogTrigger 
} from "@/components/ui/alert-dialog";

const Candidates = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"matchScore" | "experience" | "name">("matchScore");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [shortlisted, setShortlisted] = useState<Set<number>>(new Set());
  const [showShortlistedOnly, setShowShortlistedOnly] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [scraperStatus, setScraperStatus] = useState<ScraperStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    checkScraperStatus();
    const interval = setInterval(checkScraperStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchCandidates();
      setCandidates(data);
    } catch (e) {
      toast.error("Failed to load candidates");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await resetDatabase();
      toast.success("Database reset successfully");
      loadData();
    } catch (e) {
      toast.error("Failed to reset database");
    }
  };

  const checkScraperStatus = async () => {
    try {
      const status = await getScraperStatus();
      setScraperStatus(status);
      const wasScraping = isScraping;
      setIsScraping(status.active);
      
      // Auto-reload data if candidates count changed
      if (status.active && wasScraping && candidates.length < (status.candidates_found || 0)) {
         const data = await fetchCandidates();
         setCandidates(data);
      }
    } catch (e) {
      console.warn("Failed to check status");
    }
  };

  const toggleShortlist = (id: number) => {
    setShortlisted((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const filtered = useMemo(() => {
    let results = candidates.filter((c) => {
      const q = search.toLowerCase();
      const searchable = [
        c.name,
        c.current_title,
        c.company,
        c.location,
        ...(c.skills || [])
      ].join(" ").toLowerCase();
      return searchable.includes(q);
    });

    if (showShortlistedOnly) {
      results = results.filter((c) => shortlisted.has(c.id));
    }

    results.sort((a, b) => {
      if (sortBy === "matchScore") return (b.talent_score || 0) - (a.talent_score || 0);
      if (sortBy === "experience") return (b.experience_years || 0) - (a.experience_years || 0);
      return a.name.localeCompare(b.name);
    });

    return results;
  }, [candidates, search, sortBy, showShortlistedOnly, shortlisted]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-foreground tracking-tight">Talent Sourcing Intelligence</h1>
          <p className="text-sm text-muted-foreground font-medium">
            {candidates.length} profiles in radar • {shortlisted.size} expert shortlisted
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button size="sm" variant="outline" className="h-10 px-4 text-muted-foreground hover:text-destructive border-border/50 bg-white/50 shadow-sm transition-all active:scale-95 group">
                <Trash2 className="w-4 h-4 mr-2 group-hover:animate-bounce" /> Reset DB
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Wipe Talent Explorer Database?</AlertDialogTitle>
                <AlertDialogDescription className="text-sm">
                  This will permanently delete all scraped candidates. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleReset} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                  Reset Explorer
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>

          <Button size="sm" variant="outline" className="h-10 w-10 p-0 border-border/50 bg-white/50 shadow-sm" onClick={loadData}>
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
          <ExportButtons candidates={filtered} />
        </div>
      </div>

      <ScraperMissionControl />

      {/* Controls */}
      <div className="glass-card p-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, role, company, skill, city..."
              className="pl-9 h-9 text-sm bg-secondary/50"
            />
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-3.5 h-3.5 text-muted-foreground" />
            <Select value={sortBy} onValueChange={(v) => setSortBy(v as typeof sortBy)}>
              <SelectTrigger className="h-9 text-xs w-[140px] bg-secondary/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="matchScore">Match Score</SelectItem>
                <SelectItem value="experience">Experience</SelectItem>
                <SelectItem value="name">Name (A-Z)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Shortlisted filter */}
          <Button
            variant={showShortlistedOnly ? "default" : "outline"}
            size="sm"
            className="h-9 gap-1.5 text-xs"
            onClick={() => setShowShortlistedOnly(!showShortlistedOnly)}
          >
            <Star className={`w-3.5 h-3.5 ${showShortlistedOnly ? "fill-primary-foreground" : ""}`} />
            Shortlisted ({shortlisted.size})
          </Button>

          {/* View toggle */}
          <div className="flex items-center border border-border rounded-md">
            <Button
              variant="ghost"
              size="icon"
              className={`h-9 w-9 rounded-r-none ${viewMode === "grid" ? "bg-secondary" : ""}`}
              onClick={() => setViewMode("grid")}
            >
              <LayoutGrid className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-9 w-9 rounded-l-none ${viewMode === "table" ? "bg-secondary" : ""}`}
              onClick={() => setViewMode("table")}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Users className="w-4 h-4" />
        <span>{filtered.length} candidates</span>
        {search && <Badge variant="outline" className="text-[10px]">filtered</Badge>}
      </div>

      {/* Results */}
      {filtered.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Users className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No candidates found matching your criteria.</p>
        </div>
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((c) => (
            <CandidateCard
              key={c.id}
              candidate={c}
              onView={setSelectedCandidate}
              isShortlisted={shortlisted.has(c.id)}
              onToggleShortlist={toggleShortlist}
            />
          ))}
        </div>
      ) : (
        <CandidateTable 
          candidates={filtered} 
          onViewCandidate={setSelectedCandidate} 
          shortlisted={shortlisted} 
          onToggleShortlist={toggleShortlist}
        />
      )}

      <CandidateDetailModal
        candidate={selectedCandidate}
        open={!!selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
      />
    </div>
  );
};

export default Candidates;
