import { Menu } from "lucide-react";

export default function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <header className="h-14 border-b border-slate-200 bg-white flex items-center px-4 sticky top-0 z-10 md:hidden">
      <button onClick={onMenuClick} className="text-slate-600 mr-3">
        <Menu size={20} />
      </button>
      <span className="text-sm font-semibold">LoanDefault MLBC</span>
    </header>
  );
}
