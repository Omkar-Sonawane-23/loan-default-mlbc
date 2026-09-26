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
        <div className="text-xs font-medium text-slate-600 mb-2">Key contributing factors</div>
        <FeatureImportance factors={result.risk_factors} />
      </div>

      <div className="text-[11px] text-slate-400 border-t border-slate-100 pt-3 leading-relaxed">
        {result.disclaimer}
      </div>
    </div>
  );
}
