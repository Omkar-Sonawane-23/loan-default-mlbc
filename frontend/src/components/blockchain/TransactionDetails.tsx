import { truncateHash, formatDateTime } from "../../utils/formatters";

interface Props {
  transactionHash: string | null;
  blockNumber: number | null;
  contractAddress: string | null;
  chainId: number | null;
  registeredAt: string | null;
}

export default function TransactionDetails({ transactionHash, blockNumber, contractAddress, chainId, registeredAt }: Props) {
  const rows = [
    ["Transaction Hash", transactionHash ? truncateHash(transactionHash, 10) : "-"],
    ["Block Number", blockNumber ?? "-"],
    ["Contract Address", contractAddress ? truncateHash(contractAddress, 8) : "-"],
    ["Chain ID", chainId ?? "-"],
    ["Registered At", formatDateTime(registeredAt)],
  ];
  return (
    <table className="table-base">
      <tbody>
        {rows.map(([label, value]) => (
          <tr key={label as string}>
            <td className="text-slate-500 font-medium">{label}</td>
            <td className="font-mono text-xs">{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
