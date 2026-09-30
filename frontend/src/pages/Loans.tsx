import { useMemo, useState } from "react";
import { Contract, BrowserProvider, formatEther, id, keccak256, parseEther, toUtf8Bytes } from "ethers";
import { Wallet, RefreshCw, CircleDollarSign, ShieldCheck } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import { apiClient } from "../api/client";

const ADDRESS = import.meta.env.VITE_LOAN_LIFECYCLE_ADDRESS || "";
const CHAIN_ID = Number(import.meta.env.VITE_CHAIN_ID || 31337);
const WALLET_RPC_URL = import.meta.env.VITE_WALLET_RPC_URL || "";
const ABI = [
  "function submitLoan(bytes32,address,uint256,uint256,uint256,bytes32)",
  "function assessRisk(bytes32,bytes32)", "function decide(bytes32,bool)",
  "function acceptAgreement(bytes32,bytes32)", "function fundLoan(bytes32) payable",
  "function repay(bytes32) payable", "function markDefaulted(bytes32)",
  "function getLoan(bytes32) view returns ((bytes32 applicationId,bytes32 assessmentHash,bytes32 agreementHash,address borrower,address lender,uint256 principalWei,uint256 totalDueWei,uint256 repaidWei,uint256 dueAt,uint256 createdAt,uint8 state,bool agreementAccepted))",
  "function getReputation(address) view returns ((uint256 completedLoans,uint256 defaults,uint256 onTimeCompletions,uint256 lateCompletions,uint256 totalBorrowedWei,uint256 totalRepaidWei,uint256 repaymentStreak),uint256)",
];
const STATES = ["NONE", "SUBMITTED", "RISK_ASSESSED", "APPROVED", "REJECTED", "FUNDED", "ACTIVE", "PARTIALLY_REPAID", "REPAID", "DEFAULTED", "CANCELLED"];
type Eip1193 = { request(args: { method: string; params?: unknown[] }): Promise<unknown>; on?(event: string, callback: (...args: unknown[]) => void): void };
declare global { interface Window { ethereum?: Eip1193 } }

export default function Loans() {
  const [account, setAccount] = useState("");
  const [chain, setChain] = useState<number | null>(null);
  const [balance, setBalance] = useState("—");
  const [ref, setRef] = useState("DEMO-LOAN-001");
  const [borrower, setBorrower] = useState("");
  const [principal, setPrincipal] = useState("0.01");
  const [totalDue, setTotalDue] = useState("0.011");
  const [dueHours, setDueHours] = useState("24");
  const [payment, setPayment] = useState("0.003");
  const [riskHashInput, setRiskHashInput] = useState("");
  const [loan, setLoan] = useState<Record<string, unknown> | null>(null);
  const [reputation, setReputation] = useState<Record<string, unknown> | null>(null);
  const [recentTx, setRecentTx] = useState<{ hash: string; loanId: string; reference: string; block: number; gas: string; timestamp: number }[]>([]);
  const [reconciliation, setReconciliation] = useState<{ counts: Record<string, number>; records: { loan_id: string; database_state: string; blockchain_state: string | null; status: string }[] } | null>(null);
  const [message, setMessage] = useState("Connect an injected EVM wallet. Transactions use real network receipts; demo amounts are native chain currency.");
  const [working, setWorking] = useState(false);
  const provider = useMemo(() => window.ethereum ? new BrowserProvider(window.ethereum as never) : null, []);
  const contract = useMemo(() => provider && ADDRESS ? new Contract(ADDRESS, ABI, provider) : null, [provider]);
  const loanId = id(ref.trim());
  const agreementHash = keccak256(toUtf8Bytes(JSON.stringify({ ref: ref.trim(), borrower, principal, totalDue, dueHours })));
  const committedAgreementHash = loan && String(loan.applicationId).toLowerCase() === loanId.toLowerCase() ? String(loan.agreementHash) : agreementHash;
  const fmtAmount = (x: unknown) => { try { return `${formatEther(BigInt(String(x)))} ETH`; } catch { return "—"; } };

  async function connect() {
    if (!window.ethereum || !provider) { setMessage("No injected wallet detected. Install MetaMask or another EVM wallet."); return; }
    try {
      const accounts = await provider.send("eth_requestAccounts", []);
      const network = await provider.getNetwork();
      const address = String(accounts[0] || "");
      setAccount(address); setChain(Number(network.chainId));
      setBorrower((current) => current || address);
      setBalance(formatEther(await provider.getBalance(address)));
      setMessage(Number(network.chainId) === CHAIN_ID ? "Wallet connected." : `Wrong network. Expected chain ID ${CHAIN_ID}.`);
      window.ethereum.on?.("accountsChanged", () => { setAccount(""); setLoan(null); });
      window.ethereum.on?.("chainChanged", () => window.location.reload());
    } catch (e) { setMessage(errorText(e)); }
  }
  async function switchNetwork() {
    try { await window.ethereum?.request({ method: "wallet_switchEthereumChain", params: [{ chainId: `0x${CHAIN_ID.toString(16)}` }] }); }
    catch (e) {
      const err = e as { code?: number | string };
      if ((err.code === 4902 || err.code === "4902") && WALLET_RPC_URL) {
        try { await window.ethereum?.request({ method: "wallet_addEthereumChain", params: [{ chainId: `0x${CHAIN_ID.toString(16)}`, chainName: "Configured EVM demo network", nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 }, rpcUrls: [WALLET_RPC_URL] }] }); }
        catch (addError) { setMessage(errorText(addError)); }
      } else setMessage(WALLET_RPC_URL ? errorText(e) : "Add this EVM network in your wallet using the configured RPC URL, then reconnect. No browser localhost RPC is assumed.");
    }
  }
  async function send(action: (c: Contract) => Promise<unknown>) {
    if (!provider || !contract || !account) { setMessage("Connect a wallet and configure VITE_LOAN_LIFECYCLE_ADDRESS first."); return; }
    setWorking(true); setMessage("Preparing transaction…");
    try {
      if (chain !== CHAIN_ID) throw new Error(`Wrong network: switch wallet to chain ${CHAIN_ID}.`);
      const signer = await provider.getSigner();
      const c = contract.connect(signer) as Contract;
      setMessage("Waiting for wallet approval…");
      const tx = await action(c) as { hash: string; wait: () => Promise<{ hash: string; blockNumber: number; status: number; gasUsed: bigint }> };
      setMessage(`Transaction submitted: ${tx.hash}. Waiting for confirmation…`);
      const receipt = await tx.wait();
      if (receipt.status !== 1) throw new Error("Transaction reverted.");
      const blockInfo = await provider.getBlock(receipt.blockNumber);
      setRecentTx((old) => [{ hash: receipt.hash, loanId, reference: ref.trim(), block: receipt.blockNumber, gas: String(receipt.gasUsed), timestamp: blockInfo?.timestamp ?? 0 }, ...old].slice(0, 5));
      setBalance(formatEther(await provider.getBalance(account)));
      setMessage(`Confirmed in block ${receipt.blockNumber}: ${receipt.hash}. Indexing confirmed event…`);
      try {
        await apiClient.post("/loans/chain-sync", { loan_id: loanId, transaction_hash: receipt.hash, application_reference: ref.trim() });
        setMessage(`Confirmed and indexed in block ${receipt.blockNumber}: ${receipt.hash}`);
      } catch {
        setMessage(`On-chain transaction confirmed in block ${receipt.blockNumber}, but MongoDB indexing failed. Transaction: ${receipt.hash}`);
      }
      await loadLoan();
    } catch (e) { setMessage(errorText(e)); }
    finally { setWorking(false); }
  }
  async function loadLoan() {
    if (!contract || !ref.trim()) return;
    try {
      const value = await contract.getLoan(loanId);
      setLoan(value as unknown as Record<string, unknown>);
      const borrowerAddress = String(value.borrower);
      const rep = await contract.getReputation(borrowerAddress);
      setReputation({ completed: String(rep[0].completedLoans), defaults: String(rep[0].defaults), onTime: String(rep[0].onTimeCompletions), late: String(rep[0].lateCompletions), borrowed: fmtAmount(rep[0].totalBorrowedWei), repaid: fmtAmount(rep[0].totalRepaidWei), streak: String(rep[0].repaymentStreak), score: String(rep[1]) });
      setBorrower(borrowerAddress);
    } catch (e) { setLoan(null); setMessage(`Loan not found or unavailable: ${errorText(e)}`); }
  }
  async function retrySync(tx: { hash: string; loanId: string; reference: string }) {
    try {
      await apiClient.post("/loans/chain-sync", { loan_id: tx.loanId, transaction_hash: tx.hash, application_reference: tx.reference });
      setMessage(`Verified chain event indexed in MongoDB: ${tx.hash}`);
    } catch (e) { setMessage(`Indexing retry failed: ${errorText(e)}`); }
  }
  async function reconcile() {
    try { const { data } = await apiClient.get("/loans/reconciliation"); setReconciliation(data); }
    catch (e) { setMessage(`Reconciliation unavailable: ${errorText(e)}`); }
  }
  function errorText(e: unknown) {
    const err = e as { code?: string | number; shortMessage?: string; message?: string };
    if (err.code === "ACTION_REJECTED" || err.code === 4001) return "Wallet request rejected by user.";
    return err.shortMessage || err.message || "Wallet transaction failed.";
  }
  const action = async (name: string) => {
    if (!contract) { setMessage("Configure the deployed lifecycle contract address to enable transactions."); return; }
    try {
      const principalWei = parseEther(principal), totalWei = parseEther(totalDue);
      const dueAt = Math.floor(Date.now() / 1000) + Number(dueHours) * 3600;
      if (name === "Create submitted loan") await send((c) => c.submitLoan(loanId, borrower, principalWei, totalWei, dueAt, agreementHash));
      if (name === "Record risk assessment") {
        if (!/^0x[0-9a-fA-F]{64}$/.test(riskHashInput)) { setMessage("Paste a real bytes32 assessment record hash. The app will not invent one."); return; }
        try {
          const { data } = await apiClient.get<{ record_hash: string }>(`/blockchain/record/${encodeURIComponent(ref.trim())}`);
          if (data.record_hash.toLowerCase() !== riskHashInput.toLowerCase()) { setMessage("Assessment hash does not match the registered on-chain application record."); return; }
        } catch (e) { setMessage(`Could not verify the assessment record with the API: ${errorText(e)}`); return; }
        await send((c) => c.assessRisk(loanId, riskHashInput));
      }
      if (name === "Approve loan") await send((c) => c.decide(loanId, true));
      if (name === "Reject loan") await send((c) => c.decide(loanId, false));
      if (name === "Borrower accepts agreement") await send((c) => c.acceptAgreement(loanId, committedAgreementHash));
      if (name === "Fund loan") await send((c) => c.fundLoan(loanId, { value: principalWei }));
      if (name === "Record repayment") await send((c) => c.repay(loanId, { value: parseEther(payment) }));
      if (name === "Mark default") await send((c) => c.markDefaulted(loanId));
    } catch (e) { setMessage(errorText(e)); }
  };
  const buttons = ["Create submitted loan", "Record risk assessment", "Approve loan", "Reject loan", "Borrower accepts agreement", "Fund loan", "Record repayment", "Mark default"];

  return <div className="space-y-5">
    <PageHeader title="On-chain Loan Lifecycle" description="Local/testnet EVM demo: borrower agreement acknowledgement, lender funding, ETH-denominated repayments, and contract-derived reputation." />
    <section className="card p-4 flex flex-wrap items-center gap-3">
      <Wallet size={18} className="text-accent-600" />
      <button className="btn-primary" onClick={connect}>{account ? `${account.slice(0, 6)}…${account.slice(-4)}` : "Connect wallet"}</button>
      {account && <><span className="text-sm">Chain {chain} {chain !== CHAIN_ID && <button className="underline text-amber-700" onClick={switchNetwork}>Switch to {CHAIN_ID}</button>}</span><span className="text-sm">Balance {balance} ETH</span></>}
      {!ADDRESS && <span className="text-xs text-amber-700">Contract unavailable: set VITE_LOAN_LIFECYCLE_ADDRESS</span>}
    </section>
    <section className="card p-5"><h2 className="font-semibold mb-4">Loan application parameters</h2><div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <label className="text-xs text-slate-600">Application ID (must have registered risk record)<input className="input-base mt-1" value={ref} onChange={(e) => setRef(e.target.value)} /></label>
      <label className="text-xs text-slate-600">Borrower wallet<input className="input-base mt-1" value={borrower} onChange={(e) => setBorrower(e.target.value)} placeholder="0x…" /></label>
      <label className="text-xs text-slate-600">Principal (ETH)<input className="input-base mt-1" value={principal} onChange={(e) => setPrincipal(e.target.value)} /></label>
      <label className="text-xs text-slate-600">Total due (ETH)<input className="input-base mt-1" value={totalDue} onChange={(e) => setTotalDue(e.target.value)} /></label>
      <label className="text-xs text-slate-600">Due in hours<input className="input-base mt-1" type="number" value={dueHours} onChange={(e) => setDueHours(e.target.value)} /></label>
      <label className="text-xs text-slate-600">Repayment amount (ETH)<input className="input-base mt-1" value={payment} onChange={(e) => setPayment(e.target.value)} /></label>
      <label className="text-xs text-slate-600 sm:col-span-2">Existing assessment record hash (bytes32)<input className="input-base mt-1 font-mono" value={riskHashInput} onChange={(e) => setRiskHashInput(e.target.value)} placeholder="0x… paste a real assessment hash" /></label>
    </div><div className="mt-3 break-all text-[11px] text-slate-500">On-chain loan ID: {loanId}<br/>Agreement hash (borrower acknowledgement binds to this): {committedAgreementHash}</div>
      <div className="mt-4 grid sm:grid-cols-2 lg:grid-cols-4 gap-2">{buttons.map((label) => <button key={label} className="btn-secondary text-xs" disabled={working || !ADDRESS} onClick={() => void action(label)}>{label}</button>)}</div>
      <button className="mt-3 text-sm text-accent-700 inline-flex items-center gap-2" onClick={() => void loadLoan()}><RefreshCw size={14}/>Load chain loan & reputation</button>
    </section>
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm break-all" role="status">{working && <span>Transaction pending · </span>}{message}</div>
    {loan && <section className="grid lg:grid-cols-2 gap-4">
      <article className="card p-5"><h2 className="font-semibold flex gap-2 items-center"><CircleDollarSign size={17}/>Contract loan state</h2><dl className="grid grid-cols-2 gap-3 mt-4 text-sm"><dt>State</dt><dd className="font-semibold">{STATES[Number(loan.state)]}</dd><dt>Borrower</dt><dd className="break-all">{String(loan.borrower)}</dd><dt>Lender</dt><dd className="break-all">{String(loan.lender)}</dd><dt>Principal</dt><dd>{fmtAmount(loan.principalWei)}</dd><dt>Total due</dt><dd>{fmtAmount(loan.totalDueWei)}</dd><dt>Repaid</dt><dd>{fmtAmount(loan.repaidWei)}</dd><dt>Agreement accepted</dt><dd>{String(loan.agreementAccepted)}</dd></dl></article>
      {reputation && <article className="card p-5"><h2 className="font-semibold flex gap-2 items-center"><ShieldCheck size={17}/>Verifiable borrower reputation</h2><p className="text-3xl font-bold mt-4">{String(reputation.score)}<span className="text-sm font-normal text-slate-500"> / 1000 demo score</span></p><div className="text-sm mt-3 space-y-1"><p>Completed loans: {String(reputation.completed)}</p><p>Defaults: {String(reputation.defaults)}</p><p>On-time completions: {String(reputation.onTime)}</p><p>Late completions: {String(reputation.late)}</p><p>Total borrowed: {String(reputation.borrowed)}</p><p>Total repaid: {String(reputation.repaid)}</p><p>On-time streak: {String(reputation.streak)}</p></div><p className="text-xs text-slate-500 mt-3">Contract-derived reputation; distinct from model PD. Native-chain currency values are demo-only, not fiat.</p></article>}
    </section>}
    <section className="card p-4"><div className="flex items-center justify-between"><h2 className="font-semibold">Database ↔ blockchain reconciliation</h2><button className="btn-secondary text-xs" onClick={() => void reconcile()}>Run reconciliation</button></div>{reconciliation && <><div className="flex flex-wrap gap-3 mt-3 text-xs">{Object.entries(reconciliation.counts).map(([key, value]) => <span className="rounded bg-slate-100 px-2 py-1" key={key}>{key}: {value}</span>)}</div><div className="mt-3 space-y-2">{reconciliation.records.map((row) => <div className="text-xs flex flex-wrap gap-2 border-t pt-2" key={row.loan_id}><code>{row.loan_id}</code><span>{row.database_state} / {row.blockchain_state ?? "unavailable"}</span><b>{row.status}</b></div>)}</div></>}</section>
    {recentTx.length > 0 && <section className="card p-4"><h2 className="font-semibold">Recent wallet transactions</h2>{recentTx.map((tx) => <div className="text-xs flex flex-wrap items-center gap-3 mt-2" key={tx.hash}><code className="font-mono break-all">{tx.hash}</code><span>Block {tx.block}</span><span>Gas {tx.gas}</span><span>{new Date(tx.timestamp * 1000).toLocaleString()}</span><button className="underline text-accent-700" onClick={() => void retrySync(tx)}>Retry database index</button></div>)}</section>}
    <p className="text-xs text-slate-500">Risk assessment and loan parameters in this demo are submitted by wallet-connected users or configured operators. A transaction is not proof of model correctness. Use only a local chain/testnet and test currency.</p>
  </div>;
}
