import streamlit as st
import sqlite3
from pathlib import Path
from datetime import date
import json
import pandas as pd

st.set_page_config(page_title="CAVE | Wine Journal", page_icon="🍷", layout="centered")
st.markdown("""
<style>
.stApp {background:#10191a;color:#f4eee3}
h1,h2,h3 {color:#ead7ac!important}
div[data-testid="stMetric"] {background:#1d2929;padding:12px;border-radius:12px}
.stButton>button[kind="primary"] {background:#aa8255;border:0;color:#111}
[data-testid="stSidebar"] {background:#1a2525}
</style>
""",unsafe_allow_html=True)
DB=Path(__file__).with_name("wines.db")
con=sqlite3.connect(DB,check_same_thread=False)
con.execute("""CREATE TABLE IF NOT EXISTS wines(
id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, name TEXT, producer TEXT,
region TEXT, grapes TEXT, category TEXT, vintage TEXT, photo BLOB,
ratings TEXT, choices TEXT, memo TEXT)""")
con.commit()

def choices(label,options):
    return st.multiselect(label,options,placeholder="タップして選択")
def rating(label):
    return st.select_slider(label,options=[1,2,3,4,5,6],value=3)
def save(data):
    con.execute("""INSERT INTO wines(created,name,producer,region,grapes,category,vintage,photo,ratings,choices,memo)
    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",data)
    con.commit()

st.title("CAVE  /  WINE JOURNAL")
st.caption("香りを記憶し、味わいを集める。")
tab1,tab2,tab3=st.tabs(["＋ 記録する","ワイン一覧","比較・書き出し"])
with tab1:
    with st.form("new_wine",clear_on_submit=False):
        st.subheader("01  ワイン情報")
        name=st.text_input("ワイン名 *")
        producer=st.text_input("生産者・ワイナリー")
        region=st.text_input("国・産地")
        grapes=st.text_input("品種・ブレンド")
        c1,c2=st.columns(2)
        category=c1.selectbox("種類",["赤","白","ロゼ","スパークリング"])
        vintage=c2.text_input("ヴィンテージ")
        photo=st.file_uploader("ボトル写真",type=["jpg","jpeg","png"])
        st.subheader("02  外観")
        appearance={
          "清澄度":choices("清澄度",["透明","濁りあり","輝きあり","澱あり","発泡あり"]),
          "熟成度":choices("熟成度",["若い","中程度","やや熟成","熟成"]),
          "濃淡":choices("濃淡",["淡い","中程度","濃い","非常に濃い"]),
          "色味":choices("色味",["紫","赤","ルビー","ガーネット","オレンジ","黄緑","黄金","琥珀","その他"])
        }
        st.subheader("03  香り")
        aromas={
          "果実系":choices("果実系",["カシス","フランボワーズ","ラズベリー","ストロベリー","チェリー","プラム","ブルーベリー","ブラックベリー","レモン","マスカット","桃","リンゴ","洋ナシ","メロン"]),
          "植物系":choices("植物系",["森の下草","キノコ","ハーブ","紅茶","タバコ","ココナッツ","スギ","バニラ","コショウ","枯葉土"]),
          "花系":choices("花系",["バラ","スミレ","アカシア","ハチミツ","フルーツキャンディー"]),
          "動物系":choices("動物系",["ジビエ","なめし皮","ムスク","バター","ホイップクリーム"]),
          "ミネラル系":choices("ミネラル系",["鉛筆の芯","ミネラル","鉱物","石油","ヨード"]),
          "トースト系":choices("トースト系",["アーモンド","カラメル","トーストパン","コーヒー","キャラメル","燻製"])
        }
        st.subheader("04  味わい（6段階）")
        ratings={}
        for label in ["甘味（糖による甘さ）","果実感（果実の豊かさ）","ジューシーさ","酸味","渋み・タンニン","香りの強さ","ボディ","余韻"]:
            ratings[label]=rating(label)
        mouth=choices("口当たり",["弱い","中程度","強い","なめらか"])
        fruit=choices("果実の特徴",["フレッシュ","熟した果実","ドライフルーツ","ジャム感","ジューシー","凝縮感"])
        finish=choices("余韻の印象",["短い","中程度","長い"])
        st.subheader("05  自分のメモ")
        memo=st.text_area("香りや果実の特徴・飲み比べの感想を自由に",height=130)
        submitted=st.form_submit_button("このワインを保存",type="primary",use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("ワイン名を入力してください。")
            else:
                combined={**appearance,**aromas,"口当たり":mouth,"果実の特徴":fruit,"余韻の印象":finish}
                save((date.today().isoformat(),name,producer,region,grapes,category,vintage,
                    photo.getvalue() if photo else None,
                    json.dumps(ratings,ensure_ascii=False),json.dumps(combined,ensure_ascii=False),memo))
                st.success("保存しました！ 「ワイン一覧」から確認できます。")
with tab2:
    records=con.execute("SELECT id,created,name,producer,region,grapes,category,vintage,photo,ratings,choices,memo FROM wines ORDER BY id DESC").fetchall()
    search=st.text_input("ワイン名・産地・品種で検索")
    records=[r for r in records if search.lower() in " ".join(str(v) for v in (r[2],r[3],r[4],r[5])).lower()]
    if not records:st.info("まだ記録がありません。")
    for r in records:
        with st.expander(f"🍷 {r[2]}  ·  {r[6]}  ·  {r[1]}"):
            if r[8]:st.image(r[8],width=220)
            st.write(f"**生産者:** {r[3] or '—'}　 **産地:** {r[4] or '—'}")
            st.write(f"**品種:** {r[5] or '—'}　 **年:** {r[7] or '—'}")
            st.write("**評価**",json.loads(r[9]))
            st.write("**特徴**", {k:"、".join(v) for k,v in json.loads(r[10]).items() if v})
            st.write("**メモ**",r[11] or "—")
            if st.button("この記録を削除",key=f"del_{r[0]}"):
                con.execute("DELETE FROM wines WHERE id=?",(r[0],));con.commit();st.rerun()
with tab3:
    rows=con.execute("SELECT created,name,producer,region,grapes,category,vintage,ratings,choices,memo FROM wines ORDER BY id DESC").fetchall()
    if rows:
        items=[]
        for r in rows:
            obj=dict(zip(["記録日","ワイン名","生産者","産地","品種","種類","年","評価","特徴","メモ"],r))
            obj.update(json.loads(obj.pop("評価")))
            obj.update({k:"、".join(v) for k,v in json.loads(obj.pop("特徴")).items()})
            items.append(obj)
        df=pd.DataFrame(items)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("CSVでバックアップ",df.to_csv(index=False).encode("utf-8-sig"),
                           "wine_journal.csv","text/csv",use_container_width=True)
        st.caption("CSVには写真は含まれません。写真も含めた保管にはアプリのデータベースファイルを別途バックアップしてください。")
    else:st.info("記録を追加すると比較表が表示されます。")
