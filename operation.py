import streamlit as st
import pandas as pd

# --- 初期化 ---
if 'step' not in st.session_state:
    st.session_state.step = 0  # 現在のステップ数
    st.session_state.pc = 0    # プログラムカウンタ
    st.session_state.ir = ''   # 命令レジスタ
    # メモリ: 命令領域 0-4, データ領域 100-102
    st.session_state.memory = {
        0: 'READ A,100',
        1: 'READ B,101',
        2: 'ADD A,B',
        3: 'WRITE 102,C',
        4: 'STOP',
        100: 3,
        101: 5,
        102: None,
    }
    # 汎用レジスタ A, B, C
    st.session_state.registers = {'A': None, 'B': None, 'C': None}
    st.session_state.running = True

st.title('CPU 動作可視化デモ')

# ステップ実行ボタン
if st.button('次のステップへ') and st.session_state.running:
    # フェッチ
    addr = st.session_state.pc
    inst = st.session_state.memory.get(addr)
    st.session_state.ir = inst
    st.session_state.pc += 1

    # デコード＆実行
    if inst.startswith('READ'):
        # 例: READ A,100
        reg, mem_addr = inst.split()[1].split(',')
        st.session_state.registers[reg] = st.session_state.memory[int(mem_addr)]
    elif inst.startswith('ADD'):
        # ADD A,B → C = A + B
        a = st.session_state.registers['A']
        b = st.session_state.registers['B']
        st.session_state.registers['C'] = a + b
    elif inst.startswith('WRITE'):
        # WRITE 102,C
        parts = inst.split()[1].split(',')
        mem_addr = int(parts[0])
        reg = parts[1]
        st.session_state.memory[mem_addr] = st.session_state.registers[reg]
    elif inst == 'STOP':
        st.session_state.running = False

    st.session_state.step += 1

# コントロール装置表示
cu, alu, mem = st.columns(3)
with cu:
    st.subheader('制御装置')
    st.write(f"**ステップ**: {st.session_state.step}")
    st.write(f"プログラムカウンタ (PC): {st.session_state.pc}")
    st.write(f"命令レジスタ (IR): {st.session_state.ir}")

# 演算装置とレジスタ表示
with alu:
    st.subheader('演算装置')
    st.write('| レジスタ | 値 |')
    st.write('| :-: | :-: |')
    for r, v in st.session_state.registers.items():
        st.write(f'| {r} | {v} |')

# メモリ表示
with mem:
    st.subheader('主記憶装置')
    rows = []
    for addr in sorted(st.session_state.memory.keys()):
        rows.append({'アドレス': addr, '内容': st.session_state.memory[addr]})
    df = pd.DataFrame(rows)
    st.table(df)

# 終了時メッセージ
if not st.session_state.running:
    st.success('プログラムが終了しました。アドレス102に結果が保存されています。')
