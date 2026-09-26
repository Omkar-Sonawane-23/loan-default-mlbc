import { useEffect, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import RiskDistribution from "../components/charts/RiskDistribution";
import ApplicationTrend from "../components/charts/ApplicationTrend";
import ProbabilityDistribution from "../components/charts/ProbabilityDistribution";
import RiskLoanChart from "../components/charts/RiskLoanChart";
import EmploymentDistribution from "../components/charts/EmploymentDistribution";
import { analyticsApi } from "../api/analyticsApi";
import { getErrorMessage } from "../api/client";

export default function Analytics() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyticsApi.fullAnalytics().then(setData).catch((e) => setError(getErrorMessage(e))).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading analytics..." />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  return (
    <div>
      <PageHeader title="Analytics" description="Portfolio-wide risk, loan, and blockchain analytics" />

      <div className="grid lg:grid-cols-2 gap-4 mb-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Risk Distribution</h3>
          <RiskDistribution data={data.risk_distribution} />
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Monthly Applications</h3>
          <ApplicationTrend data={data.applications_over_time} />
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Default Probability Distribution</h3>
          <ProbabilityDistribution data={data.default_probability_distribution} />
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Average Loan Amount by Risk</h3>
          <RiskLoanChart data={data.loan_amount_by_risk} />
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Employment Type Distribution</h3>
          <EmploymentDistribution data={data.employment_type_distribution} />
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-3">Loan Purpose Distribution</h3>
          <div className="space-y-2">
            {data.loan_purpose_distribution.map((p: any) => (
              <div key={p.loan_purpose} className="flex items-center gap-2">
                <span className="text-xs text-slate-600 w-32 shrink-0">{p.loan_purpose}</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-accent-500 rounded-full" style={{
                    width: `${(p.count / Math.max(...data.loan_purpose_distribution.map((x: any) => x.count))) * 100}%`
                  }} />
                </div>
                <span className="text-xs text-slate-400 w-6 text-right">{p.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Blockchain Registration Rate</h3>
          <div className="text-2xl font-semibold text-accent-600 mt-2">{data.blockchain.registration_percentage}%</div>
          <p className="text-xs text-slate-400 mt-1">of all applications registered on-chain</p>
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Blockchain Verification Rate</h3>
          <div className="text-2xl font-semibold text-green-600 mt-2">{data.blockchain.verification_percentage}%</div>
          <p className="text-xs text-slate-400 mt-1">of all applications marked VERIFIED</p>
        </div>
      </div>
    </div>
  );
}
