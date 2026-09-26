import { RISK_COLORS } from "../../utils/constants";

export default function RiskMeter({ probability, risk }: { probability: number; risk: string }) {
  const pct = Math.min(Math.max(probability * 100, 0), 100);
  const color = RISK_COLORS[risk] || "#64748b";
  return (
    <div>
      <div className="flex items-baseline justify-between mb-1.5">
        <span className="text-2xl font-semibold" style={{ color }}>{pct.toFixed(1)}%</span>
        <span className="text-xs text-slate-500">Default probability</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <div className="flex justify-between text-[10px] text-slate-400 mt-1">
        <span>0%</span><span>30%</span><span>70%</span><span>100%</span>
      </div>
    </div>
  );
}
