


def zero_pnl_summary()->dict:
    return {'total_profit':0,'num_resolved_decisions':0,'wins':0,'losses':0,'current_ndx':0}


def add_pnl_summaries(pnl_1:dict,pnl_2:dict)->dict:
    pnl_fields_to_add = list(zero_pnl_summary().keys())
    if pnl_1 is None:
        pnl_1 = zero_pnl_summary()
    if pnl_2 is None:
        pnl_2 = zero_pnl_summary()
    total_pnl = dict(pnl_1)
    for ky in pnl_fields_to_add:
        total_pnl[ky] = pnl_1.get(ky,0) + pnl_2.get(ky,0)

    return total_pnl