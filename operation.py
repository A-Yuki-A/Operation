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

# ステップ操作
def next_step():
    st.session_state.step += 1

def reset():
    st.session_state.step = 0

# タイトル
st.title("CPU 命令実行フロー体験アプリ")
st.caption("※ 'READ A' の A はレジスタA を表しています。")

# サイドバー: 入力パネルとPC表示
with st.sidebar:
    st.header("入力パネル")
    A = st.number_input("値Aを入力 (番地7 に格納)", value=0, step=1)
    B = st.number_input("値Bを入力 (番地8 に格納)", value=0, step=1)
    # プログラムカウンタ
    pc_val = st.session_state.step if st.session_state.step > 0 else 1
    st.write(f"プログラムカウンタ (PC): 番地{pc_val}")
    st.button("次へ (命令実行)", on_click=next_step)
    st.button("リセット", on_click=reset)

# メモリと命令セットの初期化
memory = {
    '1': 'READ A, (7)',
    '2': 'ADD A, (8)',
    '3': 'WRITE (9), A',
    '4': 'STOP',
    '5': '--', '6': '--',
    '7': A, '8': B, '9': ''
}

# ステータス表示用関数
def show_status(pc=None, inst=None, regA=None, regB=None, result=None):
    st.markdown("<div class='status-box'>", unsafe_allow_html=True)
    if pc is not None: st.write(f"**PC**: 番地{pc}")
    if inst:       st.write(f"**実行中の命令**: {inst}")
    if regA is not None: st.write(f"**レジスタA**: {regA}")
    if regB is not None: st.write(f"**レジスタB**: {regB}")
    if result is not None: st.write(f"**計算結果**: {result}")
    st.markdown("</div>", unsafe_allow_html=True)

step = st.session_state.step

# フロー図 (Graphviz)
labels = ['1. メモリ格納','2. PC→命令','3. 命令読み込み','4. 解読','5. レジスタ転送','6. 計算','7. 書き戻し']
dot = ['digraph G {','  rankdir=LR;','  node [shape=box,fontname="Helvetica"];']
for i, l in enumerate(labels):
    style = 'style=filled,fillcolor="lightblue"' if i < step else ''
    dot.append(f'  n{i} [{style} label="{l}"];')
for i in range(len(labels)-1): dot.append(f'  n{i} -> n{i+1};')
dot.append('}')
st.subheader("命令実行フロー（フローチャート）")
st.graphviz_chart("\n".join(dot))

# ステップ詳細表示ヘッダ
show_header = lambda text: st.markdown(f"<div class='step-header'>{text}</div>", unsafe_allow_html=True)

# 各ステップの処理
# ステップ1: メモリ格納
if step >= 1:
    show_header('ステップ1: 主記憶装置にデータ／命令を格納')
    df = pd.DataFrame.from_dict(memory, orient='index', columns=['内容'])
    df.index.name = '番地'
    st.table(df)
    show_status(pc=1)
# ステップ2: PC指示
if step >= 2:
    show_header('ステップ2: プログラムカウンタが命令を指す')
    show_status(pc=1)
# ステップ3: 命令読み込み
if step >= 3:
    show_header('ステップ3: 命令を読み込む')
    inst = memory['1']
    show_status(pc=2, inst=inst)
# ステップ4: 命令解釈
if step >= 4:
    show_header('ステップ4: 命令を解釈')
    show_status(pc=2, inst=inst)
# ステップ5: レジスタ転送
if step >= 5:
    show_header('ステップ5: レジスタAにデータを転送')
    regA = memory['7']
    show_status(pc=3, inst=inst, regA=regA)
# ステップ6: 演算実行
if step >= 6:
    show_header('ステップ6: 演算を実行')
    regB = memory['8']
    calc = regA + regB
    show_status(pc=3, inst=inst, regA=regA, regB=regB, result=calc)
# ステップ7: 結果書き戻し
if step >= 7:
    show_header('ステップ7: 結果を主記憶装置に書き戻し')
    memory['9'] = calc
    show_status(pc=4, inst=memory['2'], regA=regA, regB=regB, result=calc)
    st.success(f"完了: 番地9に C = {calc} を保存しました。")
    st.info("リセットして再度実行できます。")

# 各装置の関係図（参考イメージ）
st.subheader("各装置の関係図イメージ")
dot2 = '''
digraph devices {
  rankdir=LR;
  node [shape=record,fontname="Helvetica"];
  memory [label="{主記憶装置|1|2|3|4|5|6|7|8|9}"];
  cpu [label="{CPU|{PC|レジスタA}|{演算装置}}"];
  keyboard [label="キーボード",shape=box];
  display [label="ディスプレイ",shape=box];
  keyboard -> cpu;
  cpu -> display;
  memory -> cpu;
  cpu -> memory;
}
'''
st.graphviz_chart(dot2)
