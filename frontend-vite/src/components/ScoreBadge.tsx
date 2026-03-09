import { cn } from "@/lib/utils";

const ScoresBadge = ({ score }: { score: number }) => {
  const getScoreClass = () => {
    if (score >= 85) return "bg-success/15 text-success border-success/30";
    if (score >= 70) return "bg-warning/15 text-warning border-warning/30";
    return "bg-destructive/15 text-destructive border-destructive/30";
  };

  return (
    <span className={cn("inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border font-mono", getScoreClass())}>
      {score}%
    </span>
  );
};

export default ScoresBadge;
