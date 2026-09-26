import { RISK_BG } from "../../utils/constants";

export default function RiskBadge({ risk }: { risk: string | null }) {
  if (!risk) return <span className="badge bg-slate-100 text-slate-500">-</span>;
  return <span className={`badge ${RISK_BG[risk] || "bg-slate-100 text-slate-600"}`}>{risk}</span>;
}
