import streamlit as st
import pandas as pd
import copy

# --- 用語説明 ---
def show_definitions():
    st.markdown('### 用語説明')
    defs = {
        'プログラムカウンタ (PC)': '次に実行する命令の番地を記録するレジスタ',
        '命令レジスタ (IR)': '主記憶装置から読み出した命令を一時的に保持するレジスタ',
        '主記憶装置': '命令やデータを格納しておく記憶領域',
        '演算装置': 'データの計算（加減乗除）を行う装置',
        '命令': 'CPUに対して何をするか指示するコード。例として READ A,100 の A はレジスタA、100 は主記憶装置の番地です。',
        'データ': '命令が扱う数値や文字などの情報',
        'レジスタ A, B, C': 'CPU内部の高速にアクセスできる小さな記憶領域で、主記憶装置から読み込んだデータを一時的に保持します。'
    }
    for term, desc in defs.items():
        st.write(f'**{term}**: {desc}')

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
        'active': None,
        'history': [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(val)
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

# 初期化
init_state()

# リセットボタン
if st.button('🔄 リセット'):
    st.session_state.clear()
    init_state()
    st.experimental_rerun()

# タイトルと用語説明
st.title('CPU 動作可視化デモ')
with st.expander('📖 用語説明を開く'):
    show_definitions()

# 現在の動作説明
inst = st.session_state.ir or ''
if not st.session_state.running:
    desc = 'プログラムは停止しています。'
elif st.session_state.active == 'cu':
    desc = '制御装置が次の命令をフェッチ（取得）しています。'
elif st.session_state.active == 'alu':
    desc = '演算装置がレジスタAとBのデータを使って加算を実行しています。'
elif st.session_state.active == 'mem':
    if inst.startswith('READ'):
        desc = f'主記憶装置から{inst.split()[1]}のデータを読み込んでいます。'
    elif inst.startswith('WRITE'):
        desc = f'レジスタ{inst.split()[1].split(",")[1]}の結果を主記憶装置に書き込んでいます。'
    else:
        desc = '主記憶装置でデータの読み書きを行っています。'
st.info(desc)

# 戻る／進むボタン
col1, col2 = st.columns(2)
with col1:
    if st.button('◀ 戻る') and len(st.session_state.history) > 1:
        st.session_state.history.pop()
        prev = st.session_state.history[-1]
        for k, v in prev.items():
            st.session_state[k] = copy.deepcopy(v) if isinstance(v, dict) else v
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
            mem_addr, reg = int(parts[0]), parts[1]
            st.session_state.memory[mem_addr] = st.session_state.registers[reg]
        elif inst == 'STOP':
            st.session_state.active = 'cu'
            st.session_state.running = False
        st.session_state.step += 1
        st.session_state.history.append(snapshot_state())

# 表示用スタイル
def styled_container(content_fn, unit_key):
    color = '#fffae6' if st.session_state.active == unit_key else '#f8f9fa'
    border = '3px solid #ff9900' if st.session_state.active == unit_key else '1px solid #ddd'
    st.markdown(f"<div style='padding:10px; background-color:{color}; border:{border}; border-radius:5px;'>", unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)

# 各装置表示
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

# プログラム終了メッセージ
if not st.session_state.running:
    st.success('プログラムが終了しました。アドレス102に結果が保存されています。')
