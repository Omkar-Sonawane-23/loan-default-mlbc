import { useEffect, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import FeatureImportance from "../components/risk/FeatureImportance";
import { modelApi } from "../api/modelApi";
import { getErrorMessage } from "../api/client";
import { formatDateTime } from "../utils/formatters";

export default function ModelAnalytics() {
  const [info, setInfo] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([modelApi.info(), modelApi.metrics()])
      .then(([i, m]) => { setInfo(i); setMetrics(m); })
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading model analytics..." />;
  if (error) return <ErrorState message={error} />;
  if (!info || !metrics) return null;

  const metricRows = [
    ["Accuracy", metrics.metrics.accuracy],
    ["Precision", metrics.metrics.precision],
    ["Recall", metrics.metrics.recall],
    ["F1 Score", metrics.metrics.f1_score],
    ["ROC-AUC", metrics.metrics.roc_auc],
  ];

  return (
    <div>
      <PageHeader title="Model Analytics" description="Details on the currently deployed ML model, trained on synthetic data" />

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Current Model</h3>
            <div className="grid sm:grid-cols-2 gap-4 text-sm">
              <div><div className="text-xs text-slate-400">Model Name</div><div className="font-medium">{info.model_name}</div></div>
              <div><div className="text-xs text-slate-400">Model Version</div><div className="font-medium">{info.model_version}</div></div>
              <div><div className="text-xs text-slate-400">Training Date</div><div className="font-medium">{formatDateTime(info.trained_at)}</div></div>
              <div><div className="text-xs text-slate-400">Dataset Size</div><div className="font-medium">{info.dataset_size?.toLocaleString()} records</div></div>
            </div>
            <div className="mt-4">
              <div className="text-xs text-slate-400 mb-1">Candidate Models Compared</div>
              <div className="flex flex-wrap gap-1.5">
                {info.candidate_models_compared?.map((m: string) => (
                  <span key={m} className={`badge ${m === info.model_name ? "bg-accent-50 text-accent-700 border border-accent-100" : "bg-slate-100 text-slate-500"}`}>
                    {m}{m === info.model_name ? " (selected)" : ""}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Model Evaluation Metrics</h3>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {metricRows.map(([label, value]) => (
                <div key={label as string} className="text-center p-3 rounded-lg bg-slate-50">
                  <div className="text-lg font-semibold text-accent-600">{((value as number) * 100).toFixed(1)}%</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{label}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Model Comparison</h3>
            <div className="overflow-x-auto">
              <table className="table-base">
                <thead>
                  <tr>
                    <th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>ROC-AUC</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(metrics.model_comparison || {}).map(([name, m]: any) => (
                    <tr key={name} className={name === info.model_name ? "bg-accent-50/40" : ""}>
                      <td className="font-medium">{name}{name === info.model_name && <span className="text-accent-600 ml-1">★</span>}</td>
                      <td>{(m.accuracy * 100).toFixed(1)}%</td>
                      <td>{(m.precision * 100).toFixed(1)}%</td>
                      <td>{(m.recall * 100).toFixed(1)}%</td>
                      <td>{(m.f1_score * 100).toFixed(1)}%</td>
                      <td>{(m.roc_auc * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="lg:col-span-1">
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">Feature Importance</h3>
            <p className="text-[11px] text-slate-400 mb-4">{info.feature_importance_method}</p>
            <FeatureImportance factors={metrics.feature_importance} />
          </div>
          <div className="text-[11px] text-slate-400 mt-3 leading-relaxed">{info.notice}</div>
        </div>
      </div>
    </div>
  );
}
