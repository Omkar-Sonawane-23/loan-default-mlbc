import { useEffect, useState } from "react";
import { Activity, AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import { apiClient, getErrorMessage } from "../api/client";

type Summary = {
  status: string; model_version: string; model_hash: string; window_days: number;
  recent_prediction_count: number; comparison_prediction_count: number;
  prediction_drift_psi: number | null; prediction_drift_band: string;
  recent_mean_default_probability: number | null; comparison_mean_default_probability: number | null;
  feature_drift: string; label_performance: string; interpretation: string;
};

export default function ModelMonitoring() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    apiClient.get<Summary>("/model-monitoring/summary")
      .then(({ data }) => setSummary(data))
      .catch((e: unknown) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false));
  }, []);
  if (loading) return <LoadingSpinner label="Loading monitoring summary..." />;
  if (error) return <ErrorState message={error} />;
  if (!summary) return null;
  const healthy = summary.prediction_drift_band === "LOW";
  const stat = (label: string, value: string, sub: string) => (
    <div className="card p-5"><div className="text-xs uppercase tracking-wide text-slate-400">{label}</div><div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div><div className="mt-1 text-xs text-slate-500">{sub}</div></div>
  );
  return <div>
    <PageHeader title="Model Monitoring" description="Observed inference traffic and prediction-distribution drift. No outcome-label performance is available." />
    <div className={`mb-5 rounded-xl border p-4 flex gap-3 ${healthy ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"}`}>
      {healthy ? <CheckCircle2 className="text-emerald-600" /> : <AlertTriangle className="text-amber-600" />}
      <div><div className="font-semibold text-slate-800">{summary.status} · {summary.prediction_drift_band} prediction drift</div><p className="text-sm text-slate-600">{summary.interpretation}</p></div>
    </div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stat("Model version", summary.model_version, `SHA-256 ${summary.model_hash.slice(0, 16)}…`)}
      {stat("Recent predictions", String(summary.recent_prediction_count), `${summary.window_days}-day current window`)}
      {stat("Reference predictions", String(summary.comparison_prediction_count), `preceding ${summary.window_days}-day window`)}
      {stat("Prediction PSI", summary.prediction_drift_psi?.toFixed(4) ?? "—", "Distribution shift screening indicator")}
    </div>
    <div className="grid gap-4 mt-4 lg:grid-cols-2">
      <section className="card p-5"><h2 className="font-semibold flex items-center gap-2"><Activity size={17}/>Default probability averages</h2><div className="mt-4 flex justify-between text-sm"><span>Comparison window</span><b>{summary.comparison_mean_default_probability === null ? "Insufficient data" : `${(summary.comparison_mean_default_probability * 100).toFixed(1)}%`}</b></div><div className="mt-2 flex justify-between text-sm"><span>Recent window</span><b>{summary.recent_mean_default_probability === null ? "Insufficient data" : `${(summary.recent_mean_default_probability * 100).toFixed(1)}%`}</b></div></section>
      <section className="card p-5"><h2 className="font-semibold flex items-center gap-2"><Clock3 size={17}/>Monitoring boundaries</h2><p className="mt-3 text-sm text-slate-600"><b>Feature drift:</b> {summary.feature_drift}</p><p className="mt-2 text-sm text-slate-600"><b>Label performance:</b> {summary.label_performance}</p><p className="mt-3 text-xs text-slate-500">PSI does not establish model accuracy, fairness, calibration or a changing real-world default rate.</p></section>
    </div>
  </div>;
}
