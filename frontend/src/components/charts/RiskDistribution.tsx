import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { RISK_COLORS } from "../../utils/constants";

export default function RiskDistribution({ data }: { data: Record<string, number> }) {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));
  if (chartData.length === 0) return <div className="text-xs text-slate-400 py-8 text-center">No data yet</div>;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={2}>
          {chartData.map((entry) => (
            <Cell key={entry.name} fill={RISK_COLORS[entry.name] || "#94a3b8"} />
          ))}
        </Pie>
        <Tooltip />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
