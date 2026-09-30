import { expect } from "chai";
import { ethers } from "hardhat";

describe("LoanLifecycle", () => {
  const principal = ethers.parseEther("1");
  const due = ethers.parseEther("1.1");
  const agreement = ethers.keccak256(ethers.toUtf8Bytes("agreement-v1"));
  const assessment = ethers.keccak256(ethers.toUtf8Bytes("assessment-v1"));
  async function fixture() {
    const [owner, borrower, lender, stranger] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("LoanLifecycle");
    const contract = await Factory.deploy();
    await contract.waitForDeployment();
    const id = ethers.keccak256(ethers.toUtf8Bytes("application-001"));
    const dueAt = BigInt((await ethers.provider.getBlock("latest"))!.timestamp + 3600);
    const create = async () => contract.submitLoan(id, borrower.address, principal, due, dueAt, agreement);
    const assessApprove = async () => { await contract.assessRisk(id, assessment); await contract.decide(id, true); };
    const setupApproved = async () => { await create(); await assessApprove(); };
    const setupActive = async () => { await setupApproved(); await contract.connect(borrower).acceptAgreement(id, agreement); await contract.connect(lender).fundLoan(id, { value: principal }); };
    return { contract, owner, borrower, lender, stranger, id, dueAt, create, assessApprove, setupApproved, setupActive };
  }

  it("enforces submit, risk assessment, approval, funding and event transitions", async () => {
    const { contract, borrower, lender, id, create, setupApproved } = await fixture();
    await expect(contract.connect(lender).submitLoan(id, borrower.address, principal, due, 9999999999n, agreement)).to.be.revertedWithCustomError(contract, "Unauthorized");
    await create();
    await expect(contract.decide(id, true)).to.be.revertedWithCustomError(contract, "InvalidState");
    await contract.assessRisk(id, assessment);
    await contract.decide(id, true);
    await expect(contract.connect(lender).fundLoan(id, { value: principal })).to.be.revertedWithCustomError(contract, "InvalidState");
    await expect(contract.connect(borrower).acceptAgreement(id, agreement)).to.emit(contract, "AgreementAcknowledged");
    await expect(contract.connect(lender).fundLoan(id, { value: principal })).to.emit(contract, "LoanFunded");
    expect((await contract.getLoan(id)).state).to.equal(6n); // ACTIVE
    expect(await contract.totalLoans()).to.equal(1n);
  });

  it("prevents duplicate applications, invalid amounts and unauthorized lifecycle writes", async () => {
    const { contract, borrower, stranger, id, create, setupApproved } = await fixture();
    await create();
    await expect(create()).to.be.revertedWithCustomError(contract, "InvalidLoan");
    await expect(contract.connect(stranger).assessRisk(id, assessment)).to.be.revertedWithCustomError(contract, "Unauthorized");
    await contract.assessRisk(id, assessment);
    await contract.decide(id, true);
    await contract.connect(borrower).acceptAgreement(id, agreement);
    await expect(contract.connect(stranger).fundLoan(id, { value: 5n })).to.be.revertedWithCustomError(contract, "InvalidAmount");
  });

  it("records partial and full repayments and derives on-time reputation", async () => {
    const { contract, borrower, lender, id, setupActive } = await fixture();
    await setupActive();
    await expect(contract.connect(borrower).repay(id, { value: ethers.parseEther("0.4") })).to.emit(contract, "RepaymentRecorded");
    expect((await contract.getLoan(id)).state).to.equal(7n); // PARTIALLY_REPAID
    await contract.connect(borrower).repay(id, { value: ethers.parseEther("0.7") });
    const loan = await contract.getLoan(id);
    expect(loan.state).to.equal(8n); // REPAID
    expect(loan.repaidWei).to.equal(due);
    const [rep, score] = await contract.getReputation(borrower.address);
    expect(rep.completedLoans).to.equal(1n);
    expect(rep.onTimeCompletions).to.equal(1n);
    expect(rep.totalBorrowedWei).to.equal(principal);
    expect(score).to.equal(1000n);
    expect(await ethers.provider.getBalance(contract.getAddress())).to.equal(0n);
    expect(lender.address).not.to.equal(ethers.ZeroAddress);
  });

  it("rejects wrong borrower, zero payment and overpayment", async () => {
    const { contract, borrower, stranger, id, setupActive } = await fixture();
    await setupActive();
    await expect(contract.connect(stranger).repay(id, { value: 1n })).to.be.revertedWithCustomError(contract, "Unauthorized");
    await expect(contract.connect(borrower).repay(id, { value: 0n })).to.be.revertedWithCustomError(contract, "Unauthorized");
    await expect(contract.connect(borrower).repay(id, { value: due + 1n })).to.be.revertedWithCustomError(contract, "InvalidAmount");
  });

  it("only marks default after due date and updates reputation from contract state", async () => {
    const { contract, borrower, id, setupActive, dueAt } = await fixture();
    await setupActive();
    await expect(contract.markDefaulted(id)).to.be.revertedWithCustomError(contract, "InvalidState");
    await ethers.provider.send("evm_setNextBlockTimestamp", [Number(dueAt + 1n)]);
    await contract.markDefaulted(id);
    expect((await contract.getLoan(id)).state).to.equal(9n);
    const [rep, score] = await contract.getReputation(borrower.address);
    expect(rep.defaults).to.equal(1n);
    expect(score).to.equal(0n);
  });

  it("supports rejection, cancellation and pause control", async () => {
    const { contract, borrower, id, create } = await fixture();
    await create();
    await contract.assessRisk(id, assessment);
    await contract.decide(id, false);
    expect((await contract.getLoan(id)).state).to.equal(4n);
    const id2 = ethers.keccak256(ethers.toUtf8Bytes("application-002"));
    await contract.submitLoan(id2, borrower.address, principal, due, BigInt((await ethers.provider.getBlock("latest"))!.timestamp + 4000), agreement);
    await contract.cancel(id2);
    await contract.setPaused(true);
    await expect(contract.submitLoan(ethers.keccak256(ethers.toUtf8Bytes("application-003")), borrower.address, principal, due, 9999999999n, agreement)).to.be.revertedWithCustomError(contract, "Paused");
  });

  it("allows on-time and late completions to affect reputation differently", async () => {
    const { contract, borrower, lender, id, setupActive, dueAt } = await fixture();
    await setupActive();
    await ethers.provider.send("evm_setNextBlockTimestamp", [Number(dueAt + 1n)]);
    await contract.connect(borrower).repay(id, { value: due });
    const [rep, score] = await contract.getReputation(borrower.address);
    expect(rep.lateCompletions).to.equal(1n);
    expect(rep.onTimeCompletions).to.equal(0n);
    expect(score).to.equal(600n);
    expect(await ethers.provider.getBalance(contract.getAddress())).to.equal(0n);
    expect(lender.address).to.be.properAddress;
  });
});
