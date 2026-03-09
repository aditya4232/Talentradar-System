import { useMemo } from "react";
import { Candidate } from "@/api/candidates";
import { Badge } from "@/components/ui/badge";
import { BarChart3, MapPin, Clock, Briefcase } from "lucide-react";

type Props = { candidates: Candidate[] };

const RadarInsights = ({ candidates }: Props) => {
  const stats = useMemo(() => {
    const avgScore = Math.round(candidates.reduce((a, c) => a + (c.talent_score || 0), 0) / (candidates.length || 1));
    const avgExp = (candidates.reduce((a, c) => a + (c.experience_years || 0), 0) / (candidates.length || 1)).toFixed(1);

    const locationMap: Record<string, number> = {};
    candidates.forEach((c) => {
      const city = (c.location || "Unknown").split(",")[0];
      locationMap[city] = (locationMap[city] || 0) + 1;
    });
    const topLocations = Object.entries(locationMap).sort((a, b) => b[1] - a[1]).slice(0, 3);

    const skillMap: Record<string, number> = {};
    candidates.forEach((c) => (c.skills || []).forEach((s) => { skillMap[s] = (skillMap[s] || 0) + 1; }));
    const topSkills = Object.entries(skillMap).sort((a, b) => b[1] - a[1]).slice(0, 5);

    const sourceMap: Record<string, number> = {};
    candidates.forEach((c) => { const src = c.source || "Web"; sourceMap[src] = (sourceMap[src] || 0) + 1; });

    const highScoreCount = candidates.filter((c) => (c.talent_score || 0) >= 80).length;

    return { avgScore, avgExp, topLocations, topSkills, sourceMap, highScoreCount };
  }, [candidates]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-2">
          <BarChart3 className="w-3.5 h-3.5 text-primary" />
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Score & Exp</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Avg Score</span>
            <span className="text-foreground font-semibold">{stats.avgScore}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Avg Experience</span>
            <span className="text-foreground font-semibold">{stats.avgExp} yrs</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Score ≥ 80%</span>
            <span className="text-success font-semibold">{stats.highScoreCount}</span>
          </div>
        </div>
      </div>

      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-2">
          <MapPin className="w-3.5 h-3.5 text-primary" />
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Top Locations</span>
        </div>
        <div className="space-y-1.5">
          {stats.topLocations.map(([city, count]) => (
            <div key={city} className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">{city}</span>
              <Badge variant="secondary" className="text-[10px]">{count}</Badge>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-2">
          <Briefcase className="w-3.5 h-3.5 text-primary" />
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Top Skills</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {stats.topSkills.map(([skill, count]) => (
            <Badge key={skill} variant="outline" className="text-[10px] gap-1">
              {skill} <span className="text-muted-foreground">({count})</span>
            </Badge>
          ))}
        </div>
      </div>

      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-3.5 h-3.5 text-primary" />
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Sources</span>
        </div>
        <div className="space-y-1">
          {Object.entries(stats.sourceMap).map(([source, count]) => (
            <div key={source} className="flex justify-between text-sm">
              <span className="text-muted-foreground">{source}</span>
              <span className="text-foreground">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RadarInsights;
