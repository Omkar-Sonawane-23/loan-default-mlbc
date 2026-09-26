import { STATUS_BG } from "../../utils/constants";

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`badge ${STATUS_BG[status] || "bg-slate-100 text-slate-600"}`}>{status.replace("_", " ")}</span>;
}
