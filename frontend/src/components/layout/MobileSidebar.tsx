import { NavLink } from "react-router-dom";
import { X } from "lucide-react";
import {
  LayoutDashboard, FileSpreadsheet, ListChecks, BarChart3, Brain,
  Link2, ShieldCheck, Settings as SettingsIcon, Activity, Wallet,
} from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/predict", label: "Risk Prediction", icon: FileSpreadsheet },
  { to: "/applications", label: "Applications", icon: ListChecks },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/model", label: "Model Analytics", icon: Brain },
  { to: "/model-monitoring", label: "Model Monitoring", icon: Activity },
  { to: "/loans", label: "Loan Lifecycle", icon: Wallet },
  { to: "/blockchain", label: "Blockchain", icon: Link2 },
  { to: "/verify", label: "Verify Record", icon: ShieldCheck },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function MobileSidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 md:hidden">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <aside className="absolute left-0 top-0 h-full w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200">
          <span className="text-sm font-semibold">LoanDefault MLBC</span>
          <button onClick={onClose} className="text-slate-500"><X size={18} /></button>
        </div>
        <nav className="flex-1 overflow-y-auto py-3 px-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm mb-0.5 ${
                  isActive ? "bg-accent-50 text-accent-700 font-medium" : "text-slate-600"
                }`
              }
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </div>
  );
}
