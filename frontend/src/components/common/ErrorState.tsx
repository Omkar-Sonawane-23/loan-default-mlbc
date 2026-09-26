import { AlertTriangle } from "lucide-react";

export default function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="h-10 w-10 rounded-full bg-red-50 flex items-center justify-center mb-3">
        <AlertTriangle size={18} className="text-red-500" />
      </div>
      <div className="text-sm font-medium text-slate-700">Something went wrong</div>
      <div className="text-xs text-red-500 mt-1 max-w-sm">{message}</div>
    </div>
  );
}
