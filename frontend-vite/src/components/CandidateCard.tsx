import ScoresBadge from "./ScoreBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Briefcase, Star, ExternalLink, Globe } from "lucide-react";

type CardCandidate = {
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
};

type Props = {
  candidate: CardCandidate;
  onView?: (c: any) => void;
  isShortlisted?: boolean;
  onToggleShortlist?: (id: any) => void;
};

const CandidateCard = ({ candidate: c, onView, isShortlisted, onToggleShortlist }: Props) => {
  const initials = c.name.split(" ").map((n) => n[0]).join("").substring(0, 2).toUpperCase();

  return (
    <div className="glass-card p-4 hover:border-primary/30 transition-all duration-200 group flex flex-col h-full bg-gradient-card relative overflow-hidden">
      {/* Visual Accent */}
      <div className="absolute top-0 left-0 w-1 h-full bg-primary/20 group-hover:bg-primary transition-colors" />

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-sm font-bold text-primary shrink-0 border border-primary/20">
            {initials}
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-bold text-foreground truncate group-hover:text-primary transition-colors">{c.name}</h3>
            <p className="text-[11px] text-muted-foreground truncate font-medium leading-tight">
              {c.current_title || c.currentRole || "Professional"}
            </p>
          </div>
        </div>
        <ScoresBadge score={Math.round(c.talent_score ?? c.matchScore ?? 0)} />
      </div>

      {/* Main Info */}
      <div className="space-y-1.5 mb-4 flex-1">
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          <Briefcase className="w-3 h-3 text-primary/60 shrink-0" />
          <span className="truncate">{c.company} • {c.experience_years ?? c.experience ?? 0} yrs exp</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          <MapPin className="w-3 h-3 text-primary/60 shrink-0" />
          <span className="truncate">{c.location}</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          <Globe className="w-3 h-3 text-primary/60 shrink-0" />
          <span className="truncate text-primary/80 font-medium">Source: {c.source}</span>
        </div>
      </div>

      {/* Skills */}
      <div className="flex flex-wrap gap-1 mb-4 h-[44px] overflow-hidden content-start">
        {c.skills?.slice(0, 5).map((s) => (
          <Badge key={s} variant="secondary" className="text-[9px] px-1.5 py-0 bg-primary/5 text-primary border-primary/10 hover:bg-primary/10 transition-colors uppercase tracking-tight">
            {s}
          </Badge>
        ))}
        {c.skills?.length > 5 && (
          <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-dashed">
            +{c.skills.length - 5} more
          </Badge>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-3 border-t border-border/50 mt-auto">
        <Button 
          variant="outline" 
          size="sm" 
          className="flex-1 h-8 text-[11px] gap-1.5 px-2 font-semibold shadow-sm hover:bg-primary/5 hover:text-primary transition-all active:scale-95" 
          onClick={() => onView?.(c)}
        >
          <ExternalLink className="w-3 h-3" /> View Full Profile
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className={`h-8 w-8 rounded-md transition-all active:scale-90 ${isShortlisted ? "text-accent bg-accent/10 border border-accent/20" : "text-muted-foreground hover:bg-secondary border border-transparent"}`}
          onClick={() => onToggleShortlist?.(c.id)}
        >
          <Star className={`h-4 w-4 ${isShortlisted ? "fill-accent" : ""}`} />
        </Button>
      </div>
    </div>
  );
};

export default CandidateCard;
