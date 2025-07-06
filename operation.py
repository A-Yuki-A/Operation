import streamlit as st
import pandas as pd
import math

# CSS for styling
st.markdown(
    """
    <style>
      .step-header { font-size: 15px !important; font-weight: bold; }
      .status-box { border:1px solid #ccc; padding:10px; border-radius:5px; margin-bottom:10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0

# Control functions
def next_step():
    st.session_state.step += 1

def reset():
    st.session_state.step = 0

# Title and description
st.title("CPU 命令実行フロー体験アプリ")
st.caption("※ 'READ A' の A は汎用レジスタAを表します。")

# Sidebar: inputs and PC
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0)
    step = st.session_state.step
    # PC increments on each fetch (ステップ3,5,7)
    pc = 1 if step < 3 else math.ceil((step - 1) / 2)
    st.markdown(
        f"**プログラムカウンタ :** <span style='font-size:32px'>{pc}</span>",
        unsafe_allow_html=True
    )
    if st.button("次へ (命令実行)"):
        next_step()
    if st.button("リセット"):
        reset()

# Memory initialization
data = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--', '6': '--',
    '7': A, '8': B, '9': '--'
}

# Status display helper
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

# Layout: two columns
step = st.session_state.step
col1, col2 = st.columns([2, 1])

# Left column: device diagram
with col1:
    st.subheader("各装置の関係図 (動作中)")
    # Build HTML table for memory
    rows = ""
    for addr in map(str, range(1, 10)):
        rows += f"<TR><TD ALIGN='LEFT'>{data[addr]}</TD><TD ALIGN='LEFT'>{addr}</TD></TR>"
    table_html = f"<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'>{rows}</TABLE>"
    # PC, registers, result
    pc = 1 if step < 3 else math.ceil((step - 1) / 2)
    regA = data['7']; regB = data['8']
    result = data['9'] if data['9'] != '--' else (regA + regB if step >= 6 else '')
    # Highlight
    active = 'memory' if step in (1,7) else 'cpu' if 2 <= step <= 6 else None
    color_mem = '#FFEEBA' if active == 'memory' else '#E0FFE0'
    color_cpu = '#A3E4A1' if active == 'cpu' else '#E0F7FF'
    # Graphviz template with Python .format
    dot_template = '''
    digraph cpu_flow {{
      rankdir=LR;
      subgraph cluster_ctrl {{
        label="制御装置"; style=filled; fillcolor="{ctrl_color}"; rankdir=TB;
        node [shape=box, fontsize=16, fontname="Arial"];
        PC [label="プログラムカウンタ: {pc}"];
        IR [label="命令レジスタ: {instr1}"];
        Decoder [label="命令解読器"];
        Clock [label="クロックジェネレータ"];
      }}
      subgraph cluster_alu {{
        label="演算装置"; style=filled; fillcolor="{alu_color}"; rankdir=TB;
        node [shape=box, fontsize=16, fontname="Arial"];
        RegA [label="レジスタA: {regA}"];
        RegB [label="レジスタB: {regB}"];
        ALU  [label="算術論理演算装置"];
      }}
      subgraph cluster_mem {{
        label="主記憶装置"; style=filled; fillcolor="{mem_color}";
        node [shape=plaintext];
        Memory [label=<{table}>];
      }}
      keyboard [shape=box, label="キーボード", fontsize=16];
      display  [shape=box, label="ディスプレイ", fontsize=16];
      keyboard -> PC [len=0.5];
      PC -> IR    [len=0.5];
      IR -> Decoder;
      Decoder -> RegA;
      RegA -> ALU;
      ALU -> RegA [label="結果"];
      RegA -> Memory [len=0.5];
      Memory -> PC  [len=0.5];
      ALU -> display;
    }}
    '''
    dot = dot_template.format(
        ctrl_color=color_mem,
        pc=pc,
        instr1=data['1'],
        alu_color=color_cpu,
        regA=regA,
        regB=regB,
        mem_color=color_mem,
        table=table_html
    )
    st.graphviz_chart(dot)

# Right column: step details
with col2:
    def show_step(text):
        st.markdown(f"<div class='step-header'>{text}</div>", unsafe_allow_html=True)
    if step >= 1:
        show_step('ステップ1: メモリに命令・データを格納')
        df = pd.DataFrame.from_dict(data, orient='index', columns=['内容'])
        df.index.name = '番地'
        st.table(df)
        show_status(pc=1)
    if step >= 2:
        show_step('ステップ2: 命令フェッチ')
        show_status(pc=1)
    if step >= 3:
        show_step('ステップ3: 命令を読み込む')
        inst = data['1']
        show_status(pc=2, inst=inst)
    if step >= 4:
        show_step('ステップ4: 命令を解読')
        show_status(pc=2, inst=inst)
    if step >= 5:
        show_step('ステップ5: レジスタAにデータを転送')
        show_status(pc=3, inst=inst, regA=data['7'])
    if step >= 6:
        show_step('ステップ6: 演算を実行')
        show_status(pc=3, inst=inst, regA=data['7'], regB=data['8'], result=result)
    if step >= 7:
        show_step('ステップ7: 結果を書き戻す')
        data['9'] = result
        show_status(pc=4, inst=data['2'], regA=data['7'], regB=data['8'], result=result)
        st.success(f"完了: 番地9に演算結果 {result} を格納しました。")
