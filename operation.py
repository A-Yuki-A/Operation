import streamlit as st
import graphviz as gv

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
    st.write("命令: A + B の合計をCに保存")
    if st.button("次へ (命令実行)"):
        next_step()
    if st.button("リセット"):
        reset()

# ステップ定義
dot = gv.Digraph(format='png')
step_labels = [
    '1. 主記憶に値登録',
    '2. PCが命令アドレスを指す',
    '3. IRに命令読み込み',
    '4. 命令解読',
    '5. レジスタ転送',
    '6. ALUで計算',
    '7. 結果書き戻し'
]
# ノードの追加
for idx, label in enumerate(step_labels):
    if idx <= st.session_state.step - 1:
        dot.node(str(idx), label, style='filled', fillcolor='lightblue')
    else:
        dot.node(str(idx), label)
# エッジの追加
for idx in range(len(step_labels) - 1):
    dot.edge(str(idx), str(idx+1))

# フローチャート表示
st.subheader("命令実行フロー（フローチャート表示）")
st.graphviz_chart(dot)

# ステップ詳細表示
step = st.session_state.step
steps = [
    ("ステップ1: 主記憶装置に値を登録", [f"主記憶: A = {A}", f"主記憶: B = {B}" ]),
    ("ステップ2: プログラムカウンタ → 命令アドレスを指す", ["PC が次に実行する命令のアドレスを示しています。"]),
    ("ステップ3: 命令レジスタに命令を読み込み", ["命令レジスタ (IR) に 'ADD A, B → C' が読み込まれました。"]),
    ("ステップ4: 命令解読器が命令を解読", ["命令解読器が 'A と B を足して C に保存せよ' と解読しました。"]),
    ("ステップ5: レジスタにデータを転送", [f"レジスタA ← {A}", f"レジスタB ← {B}" ]),
    ("ステップ6: 演算装置 (ALU) で計算", [f"ALU: {A} + {B} = {A + B}" ]),
    ("ステップ7: 結果を主記憶装置に書き戻し", [f"主記憶: C ← {A + B}" ]),
]
# 現在のステップまでをすべて表示
display_count = min(step, len(steps))
for i in range(display_count):
    title, lines = steps[i]
    st.subheader(title)
    for line in lines:
        st.write(f"- {line}")

# 完了時メッセージ
if step > len(steps):
    st.subheader("完了: 命令実行フローの体験が終了しました")
    st.write(f"計算結果: C = {A + B}")
    st.info("リセットして、別の値でもう一度試せます。")
