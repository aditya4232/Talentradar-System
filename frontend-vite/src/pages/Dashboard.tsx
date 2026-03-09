import { Users, Target, Brain, TrendingUp, Briefcase, Zap, ArrowRight, Radar, Timer } from "lucide-react";
import StatCard from "@/components/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Candidate, fetchCandidates, getScraperStatus } from "@/api/candidates";
import ScoresBadge from "@/components/ScoreBadge";

const Dashboard = () => {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isScraping, setIsScraping] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const data = await fetchCandidates();
      setCandidates(data);
    } catch (e) {
      console.warn("Failed to fetch candidates for dashboard");
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    try {
      const status = await getScraperStatus();
      setIsScraping(status.active);
    } catch (e) {
      console.warn("Status check failed");
    }
  };

  const topCandidates = [...candidates]
    .sort((a, b) => (b.talent_score || 0) - (a.talent_score || 0))
    .slice(0, 5);

  const avgScore = candidates.length > 0
    ? Math.round(candidates.reduce((acc, c) => acc + (c.talent_score || 0), 0) / candidates.length)
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Talent Intelligence Dashboard</h1>
          <p className="text-sm text-muted-foreground">AI-powered recruitment insights • {isScraping ? "Live Scraping Active" : "Systems Ready"}</p>
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <Button variant="outline" className="gap-2 flex-1 sm:flex-none border-primary/20 text-primary hover:bg-primary/5" onClick={loadData}>
            <Timer className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Refresh Data
          </Button>
          <Button className="gap-2 flex-1 sm:flex-none bg-primary hover:bg-primary/90" onClick={() => navigate("/job-input")}>
            <Zap className="w-4 h-4" /> Start AI Match
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Profiles in Pipeline" value={candidates.length.toString()} change="+8%" positive />
        <StatCard icon={Target} label="Avg. Match Score" value={`${avgScore}%`} change="+4.2%" positive />
        <StatCard icon={Brain} label="Top Talent Identified" value={candidates.filter(c => (c.talent_score || 0) > 85).length.toString()} change="+12%" positive />
        <StatCard icon={Radar} label="Active Scout Agents" value={isScraping ? "1" : "0"} change={isScraping ? "RUNNING" : "IDLE"} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Market Insights */}
        <div className="lg:col-span-2 glass-card p-5 relative overflow-hidden bg-gradient-card">
           <div className="absolute top-0 right-0 p-4 opacity-5">
              <TrendingUp className="w-24 h-24" />
           </div>
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-4 h-4 text-primary" />
            <h2 className="text-base font-bold text-foreground">Real-time Talent Trends (India)</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-primary/[0.03] border border-primary/10 hover:shadow-sm transition-all group">
              <p className="text-xs text-primary font-bold mb-2 flex items-center gap-1.5 uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                Skill Hotspot
              </p>
              <p className="text-sm text-foreground leading-relaxed">
                <span className="font-bold">React + Go</span> professionals are seeing a <span className="text-success font-bold">22% spike</span> in demand across Bangalore and Hyderabad startups this week.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-accent/[0.03] border border-accent/10 hover:shadow-sm transition-all">
              <p className="text-xs text-accent font-bold mb-2 uppercase tracking-wider italic">Compensation Intel</p>
              <p className="text-sm text-foreground leading-relaxed">
                Remote-friendly roles are closing <span className="font-bold">40% faster</span> even with 10-15% lower CTC offers compared to hybrid office roles.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-secondary/50 border border-border/50 hover:shadow-sm transition-all col-span-1 md:col-span-2">
               <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Active Source Mix</p>
                  <p className="text-[10px] text-primary font-mono font-bold uppercase">Live Analysis</p>
               </div>
               <div className="space-y-3 mt-4">
                 <div className="space-y-1.5">
                    <div className="flex justify-between text-[11px] font-medium">
                       <span>Naukri.com</span>
                       <span>45%</span>
                    </div>
                    <Progress value={45} className="h-1.5 bg-primary/10" />
                 </div>
                 <div className="space-y-1.5">
                    <div className="flex justify-between text-[11px] font-medium">
                       <span>LinkedIn (Scraped)</span>
                       <span>35%</span>
                    </div>
                    <Progress value={35} className="h-1.5 bg-accent/10" indicatorClassName="bg-accent" />
                 </div>
                 <div className="space-y-1.5">
                    <div className="flex justify-between text-[11px] font-medium">
                       <span>Indeed / Direct</span>
                       <span>20%</span>
                    </div>
                    <Progress value={20} className="h-1.5 bg-muted" />
                 </div>
               </div>
            </div>
          </div>
        </div>

        {/* Top Candidates Sidebar */}
        <div className="glass-card p-5 bg-gradient-to-b from-card to-secondary/30">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-base font-bold text-foreground">Top Movers</h2>
            <Button variant="link" size="sm" className="text-xs font-bold text-primary p-0 h-auto" onClick={() => navigate("/candidates")}>
              Full Pipeline <ArrowRight className="ml-1 w-3 h-3" />
            </Button>
          </div>
          <div className="space-y-3">
            {topCandidates.map((c) => (
              <div 
                key={c.id} 
                className="flex items-center gap-3 p-2.5 rounded-xl bg-white/50 border border-border/40 hover:border-primary/30 hover:bg-white hover:shadow-md transition-all cursor-pointer group" 
                onClick={() => navigate("/candidates")}
              >
                <div className="w-9 h-9 rounded-lg bg-primary/5 flex items-center justify-center text-[10px] font-bold text-primary shrink-0 group-hover:bg-primary group-hover:text-white transition-colors">
                  {c.name.split(" ").map((n) => n[0]).join("").substring(0, 2).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-bold text-foreground truncate group-hover:text-primary transition-colors">{c.name}</p>
                  <p className="text-[10px] text-muted-foreground truncate font-medium uppercase tracking-tighter">{c.current_title || "Lead Eng"}</p>
                </div>
                <div className="flex flex-col items-end gap-0.5">
                   <span className="text-xs font-bold text-primary font-mono">{Math.round(c.talent_score)}%</span>
                   <Badge variant="outline" className="text-[8px] h-3 px-1 leading-none font-bold uppercase border-primary/20 bg-primary/5 text-primary/70">{c.source}</Badge>
                </div>
              </div>
            ))}
            {loading && [1,2,3,4,5].map(v => (
              <div key={v} className="h-14 bg-secondary/50 rounded-xl animate-pulse" />
            ))}
            {!loading && candidates.length === 0 && (
              <div className="py-12 text-center">
                 <Radar className="w-8 h-8 text-muted/30 mx-auto mb-3" />
                 <p className="text-xs text-muted-foreground italic">No candidates in radar.<br/>Start a scrape cycle to scan market.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
