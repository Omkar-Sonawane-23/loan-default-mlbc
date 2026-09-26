import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

/**
 * Deploys LoanRecordRegistry to whichever network Hardhat is pointed at
 * (local in-memory `hardhat` network, or a persistent `localhost` node
 * started with `npx hardhat node`).
 *
 * After deployment, writes the deployed address + network info to
 * blockchain/deployed-address.json so the FastAPI backend (via web3.py)
 * and the frontend Settings page can pick it up.
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying LoanRecordRegistry with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Deployer balance:", ethers.formatEther(balance), "ETH");

  const Factory = await ethers.getContractFactory("LoanRecordRegistry");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const network = await ethers.provider.getNetwork();

  console.log("LoanRecordRegistry deployed to:", address);
  console.log("Chain ID:", network.chainId.toString());

  const output = {
    contractAddress: address,
    chainId: Number(network.chainId),
    deployerAddress: deployer.address,
    deployedAt: new Date().toISOString(),
  };

  const outPath = path.join(__dirname, "..", "deployed-address.json");
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log("Deployment info written to:", outPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
