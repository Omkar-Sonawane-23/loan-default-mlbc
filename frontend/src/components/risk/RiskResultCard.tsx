import { PredictionResult } from "../../types";
import RiskBadge from "./RiskBadge";
import RiskMeter from "./RiskMeter";
import FeatureImportance from "./FeatureImportance";

export default function RiskResultCard({ result }: { result: PredictionResult }) {
  return (
    <div className="card p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Risk Assessment Result</h3>
        <RiskBadge risk={result.risk_category} />
      </div>

      <RiskMeter probability={result.default_probability} risk={result.risk_category} />

      <div className="grid grid-cols-2 gap-3 text-sm">
        {result.credit_score !== undefined && <div><div className="text-xs text-slate-400">Demo risk index (0–1000)</div><div className="font-semibold">{result.credit_score}</div></div>}
        {result.expected_loss !== undefined && <div><div className="text-xs text-slate-400">Expected loss (assumption-based)</div><div className="font-semibold">₹{result.expected_loss.toLocaleString()}</div></div>}
        <div>
          <div className="text-xs text-slate-400">Non-default probability</div>
          <div className="font-medium text-slate-800">{(result.non_default_probability * 100).toFixed(1)}%</div>
        </div>
        <div>
          <div className="text-xs text-slate-400">Model</div>
          <div className="font-medium text-slate-800">{result.model_name}</div>
        </div>
        <div>
          <div className="text-xs text-slate-400">Model version</div>
          <div className="font-medium text-slate-800">{result.model_version}</div>
        </div>
      </div>

      <div>
        <div className="text-xs font-medium text-slate-600 mb-2">Global model feature importance · not local drivers</div>
        <FeatureImportance factors={result.risk_factors} />
      </div>

      {result.local_explanation?.status === "AVAILABLE" && <section className="rounded-lg border border-slate-200 p-3">
        <h4 className="text-xs font-semibold text-slate-700">Local SHAP explanation</h4>
        <p className="text-[10px] text-slate-500 mt-1">Signed contributions in base-estimator output units; not calibrated probability points.</p>
        <div className="mt-2 space-y-1">{result.local_explanation.contributors.map((item) => <div key={item.feature} className="flex justify-between text-xs"><span>{item.feature}</span><span className={item.impact >= 0 ? "text-rose-600" : "text-emerald-700"}>{item.impact >= 0 ? "+" : ""}{item.impact.toFixed(3)}</span></div>)}</div>
      </section>}
      {result.storage_status && result.storage_status !== "STORED" && <p className="text-xs text-amber-700">Prediction storage status: {result.storage_status}</p>}
      <div className="text-[11px] text-slate-400 border-t border-slate-100 pt-3 leading-relaxed">
        {result.disclaimer}
      </div>
    </div>
  );
}
