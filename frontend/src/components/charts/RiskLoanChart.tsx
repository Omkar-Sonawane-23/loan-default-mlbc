import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { RISK_COLORS } from "../../utils/constants";

interface Props { data: { risk_category: string; average_loan_amount: number }[] }

export default function RiskLoanChart({ data }: Props) {
  if (data.length === 0) return <div className="text-xs text-slate-400 py-8 text-center">No data yet</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ left: -10, right: 10, top: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="risk_category" tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} />
        <Tooltip contentStyle={{ fontSize: "11px", borderRadius: "6px" }} />
        <Bar dataKey="average_loan_amount" radius={[3, 3, 0, 0]}>
          {data.map((d) => <Cell key={d.risk_category} fill={RISK_COLORS[d.risk_category] || "#94a3b8"} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
