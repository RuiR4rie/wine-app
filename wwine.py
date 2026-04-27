import streamlit as st
import pandas as pd
import re

# =========================
# データ読み込み
# =========================
df_raw = pd.read_excel("wine.xlsx", header=None)

# =========================
# 空列削除（←これが超重要）
# =========================
df_raw = df_raw.dropna(axis=1, how='all')

# =========================
# 正しく列を割り当て
# =========================
df = pd.DataFrame()

df["種類"] = df_raw.iloc[:, 0]
df["国名"] = df_raw.iloc[:, 1]
df["ワイン名"] = df_raw.iloc[:, 2]
df["品種"] = df_raw.iloc[:, 3]
df["原価"] = df_raw.iloc[:, 4]
df["グラス価格"] = df_raw.iloc[:, 5]
df["ボトル価格"] = df_raw.iloc[:, 6]
df["特徴"] = df_raw.iloc[:, 7]
df["ボディ"] = df_raw.iloc[:, 8]

# ワイン名がある行だけ
df = df.dropna(subset=["ワイン名"])
df = df[df["国名"] != "国名"]
df = df[df["品種"] != "品種"]
# =========================
# 価格整形
# =========================
for col in ["ボトル価格", "グラス価格"]:
    df[col] = df[col].astype(str).str.replace(",", "")
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# UI
# =========================
st.title("🍷 ワイン検索アプリ")

keyword = st.text_input("🔍 ワイン検索")

# =========================
# サイドバー（絞り込み）
# =========================
st.sidebar.header("🔎 絞り込み")

wine_type = st.sidebar.selectbox(
    "種類",
    ["指定なし"] + sorted(df["種類"].dropna().unique())
)

country = st.sidebar.selectbox(
    "国名",
    ["指定なし"] + sorted(df["国名"].dropna().unique())
)

grape = st.sidebar.selectbox(
    "品種",
    ["指定なし"] + sorted(df["品種"].dropna().unique())
)

body = st.sidebar.selectbox(
    "ボディ",
    ["指定なし", "ライトボディ", "ミディアムボディ", "フルボディ"]
)



# =========================
# フィルタ処理
# =========================
filtered_df = df.copy()

# 自然文検索
if keyword:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: keyword in str(row), axis=1)
    ]

# 条件フィルタ
if wine_type != "指定なし":
    filtered_df = filtered_df[filtered_df["種類"] == wine_type]

if country != "指定なし":
    filtered_df = filtered_df[filtered_df["国名"] == country]

if grape != "指定なし":
    filtered_df = filtered_df[filtered_df["品種"] == grape]

if body != "指定なし":
    filtered_df = filtered_df[filtered_df["ボディ"] == body]


# =========================
# 表示
# =========================
st.write(f"検索結果：{len(filtered_df)}件")

if len(filtered_df) > 0:
    st.dataframe(filtered_df)
else:
    st.write("該当なし")