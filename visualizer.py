import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB = "crimson_desert_data.db"

# ---------- ★ 핵심: 테이블이 없으면 자동 생성 ----------
def ensure_table():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS steam_followers (
        ts TEXT,
        followers INTEGER
    )
    """)
    conn.commit()
    conn.close()

ensure_table()
# -------------------------------------------------------

conn = sqlite3.connect(DB)

try:
    df = pd.read_sql("SELECT * FROM steam_followers", conn)
except Exception as e:
    print("❌ DB 읽기 실패:", e)
    conn.close()
    exit(1)

conn.close()

if df.empty:
    print("⚠️ 데이터가 없습니다. 먼저 tracker.py를 실행하세요.")
    exit(0)

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
