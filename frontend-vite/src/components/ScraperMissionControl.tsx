import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Play, Square, Timer, Activity, Globe, Search, RefreshCw, Sliders, Zap } from "lucide-react";
import { ScraperStatus, getScraperStatus, startScraper, stopScraper } from "@/api/candidates";
import axios from "axios";
import { toast } from "sonner";

const ScraperMissionControl = () => {
    const [status, setStatus] = useState<ScraperStatus | null>(null);
    const [loading, setLoading] = useState(false);
    const [isScheduling, setIsScheduling] = useState(false);
    const [interval, setIntervalVal] = useState(60);

    const API_BASE = "http://localhost:8000/api/v1";

    useEffect(() => {
        const intervalId = setInterval(fetchStatus, 3000);
        fetchStatus();
        return () => clearInterval(intervalId);
    }, []);

    const fetchStatus = async () => {
        try {
            const data = await getScraperStatus();
            setStatus(data);
        } catch (e) {
            console.warn("Status poll failed");
        }
    };

    const handleToggleScheduling = async () => {
        setLoading(true);
        try {
            const next = !isScheduling;
            await axios.post(`${API_BASE}/scraper/schedule`, {
                enabled: next,
                interval_minutes: interval
            });
            setIsScheduling(next);
            toast.success(`Scraper schedule ${next ? 'enabled' : 'disabled'}`);
        } catch (e) {
            toast.error("Failed to update schedule");
        } finally {
            setLoading(false);
        }
    };

    const toggleMainScrape = async () => {
        if (status?.active) {
            await stopScraper();
            toast.info("Mission sequence aborted.");
        } else {
            await startScraper();
            toast.success("Live Talent Acquisition Launched!");
        }
    };

    return (
        <div className="glass-card p-5 bg-gradient-to-br from-card via-card to-primary/[0.03] border-primary/10 overflow-hidden relative">
            {/* Background Radar Effect */}
            <div className={`absolute -right-10 -top-10 w-40 h-40 bg-primary/5 rounded-full blur-3xl animate-pulse ${status?.active ? 'opacity-100' : 'opacity-0'}`} />

            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                        <Activity className={`w-5 h-5 ${status?.active ? 'text-primary animate-bounce' : 'text-muted-foreground'}`} />
                        <h2 className="text-lg font-bold text-foreground tracking-tight">Scraper Mission Control</h2>
                        {status?.active && (
                            <Badge className="bg-primary/20 text-primary border-none text-[10px] animate-pulse">ACTIVE MISSION</Badge>
                        )}
                    </div>
                    <p className="text-xs text-muted-foreground font-medium">
                        Autonomous scouts scanning top job portals across India in real-time.
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary/50 border border-border/50">
                        <Timer className="w-3.5 h-3.5 text-muted-foreground" />
                        <span className="text-xs font-bold text-foreground">{interval}m</span>
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-5 w-5 hover:bg-primary/10"
                            onClick={() => setIntervalVal(prev => prev === 60 ? 15 : prev + 15)}
                        >
                            <Sliders className="w-3 h-3" />
                        </Button>
                        <Badge 
                            variant={isScheduling ? "default" : "outline"} 
                            className={`text-[9px] cursor-pointer h-5 ${isScheduling ? 'bg-primary' : 'border-primary/20 text-primary'}`}
                            onClick={handleToggleScheduling}
                        >
                            {isScheduling ? "AUTO-PILOT ON" : "SHEDULED OFF"}
                        </Badge>
                    </div>

                    <Button 
                        onClick={toggleMainScrape}
                        className={`gap-2 font-bold px-6 h-10 transition-all ${status?.active ? 'bg-destructive/10 text-destructive hover:bg-destructive/20 border border-destructive/20' : 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/20'}`}
                    >
                        {status?.active ? (
                            <><Square className="w-4 h-4 fill-current" /> STOP SCOUT</>
                        ) : (
                            <><Play className="w-4 h-4 fill-current" /> LAUNCH SCAN</>
                        )}
                    </Button>
                </div>
            </div>

            {/* Progress Visualization */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-4 col-span-2">
                    <div className="flex items-center justify-between mb-1">
                        <div className="flex flex-col">
                            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest pl-1">Operational Progress</span>
                            <span className="text-sm font-bold text-foreground flex items-center gap-2">
                                <Globe className={`w-3.5 h-3.5 text-primary ${status?.active ? 'animate-spin' : ''}`} />
                                {status?.active ? `Scanning: ${status.current_target}` : "System Idle"}
                            </span>
                        </div>
                        <div className="text-right">
                            <span className="text-sm font-black text-primary font-mono">{status?.candidates_found || 0}</span>
                            <span className="text-[10px] text-muted-foreground uppercase ml-1 font-bold">Profiles</span>
                        </div>
                    </div>
                    <Progress value={status?.active ? 45 : 0} className="h-2 bg-primary/5" indicatorClassName="bg-gradient-to-r from-primary to-accent" />
                    
                    <div className="flex items-center gap-6 mt-2">
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-primary" />
                            <span className="text-[10px] font-bold text-muted-foreground uppercase">Engine: <span className="text-foreground">{status?.engine || "None"}</span></span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-accent" />
                            <span className="text-[10px] font-bold text-muted-foreground uppercase">Stability: <span className="text-foreground">Optimal (100%)</span></span>
                        </div>
                        <div className="flex items-center gap-2 ml-auto">
                           <RefreshCw className={`w-3 h-3 text-muted-foreground ${status?.active ? 'animate-spin' : ''}`} />
                           <span className="text-[9px] font-medium text-muted-foreground uppercase">Live Stream Active</span>
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 flex flex-col justify-center">
                    <div className="flex items-center gap-2 mb-2">
                         <Zap className="w-3.5 h-3.5 text-primary" />
                         <span className="text-xs font-extrabold text-foreground uppercase tracking-tight">Intelligence Signal</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground leading-relaxed italic">
                        Scout agents are currently prioritizing {status?.engine === 'Crawl4AI' ? 'LLM-powered semantic extraction' : 'stealth-mode behavioral simulation'} to bypass portal paywalls.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ScraperMissionControl;
