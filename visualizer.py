import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB = "crimson_desert_data.db"

conn = sqlite3.connect(DB)
df = pd.read_sql("SELECT * FROM steam_followers", conn)
conn.close()

df["ts"] = pd.to_datetime(df["ts"])

plt.figure(figsize=(14,6))
plt.plot(df["ts"], df["followers"], marker="o")

plt.title("Crimson Desert - Steam Followers Trend")
plt.xlabel("Date")
plt.ylabel("Followers")
plt.grid(True)

plt.tight_layout()
plt.savefig("followers_trend.png")
plt.show()

print("📈 followers_trend.png 생성 완료")
