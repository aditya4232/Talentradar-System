import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { indianCities, skillsList } from "@/data/mockCandidates";
import { Filter, X } from "lucide-react";

export type Filters = {
  minScore: number;
  minExp: number;
  maxExp: number;
  location: string;
  source: string;
  skills: string[];
};

const defaultFilters: Filters = {
  minScore: 0,
  minExp: 0,
  maxExp: 30,
  location: "all",
  source: "all",
  skills: [],
};

type Props = {
  filters: Filters;
  onChange: (f: Filters) => void;
};

const FilterPanel = ({ filters, onChange }: Props) => {
  const [showSkills, setShowSkills] = useState(false);

  const toggleSkill = (skill: string) => {
    const skills = filters.skills.includes(skill)
      ? filters.skills.filter((s) => s !== skill)
      : [...filters.skills, skill];
    onChange({ ...filters, skills });
  };

  const resetFilters = () => onChange(defaultFilters);

  const activeCount = [
    filters.minScore > 0,
    filters.minExp > 0 || filters.maxExp < 30,
    filters.location !== "all",
    filters.source !== "all",
    filters.skills.length > 0,
  ].filter(Boolean).length;

  return (
    <div className="glass-card p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">Filters</span>
          {activeCount > 0 && (
            <Badge variant="secondary" className="text-[10px]">{activeCount} active</Badge>
          )}
        </div>
        {activeCount > 0 && (
          <Button variant="ghost" size="sm" className="text-xs h-7" onClick={resetFilters}>
            <X className="w-3 h-3 mr-1" /> Clear
          </Button>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Min Talent Score</label>
          <div className="flex items-center gap-2">
            <Slider value={[filters.minScore]} max={100} step={5} onValueChange={([v]) => onChange({ ...filters, minScore: v })} className="flex-1" />
            <span className="text-xs font-mono text-foreground w-8">{filters.minScore}%</span>
          </div>
        </div>

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Location</label>
          <Select value={filters.location} onValueChange={(v) => onChange({ ...filters, location: v })}>
            <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Cities</SelectItem>
              {indianCities.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Source</label>
          <Select value={filters.source} onValueChange={(v) => onChange({ ...filters, source: v })}>
            <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sources</SelectItem>
              <SelectItem value="LinkedIn">LinkedIn</SelectItem>
              <SelectItem value="Naukri">Naukri</SelectItem>
              <SelectItem value="Indeed">Indeed</SelectItem>
              <SelectItem value="Foundit">Foundit</SelectItem>
              <SelectItem value="Web">Web</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Experience</label>
          <div className="flex items-center gap-2">
            <Slider value={[filters.minExp, filters.maxExp]} min={0} max={30} step={1} onValueChange={([a, b]) => onChange({ ...filters, minExp: a, maxExp: b })} className="flex-1" />
            <span className="text-[10px] font-mono text-foreground whitespace-nowrap">{filters.minExp}-{filters.maxExp}y</span>
          </div>
        </div>
      </div>

      <div>
        <button className="text-xs text-primary hover:underline" onClick={() => setShowSkills(!showSkills)}>
          {showSkills ? "Hide" : "Show"} skill filters {filters.skills.length > 0 && `(${filters.skills.length})`}
        </button>
        {showSkills && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {skillsList.map((s) => (
              <Badge
                key={s}
                variant={filters.skills.includes(s) ? "default" : "outline"}
                className="cursor-pointer text-[10px]"
                onClick={() => toggleSkill(s)}
              >
                {s}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export { defaultFilters };
export default FilterPanel;
