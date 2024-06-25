import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_all_trade_days():
    start_date = '20230101'
    end_date = '20231231'
    trade_days = pd.bdate_range(start=start_date, end=end_date, holidays=[]).strftime('%Y-%m-%d').tolist()
    return trade_days


def query_iwencai(query, domain='股票', timeout=6, df=True):
    url = 'https://www.iwencai.com/unifiedwap/result'

    session = requests.Session()

    params = {
        'w': query
    }

    response = session.get(url, params=params, timeout=timeout)

    # 检查请求是否成功
    if response.status_code != 200:
        print(f'查询失败: {response.status_code}')
        return None

    # 解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到结果表格
    table = soup.find('table')

    if table is None:
        print('没有找到结果表格')
        return None

    # 提取表格行
    rows = table.find_all('tr')

    # 存储结果的列表
    data = []

    # 提取表头和前两行数据
    for i, row in enumerate(rows[:3]):  # 包括表头和前两行数据
        cols = [ele.text.strip() for ele in row.find_all(['th', 'td'])]
        if i == 0:  # 表头
            header = cols
        else:
            data.append(cols)

    # 将数据转换为 DataFrame
    df = pd.DataFrame(data, columns=header)

    return df


# main
all_trade_days = get_all_trade_days()
print(all_trade_days)
data = pd.DataFrame()

for x in all_trade_days:
    query = f'{x},“成交额排序“，”前3个交易日区间涨幅在-10%和15%之间“，”10日均线斜率大于-5“，”前三个交易日区间涨幅“，”后一个交易日最大涨幅“，”涨跌幅“'
    result = query_iwencai(query)
    if result is not None:
        data = pd.concat([data, result], ignore_index=True)

print(data)
