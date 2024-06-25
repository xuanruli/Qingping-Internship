try:
    import openpyxl
    print("openpyxl is installed.")
except ImportError:
    print("openpyxl is not installed.")

all_2023_trade_days = get_trade_days("20230101","20231231").strftime('%Y-%m-%d').tolist()
data = pd.DataFrame()
for x in range(len(all_2023_trade_days)-1):
    i = all_2023_trade_days[x] #最后一天涨停板
    next_day = all_2023_trade_days[x+1] #断板日
    query = f'{i}连续涨停天数大于5并且{next_day}的非涨停'
    result = query_iwencai(query)

    if result is not None:
        result['断板日期'] = next_day
        data = pd.concat([data, result],ignore_index = True)
data = data.drop(columns=['{(}收盘价:不复权{-}涨停价{)}'])


def check_pullback(stock_code, date, days=5):
    start_date = pd.to_datetime(date).strftime('%Y%m%d')
    end_date = (pd.Timestamp(date) + pd.offsets.BusinessDay(n=days)).strftime('%Y%m%d')
    data = get_price(stock_code, start_date, end_date, '1d', ['low', 'high'])
    if all(data['low'][i] < data['low'][i + 1] for i in range(len(data) - 1)):  # 检查回调是否发生
        return 0, 0, 0  # 回调时间，回调最低价，回调百分比
    min_price = data['low'].min()
    min_date = data['low'].idxmin()
    original_price = data['low'][0]
    original_date = data.index[0]
    pullback_days = np.busday_count(original_date.date(), min_date.date())
    pullback_percent = ((original_price - min_price) / original_price * 100).round(2)

    return pullback_days, min_price, pullback_percent


def check_rebound(stock_code, date, pullback_days, end_days=15, threshold=0.05):
    start_date = (pd.Timestamp(date) + pd.offsets.BusinessDay(n=pullback_days)).strftime('%Y%m%d')
    end_date = (pd.Timestamp(start_date) + pd.offsets.BusinessDay(n=end_days)).strftime('%Y%m%d')
    data = get_price(stock_code, start_date, end_date, '1d', ['low', 'high'])

    original_high = data['high'][0]
    for i in range(1, len(data)):
        if ((data['high'].iloc[i] - original_high) / original_high) >= threshold:  # 捕捉第一次反弹（5%），回调日期15天内
            rebound_date = data.index[i]
            rebound_price = data['high'].iloc[i]
            rebound_percent = ((rebound_price - original_high) / original_high * 100).round(2)
            return rebound_price, rebound_date.strftime('%Y-%m-%d'), rebound_percent  # 反弹价格，反弹日期，反弹比率

    return None, None, 0

for idx, row in data.iterrows():
    previous_date = (pd.Timestamp(row['断板日期']) + pd.offsets.BusinessDay(n=-1)).strftime('%Y%m%d')
    previous_data = get_price(row['股票代码'], previous_date,previous_date, '1d', ['close'])
    previous_price = previous_data['close'][0]
    data.at[idx, '断板前一天收盘价'] = previous_price

for idx, row in data.iterrows():
    pullback_day, min_price, drawdown_percent = check_pullback(row['股票代码'], row['断板日期'])
    data.at[idx, '回调天数'] = pullback_day
    data.at[idx, '断板回调的最低价'] = min_price
    data.at[idx, '回调百分比'] = drawdown_percent

for idx, row in data.iterrows():
    rebound_price, rebound_date, rebound_percent = check_rebound(row['股票代码'], row['断板日期'], row['回调天数'])
    data.at[idx, '第一次反弹价格'] = rebound_price
    data.at[idx, '反弹时间'] = rebound_date
    data.at[idx, '反弹比率'] = rebound_percent
data

data = data.fillna("None")
with pd.ExcelWriter('任务3.xlsx', engine='openpyxl') as writer:
    data.to_excel(writer, sheet_name='Sheet1')