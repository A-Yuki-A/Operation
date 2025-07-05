import streamlit as st
import pandas as pd

# 初期化
if 'step' not in st.session_state:
    st.session_state.step = 0

# ステップ操作
def next_step():
    st.session_state.step += 1

def reset():
    st.session_state.step = 0

# アプリタイトル
st.title("CPU 命令実行フロー体験アプリ")

# 補足説明
st.caption("※ 'READ A' の A はレジスタA を表しています。" )

# サイドバー入力
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力", value=0, step=1)
    B = st.number_input("値Bを入力", value=0, step=1)
    st.write("命令セット (番地と説明)")
    commands = [
        ("0x00: READ A, (6)", "レジスタAに番地6のデータを読み込む"),
        ("0x01: ADD A, (7)", "レジスタAの値に番地7のデータを加算する"),
        ("0x02: WRITE (8), A", "レジスタAの値を番地8に書き戻す"),
        ("0x03: STOP", "プログラムの実行を停止する")
    ]
    for code, desc in commands:
        st.write(f"- {code}  →  {desc}")
    st.write("データ配置 (番地と内容)")
    data_layout = [
        ("0x04", "--"),
        ("0x05", "--"),
        ("0x06", f"A = {A}"),  # A の値を格納
        ("0x07", f"B = {B}"),  # B の値を格納
        ("0x08", "C (結果保存)")
    ]
    for addr, val in data_layout:
        st.write(f"- {addr}: {val}")
    if st.button("次へ (命令実行)"):
        next_step()
    if st.button("リセット"):
        reset()

# ステップ数取得
step = st.session_state.step

# フローチャート DOT
labels = ['1. メモリ格納','2. PC→命令','3. IR読み込み','4. 解読','5. レジスタ転送','6. 計算','7. 書き戻し']
dot = ['digraph G {','  rankdir=LR;','  node [shape=box,fontname="Helvetica"];']
for i,l in enumerate(labels):
    style = 'style=filled,fillcolor="lightblue"' if i < step else ''
    dot.append(f'  n{i} [{style} label="{l}"];')
for i in range(len(labels)-1):
    dot.append(f'  n{i} -> n{i+1};')
dot.append('}')

# フローチャート表示
st.subheader("命令実行フロー（フローチャート）")
st.graphviz_chart("\n".join(dot))

# ステップ詳細
if step >= 1:
    st.subheader('ステップ1: 主記憶装置にデータ／命令を格納')
    mem = pd.DataFrame({
        '番地': list(range(1,10)),
        '内容': [
            'READ A, (6) → レジスタAに番地6のデータを読み込む',
            'ADD A, (7) → レジスタAに番地7のデータを加算する',
            'WRITE (8), A → レジスタAの値を番地8に書き戻す',
            'STOP → プログラム停止',
            '--',
            '--',
            f'A = {A}',  # 番地6
            f'B = {B}',  # 番地7
            ''  # 番地8: C は未登録
        ]
    })
    st.table(mem)
if step >= 2:
    st.subheader('ステップ2: プログラムカウンタ → 命令番地指示')
    st.write('PC が 番地1 を指しています。次に実行する命令です。')
if step >= 3:
    st.subheader("ステップ3: 命令レジスタに命令を読み込み")
    inst = 'READ A, (6)'  # アドレス6から読み込み'
    st.write(f"IR に命令 '{inst}' が読み込まれました。")
if step >= 4:
    st.subheader("ステップ4: 命令解読器が命令を解読")
    st.write("命令解読器が 'READ A → レジスタA に番地6の内容を取得' と解釈しました。")
if step >= 5:
    st.subheader("ステップ5: レジスタにデータを転送")
    st.write(f"レジスタA ← メモリ[0x06] ({A})  # 番地6 を読み込み")
if step >= 6:
    st.subheader("ステップ6: 演算装置 (ALU) で計算")
    result = A + B  # 演算結果
    st.write(f"ALU: レジスタA({B}) + レジスタB({A}) = {result}")
if step >= 7:
    st.subheader("ステップ7: 結果を主記憶装置に書き戻し")
    st.write(f"主記憶 番地8: C ← {result}")
    st.success(f"命令実行完了: C = {result}")
    st.info("リセットして再度体験できます。")
