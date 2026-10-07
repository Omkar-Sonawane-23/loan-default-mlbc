"""Application configuration, loaded from environment variables / .env."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "loan_default_mlbc")

    # Backend
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8001"))

    # Blockchain
    BLOCKCHAIN_RPC_URL: str = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
    BLOCKCHAIN_PRIVATE_KEY: str = os.getenv("BLOCKCHAIN_PRIVATE_KEY", "")
    BLOCKCHAIN_CONTRACT_ADDRESS: str = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS", "")
    LOAN_LIFECYCLE_CONTRACT_ADDRESS: str = os.getenv("LOAN_LIFECYCLE_CONTRACT_ADDRESS", "")
    BLOCKCHAIN_CHAIN_ID: int = int(os.getenv("BLOCKCHAIN_CHAIN_ID", "31337"))
    BLOCKCHAIN_START_BLOCK: int | None = int(os.environ["BLOCKCHAIN_START_BLOCK"]) if os.getenv("BLOCKCHAIN_START_BLOCK") else None

    # ML
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../ml/models/loan_default_model.joblib")
    MODEL_METADATA_PATH: str = os.getenv("MODEL_METADATA_PATH", "../ml/models/model_metadata.json")
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "rf-v1")
    # Demonstration assumption only; configure after validation for any use beyond research.
    LOSS_GIVEN_DEFAULT: float = float(os.getenv("LOSS_GIVEN_DEFAULT", "0.45"))

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Misc
    APP_NAME: str = "LoanDefault MLBC API"
    APP_VERSION: str = "1.0.0"

    ACADEMIC_DISCLAIMER: str = (
        "This system is an academic Machine Learning and Blockchain demonstration. "
        "The predicted default probability is an estimated model output and is not "
        "financial advice, a guaranteed prediction, or an automated loan "
        "approval/rejection decision."
    )


settings = Settings()
