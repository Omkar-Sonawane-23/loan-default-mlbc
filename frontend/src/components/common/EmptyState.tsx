import { Inbox } from "lucide-react";

export default function EmptyState({ title = "No data yet", description }: { title?: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center mb-3">
        <Inbox size={18} className="text-slate-400" />
      </div>
      <div className="text-sm font-medium text-slate-700">{title}</div>
      {description && <div className="text-xs text-slate-400 mt-1 max-w-xs">{description}</div>}
    </div>
  );
}
