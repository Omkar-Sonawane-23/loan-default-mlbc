import { CheckCircle2, XCircle } from "lucide-react";
import { BlockchainInfo } from "../../types";

export default function BlockchainStatus({ blockchain }: { blockchain: BlockchainInfo }) {
  if (blockchain.registered) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700">
        <CheckCircle2 size={13} /> Registered
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-400">
      <XCircle size={13} /> Not registered
    </span>
  );
}
