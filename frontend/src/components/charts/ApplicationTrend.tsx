import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function ApplicationTrend({ data }: { data: { date: string; count: number }[] }) {
  if (data.length === 0) return <div className="text-xs text-slate-400 py-8 text-center">No data yet</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ left: -20, right: 10, top: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: "11px", borderRadius: "6px" }} />
        <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
