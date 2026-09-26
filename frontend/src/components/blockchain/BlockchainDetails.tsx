import { BlockchainInfo } from "../../types";
import BlockchainStatus from "./BlockchainStatus";
import TransactionDetails from "./TransactionDetails";
import { truncateHash } from "../../utils/formatters";

export default function BlockchainDetails({ blockchain }: { blockchain: BlockchainInfo }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-900">Blockchain Information</h3>
        <BlockchainStatus blockchain={blockchain} />
      </div>
      {blockchain.registered ? (
        <div className="space-y-3">
          <div>
            <div className="text-xs text-slate-400 mb-1">Record Hash</div>
            <div className="font-mono text-xs break-all bg-slate-50 border border-slate-200 rounded p-2">
              {blockchain.record_hash}
            </div>
          </div>
          <TransactionDetails
            transactionHash={blockchain.transaction_hash}
            blockNumber={blockchain.block_number}
            contractAddress={blockchain.contract_address}
            chainId={blockchain.chain_id}
            registeredAt={blockchain.registered_at}
          />
        </div>
      ) : (
        <p className="text-xs text-slate-400">
          This application has not been registered on the blockchain yet.
        </p>
      )}
    </div>
  );
}
