import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileStack, IndianRupee, ShieldAlert, TrendingDown, Link2, ShieldCheck } from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import { getErrorMessage } from "../api/client";
import PageHeader from "../components/layout/PageHeader";
import StatCard from "../components/common/StatCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import RiskDistribution from "../components/charts/RiskDistribution";
import ApplicationTrend from "../components/charts/ApplicationTrend";
import RiskBadge from "../components/risk/RiskBadge";
import StatusBadge from "../components/risk/StatusBadge";
import { formatCurrency, formatPercent, formatDate, truncateHash } from "../utils/formatters";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyticsApi.dashboardStats().then(setData).catch((e) => setError(getErrorMessage(e))).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard..." />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const { stats, recent_applications, recent_blockchain_activity, high_risk_applications, charts } = data;

  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of loan risk assessments and blockchain activity" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <StatCard label="Total Applications" value={String(stats.total_applications)} icon={FileStack} />
        <StatCard label="Total Loan Amount" value={formatCurrency(stats.total_loan_amount)} icon={IndianRupee} accentColor="#7c3aed" />
        <StatCard label="High Risk" value={String(stats.high_risk)} icon={ShieldAlert} accentColor="#dc2626" />
        <StatCard label="Avg. Default Probability" value={formatPercent(stats.average_default_probability)} icon={TrendingDown} accentColor="#d97706" />
        <StatCard label="Low Risk" value={String(stats.low_risk)} icon={ShieldCheck} accentColor="#16a34a" />
        <StatCard label="Medium Risk" value={String(stats.medium_risk)} icon={ShieldAlert} accentColor="#d97706" />
        <StatCard label="Blockchain Registered" value={String(stats.blockchain_registered)} icon={Link2} accentColor="#2563eb" />
        <StatCard label="Verified Records" value={String(stats.verified_records)} icon={ShieldCheck} accentColor="#16a34a" />
      </div>

      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Risk Distribution</h3>
          <RiskDistribution data={charts.risk_distribution} />
        </div>
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Applications Over Time</h3>
          <ApplicationTrend data={charts.applications_over_time} />
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-slate-900 mb-3">Recent Applications</h3>
          {recent_applications.length === 0 ? (
            <p className="text-xs text-slate-400">No applications yet.</p>
          ) : (
            <div className="space-y-3">
              {recent_applications.map((a: any) => (
                <Link key={a.application_id} to={`/applications/${a.application_id}`} className="flex items-center justify-between text-xs hover:bg-slate-50 -mx-1 px-1 py-1 rounded">
                  <span className="font-medium text-slate-700">{a.application_id}</span>
                  <RiskBadge risk={a.risk_category} />
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="card p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-slate-900 mb-3">Recent Blockchain Activity</h3>
          {recent_blockchain_activity.length === 0 ? (
            <p className="text-xs text-slate-400">No blockchain registrations yet.</p>
          ) : (
            <div className="space-y-3">
              {recent_blockchain_activity.map((tx: any) => (
                <div key={tx.application_id} className="text-xs">
                  <div className="flex justify-between">
                    <span className="font-medium text-slate-700">{tx.application_id}</span>
                    <span className="text-slate-400 font-mono">{truncateHash(tx.transaction_hash, 6)}</span>
                  </div>
                  <div className="text-slate-400">{formatDate(tx.registered_at)}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-slate-900 mb-3">High Risk Applications</h3>
          {high_risk_applications.length === 0 ? (
            <p className="text-xs text-slate-400">No high-risk applications.</p>
          ) : (
            <div className="space-y-3">
              {high_risk_applications.map((a: any) => (
                <Link key={a.application_id} to={`/applications/${a.application_id}`} className="flex items-center justify-between text-xs hover:bg-slate-50 -mx-1 px-1 py-1 rounded">
                  <span className="font-medium text-slate-700">{a.application_id}</span>
                  <StatusBadge status={a.status} />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
