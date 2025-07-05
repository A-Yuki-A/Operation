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

# タイトル
st.title("CPU 命令実行フロー体験アプリ")
st.caption("※ 'READ A' の A はレジスタA を表しています。" )

# サイドバー: 入力パネルとPC表示
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0)
    pc_val = st.session_state.step if st.session_state.step > 0 else 1
    st.write(f"プログラムカウンタ (PC): 番地{pc_val}")
    st.button("次へ (命令実行)", on_click=next_step)
    st.button("リセット", on_click=reset)

# メモリと命令セット
memory = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--', '6': '--',
    '7': A, '8': B, '9': ''
}

# ステータス表示
def show_status(pc=None, inst=None, regA=None, regB=None, result=None):
    st.markdown("<div class='status-box'>", unsafe_allow_html=True)
    if pc is not None:    st.write(f"**PC**: 番地{pc}")
    if inst:              st.write(f"**命令**: {inst}")
    if regA is not None:  st.write(f"**レジスタA**: {regA}")
    if regB is not None:  st.write(f"**レジスタB**: {regB}")
    if result is not None:st.write(f"**演算結果**: {result}")
    st.markdown("</div>", unsafe_allow_html=True)

step = st.session_state.step

# フローチャート表示
labels = ['1. メモリ格納','2. PC→命令','3. 命令読み込み','4. 解釈','5. レジスタ転送','6. 演算','7. 書き戻し']
dot = ['digraph G {','  rankdir=LR;','  node[shape=box,fontname="Helvetica"];']
for i,label in enumerate(labels):
    style = 'style=filled,fillcolor="lightblue"' if i < step else ''
    dot.append(f'  n{i} [{style} label="{label}"];')
for i in range(len(labels)-1):
    dot.append(f'  n{i} -> n{i+1};')
dot.append('}')
st.subheader("命令実行フロー（フローチャート）")
st.graphviz_chart("\n".join(dot))

# ステップ表示補助
def show_step(text): st.markdown(f"<div class='step-header'>{text}</div>", unsafe_allow_html=True)

# 各ステップ詳細
if step >= 1:
    show_step('ステップ1: 主記憶装置にデータ／命令を格納')
    df = pd.DataFrame.from_dict(memory, orient='index', columns=['内容'])
    df.index.name = '番地'
    st.table(df)
    show_status(pc=1)
if step >= 2:
    show_step('ステップ2: プログラムカウンタが命令を指す')
    show_status(pc=1)
if step >= 3:
    show_step('ステップ3: 命令を読み込む')
    inst = memory['1']
    show_status(pc=2, inst=inst)
if step >= 4:
    show_step('ステップ4: 命令を解釈')
    show_status(pc=2, inst=inst)
if step >= 5:
    show_step('ステップ5: レジスタAにデータ転送')
    regA = memory['7']
    show_status(pc=3, inst=inst, regA=regA)
if step >= 6:
    show_step('ステップ6: 演算を実行')
    regA = memory['7']; regB = memory['8']
    result = regA + regB
    show_status(pc=3, inst=inst, regA=regA, regB=regB, result=result)
if step >= 7:
    show_step('ステップ7: 結果を主記憶装置に書き戻し')
    memory['9'] = result
    show_status(pc=4, inst=memory['2'], regA=regA, regB=regB, result=result)
    st.success(f"完了: 番地9に演算結果 {result} を格納しました。")

# 各装置の関係図(動作中)
st.subheader("各装置の関係図(動作中)")
# 動的メモリ内容
mem_labels = "
".join([f"番地{addr}: {memory[addr]}" for addr in sorted(memory.keys(), key=int)])
# CPU内部状態
regA_val = memory['7']
regB_val = memory['8']
res_val  = memory['9'] if memory['9'] != '' else (regA_val + regB_val if step >= 6 else '')
# アクティブ装置判定
active = 'memory' if step in (1,7) else 'cpu' if 2 <= step <= 6 else None

# Graphvizで見やすくスタイル設定
mem_html  = mem_labels.replace("
", "<BR/>")
color_mem = "#FFEEBA" if active=="memory" else "black"
color_cpu = "#A3E4A1" if active=="cpu" else "black"
cpu_label = "<BR/>".join([f"PC={pc_val}", f"A={regA_val}", f"B={regB_val}", f"結果={res_val}"])

dot2 = f"""
digraph devices {{
  graph [nodesep=1.0, ranksep=1.0];
  node [shape=box, style=filled, fontname="Helvetica", fontsize=24, width=2, height=1];

  memory [label=<{mem_html}>, fillcolor="#FFF3CD", color="{color_mem}"];
  cpu    [label=<{cpu_label}>, fillcolor="#D4EDDA", color="{color_cpu}"];
  keyboard [label="キーボード", fillcolor="#F8D7DA", color="black"];
  display  [label="ディスプレイ", fillcolor="#D1ECF1", color="black"];

  keyboard -> cpu [arrowsize=2];
  cpu -> display  [arrowsize=2];
  memory -> cpu   [arrowsize=2];
  cpu -> memory   [arrowsize=2];
}}
"""
st.graphviz_chart(dot2)
