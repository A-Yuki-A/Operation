import streamlit as st
import pandas as pd
import math

# CSS 調整
st.markdown(
    """
    <style>
      .step-header { font-size: 15px !important; font-weight: bold; }
      .status-box { border:1px solid #ccc; padding:10px; border-radius:5px; margin-bottom:10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# セッション初期化
if 'step' not in st.session_state:
    st.session_state.step = 0

# 操作関数
def next_step():
    st.session_state.step += 1

def reset():
    st.session_state.step = 0

# タイトル
st.title("CPU 命令実行フロー体験アプリ")
st.caption("※ 'READ A' の A はレジスタA を表しています。")

# サイドバー: 入力とPC表示
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0)
    # プログラムカウンタ計算
    step = st.session_state.step
    if step < 3:
        pc_val = 1
    else:
        pc_val = math.ceil((step - 1) / 2)
    st.markdown(
        f"**プログラムカウンタ :** <span style='font-size:32px'>{pc_val}</span>",
        unsafe_allow_html=True
    )
    st.button("次へ (命令実行)", on_click=next_step)
    st.button("リセット", on_click=reset)

# メモリ初期化
data = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--', '6': '--',
    '7': A, '8': B, '9': '--'
}

# ステータス表示

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

# メインレイアウト
step = st.session_state.step
col1, col2 = st.columns([2,1])

# 左カラム: 装置図
with col1:
    st.subheader("各装置の関係図 (動作中)")
    # メモリ表示
    mem_labels = "\n".join([f"番地{addr}: {data[addr]}" for addr in sorted(data.keys(), key=int)])
    mem_html = mem_labels.replace("\n", "<BR/>")
    # PCカウンタ
    if step < 3:
        pc = 1
    else:
        pc = math.ceil((step - 1) / 2)
    # レジスタ・結果
    regA = data['7']; regB = data['8']
    result = data['9'] if data['9'] != '--' else (regA + regB if step >= 6 else '')
    # ハイライト色
    active = 'memory' if step in (1,7) else 'cpu' if 2 <= step <=6 else None
    color_mem = '#FFEEBA' if active=='memory' else '#FFF3CD'
    color_cpu = '#A3E4A1' if active=='cpu' else '#D4EDDA'
    cpu_html = f"PC={pc}<BR/>A={regA}<BR/>B={regB}<BR/>結果={result}"
        # Graphviz ソース (改良版)
    source = f'''
    digraph devices {{
      graph [nodesep=1.5, ranksep=2.0];
      node [shape=box, style=filled, fontname="Arial", fontsize=20, labeljust="l", width=4, height=2, penwidth=2];
      memory [label=<
        {mem_html}
      >, fillcolor="{color_mem}", color="black"];
      cpu    [label=<
        {cpu_html}
      >, fillcolor="{color_cpu}", color="black"];
      keyboard [label="キーボード", fillcolor="#F8D7DA", color="black"];
      display  [label="ディスプレイ", fillcolor="#D1ECF1", color="black"];
      keyboard -> cpu [arrowsize=2, len=0.5];
      cpu -> display [arrowsize=2, len=0.5];
      memory -> cpu  [arrowsize=2, len=0.5];
      cpu -> memory  [arrowsize=2, len=0.5];
    }}
    '''
    st.graphviz_chart(source)

# 右カラム: ステップ詳細
with col2:
    def show_step(text): st.markdown(f"<div class='step-header'>{text}</div>", unsafe_allow_html=True)
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
        show_status(pc=3, inst=inst, regA=regA)
    if step >= 6:
        show_step('ステップ6: 演算を実行')
        show_status(pc=3, inst=inst, regA=regA, regB=regB, result=result)
    if step >= 7:
        show_step('ステップ7: 結果を主記憶装置に書き戻し')
        data['9'] = result
        show_status(pc=4, inst=data['2'], regA=regA, regB=regB, result=result)
        st.success(f"完了: 番地9に演算結果 {result} を格納しました。")
