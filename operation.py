import streamlit as st
import pandas as pd
import copy

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
        'active': None,  # 'cu', 'alu', 'mem'
        'history': [],    # 状態履歴
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(val)
    # 初期状態を履歴に追加
    if not st.session_state.history:
        st.session_state.history.append(snapshot_state())

# --- スナップショット作成 ---
def snapshot_state():
    return {
        'step': st.session_state.step,
        'pc': st.session_state.pc,
        'ir': st.session_state.ir,
        'memory': copy.deepcopy(st.session_state.memory),
        'registers': copy.deepcopy(st.session_state.registers),
        'running': st.session_state.running,
        'active': st.session_state.active,
    }

init_state()

st.title('CPU 動作可視化デモ')

# 戻る／進むボタン
col1, col2 = st.columns(2)
with col1:
    if st.button('◀ 戻る') and len(st.session_state.history) > 1:
        # 履歴から戻る
        st.session_state.history.pop()  # 現在状態を削除
        prev = st.session_state.history[-1]
        # 状態を復元
        for k, v in prev.items():
            if k in ['memory', 'registers']:
                st.session_state[k] = copy.deepcopy(v)
            else:
                st.session_state[k] = v
        st.experimental_rerun()
with col2:
    if st.button('次のステップへ') and st.session_state.running:
        # フェッチ
        st.session_state.active = 'cu'
        addr = st.session_state.pc
        inst = st.session_state.memory.get(addr)
        st.session_state.ir = inst
        st.session_state.pc += 1
        # 実行
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
            mem_addr = int(parts[0]); reg = parts[1]
            st.session_state.memory[mem_addr] = st.session_state.registers[reg]
        elif inst == 'STOP':
            st.session_state.active = 'cu'
            st.session_state.running = False
        st.session_state.step += 1
        # 履歴に追加
        st.session_state.history.append(snapshot_state())
        st.experimental_rerun()

# 現在の動作説明
desc = ''
inst = st.session_state.ir or ''
if not st.session_state.running:
    desc = 'プログラムは停止しています。'
else:
    if st.session_state.active == 'cu':
        desc = '制御装置が次の命令をフェッチしています。'
    elif st.session_state.active == 'alu':
        desc = '演算装置がレジスタAとBの加算を実行しています。'
    elif st.session_state.active == 'mem':
        if inst.startswith('READ'):
            desc = f'主記憶装置から{inst.split()[1]}を読み込んでレジスタにセットしています。'
        elif inst.startswith('WRITE'):
            desc = f'レジスタ{inst.split()[1].split(",")[1]}の値を主記憶装置に書き込んでいます。'
        else:
            desc = '主記憶装置で読み書きを行っています。'
st.info(desc)

# 表示用コンテナ

def styled_container(content_fn, unit_key):
    color = '#fffae6' if st.session_state.active == unit_key else '#f8f9fa'
    border = '3px solid #ff9900' if st.session_state.active == unit_key else '1px solid #ddd'
    st.markdown(f"<div style='padding:10px; background-color:{color}; border:{border}; border-radius:5px;'>", unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)

cu_col, alu_col, mem_col = st.columns(3)
with cu_col:
    styled_container(lambda: (
        st.subheader('制御装置'),
        st.write(f"ステップ: {st.session_state.step}"),
        st.write(f"プログラムカウンタ (PC): {st.session_state.pc}"),
        st.write(f"命令レジスタ (IR): {st.session_state.ir}")
    ), 'cu')
with alu_col:
    styled_container(lambda: (
        st.subheader('演算装置'),
        st.write('| レジスタ | 値 |'),
        st.write('| :-: | :-: |'),
        [st.write(f'| {r} | {v} |') for r, v in st.session_state.registers.items()]
    ), 'alu')
with mem_col:
    styled_container(lambda: (
        st.subheader('主記憶装置'),
        st.table(pd.DataFrame([
            {'アドレス': addr, '内容': st.session_state.memory[addr]}
            for addr in sorted(st.session_state.memory.keys())
        ]))
    ), 'mem')

# 終了メッセージ
if not st.session_state.running:
    st.success('プログラムが終了しました。アドレス102に結果が保存されています。')
