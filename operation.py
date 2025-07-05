import streamlit as st
import pandas as pd

# CSS調整
st.markdown(
    """
    <style>
    .step-header {
        font-size: 15px !important;
        font-weight: bold;
    }
    .status-box {
        border:1px solid #ccc; padding:10px; border-radius:5px; margin-bottom:10px;
    }
    </style>
    """, unsafe_allow_html=True
)

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
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0, step=1)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0, step=1)
    st.button("次へ (命令実行)", on_click=next_step)
    st.button("リセット", on_click=reset)

# メモリ初期化
memory = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--',
    '6': '--',
    '7': A,
    '8': B,
    '9': ''
}

# ステータス表示用関数
def show_status(pc=None, ir=None, regA=None, regB=None, alu=None):
    st.markdown("<div class='status-box'>", unsafe_allow_html=True)
    if pc is not None:
        st.write(f"**PC**: 番地{pc}")
    if ir is not None:
        st.write(f"**IR**: {ir}")
    if regA is not None:
        st.write(f"**レジスタA**: {regA}")
    if regB is not None:
        st.write(f"**レジスタB**: {regB}")
    if alu is not None:
        st.write(f"**ALU出力**: {alu}")
    st.markdown("</div>", unsafe_allow_html=True)

step = st.session_state.step

# フローチャート表示
labels = ['1. メモリ格納','2. PC→命令','3. IR読み込み','4. 解読',
          '5. レジスタ転送','6. 計算','7. 書き戻し']
dot = ['digraph G {','  rankdir=LR;','  node [shape=box,fontname="Helvetica"];']
for i, l in enumerate(labels):
    style = 'style=filled,fillcolor="lightblue"' if i < step else ''
    dot.append(f'  n{i} [{style} label="{l}"];')
for i in range(len(labels)-1): dot.append(f'  n{i} -> n{i+1};')
dot.append('}')
st.subheader("命令実行フロー（フローチャート）")
st.graphviz_chart("\n".join(dot))

# ステップ詳細

# ステップ1: メモリ格納とステータス
if step >= 1:
    st.markdown("<div class='step-header'>ステップ1: 主記憶装置にデータ／命令を格納</div>", unsafe_allow_html=True)
    df_mem = pd.DataFrame.from_dict(memory, orient='index', columns=['内容'])
    df_mem.index.name = '番地'
    st.table(df_mem)
    show_status(pc=1)

# ステップ2: PC 指示
if step >= 2:
    st.markdown("<div class='step-header'>ステップ2: プログラムカウンタ → 命令番地指示</div>", unsafe_allow_html=True)
    show_status(pc=1)

# ステップ3: IR 読み込み
if step >= 3:
    ir = memory['1']
    st.markdown("<div class='step-header'>ステップ3: 命令レジスタに命令を読み込み</div>", unsafe_allow_html=True)
    show_status(pc=2, ir=ir)

# ステップ4: 命令解読
if step >= 4:
    st.markdown("<div class='step-header'>ステップ4: 命令解読器が命令を解読</div>", unsafe_allow_html=True)
    show_status(pc=2, ir=ir)

# ステップ5: レジスタ転送
if step >= 5:
    st.markdown("<div class='step-header'>ステップ5: レジスタにデータを転送</div>", unsafe_allow_html=True)
    regA = memory['7']
    show_status(pc=3, ir=ir, regA=regA)

# ステップ6: ALU 計算
if step >= 6:
    st.markdown("<div class='step-header'>ステップ6: 演算装置 (ALU) で計算</div>", unsafe_allow_html=True)
    regB = memory['8']
    alu_out = regA + regB
    show_status(pc=3, ir=ir, regA=regA, regB=regB, alu=alu_out)

# ステップ7: 結果書き戻し
if step >= 7:
    st.markdown("<div class='step-header'>ステップ7: 結果を主記憶装置に書き戻し</div>", unsafe_allow_html=True)
    memory['9'] = alu_out
    show_status(pc=4, ir=memory['2'], regA=regA, regB=regB, alu=alu_out)
    st.success(f"命令実行完了: 番地9に C = {alu_out} が格納されました。")
    st.info("リセットして再度体験できます。")
