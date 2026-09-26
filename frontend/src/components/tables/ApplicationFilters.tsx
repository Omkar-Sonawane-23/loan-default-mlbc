import { Search, X } from "lucide-react";
import { APPLICATION_STATUSES } from "../../utils/constants";

export interface FilterState {
  search: string;
  risk_category: string;
  status: string;
}

interface Props {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

export default function ApplicationFilters({ filters, onChange }: Props) {
  const clear = () => onChange({ search: "", risk_category: "", status: "" });
  const hasActiveFilters = filters.search || filters.risk_category || filters.status;

  return (
    <div className="flex flex-wrap items-center gap-2 mb-4">
      <div className="relative flex-1 min-w-[200px]">
        <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          className="input-base pl-8"
          placeholder="Search by ID, reference, or loan purpose"
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
        />
      </div>
      <select
        className="input-base w-auto"
        value={filters.risk_category}
        onChange={(e) => onChange({ ...filters, risk_category: e.target.value })}
      >
        <option value="">All Risk Levels</option>
        <option value="LOW">Low</option>
        <option value="MEDIUM">Medium</option>
        <option value="HIGH">High</option>
      </select>
      <select
        className="input-base w-auto"
        value={filters.status}
        onChange={(e) => onChange({ ...filters, status: e.target.value })}
      >
        <option value="">All Statuses</option>
        {APPLICATION_STATUSES.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
      </select>
      {hasActiveFilters && (
        <button onClick={clear} className="btn btn-secondary text-xs">
          <X size={13} /> Clear
        </button>
      )}
    </div>
  );
}
