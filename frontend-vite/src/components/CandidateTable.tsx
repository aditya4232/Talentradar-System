import ScoresBadge from "./ScoreBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Mail, Eye, Star, ExternalLink } from "lucide-react";

type TableCandidate = {
  id: any;
  name: string;
  current_title?: string;
  currentRole?: string;
  talent_score?: number;
  matchScore?: number;
  experience_years?: number;
  experience?: number;
  location?: string;
  skills?: string[];
  source?: string;
  company?: string;
  email?: string;
  profile_url?: string;
};

type Props = {
  candidates: TableCandidate[];
  onViewCandidate?: (c: any) => void;
  shortlisted?: Set<any>;
  onToggleShortlist?: (id: any) => void;
};

const CandidateTable = ({ candidates, onViewCandidate, shortlisted, onToggleShortlist }: Props) => {
  return (
    <div className="glass-card overflow-hidden border-border/50">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-border bg-secondary/30">
              <th className="text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 py-3.5">Candidate Info</th>
              <th className="text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 py-3.5">Talent Score</th>
              <th className="text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 py-3.5">Exp / Location</th>
              <th className="text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 py-3.5">Core Skills</th>
              <th className="text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 py-3.5">Source</th>
              <th className="text-right text-xs font-bold text-muted-foreground uppercase tracking-widest px-4 py-3.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {candidates.map((c) => (
              <tr key={c.id} className="hover:bg-primary/[0.02] transition-colors group">
                <td className="px-4 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary group-hover:bg-primary group-hover:text-white transition-all">
                      {c.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">{c.name}</p>
                      <p className="text-[11px] text-muted-foreground font-medium">{c.current_title || c.currentRole || "Professional"}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <ScoresBadge score={Math.round(c.talent_score ?? c.matchScore ?? 0)} />
                </td>
                <td className="px-4 py-4">
                  <div className="space-y-0.5">
                    <p className="text-xs font-semibold text-foreground">{c.experience_years ?? c.experience ?? 0} Years</p>
                    <p className="text-[10px] text-muted-foreground">{c.location}</p>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <div className="flex flex-wrap gap-1 max-w-[200px]">
                    {c.skills?.slice(0, 3).map((s) => (
                      <Badge key={s} variant="secondary" className="text-[9px] px-1.5 py-0 bg-primary/5 text-primary border-primary/10 uppercase">
                        {s}
                      </Badge>
                    ))}
                    {c.skills?.length > 3 && (
                      <span className="text-[10px] text-muted-foreground font-medium ml-1">+{c.skills.length - 3}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <Badge variant="outline" className="text-[9px] font-bold border-primary/20 text-primary/80 uppercase tracking-tighter shadow-sm">
                    {c.source}
                  </Badge>
                </td>
                <td className="px-4 py-4">
                  <div className="flex items-center justify-end gap-1.5">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 hover:bg-primary/10 hover:text-primary transition-colors" 
                      onClick={() => onViewCandidate?.(c)}
                      title="View Profile"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className={`h-8 w-8 transition-all ${shortlisted?.has(c.id) ? "text-accent bg-accent/10" : "text-muted-foreground hover:bg-secondary"}`}
                      onClick={() => onToggleShortlist?.(c.id)}
                    >
                      <Star className={`h-4 w-4 ${shortlisted?.has(c.id) ? "fill-accent" : ""}`} />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
            {candidates.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground italic text-sm">
                  No candidates found matching your criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CandidateTable;
