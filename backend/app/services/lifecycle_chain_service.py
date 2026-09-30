"""Read/verify LoanLifecycle contract state and transaction events via web3.py."""
import json
import os
from web3 import Web3
from web3.logs import DISCARD
from app.config import settings

STATES = ["NONE", "SUBMITTED", "RISK_ASSESSED", "APPROVED", "REJECTED", "FUNDED", "ACTIVE", "PARTIALLY_REPAID", "REPAID", "DEFAULTED", "CANCELLED"]
ABI = [
    {"type":"function","name":"submitLoan","stateMutability":"nonpayable","inputs":[{"name":"loanId","type":"bytes32"},{"name":"borrower","type":"address"},{"name":"principalWei","type":"uint256"},{"name":"totalDueWei","type":"uint256"},{"name":"dueAt","type":"uint256"},{"name":"agreementHash","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"assessRisk","stateMutability":"nonpayable","inputs":[{"name":"loanId","type":"bytes32"},{"name":"assessmentHash","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"decide","stateMutability":"nonpayable","inputs":[{"name":"loanId","type":"bytes32"},{"name":"approved","type":"bool"}],"outputs":[]},
    {"type":"function","name":"acceptAgreement","stateMutability":"nonpayable","inputs":[{"name":"loanId","type":"bytes32"},{"name":"agreementHash","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"fundLoan","stateMutability":"payable","inputs":[{"name":"loanId","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"repay","stateMutability":"payable","inputs":[{"name":"loanId","type":"bytes32"}],"outputs":[]},
    {"type":"function","name":"getLoan","stateMutability":"view","inputs":[{"name":"loanId","type":"bytes32"}],"outputs":[{"name":"loan","type":"tuple","components":[{"name":"applicationId","type":"bytes32"},{"name":"assessmentHash","type":"bytes32"},{"name":"agreementHash","type":"bytes32"},{"name":"borrower","type":"address"},{"name":"lender","type":"address"},{"name":"principalWei","type":"uint256"},{"name":"totalDueWei","type":"uint256"},{"name":"repaidWei","type":"uint256"},{"name":"dueAt","type":"uint256"},{"name":"createdAt","type":"uint256"},{"name":"state","type":"uint8"},{"name":"agreementAccepted","type":"bool"}]}]},
    {"type":"event","name":"LoanSubmitted","anonymous":False,"inputs":[{"indexed":True,"name":"loanId","type":"bytes32"},{"indexed":True,"name":"borrower","type":"address"},{"indexed":False,"name":"principalWei","type":"uint256"}]},
    {"type":"event","name":"LoanStateChanged","anonymous":False,"inputs":[{"indexed":True,"name":"loanId","type":"bytes32"},{"indexed":False,"name":"previousState","type":"uint8"},{"indexed":False,"name":"nextState","type":"uint8"},{"indexed":False,"name":"timestamp","type":"uint256"}]},
    {"type":"event","name":"AgreementAcknowledged","anonymous":False,"inputs":[{"indexed":True,"name":"loanId","type":"bytes32"},{"indexed":True,"name":"borrower","type":"address"},{"indexed":False,"name":"agreementHash","type":"bytes32"}]},
    {"type":"event","name":"LoanFunded","anonymous":False,"inputs":[{"indexed":True,"name":"loanId","type":"bytes32"},{"indexed":True,"name":"lender","type":"address"},{"indexed":False,"name":"amountWei","type":"uint256"},{"indexed":False,"name":"agreementHash","type":"bytes32"}]},
    {"type":"event","name":"RepaymentRecorded","anonymous":False,"inputs":[{"indexed":True,"name":"loanId","type":"bytes32"},{"indexed":True,"name":"borrower","type":"address"},{"indexed":False,"name":"amountWei","type":"uint256"},{"indexed":False,"name":"repaidWei","type":"uint256"},{"indexed":False,"name":"outstandingWei","type":"uint256"},{"indexed":False,"name":"late","type":"bool"}]},
]


class LifecycleChain:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL, request_kwargs={"timeout": 10}))
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "blockchain", "loan-lifecycle-address.json"))
        deployment = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as stream:
                deployment = json.load(stream)
        address = settings.LOAN_LIFECYCLE_CONTRACT_ADDRESS or deployment.get("contractAddress", "")
        self.deployment_block = settings.BLOCKCHAIN_START_BLOCK if settings.BLOCKCHAIN_START_BLOCK is not None else int(deployment.get("deploymentBlock", 0))
        self.address = Web3.to_checksum_address(address) if address else ""
        self.contract = self.w3.eth.contract(address=self.address, abi=ABI) if self.address else None

    def _require(self):
        if self.contract is None or not self.w3.is_connected():
            raise RuntimeError("Loan lifecycle contract is not configured or RPC unavailable")
        if self.w3.eth.chain_id != settings.BLOCKCHAIN_CHAIN_ID:
            raise RuntimeError("RPC chain ID does not match configured BLOCKCHAIN_CHAIN_ID")
        if not self.w3.eth.get_code(self.address):
            raise RuntimeError("No contract bytecode found at configured LoanLifecycle address")

    @staticmethod
    def normalize_id(loan_id: str) -> bytes:
        value = Web3.to_bytes(hexstr=loan_id)
        if len(value) != 32:
            raise ValueError("loan_id must be a 32-byte hex value")
        return value

    def loan(self, loan_id: str) -> dict:
        self._require()
        raw = self.contract.functions.getLoan(self.normalize_id(loan_id)).call()
        state = int(raw[10])
        return {
            "loan_id": loan_id.lower(), "contract_state": STATES[state], "state_code": state,
            "borrower": raw[3], "lender": raw[4], "principal_wei": str(raw[5]),
            "total_due_wei": str(raw[6]), "repaid_wei": str(raw[7]),
            "due_at": int(raw[8]), "assessment_hash": Web3.to_hex(raw[1]),
            "agreement_hash": Web3.to_hex(raw[2]), "agreement_accepted": bool(raw[11]),
        }

    def submitted_loan_ids(self) -> set[str]:
        """Discover on-chain submissions so missing Mongo snapshots are visible as PENDING."""
        self._require()
        latest = self.w3.eth.block_number
        discovered: set[str] = set()
        # Chunk log queries to avoid common RPC provider eth_getLogs range limits.
        start = self.deployment_block
        step = 2_000
        while start <= latest:
            end = min(start + step - 1, latest)
            events = self.contract.events.LoanSubmitted().get_logs(from_block=start, to_block=end)
            discovered.update(Web3.to_hex(event["args"]["loanId"]).lower() for event in events)
            start = end + 1
        return discovered

    def verify_transaction(self, transaction_hash: str, loan_id: str) -> dict:
        self._require()
        receipt = self.w3.eth.get_transaction_receipt(transaction_hash)
        if receipt is None or receipt.status != 1:
            raise ValueError("transaction is not confirmed successfully")
        if not receipt.to or Web3.to_checksum_address(receipt.to) != self.address:
            raise ValueError("transaction was not sent to configured LoanLifecycle contract")
        logs = self.contract.events.LoanStateChanged().process_receipt(receipt, errors=DISCARD)
        loan_id_bytes = self.normalize_id(loan_id)
        matching = [log for log in logs if bytes(log["args"]["loanId"]) == loan_id_bytes]
        # Funding/repayment/acceptance may produce only specialized events; validate any known event.
        if not matching:
            for event_name in ("AgreementAcknowledged", "LoanFunded", "RepaymentRecorded"):
                try:
                    event_logs = getattr(self.contract.events, event_name)().process_receipt(receipt, errors=DISCARD)
                    if any(bytes(log["args"]["loanId"]) == loan_id_bytes for log in event_logs):
                        matching = event_logs
                        break
                except Exception:
                    continue
        if not matching:
            raise ValueError("transaction has no lifecycle event for this loan ID")
        block = self.w3.eth.get_block(receipt.blockNumber)
        return {"transaction_hash": Web3.to_hex(receipt.transactionHash), "block_number": int(receipt.blockNumber), "gas_used": int(receipt.gasUsed), "timestamp": int(block.timestamp), "contract_address": self.address}
