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
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0)
    pc_sidebar = st.session_state.step if st.session_state.step > 0 else 1
    st.write(f"プログラムカウンタ (PC): 番地{pc_sidebar}")
    st.button("次へ (命令実行)", on_click=next_step)
    st.button("リセット", on_click=reset)

# メモリと命令セット初期化
data = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--', '6': '--',
    '7': A, '8': B, '9': ''
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

# レイアウト：左に図、右にステップ詳細
col1, col2 = st.columns([2, 1])

# 左カラム：各装置の関係図（固定）
with col1:
    st.subheader("各装置の関係図 (動作中)")
    # メモリ内容HTML
    mem_labels = "\n".join([f"番地{addr}: {data[addr]}" for addr in sorted(data.keys(), key=int)])
    mem_html = mem_labels.replace("\n", "<BR/>")
    # CPU状態
    pc_val   = step if step > 0 else 1
    regA_val = data['7']; regB_val = data['8']
    res_val  = data['9'] if data['9'] != '' else (regA_val + regB_val if step >= 6 else '')
    # アクティブ装置判定
    active   = 'memory' if step in (1,7) else 'cpu' if 2 <= step <= 6 else None
    color_mem = "#FFEEBA" if active == 'memory' else "#FFF3CD"
    color_cpu = "#A3E4A1" if active == 'cpu' else "#D4EDDA"
    cpu_html = f"PC={pc_val}<BR/>A={regA_val}<BR/>B={regB_val}<BR/>結果={res_val}"
    # Graphvizソース（フォントサイズ大きく）
    source = f'''digraph devices {{
      graph [nodesep=1.5, ranksep=2.0];
      node [shape=box, style=filled, fontname="Arial", width=4, height=2, penwidth=2];
      memory [label=<<FONT POINT-SIZE="36">{mem_html}</FONT>>,
              fillcolor="{color_mem}", color="black"];
      cpu    [label=<<FONT POINT-SIZE="36">{cpu_html}</FONT>>,
              fillcolor="{color_cpu}", color="black"];
      keyboard [label=<<FONT POINT-SIZE="36">キーボード</FONT>>,
                fillcolor="#F8D7DA", color="black"];
      display  [label=<<FONT POINT-SIZE="36">ディスプレイ</FONT>>,
                fillcolor="#D1ECF1", color="black"];
      keyboard -> cpu [arrowsize=3];
      cpu -> display  [arrowsize=3];
      memory -> cpu   [arrowsize=3];
      cpu -> memory   [arrowsize=3];
    }}'''
    st.graphviz_chart(source)

# 右カラム：ステップ詳細表示
with col2:
    def show_step(text):
        st.markdown(f"<div class='step-header'>{text}</div>", unsafe_allow_html=True)
    if step >= 1:
        show_step('ステップ1: 主記憶装置にデータ／命令を格納')
        df = pd.DataFrame.from_dict(data, orient='index', columns=['内容'])
        df.index.name = '番地'
        st.table(df)
        show_status(pc=1)
    if step >= 2:
        show_step('ステップ2: プログラムカウンタが命令を指す')
        show_status(pc=1)
    if step >= 3:
        show_step('ステップ3: 命令を読み込む')
        inst = data['1']
        show_status(pc=2, inst=inst)
    if step >= 4:
        show_step('ステップ4: 命令を解釈')
        show_status(pc=2, inst=inst)
    if step >= 5:
        show_step('ステップ5: レジスタAにデータ転送')
        regA = data['7']
        show_status(pc=3, inst=inst, regA=regA)
    if step >= 6:
        show_step('ステップ6: 演算を実行')
        regA = data['7']; regB = data['8']
        result = regA + regB
        show_status(pc=3, inst=inst, regA=regA, regB=regB, result=result)
    if step >= 7:
        show_step('ステップ7: 結果を主記憶装置に書き戻し')
        data['9'] = result
        show_status(pc=4, inst=data['2'], regA=regA, regB=regB, result=result)
        st.success(f"完了: 番地9に演算結果 {result} を格納しました。")
