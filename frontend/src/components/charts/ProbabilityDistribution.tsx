import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function ProbabilityDistribution({ data }: { data: { range: string; count: number }[] }) {
  if (data.length === 0) return <div className="text-xs text-slate-400 py-8 text-center">No data yet</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ left: -20, right: 10, top: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="range" tick={{ fontSize: 9 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: "11px", borderRadius: "6px" }} />
        <Bar dataKey="count" fill="#2563eb" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
