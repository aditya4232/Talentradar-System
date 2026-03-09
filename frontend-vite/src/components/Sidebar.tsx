import { Brain, LayoutDashboard, Search, FileText, Settings, Users, Mail, Database, Radar } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/", section: "main" },
  { icon: FileText, label: "Job Input", path: "/job-input", section: "main" },
  { icon: Radar, label: "Talent Radar", path: "/talent-radar", section: "main" },
  { icon: Users, label: "Candidates", path: "/candidates", section: "main" },
  { icon: Mail, label: "Outreach", path: "/outreach", section: "tools" },
  { icon: Database, label: "Knowledge Base", path: "/knowledge-base", section: "tools" },
  { icon: Settings, label: "Settings", path: "/settings", section: "tools" },
];

const Sidebar = () => {
  const mainItems = navItems.filter((i) => i.section === "main");
  const toolItems = navItems.filter((i) => i.section === "tools");

  return (
    <aside className="w-64 h-screen bg-card border-r border-border flex flex-col fixed left-0 top-0 z-30">
      <div className="p-5 border-b border-border flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
          <Radar className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-foreground tracking-tight">TalentRadar</h1>
          <p className="text-[10px] text-muted-foreground uppercase tracking-widest">AI Recruitment</p>
        </div>
      </div>

      <nav className="flex-1 p-3 overflow-y-auto">
        <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-3 mb-2">Hiring</p>
        <div className="space-y-0.5 mb-4">
          {mainItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all duration-150",
                  isActive
                    ? "bg-primary/10 text-primary font-medium border-l-2 border-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                )
              }
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          ))}
        </div>

        <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-3 mb-2">Tools</p>
        <div className="space-y-0.5">
          {toolItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all duration-150",
                  isActive
                    ? "bg-primary/10 text-primary font-medium border-l-2 border-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                )
              }
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>

      <div className="p-4 border-t border-border space-y-2">
        <div className="flex items-center gap-2">
          <div className="pulse-dot" />
          <span className="text-xs text-muted-foreground">Agents: Idle</span>
        </div>
        <div className="p-2 rounded-md bg-primary/5 border border-primary/15">
          <p className="text-[10px] text-primary/70">🇮🇳 Indian Market Focus</p>
          <p className="text-[10px] text-muted-foreground">8 candidates in pipeline</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
