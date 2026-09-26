import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  hint?: string;
  accentColor?: string;
}

export default function StatCard({ label, value, icon: Icon, hint, accentColor = "#2563eb" }: StatCardProps) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-slate-500">{label}</span>
        <div className="h-7 w-7 rounded-md flex items-center justify-center" style={{ backgroundColor: `${accentColor}15` }}>
          <Icon size={14} style={{ color: accentColor }} />
        </div>
      </div>
      <div className="text-xl font-semibold text-slate-900">{value}</div>
      {hint && <div className="text-xs text-slate-400 mt-1">{hint}</div>}
    </div>
  );
}
