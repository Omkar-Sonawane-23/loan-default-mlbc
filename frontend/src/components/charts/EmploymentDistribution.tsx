import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function EmploymentDistribution({ data }: { data: { employment_type: string; count: number }[] }) {
  if (data.length === 0) return <div className="text-xs text-slate-400 py-8 text-center">No data yet</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20, top: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis type="number" tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} allowDecimals={false} />
        <YAxis dataKey="employment_type" type="category" tick={{ fontSize: 10 }} width={90} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} />
        <Tooltip contentStyle={{ fontSize: "11px", borderRadius: "6px" }} />
        <Bar dataKey="count" fill="#2563eb" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
