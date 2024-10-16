from midone.accounting.pnlutil import zero_pnl_summary, add_pnl_summaries


def test_zero_pnl_summary():
    expected = {'total_profit': 0, 'num_resolved_decisions': 0, 'wins': 0, 'losses': 0, 'current_ndx': 0}
    result = zero_pnl_summary()
    assert result == expected

def test_add_pnl_summaries_both_non_empty():
    pnl_1 = {'total_profit': 10, 'num_resolved_decisions': 2, 'wins': 1, 'losses': 1, 'current_ndx': 5}
    pnl_2 = {'total_profit': 5, 'num_resolved_decisions': 3, 'wins': 2, 'losses': 1, 'current_ndx': 10}
    expected = {'total_profit': 15, 'num_resolved_decisions': 5, 'wins': 3, 'losses': 2, 'current_ndx': 15}
    result = add_pnl_summaries(pnl_1, pnl_2)
    assert result == expected

def test_add_pnl_summaries_pnl_1_none():
    pnl_1 = None
    pnl_2 = {'total_profit': 5, 'num_resolved_decisions': 3, 'wins': 2, 'losses': 1, 'current_ndx': 10}
    expected = {'total_profit': 5, 'num_resolved_decisions': 3, 'wins': 2, 'losses': 1, 'current_ndx': 10}
    result = add_pnl_summaries(pnl_1, pnl_2)
    assert result == expected

def test_add_pnl_summaries_pnl_2_none():
    pnl_1 = {'total_profit': 10, 'num_resolved_decisions': 2, 'wins': 1, 'losses': 1, 'current_ndx': 5}
    pnl_2 = None
    expected = {'total_profit': 10, 'num_resolved_decisions': 2, 'wins': 1, 'losses': 1, 'current_ndx': 5}
    result = add_pnl_summaries(pnl_1, pnl_2)
    assert result == expected

def test_add_pnl_summaries_both_none():
    pnl_1 = None
    pnl_2 = None
    expected = {'total_profit': 0, 'num_resolved_decisions': 0, 'wins': 0, 'losses': 0, 'current_ndx': 0}
    result = add_pnl_summaries(pnl_1, pnl_2)
    assert result == expected

if __name__=='__main__':
    import pytest
    pytest.main(__file__)
