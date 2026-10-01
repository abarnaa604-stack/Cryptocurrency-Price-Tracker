from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime
import time
import os


# =========================================================
# CHROME SETUP
# =========================================================

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Do not wait forever for the page
driver.set_page_load_timeout(60)

print("Opening CoinGecko...")


# =========================================================
# OPEN WEBSITE
# =========================================================

try:
    driver.get("https://www.coingecko.com/")

except Exception as e:
    print("Page loading took too long.")
    print("Continuing with the loaded page...")

time.sleep(15)


# =========================================================
# FIND CRYPTO TABLE
# =========================================================

rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

print("Rows found:", len(rows))

data = []

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# =========================================================
# EXTRACT TOP 10 COINS
# =========================================================

for row in rows[:10]:

    try:
        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) < 11:
            continue

        coin = cols[2].text.split("\n")[0]
        price = cols[4].text
        change = cols[5].text
        market_cap = cols[10].text

        data.append({
            "Timestamp": timestamp,
            "Coin Name": coin,
            "Current Price": price,
            "24h Change": change,
            "Market Cap": market_cap
        })

    except Exception as e:
        continue


# =========================================================
# CLOSE BROWSER
# =========================================================

driver.quit()


# =========================================================
# CHECK DATA
# =========================================================

if len(data) == 0:

    print("\nNo cryptocurrency data was collected.")
    print("Please check your internet connection and try again.")

else:

    # Create DataFrame
    df = pd.DataFrame(data)

    file_name = "crypto_prices.csv"


    # =====================================================
    # HISTORICAL DATA STORAGE
    # =====================================================

    if os.path.exists(file_name):

        print("\nPrevious history found.")

        old_data = pd.read_csv(file_name)

        final_data = pd.concat(
            [old_data, df],
            ignore_index=True
        )

    else:

        print("\nNo previous history found.")

        final_data = df


    # =====================================================
    # SAVE CSV
    # =====================================================

    final_data.to_csv(
        file_name,
        index=False
    )


    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    print("\nData saved successfully!")
    print("Historical data stored in:", file_name)

    print("\nCurrent Run Data:\n")
    print(df)

    print("\nTotal Historical Records:", len(final_data))
    print("\n========== FILTERED DATA ==========")

change_values = pd.to_numeric(
    df["24h Change"]
    .str.replace("%", "", regex=False)
    .str.replace("+", "", regex=False)
    .replace("-", ""),
    errors="coerce"
)

filtered_data = df[change_values > 5]

if len(filtered_data) > 0:
    print("\nCoins with 24h Change > 5%:\n")
    print(filtered_data)
else:
    print("\nNo coins have 24h Change above 5%.")