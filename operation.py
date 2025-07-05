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
    st.write("命令セット:")
    st.write("0x00: READ A, (4) → レジスタAに番地4のデータを読み込む")
    st.write("0x01: ADD A, (5) → レジスタAの値に番地5のデータを加算する")
    st.write("0x02: WRITE (6), A → 計算結果をレジスタAから番地6に書き戻す")
    st.write("0x03: STOP → プログラムの実行を停止する")
    st.write("データ配置:")
    st.write("0x04: B の値")
    st.write("0x05: -- (未使用)")
    st.write("0x06: A の値")
    st.write("0x07: B の値")
    st.write("0x08: C (結果保存)")
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
for i in range(len(labels)-1): dot.append(f'  n{i} -> n{i+1};')
dot.append('}')

# フローチャート表示
st.subheader("命令実行フロー（フローチャート）")
st.graphviz_chart("\n".join(dot))

# ステップ詳細
if step >= 1:
    st.subheader('ステップ1: 主記憶装置にデータ／命令を格納')
    # メモリ内容をテーブルで表示（C は空に）
    mem = pd.DataFrame({
        '番地': list(range(1,10)),
        '内容': [
            'READ A, (4)',
            'ADD A, (5)',
            'WRITE (6), A',
            'STOP',
            '--',
            '--',
            f'A = {A}',
            f'B = {B}',
            ''  # C はまだ空
        ]
    })
    st.table(mem)

if step >= 2:
    st.subheader('ステップ2: プログラムカウンタ → 命令番地指示')
    st.write('PC が 番地1 を指しています。次に実行する命令です。')
if step >= 3:
    st.subheader("ステップ3: 命令レジスタに命令を読み込み")
    inst = 'READ A, (4)'
    st.write(f"IR に命令 '{inst}' が読み込まれました。")
if step >= 4:
    st.subheader("ステップ4: 命令解読器が命令を解読")
    st.write("命令解読器が 'READ A → レジスタA にアドレス4の内容を取得' と解釈しました。")
if step >= 5:
    st.subheader("ステップ5: レジスタにデータを転送")
    st.write(f"レジスタA ← メモリ[0x04] ({B})")
if step >= 6:
    st.subheader("ステップ6: 演算装置 (ALU) で計算")
    result = A + B
    st.write(f"ALU: レジスタA({B}) + レジスタB({A}) = {result}")
if step >= 7:
    st.subheader("ステップ7: 結果を主記憶装置に書き戻し")
    st.write(f"主記憶 0x08: C ← {result}")
    st.success(f"命令実行完了: C = {result}")
    st.info("リセットして再度体験できます。")
