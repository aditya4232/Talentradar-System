import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Upload, Brain, Zap, X, FileText, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { indianCities, skillsList } from "@/data/mockCandidates";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

const JobInput = () => {
  const navigate = useNavigate();
  const [jd, setJd] = useState("");
  const [title, setTitle] = useState("");
  const [location, setLocation] = useState("");
  const [minExp, setMinExp] = useState("");
  const [maxExp, setMaxExp] = useState("");
  const [budget, setBudget] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [isParsing, setIsParsing] = useState(false);
  const [parsed, setParsed] = useState(false);

  const toggleSkill = (skill: string) => {
    setSelectedSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".pdf")) {
      toast.error("Only PDF files are supported.");
      return;
    }

    setIsParsing(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post(`${API_BASE}/jd/upload`, formData);
      const data = res.data;
      setTitle(data.title || "");
      setJd(data.raw_text || "");
      setSelectedSkills(data.required_skills || []);
      if (data.experience_min != null) setMinExp(String(data.experience_min));
      if (data.experience_max != null) setMaxExp(String(data.experience_max));
      setParsed(true);
      toast.success("AI parsed the job description from PDF!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to parse PDF");
    } finally {
      setIsParsing(false);
    }
  };

  const handleAIParse = async () => {
    if (!jd.trim()) {
      toast.error("Please enter a job description first.");
      return;
    }
    setIsParsing(true);
    try {
      const res = await axios.post(`${API_BASE}/jd/parse-text`, { text: jd });
      const data = res.data;
      setTitle(data.title || title);
      setSelectedSkills(data.required_skills || []);
      if (data.experience_min != null) setMinExp(String(data.experience_min));
      if (data.experience_max != null) setMaxExp(String(data.experience_max));
      setParsed(true);
      toast.success("AI parsed the job description!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to parse JD");
    } finally {
      setIsParsing(false);
    }
  };

  const handleStartSearch = async () => {
    if (!jd && !title) {
      toast.error("Please enter a job description or upload a PDF.");
      return;
    }

    // If not already parsed, parse first
    if (!parsed && jd.trim()) {
      await handleAIParse();
    }

    toast.success("Navigating to Talent Radar to find matching candidates...");
    navigate("/talent-radar");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Job Description Input</h1>
        <p className="text-sm text-muted-foreground">Paste a JD, upload a PDF, or let AI help you define the role.</p>
      </div>

      {/* Upload Section */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-3 mb-4">
          <Upload className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Upload JD (PDF/DOCX)</h2>
        </div>
        <label className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-border rounded-lg hover:border-primary/50 transition-colors cursor-pointer bg-secondary/30">
          <FileText className="w-8 h-8 text-muted-foreground mb-2" />
          <p className="text-sm text-muted-foreground">Drop file here or click to upload</p>
          <p className="text-[10px] text-muted-foreground mt-1">PDF, DOCX up to 10MB</p>
          <input type="file" className="hidden" accept=".pdf,.docx,.doc" onChange={handleFileUpload} />
        </label>
      </div>

      {/* Manual Input */}
      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Job Details</h2>
          {!parsed && jd.trim() && (
            <Button variant="outline" size="sm" className="ml-auto text-xs h-7 gap-1" onClick={handleAIParse} disabled={isParsing}>
              {isParsing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />} AI Parse JD
            </Button>
          )}
        </div>

        {isParsing && (
          <div className="flex items-center gap-2 p-3 rounded-md bg-primary/5 border border-primary/20">
            <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-primary">AI is parsing the job description...</span>
          </div>
        )}

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Job Title</label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Senior React Developer" className="bg-secondary/50" />
        </div>

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Job Description</label>
          <Textarea value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the full job description here..." rows={6} className="bg-secondary/50" />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Location</label>
            <Select value={location} onValueChange={setLocation}>
              <SelectTrigger className="h-8 text-xs bg-secondary/50"><SelectValue placeholder="Select city" /></SelectTrigger>
              <SelectContent>
                {indianCities.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Min Experience</label>
            <Input value={minExp} onChange={(e) => setMinExp(e.target.value)} placeholder="0" type="number" className="h-8 text-xs bg-secondary/50" />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Max Experience</label>
            <Input value={maxExp} onChange={(e) => setMaxExp(e.target.value)} placeholder="15" type="number" className="h-8 text-xs bg-secondary/50" />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Budget (CTC)</label>
            <Input value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="e.g. 20-30 LPA" className="h-8 text-xs bg-secondary/50" />
          </div>
        </div>

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Required Skills</label>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {skillsList.map((s) => (
              <Badge
                key={s}
                variant={selectedSkills.includes(s) ? "default" : "outline"}
                className="cursor-pointer text-[10px]"
                onClick={() => toggleSkill(s)}
              >
                {s}
              </Badge>
            ))}
          </div>
          {selectedSkills.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              <span className="text-[10px] text-muted-foreground mr-1">Selected:</span>
              {selectedSkills.map((s) => (
                <Badge key={s} className="text-[10px] gap-1">
                  {s}
                  <X className="w-2.5 h-2.5 cursor-pointer" onClick={() => toggleSkill(s)} />
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      <Button className="w-full gap-2 h-11" onClick={handleStartSearch}>
        <Zap className="w-4 h-4" /> Start AI Talent Search
      </Button>
    </div>
  );
};

export default JobInput;
