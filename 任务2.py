import pandas as pd
try:
    import openpyxl
    print("openpyxl is installed.")
except ImportError:
    print("openpyxl is not installed.")

all_2023_trade_days = get_trade_days("20230101","20231231").strftime('%Y-%m-%d').tolist()
df1 = pd.DataFrame()
for x in all_2023_trade_days:
    query = '{x}地天板,"前三个交易日区间涨幅","后一个交易日涨跌幅"'.format(x=x)
    result = query_iwencai(query)
    if result is not None:
        result['地天板日期'] = x
        df1 = pd.concat([df1, result],ignore_index = True)

df1

all_2023_trade_days = get_trade_days("20230101","20231231").strftime('%Y-%m-%d').tolist()
data = pd.DataFrame()
for x in all_2023_trade_days:
    query = '{x},"成交额排序","前3个交易日区间涨幅在-10%%和15%%之间","10日均线斜率大于-5","前三个交易日区间涨幅","后一个交易日最大涨幅","涨跌幅"'.format(x=x)
    result = query_iwencai(query).head(2)
    result['date'] = x
    if result is not None:
        data = pd.concat([data, result],ignore_index = True)

data.set_index('date',inplace=True)
data.index.name = None
data

with pd.ExcelWriter('任务2.xlsx', engine='openpyxl') as writer:
    df1.to_excel(writer, sheet_name='Sheet1')
    data.to_excel(writer, sheet_name='Sheet2')