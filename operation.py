import streamlit as st
import pandas as pd

# --- 初期化 ---
def init_state():
    defaults = {
        'step': 0,
        'pc': 0,
        'ir': '',
        'memory': {
            0: 'READ A,100',
            1: 'READ B,101',
            2: 'ADD A,B',
            3: 'WRITE 102,C',
            4: 'STOP',
            100: 3,
            101: 5,
            102: None,
        },
        'registers': {'A': None, 'B': None, 'C': None},
        'running': True,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

st.title('CPU 動作可視化デモ')

# ステップ実行ボタン
if st.button('次のステップへ') and st.session_state.running:
    # フェッチ
    addr = st.session_state.pc
    inst = st.session_state.memory.get(addr)
    st.session_state.ir = inst
    st.session_state.pc += 1

    # デコード＆実行
    if inst and inst.startswith('READ'):
        reg, mem_addr = inst.split()[1].split(',')
        st.session_state.registers[reg] = st.session_state.memory[int(mem_addr)]
    elif inst and inst.startswith('ADD'):
        a = st.session_state.registers['A']
        b = st.session_state.registers['B']
        st.session_state.registers['C'] = a + b
    elif inst and inst.startswith('WRITE'):
        parts = inst.split()[1].split(',')
        mem_addr = int(parts[0])
        reg = parts[1]
        st.session_state.memory[mem_addr] = st.session_state.registers[reg]
    elif inst == 'STOP':
        st.session_state.running = False

    st.session_state.step += 1

# 制御装置、演算装置、主記憶装置の表示
cu, alu, mem = st.columns(3)
with cu:
    st.subheader('制御装置')
    st.write(f"**ステップ**: {st.session_state.step}")
    st.write(f"プログラムカウンタ (PC): {st.session_state.pc}")
    st.write(f"命令レジスタ (IR): {st.session_state.ir}")

with alu:
    st.subheader('演算装置')
    st.write('| レジスタ | 値 |')
    st.write('| :-: | :-: |')
    for r, v in st.session_state.registers.items():
        st.write(f'| {r} | {v} |')

with mem:
    st.subheader('主記憶装置')
    rows = []
    for addr in sorted(st.session_state.memory.keys()):
        rows.append({'アドレス': addr, '内容': st.session_state.memory[addr]})
    df = pd.DataFrame(rows)
    st.table(df)

# プログラム終了時のメッセージ
if not st.session_state.running:
    st.success('プログラムが終了しました。アドレス102に結果が保存されています。')
