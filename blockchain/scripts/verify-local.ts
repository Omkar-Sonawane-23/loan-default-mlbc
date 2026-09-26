import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

/**
 * Small sanity-check script: registers a dummy record on whichever
 * deployed contract address is in deployed-address.json, then reads it
 * back and verifies the hash matches. Useful for confirming a local
 * deployment is functioning before wiring up the FastAPI backend.
 */
async function main() {
  const deployedPath = path.join(__dirname, "..", "deployed-address.json");
  if (!fs.existsSync(deployedPath)) {
    throw new Error("deployed-address.json not found. Run deploy.ts first.");
  }
  const { contractAddress } = JSON.parse(fs.readFileSync(deployedPath, "utf-8"));

  const contract = await ethers.getContractAt("LoanRecordRegistry", contractAddress);

  const applicationId = "LN-VERIFY-TEST";
  const sampleHash = ethers.keccak256(ethers.toUtf8Bytes("sample-canonical-record"));

  const alreadyExists = await contract.recordExists(applicationId);
  if (!alreadyExists) {
    const tx = await contract.registerRecord(applicationId, sampleHash, "LOW");
    const receipt = await tx.wait();
    console.log("Registered test record. Tx hash:", receipt?.hash);
  } else {
    console.log("Test record already exists, skipping registration.");
  }

  const record = await contract.getRecord(applicationId);
  console.log("Fetched record:", record);

  const verified = await contract.verifyRecord(applicationId, sampleHash);
  console.log("Verification result:", verified ? "VERIFIED" : "VERIFICATION FAILED");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
