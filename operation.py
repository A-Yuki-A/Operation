import streamlit as st
import pandas as pd

# CSS調整
st.markdown(
    """
    <style>
    .step-header { font-size: 15px !important; font-weight: bold; }
    .status-box { border:1px solid #ccc; padding:10px; border-radius:5px; margin-bottom:10px; }
    </style>
    """, unsafe_allow_html=True
)

# 初期化
if 'step' not in st.session_state:
    st.session_state.step = 0

# 操作関数
def next_step():
    st.session_state.step += 1

def reset():
    st.session_state.step = 0

# タイトルと説明
st.title("CPU 命令実行フロー体験アプリ")
st.caption("※ 'READ A' の A はレジスタA を表しています。")

# サイドバー: 入力パネルとPC表示
import math
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0)
    # プログラムカウンタ: 命令フェッチごとにインクリメント (実際のCPUのように)
    if st.session_state.step < 3:
        pc_sidebar = 1
    else:
        pc_sidebar = math.ceil((st.session_state.step - 1) / 2)
    st.markdown(f"**プログラムカウンタ :** <span style='font-size:32px'>{pc_sidebar}</span>", unsafe_allow_html=True)
    st.button("次へ (命令実行)", on_click=next_step)
    st.button("リセット", on_click=reset)

# メモリと命令セット初期化
data = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--', '6': '--',
    '7': A, '8': B, '9': '--'
}

# ステータス表示関数
def show_status(pc=None, inst=None, regA=None, regB=None, result=None):
    st.markdown("<div class='status-box'>", unsafe_allow_html=True)
    if pc is not None:
        st.write(f"**PC**: 番地{pc}")
    if inst:
        st.write(f"**命令**: {inst}")
    if regA is not None:
        st.write(f"**レジスタA**: {regA}")
    if regB is not None:
        st.write(f"**レジスタB**: {regB}")
    if result is not None:
        st.write(f"**演算結果**: {result}")
    st.markdown("</div>", unsafe_allow_html=True)

step = st.session_state.step

# レイアウト：左に関係図、右にステップ詳細
col1, col2 = st.columns([2, 1])

# 左カラム：各装置の関係図（固定描画）
with col1:
    st.subheader("各装置の関係図 (動作中)")
    mem_labels = "
".join([f"番地{addr}: {data[addr]}" for addr in sorted(data.keys(), key=int)]), key=int)])
        mem_html = mem_labels.replace("
", "<BR/>")
