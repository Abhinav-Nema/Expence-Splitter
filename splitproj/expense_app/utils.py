from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP


def _round_dec(x):
    if not isinstance(x, Decimal):
        x = Decimal(str(x))
    return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_group_overview(group):
    totals = defaultdict(Decimal)
    paid = defaultdict(Decimal)


    for exp in group.expenses.all():
        amt = Decimal(str(exp.amount))
        paid[exp.paid_by.id] += amt
        for sh in exp.shares.all():
            totals[sh.member.id] += Decimal(str(sh.share_amount))


    members = []
    for m in group.members.all():
        p = _round_dec(paid.get(m.id, Decimal('0')))
        owed = _round_dec(totals.get(m.id, Decimal('0')))
        net = _round_dec(p - owed)
        members.append({'member_id': m.id, 'name': m.name, 'paid': float(p), 'owed': float(owed), 'net': float(net)})


    total_expenses = sum([Decimal(str(e.amount)) for e in group.expenses.all()])
    return {'group_id': group.id, 'group_name': group.name, 'total_expenses': float(_round_dec(total_expenses)), 'members': members}



def settle_group_balances(group):
    net = {}
    for m in group.members.all():
        net[m.id] = Decimal('0')


    for exp in group.expenses.all():
        net[exp.paid_by.id] += Decimal(str(exp.amount))
        for sh in exp.shares.all():
            net[sh.member.id] -= Decimal(str(sh.share_amount))


    for k in net:
        net[k] = _round_dec(net[k])


    creditors = []
    debtors = []
    for m_id, bal in net.items():
        if bal > 0:
            creditors.append([m_id, bal])
        elif bal < 0:
            debtors.append([m_id, -bal])


    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)


    transactions = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt_amt = debtors[i]
        creditor_id, cred_amt = creditors[j]
        transfer = min(debt_amt, cred_amt)
        transactions.append({'from': debtor_id, 'to': creditor_id, 'amount': float(_round_dec(transfer))})
        debt_amt -= transfer
        cred_amt -= transfer
        debtors[i][1] = debt_amt
        creditors[j][1] = cred_amt
        if debt_amt == 0:
            i += 1
        if cred_amt == 0:
            j += 1


    return transactions



