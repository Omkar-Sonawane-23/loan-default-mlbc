import { CheckCircle2, XCircle } from "lucide-react";
import { BlockchainVerifyResponse } from "../../types";
import { truncateHash, formatDateTime } from "../../utils/formatters";

export default function VerificationResult({ result }: { result: BlockchainVerifyResponse }) {
  return (
    <div className="card p-5 space-y-4">
      <div
        className={`flex items-center gap-3 p-4 rounded-lg border ${
          result.verified ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
        }`}
      >
        {result.verified ? (
          <CheckCircle2 className="text-green-600 shrink-0" size={28} />
        ) : (
          <XCircle className="text-red-600 shrink-0" size={28} />
        )}
        <div>
          <div className={`text-base font-semibold ${result.verified ? "text-green-700" : "text-red-700"}`}>
            {result.verified ? "VERIFIED" : "VERIFICATION FAILED"}
          </div>
          <div className="text-xs text-slate-600 mt-0.5">{result.message}</div>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4 text-xs">
        <div>
          <div className="text-slate-400 mb-1">Current Database Hash</div>
          <div className="font-mono break-all bg-slate-50 border border-slate-200 rounded p-2">
            {result.current_database_hash}
          </div>
        </div>
        <div>
          <div className="text-slate-400 mb-1">Blockchain Hash</div>
          <div className="font-mono break-all bg-slate-50 border border-slate-200 rounded p-2">
            {result.blockchain_hash || "-"}
          </div>
        </div>
      </div>

      <table className="table-base">
        <tbody>
          <tr><td className="text-slate-500 font-medium">Transaction Hash</td><td className="font-mono text-xs">{truncateHash(result.transaction_hash, 10)}</td></tr>
          <tr><td className="text-slate-500 font-medium">Block Number</td><td>{result.block_number ?? "-"}</td></tr>
          <tr><td className="text-slate-500 font-medium">Registered At</td><td>{formatDateTime(result.registered_at)}</td></tr>
        </tbody>
      </table>
    </div>
  );
}
