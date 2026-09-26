import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import StatCard from "../components/common/StatCard";
import { blockchainApi } from "../api/blockchainApi";
import { getErrorMessage } from "../api/client";
import { truncateHash, formatDateTime } from "../utils/formatters";
import { Network, Database, ShieldCheck, Activity } from "lucide-react";

export default function Blockchain() {
  const [status, setStatus] = useState<any>(null);
  const [txData, setTxData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([blockchainApi.status(), blockchainApi.transactions()])
      .then(([s, t]) => { setStatus(s); setTxData(t); })
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading blockchain status..." />;
  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <PageHeader title="Blockchain" description="Local Hardhat network status and on-chain registration activity" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <StatCard label="Network Status" value={status?.available ? "Connected" : "Unavailable"} icon={Network} accentColor={status?.available ? "#16a34a" : "#dc2626"} />
        <StatCard label="Chain ID" value={String(status?.chain_id ?? "-")} icon={Database} />
        <StatCard label="Records On-Chain" value={String(status?.total_records_on_chain ?? "-")} icon={ShieldCheck} accentColor="#7c3aed" />
        <StatCard label="Registered (DB)" value={String(txData?.total_registered ?? 0)} icon={Activity} accentColor="#2563eb" />
      </div>

      <div className="card p-5 mb-6">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Smart Contract</h3>
        {status?.available ? (
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            <div><div className="text-xs text-slate-400">Contract Address</div><div className="font-mono text-xs">{status.contract_address}</div></div>
            <div><div className="text-xs text-slate-400">RPC URL</div><div className="font-mono text-xs">{status.rpc_url}</div></div>
          </div>
        ) : (
          <p className="text-xs text-slate-500">
            No local blockchain detected. Start one with <code className="bg-slate-100 px-1 py-0.5 rounded">npx hardhat node</code> and
            deploy the contract (see <code className="bg-slate-100 px-1 py-0.5 rounded">blockchain/README.md</code>).
            {status?.error && <span className="block mt-1 text-red-500">{status.error}</span>}
          </p>
        )}
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Recent Transactions</h3>
        {!txData || txData.transactions.length === 0 ? (
          <EmptyState title="No transactions yet" description="Register an application on the blockchain to see it here." />
        ) : (
          <div className="overflow-x-auto">
            <table className="table-base">
              <thead>
                <tr>
                  <th>Application ID</th><th>Risk</th><th>Transaction Hash</th><th>Block</th><th>Timestamp</th><th></th>
                </tr>
              </thead>
              <tbody>
                {txData.transactions.map((tx: any) => (
                  <tr key={tx.application_id}>
                    <td className="font-medium">{tx.application_id}</td>
                    <td>{tx.risk_category}</td>
                    <td className="font-mono text-xs">{truncateHash(tx.transaction_hash, 8)}</td>
                    <td>{tx.block_number}</td>
                    <td className="text-slate-500">{formatDateTime(tx.registered_at)}</td>
                    <td><Link to={`/applications/${tx.application_id}`} className="text-accent-600 text-xs hover:underline">View</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
