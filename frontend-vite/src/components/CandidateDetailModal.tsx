import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import ScoresBadge from "./ScoreBadge";
import { Mail, Phone, MapPin, Briefcase, GraduationCap, Copy, Globe, ExternalLink, Timer } from "lucide-react";
import { toast } from "sonner";

type ModalCandidate = {
  id: any;
  name: string;
  email?: string | null;
  phone?: string | null;
  current_title?: string;
  currentRole?: string;
  company?: string;
  location?: string;
  experience_years?: number;
  experience?: number;
  skills?: string[];
  talent_score?: number;
  matchScore?: number;
  source?: string;
  summary?: string;
  profile_url?: string;
  profileUrl?: string;
};

type Props = {
  candidate: ModalCandidate | null;
  open: boolean;
  onClose: () => void;
};

const CandidateDetailModal = ({ candidate, open, onClose }: Props) => {
  if (!candidate) return null;

  const copyEmail = () => {
    if (candidate.email) {
      navigator.clipboard.writeText(candidate.email);
      toast.success("Email copied!");
    } else {
      toast.error("No email available");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg bg-card border-border shadow-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between gap-4">
            <span className="truncate pr-4 text-xl font-bold">{candidate.name}</span>
            <div className="shrink-0 flex items-center gap-2">
               <Badge variant="outline" className="text-[10px] border-primary/20 bg-primary/5 text-primary uppercase h-6">{candidate.source}</Badge>
               <ScoresBadge score={Math.round(candidate.talent_score ?? candidate.matchScore ?? 0)} />
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-5 mt-4">
          <div className="p-4 rounded-xl bg-secondary/30 border border-border/40">
             <p className="text-sm text-foreground leading-relaxed italic">"{candidate.summary || "No professional summary provided."}"</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 text-sm text-muted-foreground bg-white/50 p-2 rounded-lg border border-border/30">
              <Briefcase className="w-4 h-4 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/60 leading-none mb-1">Current Role</p>
                <p className="text-foreground font-semibold truncate">{candidate.current_title || candidate.currentRole || "Engineer"} at {candidate.company || "Unknown"}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground bg-white/50 p-2 rounded-lg border border-border/30">
              <MapPin className="w-4 h-4 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/60 leading-none mb-1">Location</p>
                <p className="text-foreground font-semibold truncate">{candidate.location || "India (Remote)"}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground bg-white/50 p-2 rounded-lg border border-border/30">
              <Timer className="w-4 h-4 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/60 leading-none mb-1">Experience</p>
                <p className="text-foreground font-semibold truncate">{candidate.experience_years ?? candidate.experience ?? 0} Years Relevant</p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground bg-white/50 p-2 rounded-lg border border-border/30">
              <Globe className="w-4 h-4 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/60 leading-none mb-1">Talent Pipeline</p>
                <p className="text-foreground font-semibold truncate">{candidate.source || "Web Scrape"}</p>
              </div>
            </div>
          </div>

          <div>
            <p className="text-[10px] text-muted-foreground mb-2 uppercase font-bold tracking-widest pl-1">Identified Expert Skills</p>
            <div className="flex flex-wrap gap-1.5">
              {candidate.skills?.map((s) => (
                <Badge key={s} variant="outline" className="text-[11px] px-2 py-0.5 border-primary/20 bg-primary/[0.02] text-primary/80 uppercase font-medium">{s}</Badge>
              ))}
              {(!candidate.skills || candidate.skills.length === 0) && <span className="text-xs text-muted-foreground italic">No specific skills extracted.</span>}
            </div>
          </div>

          <div className="flex gap-2 pt-4 border-t border-border/50">
            <Button size="sm" className="flex-1 gap-2 bg-primary hover:bg-primary/90 text-white" onClick={copyEmail} disabled={!candidate.email}>
              <Mail className="w-4 h-4" /> Message
            </Button>
            {(candidate.profile_url || candidate.profileUrl) && (
              <Button size="sm" variant="outline" className="flex-1 gap-2 border-primary/20 text-primary hover:bg-primary/5" asChild>
                <a href={candidate.profile_url || candidate.profileUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4" /> Open Profile
                </a>
              </Button>
            )}
            <Button size="sm" variant="secondary" className="gap-2 px-3" onClick={copyEmail} disabled={!candidate.email}>
              <Copy className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CandidateDetailModal;
