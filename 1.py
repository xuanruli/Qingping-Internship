import requests
from bs4 import BeautifulSoup


def get_index_components(index_id, max_pages=50):
    page_num = 1
    stock_data = []
    base_url = "https://vip.stock.finance.sina.com.cn/corp/view/vII_NewestComponent.php"
    seen_data = set()

    while page_num <= max_pages:
        url = f"{base_url}?page={page_num}&indexid={index_id}"
        print(f"Fetching URL: {url}")
        response = requests.get(url)
        print(f"Status code: {response.status_code}")

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
            entry = (code, name)
            if entry not in seen_data:
                seen_data.add(entry)
                stock_data.append({'code': code, 'name': name})
                new_data_found = True

        if not new_data_found:
            if index_id == "932000":
                page_num += 1
                continue
            print("No new data found on this page.")
            break

        print(f"Processed page {page_num}")
        page_num += 1

    return stock_data


indices = {
    "sz50": "000016",
    "hs300": "000300",
    "zz500": "000905",
    "zz1000": "000852",
    "zz2000": "932000"
}

for name, index_id in indices.items():
    stock_components = get_index_components(index_id)
    print(f"Data for {name}:")
    for stock in stock_components:
        print(f"Code: {stock['code']}, Name: {stock['name']}")
    print("\n")
