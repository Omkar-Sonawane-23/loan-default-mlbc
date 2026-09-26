interface Factor { feature: string; importance: number }

export default function FeatureImportance({ factors }: { factors: Factor[] }) {
  if (!factors || factors.length === 0) {
    return <p className="text-xs text-slate-400">No feature importance data available.</p>;
  }
  const max = Math.max(...factors.map((f) => f.importance), 0.0001);
  return (
    <div className="space-y-2.5">
      {factors.map((f) => (
        <div key={f.feature}>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-600">{f.feature}</span>
            <span className="text-slate-400">{f.importance.toFixed(4)}</span>
          </div>
          <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
            <div className="h-full rounded-full bg-accent-500" style={{ width: `${(f.importance / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
