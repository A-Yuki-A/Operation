import streamlit as st
import pandas as pd

# 初期化
if 'step' not in st.session_state:
    st.session_state.step = 0

# ステップを進める関数
def next_step():
    st.session_state.step += 1

# リセット関数
def reset():
    st.session_state.step = 0

# アプリタイトル
st.title("CPU 命令実行フロー体験アプリ")

# サイドバーで入力
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力", value=0, step=1)
    B = st.number_input("値Bを入力", value=0, step=1)
    st.write("命令: A + B の合計をCに保存 (命令コード 0x01)")
    if st.button("次へ (命令実行)"):
        next_step()
    if st.button("リセット"):
        reset()

# ステップ管理
dot_src = None
step = st.session_state.step
step_labels = [
    '1. 主記憶: データ/命令格納',
    '2. PCが命令アドレスを指す',
    '3. IRに命令読み込み',
    '4. 命令解読',
    '5. レジスタ転送',
    '6. ALUで計算',
    '7. 結果書き戻し'
]
# DOT生成
dot_lines = ['digraph G {', '  rankdir=LR;', '  node [shape=box, fontname="Helvetica"];']
for idx, label in enumerate(step_labels):
    attrs = []
    if idx < step:
        attrs.append('style=filled')
        attrs.append('fillcolor="lightblue"')
    attr_str = '[' + ','.join(attrs) + ']' if attrs else ''
    dot_lines.append(f'  node{idx} {attr_str} label="{label}";')
for idx in range(len(step_labels) - 1):
    dot_lines.append(f'  node{idx} -> node{idx+1};')
dot_lines.append('}')
dot_src = "\n".join(dot_lines)

# フローチャート表示
st.subheader("命令実行フロー（フローチャート）")
st.graphviz_chart(dot_src)

# ステップ詳細表示
display = []
# ステップごとの内容
if step >= 1:
    # メモリ表示（ステップ1）
    st.subheader("ステップ1: 主記憶装置にデータ／命令を格納")
    mem = pd.DataFrame({
        'アドレス': ['0x00', '0x01', '0x02'],
        '内容': [f'A = {A}', f'B = {B}', '命令コード 0x01 (ADD A,B→C)']
    })
    st.table(mem)
if step >= 2:
    st.subheader("ステップ2: プログラムカウンタ → 命令アドレス指示")
    st.write("PC が 0x02 を指しています。次に実行する命令の位置です。")
if step >= 3:
    st.subheader("ステップ3: 命令レジスタに命令を読み込み")
    st.write("IR に命令コード 0x01 が読み込まれました。")
if step >= 4:
    st.subheader("ステップ4: 命令解読器が命令を解読")
    st.write("命令解読器が 'A と B を足して C に保存せよ' と解釈しました。")
if step >= 5:
    st.subheader("ステップ5: レジスタにデータを転送")
    st.write(f"レジスタA ← {A}")
    st.write(f"レジスタB ← {B}")
if step >= 6:
    st.subheader("ステップ6: 演算装置 (ALU) で計算")
    result = A + B
    st.write(f"ALU: {A} + {B} = {result}")
if step >= 7:
    st.subheader("ステップ7: 結果を主記憶装置に書き戻し")
    st.write(f"主記憶: C ← {A + B}")
    st.success(f"命令実行完了: C = {A + B}")
    st.info("リセットして、再度体験できます。")
