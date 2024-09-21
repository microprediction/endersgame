import pytest
from endersgame.accounting.simplepnl import SimplePnL  # Assuming you saved the class in baseaccountant.py


@pytest.fixture
def accountant():
    """Fixture to initialize a new instance of BaseAccountant."""
    return SimplePnL()


def test_initial_state(accountant):
    """Test if the initial state of the accountant is correctly initialized."""
    assert accountant.accounting["current_ndx"] == 0
    assert accountant.accounting["last_attack_ndx"] is None
    assert accountant.accounting["pending_decisions"] == []
    assert accountant.accounting["pnl_data"] == []


def test_sequential_record_and_resolve(accountant):
    """Test recording and resolving decisions sequentially."""

    # Step 1: Record a decision at step 0
    accountant._record_decision(y=100, decision=1)
    assert len(accountant.accounting["pending_decisions"]) == 1
    assert accountant.accounting["pending_decisions"][0] == (0, 100, 1)

    # Step 2: Increment to step 100 (enough for the decision to be resolved)
    accountant.accounting["current_ndx"] = 100
    accountant._resolve_decisions(y=150)  # Resolve the first decision
    assert len(accountant.accounting["pending_decisions"]) == 0  # Should be empty
    assert len(accountant.accounting["pnl_data"]) == 1  # 1 decision resolved
    resolved = accountant.accounting["pnl_data"][0]
    assert resolved == (0, 100, 1, 100, 150, 50)  # Correct PnL calculation: 150 - 100 = 50

    # Step 3: Record another decision at step 100
    accountant._record_decision(y=150, decision=-1)
    assert len(accountant.accounting["pending_decisions"]) == 1
    assert accountant.accounting["pending_decisions"][0] == (100, 150, -1)

    # Step 4: Increment to step 200 and resolve
    accountant.accounting["current_ndx"] = 200
    accountant._resolve_decisions(y=100)
    assert len(accountant.accounting["pending_decisions"]) == 0
    assert len(accountant.accounting["pnl_data"]) == 2  # 2 decisions resolved
    resolved = accountant.accounting["pnl_data"][1]
    assert resolved == (100, 200, -1, 150, 100, 50)  # Correct PnL: 150 - 100 = 50 (down bet)


def test_multiple_decisions_sequentially(accountant):
    """Test multiple decisions made and resolved in sequence."""

    # Step 1: Record two decisions at steps 0 and 100
    accountant._record_decision(y=100, decision=1)
    accountant.accounting["current_ndx"] = 100
    accountant._record_decision(y=150, decision=-1)

    # Assert the two decisions are recorded
    assert len(accountant.accounting["pending_decisions"]) == 2
    assert accountant.accounting["pending_decisions"][0] == (0, 100, 1)
    assert accountant.accounting["pending_decisions"][1] == (100, 150, -1)

    # Step 2: Increment to step 200 and resolve the first decision
    accountant.accounting["current_ndx"] = 200
    accountant._resolve_decisions(y=200)  # Resolving first decision at 0
    assert len(accountant.accounting["pending_decisions"]) == 1  # Second decision is still pending
    assert len(accountant.accounting["pnl_data"]) == 1  # First decision resolved
    resolved = accountant.accounting["pnl_data"][0]
    assert resolved == (0, 200, 1, 100, 200, 100)  # PnL: 200 - 100 = 100

    # Step 3: Increment to step 300 and resolve the second decision
    accountant.accounting["current_ndx"] = 300
    accountant._resolve_decisions(y=100)
    assert len(accountant.accounting["pending_decisions"]) == 0  # All decisions resolved
    assert len(accountant.accounting["pnl_data"]) == 2  # Second decision resolved
    resolved = accountant.accounting["pnl_data"][1]
    assert resolved == (100, 300, -1, 150, 100, 50)  # PnL: 150 - 100 = 50 (down bet)


def test_pnl_summary(accountant):
    """Test that PnL summary correctly reflects resolved decisions."""

    # Step 1: Record and resolve two decisions
    accountant._record_decision(y=100, decision=1)
    accountant.accounting["current_ndx"] = 100
    accountant._resolve_decisions(y=150)  # Resolve first decision

    accountant._record_decision(y=150, decision=-1)
    accountant.accounting["current_ndx"] = 200
    accountant._resolve_decisions(y=100)  # Resolve second decision

    # Step 2: Get the summary
    summary = accountant.get_pnl_summary()
    assert summary["current_ndx"] == 200
    assert summary["num_resolved_decisions"] == 2
    assert summary["total_profit"] == 100  # 50 from the first decision, 50 from the second


def test_get_pnl_records(accountant):
    """Test conversion of PnL data into dictionary format."""

    # Step 1: Record and resolve a decision
    accountant._record_decision(y=100, decision=1)
    accountant.accounting["current_ndx"] = 100
    accountant._resolve_decisions(y=150)  # Resolve first decision

    # Step 2: Get the records
    pnl_records = accountant.get_pnl_records()
    assert len(pnl_records) == 1
    record = pnl_records[0]
    assert record == {
        'decision_ndx': 0,
        'resolution_ndx': 100,
        'decision': 1,
        'y_decision': 100,
        'y_resolution': 150,
        'pnl': 50
    }
