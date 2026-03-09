import { Candidate } from "@/api/candidates";
import ScoresBadge from "./ScoreBadge";
import { Badge } from "@/components/ui/badge";
import { Sparkles, ThumbsUp } from "lucide-react";

type Props = {
  candidates: Candidate[];
  onView?: (c: Candidate) => void;
};

const AIRecommendations = ({ candidates, onView }: Props) => {
  const top3 = candidates.slice(0, 3);

  const reasons = [
    "Perfect skill alignment + strong talent score",
    "Strong leadership experience in similar domain",
    "Top education + high growth trajectory",
  ];

  return (
    <div className="glass-card p-5 glow-border">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-primary" />
        <h2 className="text-sm font-semibold text-foreground">AI Top Recommendations</h2>
        <Badge variant="secondary" className="text-[10px]">Smart Pick</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {top3.map((c, i) => (
          <div
            key={c.id}
            className="p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors cursor-pointer border border-transparent hover:border-primary/20"
            onClick={() => onView?.(c)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-primary/15 flex items-center justify-center text-xs font-bold text-primary">
                  #{i + 1}
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{c.name}</p>
                  <p className="text-[10px] text-muted-foreground">{c.current_title || "Professional"}</p>
                </div>
              </div>
              <ScoresBadge score={Math.round(c.talent_score || 0)} />
            </div>

            <div className="flex items-start gap-1.5 mt-2 p-2 rounded-md bg-primary/5">
              <ThumbsUp className="w-3 h-3 text-primary mt-0.5 shrink-0" />
              <p className="text-[11px] text-primary/80">{reasons[i]}</p>
            </div>

            <div className="flex flex-wrap gap-1 mt-2">
              {(c.skills || []).slice(0, 3).map((s) => (
                <Badge key={s} variant="secondary" className="text-[9px] px-1 py-0">{s}</Badge>
              ))}
            </div>

            <div className="flex items-center justify-between mt-2 text-[10px] text-muted-foreground">
              <span>{c.experience_years || 0} yrs • {(c.location || "India").split(",")[0]}</span>
              <span>{c.source}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIRecommendations;
