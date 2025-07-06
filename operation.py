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
        'active': None,  # 現在動いているユニット: 'cu', 'alu', 'mem'
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

st.title('CPU 動作可視化デモ')

# ステップ実行ボタン
if st.button('次のステップへ') and st.session_state.running:
    # フェッチ（制御装置）
    st.session_state.active = 'cu'
    addr = st.session_state.pc
    inst = st.session_state.memory.get(addr)
    st.session_state.ir = inst
    st.session_state.pc += 1

    # 実行フェーズ: アクティブユニットを切り替え
    if inst and inst.startswith('READ'):
        st.session_state.active = 'mem'
        reg, mem_addr = inst.split()[1].split(',')
        st.session_state.registers[reg] = st.session_state.memory[int(mem_addr)]
    elif inst and inst.startswith('ADD'):
        st.session_state.active = 'alu'
        a = st.session_state.registers['A']
        b = st.session_state.registers['B']
        st.session_state.registers['C'] = a + b
    elif inst and inst.startswith('WRITE'):
        st.session_state.active = 'mem'
        parts = inst.split()[1].split(',')
        mem_addr = int(parts[0])
        reg = parts[1]
        st.session_state.memory[mem_addr] = st.session_state.registers[reg]
    elif inst == 'STOP':
        st.session_state.active = 'cu'
        st.session_state.running = False

    st.session_state.step += 1

# 状態表示用スタイル関数
def styled_container(label, content_fn, unit_key):
    color = '#fffae6' if st.session_state.active == unit_key else '#f8f9fa'
    border = '3px solid #ff9900' if st.session_state.active == unit_key else '1px solid #ddd'
    st.markdown(f"<div style='padding:10px; background-color:{color}; border:{border}; border-radius:5px;'>", unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)

cu, alu, mem = st.columns(3)

with cu:
    styled_container('制御装置', lambda: (
        st.subheader('制御装置'),
        st.write(f"**ステップ**: {st.session_state.step}"),
        st.write(f"プログラムカウンタ (PC): {st.session_state.pc}"),
        st.write(f"命令レジスタ (IR): {st.session_state.ir}")
    ), 'cu')

with alu:
    styled_container('演算装置', lambda: (
        st.subheader('演算装置'),
        st.write('| レジスタ | 値 |'),
        st.write('| :-: | :-: |'),
        [st.write(f'| {r} | {v} |') for r, v in st.session_state.registers.items()]
    ), 'alu')

with mem:
    styled_container('主記憶装置', lambda: (
        st.subheader('主記憶装置'),
        (st.table(pd.DataFrame([
            {'アドレス': addr, '内容': st.session_state.memory[addr]}
            for addr in sorted(st.session_state.memory.keys())
        ])))
    ), 'mem')

# プログラム終了時メッセージ
if not st.session_state.running:
    st.success('プログラムが終了しました。アドレス102に結果が保存されています。')
