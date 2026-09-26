import { AuditEvent } from "../../types";
import { formatDateTime } from "../../utils/formatters";
import { FileText, Activity, RefreshCw, ArrowRightLeft, Link2, ShieldCheck, ShieldAlert } from "lucide-react";

const EVENT_ICONS: Record<string, any> = {
  "Application Created": FileText,
  "Risk Prediction Generated": Activity,
  "Application Updated": RefreshCw,
  "Status Changed": ArrowRightLeft,
  "Blockchain Registered": Link2,
  "Blockchain Verified": ShieldCheck,
  "Record Verification Failed": ShieldAlert,
};

export default function AuditTimeline({ events }: { events: AuditEvent[] }) {
  if (events.length === 0) {
    return <p className="text-xs text-slate-400">No audit events recorded yet.</p>;
  }
  return (
    <div className="relative pl-5">
      <div className="absolute left-[7px] top-1 bottom-1 w-px bg-slate-200" />
      <div className="space-y-5">
        {events.map((e, i) => {
          const Icon = EVENT_ICONS[e.event] || Activity;
          return (
            <div key={i} className="relative">
              <div className="absolute -left-5 top-0.5 h-3.5 w-3.5 rounded-full bg-white border-2 border-accent-500" />
              <div className="flex items-center gap-2">
                <Icon size={13} className="text-accent-600" />
                <span className="text-sm font-medium text-slate-800">{e.event}</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">{formatDateTime(e.timestamp)}</div>
              {Object.keys(e.details || {}).length > 0 && (
                <div className="text-[11px] text-slate-500 mt-1 font-mono bg-slate-50 rounded p-1.5 inline-block max-w-full overflow-x-auto">
                  {Object.entries(e.details).map(([k, v]) => `${k}: ${v}`).join("  •  ")}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
