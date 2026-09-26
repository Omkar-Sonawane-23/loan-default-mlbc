import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, FileSpreadsheet, ListChecks, BarChart3, Brain,
  Link2, ShieldCheck, Settings as SettingsIcon,
} from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/predict", label: "Risk Prediction", icon: FileSpreadsheet },
  { to: "/applications", label: "Applications", icon: ListChecks },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/model", label: "Model Analytics", icon: Brain },
  { to: "/blockchain", label: "Blockchain", icon: Link2 },
  { to: "/verify", label: "Verify Record", icon: ShieldCheck },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function Sidebar() {
  return (
    <aside className="hidden md:flex md:flex-col w-60 shrink-0 border-r border-slate-200 bg-white h-screen sticky top-0">
      <div className="h-14 flex items-center px-4 border-b border-slate-200">
        <div className="h-7 w-7 rounded bg-accent-500 flex items-center justify-center text-white font-bold text-xs">
          LD
        </div>
        <div className="ml-2">
          <div className="text-sm font-semibold text-slate-900 leading-tight">LoanDefault</div>
          <div className="text-[10px] text-slate-400 leading-tight">MLBC Academic Project</div>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm mb-0.5 transition-colors ${
                isActive
                  ? "bg-accent-50 text-accent-700 font-medium"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`
            }
          >
            <item.icon size={16} strokeWidth={2} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-slate-200 text-[10px] text-slate-400 leading-relaxed">
        Academic demonstration only. Not financial advice.
      </div>
    </aside>
  );
}
