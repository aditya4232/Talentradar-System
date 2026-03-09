import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { toast } from "sonner";

type ExportCandidate = {
  name: string;
  email?: string | null;
  phone?: string | null;
  location?: string;
  current_title?: string;
  currentRole?: string;
  company?: string;
  experience_years?: number;
  experience?: number;
  skills?: string[];
  talent_score?: number;
  matchScore?: number;
  source?: string;
  expectedCTC?: string;
  currentCTC?: string;
  availability?: string;
};

type Props = { candidates: ExportCandidate[] };

const ExportButtons = ({ candidates }: Props) => {
  const getRole = (c: ExportCandidate) => c.current_title || c.currentRole || "";
  const getExp = (c: ExportCandidate) => c.experience_years ?? c.experience ?? 0;
  const getScore = (c: ExportCandidate) => c.talent_score ?? c.matchScore ?? 0;

  const exportCSV = () => {
    const headers = ["Name", "Email", "Phone", "Location", "Role", "Company", "Experience", "Skills", "Score", "Source"];
    const rows = candidates.map((c) => [
      c.name, c.email || "", c.phone || "", c.location || "", getRole(c), c.company || "", getExp(c), (c.skills || []).join("; "), getScore(c), c.source || "",
    ]);
    const csv = [headers, ...rows].map((r) => r.map((v) => `"${v}"`).join(",")).join("\n");
    downloadFile(csv, "candidates.csv", "text/csv");
    toast.success("CSV exported!");
  };

  const exportExcel = () => {
    const headers = ["Name", "Email", "Phone", "Location", "Role", "Company", "Experience", "Skills", "Score", "Source"];
    let xml = '<?xml version="1.0"?><?mso-application progid="Excel.Sheet"?>';
    xml += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">';
    xml += "<Worksheet ss:Name='Candidates'><Table>";
    xml += "<Row>" + headers.map((h) => `<Cell><Data ss:Type="String">${h}</Data></Cell>`).join("") + "</Row>";
    candidates.forEach((c) => {
      const vals = [c.name, c.email || "", c.phone || "", c.location || "", getRole(c), c.company || "", String(getExp(c)), (c.skills || []).join("; "), String(getScore(c)), c.source || ""];
      xml += "<Row>" + vals.map((v) => `<Cell><Data ss:Type="String">${v}</Data></Cell>`).join("") + "</Row>";
    });
    xml += "</Table></Worksheet></Workbook>";
    downloadFile(xml, "candidates.xls", "application/vnd.ms-excel");
    toast.success("Excel exported!");
  };

  const exportDoc = () => {
    let html = "<html><head><meta charset='utf-8'><style>body{font-family:Arial,sans-serif}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#f4f4f4}</style></head><body>";
    html += "<h1>Candidate Report</h1><p>Generated: " + new Date().toLocaleDateString() + "</p>";
    html += "<table><tr><th>Name</th><th>Score</th><th>Role</th><th>Location</th><th>Experience</th><th>Skills</th><th>Source</th><th>Email</th></tr>";
    candidates.forEach((c) => {
      html += `<tr><td>${c.name}</td><td>${getScore(c)}%</td><td>${getRole(c)}</td><td>${c.location || ""}</td><td>${getExp(c)} yrs</td><td>${(c.skills || []).join(", ")}</td><td>${c.source || ""}</td><td>${c.email || ""}</td></tr>`;
    });
    html += "</table></body></html>";
    downloadFile(html, "candidates.doc", "application/msword");
    toast.success("DOC exported!");
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" className="text-xs h-8 gap-1.5" onClick={exportCSV}>
        <Download className="w-3 h-3" /> CSV
      </Button>
      <Button variant="outline" size="sm" className="text-xs h-8 gap-1.5" onClick={exportExcel}>
        <Download className="w-3 h-3" /> Excel
      </Button>
      <Button variant="outline" size="sm" className="text-xs h-8 gap-1.5" onClick={exportDoc}>
        <Download className="w-3 h-3" /> DOC
      </Button>
    </div>
  );
};

export default ExportButtons;
