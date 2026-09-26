import { Loader2 } from "lucide-react";

export default function LoadingSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <Loader2 size={22} className="animate-spin mb-2" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
