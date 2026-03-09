import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Mail, Wand2, Copy, Send } from "lucide-react";
import { toast } from "sonner";

const templates = [
  { id: "intro", label: "Introduction", subject: "Exciting Opportunity at {company}" },
  { id: "followup", label: "Follow-up", subject: "Following up on our conversation" },
  { id: "referral", label: "Referral", subject: "You were recommended by a colleague" },
];

const sampleEmail = `Hi {name},

I hope this message finds you well. I came across your profile and was impressed by your experience as a {role} at {company}.

We have an exciting opportunity for a Senior Full-Stack Developer role at our company. Given your background in {skills}, I believe you'd be a great fit.

Key highlights:
• Competitive compensation (₹25-35 LPA)
• Work with cutting-edge tech stack
• Bangalore location with hybrid work model
• Strong growth trajectory

Would you be open to a brief 15-minute conversation this week?

Best regards,
{hr_name}
Talent Acquisition, {hr_company}`;

const Outreach = () => {
  const [selectedTemplate, setSelectedTemplate] = useState("intro");
  const [email, setEmail] = useState(sampleEmail);
  const [subject, setSubject] = useState("Exciting Opportunity at TechCorp");
  const [recipientName, setRecipientName] = useState("Priya Sharma");

  const handleGenerate = () => {
    toast.success("AI generated personalized email!");
    setEmail(sampleEmail);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(email);
    toast.success("Email copied to clipboard!");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Outreach & Email Generator</h1>
        <p className="text-sm text-muted-foreground">AI-powered personalized emails for candidate outreach</p>
      </div>

      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center gap-3">
          <Mail className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Email Template</h2>
        </div>

        <div className="flex gap-2">
          {templates.map((t) => (
            <Badge
              key={t.id}
              variant={selectedTemplate === t.id ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setSelectedTemplate(t.id)}
            >
              {t.label}
            </Badge>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Recipient</label>
            <Input value={recipientName} onChange={(e) => setRecipientName(e.target.value)} className="bg-secondary/50" />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Subject</label>
            <Input value={subject} onChange={(e) => setSubject(e.target.value)} className="bg-secondary/50" />
          </div>
        </div>

        <div>
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Email Body</label>
          <Textarea value={email} onChange={(e) => setEmail(e.target.value)} rows={14} className="bg-secondary/50 font-mono text-xs" />
        </div>

        <div className="flex gap-2">
          <Button className="gap-2" onClick={handleGenerate}>
            <Wand2 className="w-4 h-4" /> AI Generate
          </Button>
          <Button variant="secondary" className="gap-2" onClick={handleCopy}>
            <Copy className="w-4 h-4" /> Copy
          </Button>
          <Button variant="outline" className="gap-2">
            <Send className="w-4 h-4" /> Send
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Outreach;
