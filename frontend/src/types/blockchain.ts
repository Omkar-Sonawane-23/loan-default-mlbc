export interface BlockchainRegisterResponse {
  application_id: string;
  record_hash: string;
  transaction_hash: string;
  block_number: number;
  contract_address: string;
  chain_id: number;
  registered_at: string;
  gas_used?: number;
}

export interface BlockchainVerifyResponse {
  application_id: string;
  verified: boolean;
  current_database_hash: string;
  blockchain_hash: string | null;
  transaction_hash: string | null;
  block_number: number | null;
  registered_at: string | null;
  message: string;
}

export interface BlockchainStatus {
  available: boolean;
  rpc_url?: string;
  chain_id?: number;
  contract_address?: string | null;
  total_records_on_chain?: number | null;
  error?: string;
}

export interface BlockchainTransaction {
  application_id: string;
  risk_category: string;
  registered: boolean;
  record_hash: string;
  transaction_hash: string;
  block_number: number;
  contract_address: string;
  chain_id: number;
  registered_at: string;
}
