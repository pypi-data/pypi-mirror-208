# from sharetop.core.fund.get_fund_rank import fund_open_fund_rank, fund_exchange_rank, fund_money_rank, fund_hk_rank
from sharetop.core.stock import get_real_time_data

h = get_real_time_data('1.000001')

print(h)