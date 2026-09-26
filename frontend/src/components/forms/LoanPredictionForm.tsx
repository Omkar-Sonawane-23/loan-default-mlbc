import { useState } from "react";
import { LoanFeatures } from "../../types";
import { EMPLOYMENT_TYPES, LOAN_PURPOSES } from "../../utils/constants";
import Button from "../common/Button";
import { RotateCcw, Sparkles } from "lucide-react";

const DEFAULT_FEATURES: LoanFeatures = {
  age: 32,
  annual_income: 600000,
  employment_years: 4,
  employment_type: "Salaried",
  credit_score: 680,
  loan_amount: 500000,
  loan_term_months: 60,
  existing_debt: 100000,
  debt_to_income_ratio: 0.35,
  number_of_previous_loans: 1,
  previous_default: 0,
  dependents: 1,
  savings_amount: 150000,
  requested_loan_purpose: "Home",
};

interface Props {
  onSubmit: (features: LoanFeatures) => void;
  loading: boolean;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium text-slate-600 mb-1.5">{label}</span>
      {children}
    </label>
  );
}

export default function LoanPredictionForm({ onSubmit, loading }: Props) {
  const [features, setFeatures] = useState<LoanFeatures>(DEFAULT_FEATURES);

  const update = <K extends keyof LoanFeatures>(key: K, value: LoanFeatures[K]) =>
    setFeatures((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(features);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <section className="card p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Personal Information</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Age">
            <input type="number" className="input-base" min={18} max={100} value={features.age}
              onChange={(e) => update("age", Number(e.target.value))} required />
          </Field>
          <Field label="Dependents">
            <input type="number" className="input-base" min={0} max={20} value={features.dependents}
              onChange={(e) => update("dependents", Number(e.target.value))} required />
          </Field>
        </div>
      </section>

      <section className="card p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Employment Information</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Employment Type">
            <select className="input-base" value={features.employment_type}
              onChange={(e) => update("employment_type", e.target.value as LoanFeatures["employment_type"])}>
              {EMPLOYMENT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </Field>
          <Field label="Employment Years">
            <input type="number" step="0.5" className="input-base" min={0} max={80} value={features.employment_years}
              onChange={(e) => update("employment_years", Number(e.target.value))} required />
          </Field>
          <Field label="Annual Income (INR)">
            <input type="number" className="input-base" min={0} value={features.annual_income}
              onChange={(e) => update("annual_income", Number(e.target.value))} required />
          </Field>
          <Field label="Savings Amount (INR)">
            <input type="number" className="input-base" min={0} value={features.savings_amount}
              onChange={(e) => update("savings_amount", Number(e.target.value))} required />
          </Field>
        </div>
      </section>

      <section className="card p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Financial Information</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label={`Credit Score: ${features.credit_score}`}>
            <input type="range" min={300} max={900} className="w-full accent-accent-600" value={features.credit_score}
              onChange={(e) => update("credit_score", Number(e.target.value))} />
          </Field>
          <Field label={`Debt-to-Income Ratio: ${features.debt_to_income_ratio.toFixed(2)}`}>
            <input type="range" min={0} max={2} step={0.01} className="w-full accent-accent-600" value={features.debt_to_income_ratio}
              onChange={(e) => update("debt_to_income_ratio", Number(e.target.value))} />
          </Field>
          <Field label="Existing Debt (INR)">
            <input type="number" className="input-base" min={0} value={features.existing_debt}
              onChange={(e) => update("existing_debt", Number(e.target.value))} required />
          </Field>
          <Field label="Number of Previous Loans">
            <input type="number" className="input-base" min={0} value={features.number_of_previous_loans}
              onChange={(e) => update("number_of_previous_loans", Number(e.target.value))} required />
          </Field>
          <Field label="Previous Default">
            <select className="input-base" value={features.previous_default}
              onChange={(e) => update("previous_default", Number(e.target.value) as 0 | 1)}>
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </Field>
        </div>
      </section>

      <section className="card p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Loan Information</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Loan Amount (INR)">
            <input type="number" className="input-base" min={1} value={features.loan_amount}
              onChange={(e) => update("loan_amount", Number(e.target.value))} required />
          </Field>
          <Field label="Loan Term (months)">
            <select className="input-base" value={features.loan_term_months}
              onChange={(e) => update("loan_term_months", Number(e.target.value))}>
              {[12, 24, 36, 48, 60, 84, 120, 180, 240].map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </Field>
          <Field label="Loan Purpose">
            <select className="input-base" value={features.requested_loan_purpose}
              onChange={(e) => update("requested_loan_purpose", e.target.value as LoanFeatures["requested_loan_purpose"])}>
              {LOAN_PURPOSES.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </Field>
        </div>
      </section>

      <div className="flex gap-2">
        <Button type="submit" loading={loading} className="flex-1 justify-center">
          <Sparkles size={14} /> Predict Risk
        </Button>
        <Button type="button" variant="secondary" onClick={() => setFeatures(DEFAULT_FEATURES)}>
          <RotateCcw size={14} /> Reset
        </Button>
      </div>
    </form>
  );
}
