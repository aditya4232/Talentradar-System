import { useState, useEffect } from "react";
import { Bot, Loader2, CheckCircle, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

type AgentStatus = "idle" | "scanning" | "analyzing" | "ranking" | "complete";

type Props = {
  isRunning: boolean;
  onComplete?: () => void;
};

const stages: { key: AgentStatus; label: string; duration: number }[] = [
  { key: "scanning", label: "Scanning Naukri & LinkedIn...", duration: 2000 },
  { key: "analyzing", label: "AI analyzing candidate profiles...", duration: 2500 },
  { key: "ranking", label: "Computing match scores & ranking...", duration: 1500 },
  { key: "complete", label: "Search complete! Results ready.", duration: 0 },
];

const AgentStatusBar = ({ isRunning, onComplete }: Props) => {
  const [status, setStatus] = useState<AgentStatus>("idle");
  const [stageIndex, setStageIndex] = useState(-1);

  useEffect(() => {
    if (!isRunning) {
      setStatus("idle");
      setStageIndex(-1);
      return;
    }

    setStageIndex(0);
    setStatus("scanning");
  }, [isRunning]);

  useEffect(() => {
    if (stageIndex < 0 || stageIndex >= stages.length) return;
    const stage = stages[stageIndex];
    setStatus(stage.key);

    if (stage.key === "complete") {
      onComplete?.();
      return;
    }

    const timer = setTimeout(() => setStageIndex((i) => i + 1), stage.duration);
    return () => clearTimeout(timer);
  }, [stageIndex, onComplete]);

  if (status === "idle") return null;

  return (
    <div className={cn(
      "glass-card p-3 flex items-center gap-3 transition-all",
      status === "complete" ? "glow-border" : "border-warning/30"
    )}>
      {status === "complete" ? (
        <CheckCircle className="w-4 h-4 text-success" />
      ) : (
        <Loader2 className="w-4 h-4 text-warning animate-spin" />
      )}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <Bot className="w-3.5 h-3.5 text-primary" />
          <span className="text-xs font-medium text-foreground">
            {stages[stageIndex]?.label || "Processing..."}
          </span>
        </div>
        {status !== "complete" && (
          <div className="mt-2 h-1 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-1000"
              style={{ width: `${((stageIndex + 1) / stages.length) * 100}%` }}
            />
          </div>
        )}
      </div>
      <Zap className="w-3.5 h-3.5 text-primary/50" />
    </div>
  );
};

export default AgentStatusBar;
