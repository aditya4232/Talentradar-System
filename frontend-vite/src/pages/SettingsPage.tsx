import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Settings, Clock, Brain } from "lucide-react";

const SettingsPage = () => {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground">Configure your talent radar agents and preferences</p>
      </div>

      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center gap-3">
          <Clock className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Cron Job Scheduling</h2>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-secondary/50 rounded-md">
            <div>
              <p className="text-sm text-foreground">Auto-scan for new candidates</p>
              <p className="text-xs text-muted-foreground">Run scraper agents on schedule</p>
            </div>
            <Switch />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Scan Frequency</label>
            <Select defaultValue="daily">
              <SelectTrigger className="h-8 text-xs bg-secondary/50"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="hourly">Every Hour</SelectItem>
                <SelectItem value="6hours">Every 6 Hours</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center gap-3">
          <Brain className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">AI Preferences</h2>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-secondary/50 rounded-md">
            <div>
              <p className="text-sm text-foreground">Build knowledge base automatically</p>
              <p className="text-xs text-muted-foreground">Learn from search results to improve future matches</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between p-3 bg-secondary/50 rounded-md">
            <div>
              <p className="text-sm text-foreground">Smart email generation</p>
              <p className="text-xs text-muted-foreground">AI personalizes emails based on candidate profile</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Min Match Score Threshold</label>
            <Input type="number" defaultValue="60" className="h-8 text-xs bg-secondary/50 w-32" />
          </div>
        </div>
      </div>

      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center gap-3">
          <Settings className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Company Profile</h2>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Company Name</label>
            <Input placeholder="Your Company" className="h-8 text-xs bg-secondary/50" />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">HR Name</label>
            <Input placeholder="Your Name" className="h-8 text-xs bg-secondary/50" />
          </div>
        </div>
      </div>

      <Button className="w-full">Save Settings</Button>
    </div>
  );
};

export default SettingsPage;
