"""
blockchain_service.py

Wraps web3.py communication with the deployed LoanRecordRegistry smart
contract on the local Hardhat network. Every function here performs a
REAL RPC call / transaction against whatever node is configured via
BLOCKCHAIN_RPC_URL -- there are no simulated transaction hashes.
"""
import json
import os
import time

from web3 import Web3
from web3.exceptions import ContractLogicError

from app.config import settings

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "applicationIdIndexed", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "applicationId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "recordHash", "type": "bytes32"},
            {"indexed": False, "internalType": "string", "name": "riskCategory", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "registrar", "type": "address"},
        ],
        "name": "LoanRecordRegistered",
        "type": "event",
    },
    {
        "inputs": [{"internalType": "string", "name": "applicationId", "type": "string"}],
        "name": "getRecord",
        "outputs": [
            {"internalType": "string", "name": "applicationId_", "type": "string"},
            {"internalType": "bytes32", "name": "recordHash", "type": "bytes32"},
            {"internalType": "string", "name": "riskCategory", "type": "string"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "address", "name": "registrar", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "applicationId", "type": "string"}],
        "name": "getRecordTimestamp",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "applicationId", "type": "string"}],
        "name": "recordExists",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "applicationId", "type": "string"},
            {"internalType": "bytes32", "name": "recordHash", "type": "bytes32"},
            {"internalType": "string", "name": "riskCategory", "type": "string"},
        ],
        "name": "registerRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalRecords",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "applicationId", "type": "string"},
            {"internalType": "bytes32", "name": "currentHash", "type": "bytes32"},
        ],
        "name": "verifyRecord",
        "outputs": [{"internalType": "bool", "name": "verified", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class BlockchainNotConfiguredError(Exception):
    pass


class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL, request_kwargs={"timeout": 10}))
        self.contract_address = settings.BLOCKCHAIN_CONTRACT_ADDRESS or self._load_deployed_address()
        self.private_key = settings.BLOCKCHAIN_PRIVATE_KEY or self._default_dev_key()
        self.chain_id = settings.BLOCKCHAIN_CHAIN_ID

        self._contract = None
        if self.contract_address:
            self._contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address), abi=CONTRACT_ABI
            )

    @staticmethod
    def _load_deployed_address() -> str:
        path = os.path.normpath(
            os.path.join(_BASE_DIR, "..", "..", "blockchain", "deployed-address.json")
        )
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            return data.get("contractAddress", "")
        return ""

    @staticmethod
    def _default_dev_key() -> str:
        # Hardhat's well-known, publicly documented account #0 private key.
        # Used only for the local development network (chain id 31337).
        # This is NOT a secret and must never be used on a real network.
        return "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    def is_available(self) -> bool:
        try:
            return self.w3.is_connected() and self._contract is not None
        except Exception:
            return False

    def _require_contract(self):
        if self._contract is None:
            raise BlockchainNotConfiguredError(
                "Smart contract address is not configured. Deploy the contract "
                "(see blockchain/README.md) and set BLOCKCHAIN_CONTRACT_ADDRESS."
            )

    def _account(self):
        return self.w3.eth.account.from_key(self.private_key)

    def register_record(self, application_id: str, record_hash_hex: str, risk_category: str) -> dict:
        """Sends a real transaction to registerRecord() and waits for the receipt."""
        self._require_contract()
        account = self._account()

        record_hash_bytes = Web3.to_bytes(hexstr=record_hash_hex)

        nonce = self.w3.eth.get_transaction_count(account.address)
        tx = self._contract.functions.registerRecord(
            application_id, record_hash_bytes, risk_category
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "chainId": self.chain_id,
            "gas": 300000,
            "gasPrice": self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        block = self.w3.eth.get_block(receipt["blockNumber"])

        return {
            "transaction_hash": "0x" + receipt["transactionHash"].hex().removeprefix("0x"),
            "block_number": receipt["blockNumber"],
            "contract_address": self._contract.address,
            "chain_id": self.chain_id,
            "registered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(block["timestamp"])),
            "gas_used": receipt["gasUsed"],
        }

    def get_record(self, application_id: str) -> dict:
        self._require_contract()
        try:
            result = self._contract.functions.getRecord(application_id).call()
        except ContractLogicError:
            return None
        return {
            "application_id": result[0],
            "record_hash": "0x" + result[1].hex(),
            "risk_category": result[2],
            "timestamp": result[3],
            "registrar": result[4],
        }

    def record_exists(self, application_id: str) -> bool:
        self._require_contract()
        return self._contract.functions.recordExists(application_id).call()

    def verify_record(self, application_id: str, current_hash_hex: str) -> bool:
        self._require_contract()
        current_hash_bytes = Web3.to_bytes(hexstr=current_hash_hex)
        return self._contract.functions.verifyRecord(application_id, current_hash_bytes).call()

    def total_records(self) -> int:
        self._require_contract()
        return self._contract.functions.totalRecords().call()


_instance: BlockchainService | None = None


def get_blockchain_service() -> BlockchainService:
    global _instance
    if _instance is None:
        _instance = BlockchainService()
    return _instance
