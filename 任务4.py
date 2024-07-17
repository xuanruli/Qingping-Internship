import requests
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
import openpyxl
import aiohttp
import asyncio


def get_total_stocks(url):
    response = requests.get(url.format(page=1, size=20))
    text = response.text
    match = re.search(r'jQuery\d+_\d+\((.*)\)', text)
    if match:
        data = json.loads(match.group(1))
        total = data['data']['total']
        return total
    return 0


def get_all_stock_codes():
    all_stock_codes = []
    base_url = "http://28.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112406991311508785201_1720860154712&pn={page}&pz={size}&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&dect=1&wbp2u=|0|0|0|web&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f12,f14&_=1720860154713"
    page_size = 20

    total_stocks = get_total_stocks(base_url)
    total_pages = (total_stocks + page_size - 1) // page_size

    for page in range(1, total_pages + 1):
        url = base_url.format(page=page, size=page_size)
        response = requests.get(url)
        text = response.text
        match = re.search(r'jQuery\d+_\d+\((.*)\)', text)
        if match:
            data = json.loads(match.group(1))
            if 'data' in data and 'diff' in data['data']:
                for stock in data['data']['diff']:
                    all_stock_codes.append({
                        "code": stock["f12"],
                        "name": stock["f14"]
                    })

    return all_stock_codes


# 将数据转换为 pandas DataFrame
def convert_to_dataframe(stock_codes):
    df = pd.DataFrame(stock_codes)
    return df


def add_exchange_prefix(stock_codes):
    prefixed_codes = []

    for code in stock_codes["code"]:
        if code.startswith('6'):
            prefixed_code = "sh" + code
        elif code.startswith('0') or code.startswith('3'):
            prefixed_code = "sz" + code
        elif code.startswith('8') or code.startswith('4'):
            prefixed_code = "bj" + code
        else:
            prefixed_code = code
        prefixed_codes.append(prefixed_code)

    stock_codes["code"] = prefixed_codes
    return stock_codes


async def fetch_data(session, stock):
    url = f'https://eminterservice.eastmoney.com/UserData/GetWebTape?code={stock}'
    try:
        async with session.get(url) as response:
            response_data = await response.json()
            if 'Data' in response_data:
                datas = response_data.get('Data')
                return (stock, datas.get('TapeZ'), datas.get('Date'))
    except aiohttp.ClientError as e:
        print(f"Client error for stock {stock}: {e}")
    except asyncio.TimeoutError:
        print(f"Timeout error for stock {stock}")
    except Exception as e:
        print(f"Unexpected error for stock {stock}: {e}")
    return (stock, None, None)


async def addZD(df):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, stock) for stock in df['code']]
        results = await asyncio.gather(*tasks)

    for stock, ZD, date in results:
        df.loc[df['code'] == stock, '看涨百分比'] = ZD
        df.loc[df['code'] == stock, 'Date'] = date

    return df


def get_index_components(index_id, max_pages=50):
    page_num = 1
    stock_data = []
    base_url = "https://vip.stock.finance.sina.com.cn/corp/view/vII_NewestComponent.php"

    while page_num <= max_pages:
        url = f"{base_url}?page={page_num}&indexid={index_id}"
        print(f"Fetching URL: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print("Failed to retrieve the page.")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'NewStockTable'})
        if not table:
            print("No table found.")
            break

        rows = table.find_all('tr')[2:]

        if not rows:
            print("No rows found.")
            break

        new_data_found = False
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue
            code = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            stock_data.append({'code': code, 'name': name})

        if index_id == "000016" and page_num == 1:
            print("Only one page for 000016")
            break

        print(f"Processed page {page_num}")
        page_num += 1

    return stock_data


async def main():
    indices = {
        "sz50": "000016",
        "hs300": "000300",
        "zz500": "000905",
        "zz1000": "000852",
        "zz2000": "932000"
    }

    stock_codes = get_all_stock_codes()

    df = convert_to_dataframe(stock_codes)
    df = add_exchange_prefix(df)
    df = await addZD(df)

    with pd.ExcelWriter('任务4.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1')
        sheet_number = 2
        df['code'] = df['code'].str.strip().str.slice(2)

        for name, index_id in indices.items():

            print(f"Retrieving data for {name} (index ID: {index_id})")
            stock_components = get_index_components(index_id)
            components_df = pd.DataFrame(stock_components)
            components_df['code'] = components_df['code'].str.strip()
            sub_df = pd.merge(components_df[["code"]], df, on=['code'], how='inner')
            print(sub_df)
            sub_df.to_excel(writer, sheet_name=f'Sheet{sheet_number}')
            sheet_number += 1


if __name__ == "__main__":
    asyncio.run(main())
