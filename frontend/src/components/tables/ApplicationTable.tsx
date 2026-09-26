import { useNavigate } from "react-router-dom";
import { Eye, ShieldCheck, Link2, Trash2 } from "lucide-react";
import { Application } from "../../types";
import RiskBadge from "../risk/RiskBadge";
import StatusBadge from "../risk/StatusBadge";
import BlockchainStatus from "../blockchain/BlockchainStatus";
import { formatCurrency, formatPercent, formatDate } from "../../utils/formatters";

interface Props {
  applications: Application[];
  onDelete: (applicationId: string) => void;
  onRegister: (applicationId: string) => void;
  onVerify: (applicationId: string) => void;
}

export default function ApplicationTable({ applications, onDelete, onRegister, onVerify }: Props) {
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto">
      <table className="table-base">
        <thead>
          <tr>
            <th>Application ID</th>
            <th>Applicant Ref.</th>
            <th>Loan Amount</th>
            <th>Credit Score</th>
            <th>Default Prob.</th>
            <th>Risk</th>
            <th>Status</th>
            <th>Blockchain</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.application_id}>
              <td className="font-medium text-slate-800">{app.application_id}</td>
              <td className="text-slate-600">{app.applicant_reference}</td>
              <td>{formatCurrency(app.input_features.loan_amount)}</td>
              <td>{app.input_features.credit_score}</td>
              <td>{formatPercent(app.default_probability)}</td>
              <td><RiskBadge risk={app.risk_category} /></td>
              <td><StatusBadge status={app.status} /></td>
              <td><BlockchainStatus blockchain={app.blockchain} /></td>
              <td className="text-slate-500">{formatDate(app.created_at)}</td>
              <td>
                <div className="flex items-center gap-1.5">
                  <button title="View" onClick={() => navigate(`/applications/${app.application_id}`)} className="text-slate-500 hover:text-accent-600">
                    <Eye size={15} />
                  </button>
                  {!app.blockchain.registered ? (
                    <button title="Register on blockchain" onClick={() => onRegister(app.application_id)} className="text-slate-500 hover:text-accent-600">
                      <Link2 size={15} />
                    </button>
                  ) : (
                    <button title="Verify" onClick={() => onVerify(app.application_id)} className="text-slate-500 hover:text-green-600">
                      <ShieldCheck size={15} />
                    </button>
                  )}
                  <button title="Delete" onClick={() => onDelete(app.application_id)} className="text-slate-500 hover:text-red-600">
                    <Trash2 size={15} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
