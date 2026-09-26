import { expect } from "chai";
import { ethers } from "hardhat";
import { anyValue } from "@nomicfoundation/hardhat-chai-matchers/withArgs";
import { LoanRecordRegistry } from "../typechain-types";

describe("LoanRecordRegistry", function () {
  async function deployFixture() {
    const [owner, registrarTwo] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("LoanRecordRegistry");
    const contract = (await Factory.deploy()) as unknown as LoanRecordRegistry;
    await contract.waitForDeployment();
    return { contract, owner, registrarTwo };
  }

  const applicationId = "LN-000001";
  const recordHash = ethers.keccak256(ethers.toUtf8Bytes("canonical-record-v1"));
  const riskCategory = "LOW";

  it("registers a new loan record and emits LoanRecordRegistered", async function () {
    const { contract, owner } = await deployFixture();

    await expect(contract.registerRecord(applicationId, recordHash, riskCategory))
      .to.emit(contract, "LoanRecordRegistered")
      .withArgs(applicationId, applicationId, recordHash, riskCategory, anyValue, owner.address);

    expect(await contract.totalRecords()).to.equal(1n);
  });

  it("stores the correct record data and can be retrieved with getRecord", async function () {
    const { contract, owner } = await deployFixture();
    await (await contract.registerRecord(applicationId, recordHash, riskCategory)).wait();

    const record = await contract.getRecord(applicationId);
    expect(record[0]).to.equal(applicationId);
    expect(record[1]).to.equal(recordHash);
    expect(record[2]).to.equal(riskCategory);
    expect(record[4]).to.equal(owner.address);
  });

  it("recordExists returns false before registration and true after", async function () {
    const { contract } = await deployFixture();
    expect(await contract.recordExists(applicationId)).to.equal(false);
    await (await contract.registerRecord(applicationId, recordHash, riskCategory)).wait();
    expect(await contract.recordExists(applicationId)).to.equal(true);
  });

  it("prevents duplicate registration of the same applicationId", async function () {
    const { contract } = await deployFixture();
    await (await contract.registerRecord(applicationId, recordHash, riskCategory)).wait();

    await expect(
      contract.registerRecord(applicationId, recordHash, riskCategory)
    ).to.be.revertedWith("Record already registered");
  });

  it("verifyRecord returns true for a matching hash and false for a tampered hash", async function () {
    const { contract } = await deployFixture();
    await (await contract.registerRecord(applicationId, recordHash, riskCategory)).wait();

    expect(await contract.verifyRecord(applicationId, recordHash)).to.equal(true);

    const tamperedHash = ethers.keccak256(ethers.toUtf8Bytes("tampered-record"));
    expect(await contract.verifyRecord(applicationId, tamperedHash)).to.equal(false);
  });

  it("reverts when querying a record that does not exist", async function () {
    const { contract } = await deployFixture();
    await expect(contract.getRecord("LN-DOES-NOT-EXIST")).to.be.revertedWith("Record not found");
    await expect(
      contract.verifyRecord("LN-DOES-NOT-EXIST", recordHash)
    ).to.be.revertedWith("Record not found");
  });

  it("returns a sensible registration timestamp", async function () {
    const { contract } = await deployFixture();
    const before = Math.floor(Date.now() / 1000) - 5;
    await (await contract.registerRecord(applicationId, recordHash, riskCategory)).wait();
    const ts = await contract.getRecordTimestamp(applicationId);
    expect(Number(ts)).to.be.greaterThanOrEqual(before);
  });

  it("allows a different account to register a different applicationId (registrar tracked correctly)", async function () {
    const { contract, registrarTwo } = await deployFixture();
    await (
      await contract.connect(registrarTwo).registerRecord("LN-000002", recordHash, "MEDIUM")
    ).wait();

    const record = await contract.getRecord("LN-000002");
    expect(record[4]).to.equal(registrarTwo.address);
  });
});
