import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  const [deployer] = await ethers.getSigners();
  const Factory = await ethers.getContractFactory("LoanLifecycle");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();
  const deploymentReceipt = await contract.deploymentTransaction()?.wait();
  const network = await ethers.provider.getNetwork();
  const output = { contractAddress: await contract.getAddress(), chainId: Number(network.chainId), deploymentBlock: deploymentReceipt?.blockNumber ?? 0, deployerAddress: deployer.address, deployedAt: new Date().toISOString() };
  const outPath = path.join(__dirname, "..", "loan-lifecycle-address.json");
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log("LoanLifecycle deployed:", JSON.stringify(output, null, 2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
