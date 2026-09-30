// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title LoanLifecycle
/// @notice Demo ETH-denominated loan state machine. No fiat/stablecoin oracle is used.
///         Sensitive borrower details remain off-chain; IDs and hashes are opaque.
contract LoanLifecycle {
    enum State { NONE, SUBMITTED, RISK_ASSESSED, APPROVED, REJECTED, FUNDED, ACTIVE, PARTIALLY_REPAID, REPAID, DEFAULTED, CANCELLED }

    struct Loan {
        bytes32 applicationId;
        bytes32 assessmentHash;
        bytes32 agreementHash;
        address borrower;
        address lender;
        uint256 principalWei;
        uint256 totalDueWei;
        uint256 repaidWei;
        uint256 dueAt;
        uint256 createdAt;
        State state;
        bool agreementAccepted;
    }

    struct Reputation {
        uint256 completedLoans;
        uint256 defaults;
        uint256 onTimeCompletions;
        uint256 lateCompletions;
        uint256 totalBorrowedWei;
        uint256 totalRepaidWei;
        uint256 repaymentStreak;
    }

    address public owner;
    bool public paused;
    uint256 private entered;
    mapping(address => bool) public operators;
    mapping(bytes32 => Loan) private loans;
    mapping(address => Reputation) private reputations;
    uint256 public totalLoans;

    error Unauthorized();
    error Paused();
    error InvalidLoan();
    error InvalidState();
    error InvalidAmount();
    error TransferFailed();
    error ReentrantCall();

    event OperatorUpdated(address indexed operator, bool enabled);
    event LoanSubmitted(bytes32 indexed loanId, address indexed borrower, uint256 principalWei);
    event RiskAssessed(bytes32 indexed loanId, bytes32 indexed assessmentHash);
    event LoanStateChanged(bytes32 indexed loanId, State previousState, State nextState, uint256 timestamp);
    event AgreementAcknowledged(bytes32 indexed loanId, address indexed borrower, bytes32 agreementHash);
    event LoanFunded(bytes32 indexed loanId, address indexed lender, uint256 amountWei, bytes32 agreementHash);
    event RepaymentRecorded(bytes32 indexed loanId, address indexed borrower, uint256 amountWei, uint256 repaidWei, uint256 outstandingWei, bool late);
    event ReputationChanged(address indexed borrower, uint256 score, uint256 completedLoans, uint256 defaults);

    constructor() { owner = msg.sender; operators[msg.sender] = true; }

    modifier onlyOwner() { if (msg.sender != owner) revert Unauthorized(); _; }
    modifier onlyOperator() { if (!operators[msg.sender]) revert Unauthorized(); _; }
    modifier whenNotPaused() { if (paused) revert Paused(); _; }
    modifier nonReentrant() { if (entered != 0) revert ReentrantCall(); entered = 1; _; entered = 0; }

    function setOperator(address account, bool enabled) external onlyOwner {
        if (account == address(0)) revert InvalidAmount();
        operators[account] = enabled;
        emit OperatorUpdated(account, enabled);
    }

    function setPaused(bool value) external onlyOwner { paused = value; }

    function submitLoan(bytes32 loanId, address borrower, uint256 principalWei, uint256 totalDueWei, uint256 dueAt, bytes32 agreementHash) external onlyOperator whenNotPaused {
        if (loanId == bytes32(0) || loans[loanId].state != State.NONE || borrower == address(0)) revert InvalidLoan();
        if (principalWei == 0 || totalDueWei < principalWei || dueAt <= block.timestamp || agreementHash == bytes32(0)) revert InvalidAmount();
        loans[loanId] = Loan(loanId, bytes32(0), agreementHash, borrower, address(0), principalWei, totalDueWei, 0, dueAt, block.timestamp, State.SUBMITTED, false);
        totalLoans++;
        emit LoanSubmitted(loanId, borrower, principalWei);
        emit LoanStateChanged(loanId, State.NONE, State.SUBMITTED, block.timestamp);
    }

    function assessRisk(bytes32 loanId, bytes32 assessmentHash) external onlyOperator whenNotPaused {
        Loan storage loan = loans[loanId];
        if (loan.state != State.SUBMITTED || assessmentHash == bytes32(0)) revert InvalidState();
        loan.assessmentHash = assessmentHash;
        _transition(loan, State.RISK_ASSESSED);
        emit RiskAssessed(loanId, assessmentHash);
    }

    function decide(bytes32 loanId, bool approved) external onlyOperator whenNotPaused {
        Loan storage loan = loans[loanId];
        if (loan.state != State.RISK_ASSESSED) revert InvalidState();
        _transition(loan, approved ? State.APPROVED : State.REJECTED);
    }

    /// @notice Borrower acknowledges the exact off-chain agreement hash by sending this wallet transaction.
    function acceptAgreement(bytes32 loanId, bytes32 agreementHash) external whenNotPaused {
        Loan storage loan = loans[loanId];
        if (loan.state != State.APPROVED || msg.sender != loan.borrower || agreementHash != loan.agreementHash) revert InvalidState();
        loan.agreementAccepted = true;
        emit AgreementAcknowledged(loanId, msg.sender, agreementHash);
    }

    /// @notice Lender funds the principal in native chain currency (ETH on Hardhat).
    function fundLoan(bytes32 loanId) external payable whenNotPaused nonReentrant {
        Loan storage loan = loans[loanId];
        if (loan.state != State.APPROVED || !loan.agreementAccepted) revert InvalidState();
        if (msg.value != loan.principalWei) revert InvalidAmount();
        loan.lender = msg.sender;
        reputations[loan.borrower].totalBorrowedWei += loan.principalWei;
        _transition(loan, State.FUNDED);
        _transition(loan, State.ACTIVE);
        (bool disbursed,) = payable(loan.borrower).call{value: msg.value}("");
        if (!disbursed) revert TransferFailed();
        emit LoanFunded(loanId, msg.sender, msg.value, loan.agreementHash);
    }

    /// @notice Borrower pays down the wei-denominated balance; overpayment is rejected.
    function repay(bytes32 loanId) external payable whenNotPaused nonReentrant {
        Loan storage loan = loans[loanId];
        if (loan.state != State.ACTIVE && loan.state != State.PARTIALLY_REPAID) revert InvalidState();
        if (msg.sender != loan.borrower || msg.value == 0) revert Unauthorized();
        uint256 outstanding = loan.totalDueWei - loan.repaidWei;
        if (msg.value > outstanding) revert InvalidAmount();
        loan.repaidWei += msg.value;
        Reputation storage r = reputations[loan.borrower];
        r.totalRepaidWei += msg.value;
        bool late = block.timestamp > loan.dueAt;
        State nextState = loan.repaidWei == loan.totalDueWei ? State.REPAID : State.PARTIALLY_REPAID;
        _transition(loan, nextState);
        emit RepaymentRecorded(loanId, loan.borrower, msg.value, loan.repaidWei, loan.totalDueWei - loan.repaidWei, late);
        if (nextState == State.REPAID) {
            r.completedLoans++;
            if (late) { r.lateCompletions++; r.repaymentStreak = 0; }
            else { r.onTimeCompletions++; r.repaymentStreak++; }
            emit ReputationChanged(loan.borrower, reputationScore(loan.borrower), r.completedLoans, r.defaults);
        }
        (bool sent,) = payable(loan.lender).call{value: msg.value}("");
        if (!sent) revert TransferFailed();
    }

    function markDefaulted(bytes32 loanId) external onlyOperator whenNotPaused {
        Loan storage loan = loans[loanId];
        if ((loan.state != State.ACTIVE && loan.state != State.PARTIALLY_REPAID) || block.timestamp <= loan.dueAt) revert InvalidState();
        _transition(loan, State.DEFAULTED);
        Reputation storage r = reputations[loan.borrower];
        r.defaults++;
        r.repaymentStreak = 0;
        emit ReputationChanged(loan.borrower, reputationScore(loan.borrower), r.completedLoans, r.defaults);
    }

    function cancel(bytes32 loanId) external onlyOperator whenNotPaused {
        Loan storage loan = loans[loanId];
        if (loan.state != State.SUBMITTED && loan.state != State.RISK_ASSESSED && loan.state != State.APPROVED) revert InvalidState();
        _transition(loan, State.CANCELLED);
    }

    function getLoan(bytes32 loanId) external view returns (Loan memory) {
        if (loans[loanId].state == State.NONE) revert InvalidLoan();
        return loans[loanId];
    }

    function getReputation(address borrower) external view returns (Reputation memory, uint256 score) {
        return (reputations[borrower], reputationScore(borrower));
    }

    /// @dev A demo reputation measure; new borrowers start at 500. It is distinct from ML PD.
    function reputationScore(address borrower) public view returns (uint256) {
        Reputation storage r = reputations[borrower];
        uint256 resolved = r.completedLoans + r.defaults;
        if (resolved == 0) return 500;
        uint256 completion = (r.completedLoans * 600) / resolved;
        uint256 timeliness = r.completedLoans == 0 ? 0 : (r.onTimeCompletions * 400) / r.completedLoans;
        return completion + timeliness;
    }

    function _transition(Loan storage loan, State next) private {
        State previous = loan.state;
        loan.state = next;
        emit LoanStateChanged(loan.applicationId, previous, next, block.timestamp);
    }
}
