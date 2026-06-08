import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from deep_translator import GoogleTranslator

# ==============================================================================
# 中英名稱對照表 (常用/預設熱門股票)
# ==============================================================================
STOCK_NAME_CN = {
    '2330.TW': '台積電',
    'AAPL': '蘋果',
    '005930.KS': '三星電子',
    'SONY': '索尼',
    '090430.KS': '愛茉莉太平洋',
    'EL': '雅詩蘭黛',
    'LYV': 'Live Nation',
    'SPOT': 'Spotify',
    'SBUX': '星巴克',
    'KO': '可口可樂',
    'NKE': 'Nike'
}

# ==============================================================================
# 1. 網頁基礎設定與視覺美化 (CSS)
# ==============================================================================
st.set_page_config(
    page_title="互動式股票分析與財報評估系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自訂 CSS，打造現代感的高級 UI (支持紅黃綠燈卡片、同業PK表格與精緻佈局)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    
    /* 全域字體設定 */
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    /* 頂部漸層大標題 */
    .title-container {
        background: linear-gradient(135deg, #0f172a, #1e293b, #0f172a);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .main-title {
        background: linear-gradient(45deg, #00f2fe, #4facfe, #00ff87);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* 財務指標卡片樣式 */
    .health-card {
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: help;
    }
    
    .health-card:hover {
        transform: translateY(-3px);
    }
    
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* 紅黃綠燈上色等級 */
    .status-green {
        background: rgba(76, 175, 80, 0.12) !important;
        border: 1px solid rgba(76, 175, 80, 0.4) !important;
        color: #4caf50 !important;
    }
    
    .status-yellow {
        background: rgba(255, 152, 0, 0.12) !important;
        border: 1px solid rgba(255, 152, 0, 0.4) !important;
        color: #ff9800 !important;
    }
    
    .status-red {
        background: rgba(244, 67, 54, 0.12) !important;
        border: 1px solid rgba(244, 67, 54, 0.4) !important;
        color: #f44336 !important;
    }
    
    .status-gray {
        background: rgba(148, 163, 184, 0.1) !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        color: #94a3b8 !important;
    }

    /* 評估結果容器 */
    .eval-container {
        background: rgba(76, 175, 80, 0.05);
        border-left: 6px solid #4caf50;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .eval-container-warning {
        background: rgba(255, 152, 0, 0.05);
        border-left: 6px solid #ff9800;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .eval-header {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* 同業 PK 表格樣式 */
    .peer-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .peer-table th, .peer-table td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .peer-table th {
        background-color: rgba(79, 172, 254, 0.15);
        color: #4facfe;
        font-weight: 700;
    }
    .peer-table tr:hover {
        background-color: rgba(255, 255, 255, 0.03);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 同業對照字典定義 (自動推薦同業用)
# ==============================================================================
PEER_MAP = {
    # --- 台股權值股 ---
    "2330.TW": "2303.TW",  # 台積電 -> 聯電
    "2317.TW": "2382.TW",  # 鴻海 -> 廣達
    "2454.TW": "QCOM",     # 聯發科 -> 高通
    "2308.TW": "2301.TW",  # 台達電 -> 光寶科
    "2881.TW": "2882.TW",  # 富邦金 -> 國泰金
    "2882.TW": "2881.TW",  # 國泰金 -> 富邦金
    "2382.TW": "2317.TW",  # 廣達 -> 鴻海
    "3711.TW": "2449.TW",  # 日月光投控 -> 京元電子
    "2412.TW": "3045.TW",  # 中華電 -> 台灣大
    "2603.TW": "2609.TW",  # 長榮 -> 陽明
    # --- 台股熱門 ETF ---
    "0056.TW": "00878.TW",
    "00878.TW": "0056.TW",
    "0050.TW": "006208.TW",
    "006208.TW": "0050.TW",
    "00919.TW": "00929.TW",
    "00929.TW": "00919.TW",
    # --- 美股科技巨頭與熱門股 ---
    "AAPL": "MSFT",        # Apple -> Microsoft
    "MSFT": "GOOGL",       # Microsoft -> Alphabet
    "NVDA": "AMD",         # NVIDIA -> AMD
    "TSLA": "BYDDF",       # Tesla -> 比亞迪
    "GOOGL": "MSFT",       # Alphabet -> Microsoft
    "AMZN": "WMT",         # Amazon -> Walmart
    "META": "GOOGL",       # Meta -> Alphabet
    "NFLX": "DIS",         # Netflix -> Disney
    "AMD": "NVDA",         # AMD -> NVIDIA
    "QCOM": "2454.TW"      # Qualcomm -> 聯發科
}

# ==============================================================================
# 3. 數據載入與快取機制
# ==============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(symbol):
    """
    使用 yfinance 獲取歷史股價與基本面資料。
    快取時間設定為 1 小時 (3600秒)，提升重複點選時的讀取速度。
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y")
    
    info = {}
    try:
        info = ticker.info
    except Exception:
        info = {}
        
    return df, info

# ==============================================================================
# 4. 側邊欄控制面板配置
# ==============================================================================
st.sidebar.markdown("### 🔍 股票檢索")

# 初始化 session state，以利與快捷按鈕連動
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "2330.TW"

# Callback 函數：在 Rerun 之前安全更新指定 state
def update_symbol_callback(symbol):
    st.session_state.selected_symbol = symbol

# 4.1 搜尋框輸入
selected_symbol_input = st.sidebar.text_input(
    "搜尋股票代號",
    key="selected_symbol",
    help="輸入正確的股票代號，例如台股：2330.TW、美股：AAPL"
)
selected_symbol = selected_symbol_input.strip().upper()

st.sidebar.caption("💡 提示：輸入完成後，請按下 Enter 進行分析（支援代號例如：2330.TW, AAPL, 005930.KS）。目前系統已內建部分熱門股票之中英對照。")

# 4.2 技術指標動態控制
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 技術指標控制")
selected_indicators = st.sidebar.multiselect(
    "請選擇要顯示的技術指標：",
    options=['MA10', 'MA20', 'MA60', 'MA100', 'RSI', 'MACD'],
    default=['MA20', 'MA60'],
    help="選擇你想在圖表上疊加的分析工具，不知道怎麼選可以看下方的小辭典喔！"
)

with st.sidebar.expander("💡 這些指標代表什麼？", expanded=False):
    st.markdown("""
    *   **MA (移動平均線)**：  
        就像學生的「平時測驗平均分數」。**MA20 (月線)** 代表近一個月的短期趨勢；**MA60 (季線)** 代表近三個月的中期趨勢。當短線向上穿過長線（黃金交叉），通常代表近期有轉強趨勢。
    *   **RSI (相對強弱指標)**：  
        判斷這檔股票現在是不是「過熱」或「過冷」。數值通常在 0~100 之間。**超過 70** 代表可能買過頭了（容易回檔），**低於 30** 代表可能賣過頭了（有機會反彈）。
    *   **MACD (平滑異同移動平均線)**：  
        用來看出「趨勢的動能」。如果有**紅柱狀圖**出現並變長，代表上漲動能強；**綠柱狀圖**出現，則代表下跌動能較強。
    """)

# 4.3 生活化產業探索 Expander
st.sidebar.markdown("---")
with st.sidebar.expander("🍔 探索生活化產業股票", expanded=False):
    # 分類 1: 科技與攝影美學
    st.markdown("<small>**【科技與攝影美學】**</small>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("AAPL", help="蘋果 (Apple)", key="btn_AAPL", use_container_width=True, on_click=update_symbol_callback, args=("AAPL",))
    with c2:
        st.button("005930", help="三星電子 (005930.KS)", key="btn_005930.KS", use_container_width=True, on_click=update_symbol_callback, args=("005930.KS",))
    with c3:
        st.button("SONY", help="索尼 (Sony)", key="btn_SONY", use_container_width=True, on_click=update_symbol_callback, args=("SONY",))

    # 分類 2: 國際美妝與設計
    st.markdown("<small>**【國際美妝與設計】**</small>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("AMORE", help="愛茉莉太平洋 (090430.KS)", key="btn_090430.KS", use_container_width=True, on_click=update_symbol_callback, args=("090430.KS",))
    with c2:
        st.button("EL", help="雅詩蘭黛 (Estée Lauder)", key="btn_EL", use_container_width=True, on_click=update_symbol_callback, args=("EL",))

    # 分類 3: 流行音樂與展演
    st.markdown("<small>**【流行音樂與展演】**</small>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("LYV", help="Live Nation 演唱會娛樂", key="btn_LYV", use_container_width=True, on_click=update_symbol_callback, args=("LYV",))
    with c2:
        st.button("SPOT", help="Spotify", key="btn_SPOT", use_container_width=True, on_click=update_symbol_callback, args=("SPOT",))

    # 分類 4: 日常消費巨頭
    st.markdown("<small>**【日常消費巨頭】**</small>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("SBUX", help="星巴克 (Starbucks)", key="btn_SBUX", use_container_width=True, on_click=update_symbol_callback, args=("SBUX",))
    with c2:
        st.button("KO", help="可口可樂 (Coca-Cola)", key="btn_KO", use_container_width=True, on_click=update_symbol_callback, args=("KO",))
    with c3:
        st.button("NKE", help="Nike", key="btn_NKE", use_container_width=True, on_click=update_symbol_callback, args=("NKE",))

# 載入主股票數據
with st.spinner("正在加載歷史股價與財務數據..."):
    df, info = fetch_stock_data(selected_symbol)

if df.empty:
    st.error(f"⚠️ 無法獲取代號 `{selected_symbol}` 的歷史數據。請確認代號是否輸入正確（台股需加上 `.TW`，美股如 `AAPL`）。")
    st.stop()

# ==============================================================================
# 5. 基本資料與財務指標提取 (主標題)
# ==============================================================================
# 檢查是否在中文對照表中，若無則透過 GoogleTranslator 自動翻譯並動態快取
if selected_symbol in STOCK_NAME_CN:
    company_name = STOCK_NAME_CN[selected_symbol]
else:
    raw_name = info.get('shortName', info.get('longName', selected_symbol))
    if raw_name and raw_name != selected_symbol:
        try:
            # 自動將英文或外國名稱翻譯成繁體中文
            translated_name = GoogleTranslator(source='auto', target='zh-TW').translate(raw_name)
            # 動態寫入快取對照表中，避免重複打 API
            STOCK_NAME_CN[selected_symbol] = translated_name
            company_name = translated_name
        except Exception:
            # 翻譯出錯時 fallback 回原始英文名稱
            company_name = raw_name
    else:
        company_name = raw_name

# 判斷是否為 ETF
stock_code_clean = selected_symbol.split('.')[0]
is_etf = stock_code_clean.startswith('00')

title_suffix = "ETF 分析與健康度評估" if is_etf else "股票分析與財報體質評估"
subtitle_suffix = "當前市場走勢與 ETF 健康度評分" if is_etf else "當前市場走勢與基本面健康度評分"

st.markdown(f"""
<div class="title-container">
    <h1 class="main-title">{company_name} ({selected_symbol}) {title_suffix}</h1>
    <div class="sub-title">代號：{selected_symbol} | {subtitle_suffix}</div>
</div>
""", unsafe_allow_html=True)

if is_etf:
    # 提取 ETF 指標
    nav_price = info.get('navPrice')
    market_price = info.get('previousClose')
    if market_price is None and not df.empty:
        market_price = df['Close'].iloc[-1]
        
    if nav_price is not None and market_price is not None and nav_price > 0:
        premium_discount = ((market_price - nav_price) / nav_price) * 100
    else:
        premium_discount = None
        
    dividend_yield_val = info.get('dividendYield')
    if dividend_yield_val is None:
        dividend_yield_val = info.get('yield')
        if dividend_yield_val is not None:
            dividend_yield_val = dividend_yield_val * 100
            
    avg_volume = info.get('averageVolume')
    expense_ratio = info.get('netExpenseRatio')
else:
    # 提取個股財務指標
    pe_ratio = info.get('trailingPE')
    eps = info.get('trailingEps')
    gross_margin = info.get('grossMargins')  # 通常是小數 (例如: 0.53代表53%)
    debt_to_equity = info.get('debtToEquity')  # 通常是百分比 (例如: 50代表50%)
    dividend_yield = info.get('dividendYield')  
    price_to_book = info.get('priceToBook')

# ==============================================================================
# 6. 【創新功能】AI 財務健康評分與紅綠燈數據卡片
# ==============================================================================
st.markdown("### 🚦 財務健康度總覽 (紅綠燈)")

# A. 計算指標狀態與健康分數
if is_etf:
    etf_score = 0
    etf_total_checks = 0
    
    # 1. 折溢價評分
    if premium_discount is not None:
        etf_total_checks += 1
        if -0.5 <= premium_discount <= 0.5:
            pd_status = "status-green"
            etf_score += 3
        elif -1.0 <= premium_discount < -0.5 or 0.5 < premium_discount <= 1.0:
            pd_status = "status-yellow"
            etf_score += 2
        else:
            pd_status = "status-red"
            etf_score += 1
    else:
        pd_status = "status-gray"
        
    # 2. 殖利率評分
    if dividend_yield_val is not None:
        etf_total_checks += 1
        if dividend_yield_val >= 5.0:
            dy_status = "status-green"
            etf_score += 3
        elif 3.0 <= dividend_yield_val < 5.0:
            dy_status = "status-yellow"
            etf_score += 2
        else:
            dy_status = "status-red"
            etf_score += 1
    else:
        dy_status = "status-gray"
        
    # 3. 日均成交量評分
    if avg_volume is not None:
        etf_total_checks += 1
        avg_volume_lots = avg_volume / 1000
        if avg_volume_lots >= 5000:
            vol_status = "status-green"
            etf_score += 2
        elif 1000 <= avg_volume_lots < 5000:
            vol_status = "status-yellow"
            etf_score += 1
        else:
            vol_status = "status-red"
            etf_score += 0
    else:
        vol_status = "status-gray"
        
    # 4. 內扣費用評分
    if expense_ratio is not None:
        etf_total_checks += 1
        if expense_ratio <= 0.4:
            exp_status = "status-green"
            etf_score += 2
        elif 0.4 < expense_ratio <= 0.8:
            exp_status = "status-yellow"
            etf_score += 1
        else:
            exp_status = "status-red"
            etf_score += 0.5
    else:
        exp_status = "status-gray"
        
    health_score = 0.0
    if etf_total_checks > 0:
        health_score = min(etf_score, 10.0)
        
    if health_score >= 8:
        overall_status = "status-green"
        overall_text = "極佳"
    elif 5 <= health_score < 8:
        overall_status = "status-yellow"
        overall_text = "良好"
    else:
        overall_status = "status-red"
        overall_text = "待觀察"
        
    pd_text = f"{premium_discount:.2f}%" if premium_discount is not None else "無資料"
    dy_text = f"{dividend_yield_val:.2f}%" if dividend_yield_val is not None else "無資料"
    vol_text = f"{avg_volume / 1000:,.0f} 張" if avg_volume is not None else "無資料"
    exp_text = f"{expense_ratio:.3f}%" if expense_ratio is not None else "無資料"
    health_score_text = f"{health_score:.1f} / 10"
    
    health_tooltip = "AI ETF 健康度評估：結合折溢價、殖利率、日均成交量與內扣費用等數據分析 (0-10 分)。分值越高代表基金追蹤精確度、流動性與投資性價比越佳。"
    pd_tooltip = "折溢價 (Premium/Discount)：市價相對於基金實際淨值的偏離度。折溢價在 -0.5% 到 0.5% 之間為最健康 (綠燈)，溢價過大代表投資人正以高於實際價值的價格『買貴了』(紅燈)。"
    dy_tooltip = "股息殖利率 (Dividend Yield)：基金過去年度的配息水準。大於 5.0% 為優良 (綠燈)，對於主打高股息之 ETF 尤為關鍵。"
    vol_tooltip = "日均成交量 (Average Volume)：基金的市場流動性（單位：張）。大於 5,000 張代表市場極為活躍且買賣差價小 (綠燈)，過低可能面臨難以變現的流動性風險。"
    exp_tooltip = "內扣費用 (Expense Ratio)：基金的經理與保管費總和。低於 0.4% 代表費用低廉划算 (綠燈)，高於 0.8% 代表成本偏高，會長期蠶食投資人的獲利 (紅燈)。"
    
    col_score, col_pd, col_dy, col_vol, col_exp = st.columns(5)
    
    with col_score:
        st.markdown(f"""
        <div class="health-card {overall_status}" title="{health_tooltip}">
            <div class="metric-label">AI ETF 健康評估 ℹ️</div>
            <div class="metric-value">{health_score_text}</div>
            <div style="font-size: 0.8rem; font-weight: bold; margin-top: 5px;">【評級：{overall_text}】</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_pd:
        st.markdown(f"""
        <div class="health-card {pd_status}" title="{pd_tooltip}">
            <div class="metric-label">折溢價率 ℹ️</div>
            <div class="metric-value">{pd_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">市價與淨值偏離</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_dy:
        st.markdown(f"""
        <div class="health-card {dy_status}" title="{dy_tooltip}">
            <div class="metric-label">股息殖利率 ℹ️</div>
            <div class="metric-value">{dy_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">基金配息能力</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_vol:
        st.markdown(f"""
        <div class="health-card {vol_status}" title="{vol_tooltip}">
            <div class="metric-label">日均成交量 ℹ️</div>
            <div class="metric-value">{vol_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">市場流動性</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_exp:
        st.markdown(f"""
        <div class="health-card {exp_status}" title="{exp_tooltip}">
            <div class="metric-label">內扣年費用率 ℹ️</div>
            <div class="metric-value">{exp_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">經理與保管費</div>
        </div>
        """, unsafe_allow_html=True)
else:
    score = 0
    total_checks = 0

    # 1. EPS 評分
    if eps is not None:
        total_checks += 1
        if eps > 0:
            eps_status = "status-green"
            score += 3
        else:
            eps_status = "status-red"
    else:
        eps_status = "status-gray"

    # 2. PE 評分
    if pe_ratio is not None:
        total_checks += 1
        if pe_ratio < 0:
            pe_status = "status-red"
        elif pe_ratio < 15:
            pe_status = "status-green"
            score += 3
        elif 15 <= pe_ratio <= 35:
            pe_status = "status-yellow"
            score += 2
        else:
            pe_status = "status-red"
            score += 0.5
    else:
        pe_status = "status-gray"

    # 3. 毛利率評分
    if gross_margin is not None:
        total_checks += 1
        gm_percent = gross_margin * 100
        if gm_percent >= 45:
            gm_status = "status-green"
            score += 2
        elif 20 <= gm_percent < 45:
            gm_status = "status-yellow"
            score += 1
        else:
            gm_status = "status-red"
    else:
        gm_status = "status-gray"

    # 4. 負債比評分
    if debt_to_equity is not None:
        total_checks += 1
        is_financial = "2881" in selected_symbol or "2882" in selected_symbol
        if is_financial:
            de_status = "status-green"
            score += 2
        elif debt_to_equity <= 80:
            de_status = "status-green"
            score += 2
        elif 80 < debt_to_equity <= 150:
            de_status = "status-yellow"
            score += 1
        else:
            de_status = "status-red"
    else:
        de_status = "status-gray"

    # 計算滿分 10 分之綜合分數
    health_score = 0.0
    if total_checks > 0:
        # 比例換算：最高分為上述累加值 (3+3+2+2 = 10 分)
        health_score = min(score, 10.0)
        
    if health_score >= 8:
        overall_status = "status-green"
        overall_text = "極佳"
    elif 5 <= health_score < 8:
        overall_status = "status-yellow"
        overall_text = "良好"
    else:
        overall_status = "status-red"
        overall_text = "待觀察"

    # 格式化輸出文字
    pe_text = f"{pe_ratio:.2f} 倍" if pe_ratio is not None else "無資料"
    eps_text = f"{eps:.2f} 元" if eps is not None else "無資料"
    gm_text = f"{gross_margin * 100:.2f}%" if gross_margin is not None else "無資料"
    de_text = f"{debt_to_equity:.2f}%" if debt_to_equity is not None else "無資料"
    health_score_text = f"{health_score:.1f} / 10"

    # 懸浮提示內容 (Tooltip)
    health_tooltip = "AI 綜合體質評估：結合 EPS、PE、毛利率與負債比等數據分析 (0-10 分)。分值越高代表財務防守性與賺錢能力越強。"
    eps_tooltip = "每股盈餘 (EPS)：反映公司目前每股賺了多少錢。正值代表目前獲利，負值代表虧損。"
    pe_tooltip = "本益比 (PE)：代表目前估值水位。低於 15 倍相對便宜 (綠燈)，高於 35 倍偏貴或虧損 (紅燈)。"
    gm_tooltip = "毛利率 (Gross Margin)：反映公司產品的定價權與核心技術優勢。高於 45% 代表毛利極高，定價優勢明顯。"
    de_tooltip = "負債權益比 (D/E)：公司債務相較於股東權益的比例。低於 80% 代表槓桿適當、財務結構安全穩健。"

    # 渲染卡片 (st.columns 並排)
    col_score, col_eps, col_pe, col_gm, col_de = st.columns(5)

    with col_score:
        st.markdown(f"""
        <div class="health-card {overall_status}" title="{health_tooltip}">
            <div class="metric-label">AI 財務體質總評 ℹ️</div>
            <div class="metric-value">{health_score_text}</div>
            <div style="font-size: 0.8rem; font-weight: bold; margin-top: 5px;">【評級：{overall_text}】</div>
        </div>
        """, unsafe_allow_html=True)

    with col_eps:
        st.markdown(f"""
        <div class="health-card {eps_status}" title="{eps_tooltip}">
            <div class="metric-label">每股盈餘 (EPS) ℹ️</div>
            <div class="metric-value">{eps_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">獲利能力</div>
        </div>
        """, unsafe_allow_html=True)

    with col_pe:
        st.markdown(f"""
        <div class="health-card {pe_status}" title="{pe_tooltip}">
            <div class="metric-label">本益比 (PE) ℹ️</div>
            <div class="metric-value">{pe_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">估值合理性</div>
        </div>
        """, unsafe_allow_html=True)

    with col_gm:
        st.markdown(f"""
        <div class="health-card {gm_status}" title="{gm_tooltip}">
            <div class="metric-label">毛利率 (Gross Margin) ℹ️</div>
            <div class="metric-value">{gm_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">產品競爭力</div>
        </div>
        """, unsafe_allow_html=True)

    with col_de:
        st.markdown(f"""
        <div class="health-card {de_status}" title="{de_tooltip}">
            <div class="metric-label">負債權益比 (D/E) ℹ️</div>
            <div class="metric-value">{de_text}</div>
            <div style="font-size: 0.8rem; margin-top: 5px;">財務結構安全性</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ==============================================================================
# 7. 技術指標計算與動態 Plotly 均線/技術圖繪製
# ==============================================================================
# 7.1 技術指標計算
# 移動平均線
if 'MA10' in selected_indicators:
    df['MA10'] = df['Close'].rolling(window=10).mean()
if 'MA20' in selected_indicators:
    df['MA20'] = df['Close'].rolling(window=20).mean()
if 'MA60' in selected_indicators:
    df['MA60'] = df['Close'].rolling(window=60).mean()
if 'MA100' in selected_indicators:
    df['MA100'] = df['Close'].rolling(window=100).mean()

# RSI (14) 計算
if 'RSI' in selected_indicators:
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    loss = loss.replace(0, 0.00001)  # 避免除以零
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

# MACD 計算
if 'MACD' in selected_indicators:
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

# 7.2 Plotly Subplot 動態建構
show_rsi = 'RSI' in selected_indicators
show_macd = 'MACD' in selected_indicators

rows = 1
row_heights = [1.0]
if show_rsi and show_macd:
    rows = 3
    row_heights = [0.6, 0.2, 0.2]
elif show_rsi or show_macd:
    rows = 2
    row_heights = [0.7, 0.3]

fig = make_subplots(
    rows=rows,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=row_heights
)

# Row 1: 主 K 線與均線 (MA)
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='K 線',
    increasing_line_color='#FF4B4B',
    decreasing_line_color='#2E7D32'
), row=1, col=1)

# 疊加 MA 均線
ma_colors = {
    'MA10': '#E1BEE7',   # 粉紫
    'MA20': '#FFA726',   # 亮橘
    'MA60': '#29B6F6',   # 水藍
    'MA100': '#66BB6A'   # 淺綠
}
for ma in ['MA10', 'MA20', 'MA60', 'MA100']:
    if ma in selected_indicators and ma in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[ma],
            line=dict(color=ma_colors[ma], width=1.5),
            name=ma
        ), row=1, col=1)

# Row 2 (或 3): 繪製 RSI
current_row = 2
if show_rsi:
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        line=dict(color='#EC407A', width=1.5),
        name='RSI(14)'
    ), row=current_row, col=1)
    
    # 加上 70 / 30 臨界線
    fig.add_hline(y=70, line_dash="dash", line_color="#E53935", line_width=1, row=current_row, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#43A047", line_width=1, row=current_row, col=1)
    fig.update_yaxes(range=[0, 100], title_text="RSI(14)", row=current_row, col=1)
    current_row += 1

# Row 2 (或 3): 繪製 MACD
if show_macd:
    # MACD Line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD'],
        line=dict(color='#26A69A', width=1.2),
        name='MACD'
    ), row=current_row, col=1)
    
    # Signal Line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD_Signal'],
        line=dict(color='#FFA726', width=1.2),
        name='Signal'
    ), row=current_row, col=1)
    
    # Histograms
    hist_colors = ['#26A69A' if val >= 0 else '#EF5350' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['MACD_Hist'],
        marker_color=hist_colors,
        name='MACD Hist'
    ), row=current_row, col=1)
    fig.update_yaxes(title_text="MACD", row=current_row, col=1)

# 美化圖表版面
fig.update_layout(
    title=dict(
        text=f"📈 {company_name} ({selected_symbol}) 技術分析圖表",
        font=dict(size=18, family="Noto Sans TC")
    ),
    xaxis_title="日期" if rows == 1 else "",
    yaxis_title="股價",
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    height=400 + (rows - 1) * 150,  # 動態調整高度，避免擠壓
    margin=dict(l=50, r=50, t=80, b=50),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 8. 【創新功能】同業對比洞察面板 (PK 面板)
# ==============================================================================
st.markdown("---")
st.markdown("### 👥 同業對比 PK 面板")

default_peer = PEER_MAP.get(selected_symbol, "AAPL")
peer_symbol_input = st.text_input(
    "📊 輸入要 PK 的同業代號：",
    value=default_peer,
    help="系統會自動為你推薦最合適的對手，你也可以在此手動更改成其他股票代號！"
)
peer_symbol = peer_symbol_input.strip().upper()

# 抓取對比同業資料
with st.spinner(f"正在加載對手 {peer_symbol} 的財務數據..."):
    _, peer_info = fetch_stock_data(peer_symbol)

if not peer_info:
    st.warning(f"無法載入對手 `{peer_symbol}` 的基本面數據，請更換代號或檢查代號。")
else:
    # 提取對手名稱
    peer_name = peer_info.get('longName', peer_symbol)
    
    if is_etf:
        # 對手 ETF 數據提取
        peer_nav = peer_info.get('navPrice')
        peer_close = peer_info.get('previousClose')
        if peer_close is None:
            peer_close = 0
            
        if peer_nav is not None and peer_nav > 0:
            peer_pd = ((peer_close - peer_nav) / peer_nav) * 100
        else:
            peer_pd = None
            
        peer_dy = peer_info.get('dividendYield')
        if peer_dy is None:
            peer_dy = peer_info.get('yield')
            if peer_dy is not None:
                peer_dy = peer_dy * 100
                
        peer_vol = peer_info.get('averageVolume')
        peer_exp = peer_info.get('netExpenseRatio')
        
        # ETF PK 邏輯
        def judge_etf_pd(pd1, pd2):
            if pd1 is None or pd2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 追蹤較準" if abs(pd1) < abs(pd2) else f"🔵 {peer_symbol} 追蹤較準"
            
        def judge_etf_dy(dy1, dy2):
            if dy1 is None or dy2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 殖利率較高" if dy1 > dy2 else f"🔵 {peer_symbol} 殖利率較高"
            
        def judge_etf_vol(vol1, vol2):
            if vol1 is None or vol2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 流動性佳" if vol1 > vol2 else f"🔵 {peer_symbol} 流動性佳"
            
        def judge_etf_exp(exp1, exp2):
            if exp1 is None or exp2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 費用較低" if exp1 < exp2 else f"🔵 {peer_symbol} 費用較低"
            
        pk_pd = judge_etf_pd(premium_discount, peer_pd)
        pk_dy = judge_etf_dy(dividend_yield_val, peer_dy)
        pk_vol = judge_etf_vol(avg_volume, peer_vol)
        pk_exp = judge_etf_exp(expense_ratio, peer_exp)
        
        peer_pd_text = f"{peer_pd:.2f}%" if peer_pd is not None else "無資料"
        peer_dy_text = f"{peer_dy:.2f}%" if peer_dy is not None else "無資料"
        peer_vol_text = f"{peer_vol / 1000:,.0f} 張" if peer_vol is not None else "無資料"
        peer_exp_text = f"{peer_exp:.3f}%" if peer_exp is not None else "無資料"
        
        st.markdown(f"""
        <table class="peer-table">
            <thead>
                <tr>
                    <th>ETF 健康指標</th>
                    <th>🔍 當前標的：{company_name} ({selected_symbol})</th>
                    <th>⚔️ 對抗同業：{peer_name} ({peer_symbol})</th>
                    <th>🏆 優勢方</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>折溢價率</b></td>
                    <td>{pd_text}</td>
                    <td>{peer_pd_text}</td>
                    <td>{pk_pd}</td>
                </tr>
                <tr>
                    <td><b>股息殖利率</b></td>
                    <td>{dy_text}</td>
                    <td>{peer_dy_text}</td>
                    <td>{pk_dy}</td>
                </tr>
                <tr>
                    <td><b>日均成交量</b></td>
                    <td>{vol_text}</td>
                    <td>{peer_vol_text}</td>
                    <td>{pk_vol}</td>
                </tr>
                <tr>
                    <td><b>內扣年費用率</b></td>
                    <td>{exp_text}</td>
                    <td>{peer_exp_text}</td>
                    <td>{pk_exp}</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        # 提取個股財務指標
        peer_pe = peer_info.get('trailingPE')
        peer_eps = peer_info.get('trailingEps')
        peer_gm = peer_info.get('grossMargins')
        peer_de = peer_info.get('debtToEquity')

        # PK 對比邏輯
        def judge_pe(pe1, pe2):
            if pe1 is None or pe2 is None: return "無法判定 (資料缺失)"
            if pe1 > 0 and pe2 > 0:
                return f"🟢 {selected_symbol} 勝" if pe1 < pe2 else f"🔵 {peer_symbol} 勝"
            if pe1 > 0 and pe2 <= 0: return f"🟢 {selected_symbol} 勝"
            if pe2 > 0 and pe1 <= 0: return f"🔵 {peer_symbol} 勝"
            return f"🟢 {selected_symbol} 勝" if pe1 > pe2 else f"🔵 {peer_symbol} 勝"

        def judge_eps(eps1, eps2):
            if eps1 is None or eps2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 勝" if eps1 > eps2 else f"🔵 {peer_symbol} 勝"

        def judge_gm(gm1, gm2):
            if gm1 is None or gm2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 勝" if gm1 > gm2 else f"🔵 {peer_symbol} 勝"

        def judge_de(de1, de2):
            if de1 is None or de2 is None: return "無法判定"
            return f"🟢 {selected_symbol} 槓桿較輕" if de1 < de2 else f"🔵 {peer_symbol} 槓桿較輕"

        # 表格顯示對比
        pk_pe = judge_pe(pe_ratio, peer_pe)
        pk_eps = judge_eps(eps, peer_eps)
        pk_gm = judge_gm(gross_margin, peer_gm)
        pk_de = judge_de(debt_to_equity, peer_de)

        # 格式化同業資料
        peer_pe_text = f"{peer_pe:.2f} 倍" if peer_pe is not None else "無資料"
        peer_eps_text = f"{peer_eps:.2f} 元" if peer_eps is not None else "無資料"
        peer_gm_text = f"{peer_gm * 100:.2f}%" if peer_gm is not None else "無資料"
        peer_de_text = f"{peer_de:.2f}%" if peer_de is not None else "無資料"

        st.markdown(f"""
        <table class="peer-table">
            <thead>
                <tr>
                    <th>財務指標</th>
                    <th>🔍 當前標的：{company_name} ({selected_symbol})</th>
                    <th>⚔️ 對抗同業：{peer_name} ({peer_symbol})</th>
                    <th>🏆 優勢方</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>每股盈餘 (EPS)</b></td>
                    <td>{eps_text}</td>
                    <td>{peer_eps_text}</td>
                    <td>{pk_eps}</td>
                </tr>
                <tr>
                    <td><b>本益比 (PE)</b></td>
                    <td>{pe_text}</td>
                    <td>{peer_pe_text}</td>
                    <td>{pk_pe}</td>
                </tr>
                <tr>
                    <td><b>毛利率 (Gross Margin)</b></td>
                    <td>{gm_text}</td>
                    <td>{peer_gm_text}</td>
                    <td>{pk_gm}</td>
                </tr>
                <tr>
                    <td><b>負債權益比 (D/E)</b></td>
                    <td>{de_text}</td>
                    <td>{peer_de_text}</td>
                    <td>{pk_de}</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

# ==============================================================================
# 9. 基礎財報體質評估文字解析
# ==============================================================================
st.markdown("---")
st.markdown("### 📝 綜合體質診斷報告")

eval_comments = []

if is_etf:
    # (A) 折溢價分析
    if premium_discount is not None:
        if -0.5 <= premium_discount <= 0.5:
            eval_comments.append(f"🟢 **折溢價表現極佳**：當前折溢價為 {premium_discount:.2f}%，處於最健康的合理波動範圍（±0.5%），投資人此時買入幾乎沒有溢價「買貴」的風險。")
        elif 0.5 < premium_discount <= 1.0:
            eval_comments.append(f"🟡 **面臨輕微溢價**：當前溢價為 {premium_discount:.2f}%，代表市場熱度偏高，投資人正以略高於基金淨值的價格購入，建議留意是否回落。")
        elif -1.0 <= premium_discount < -0.5:
            eval_comments.append(f"🟡 **面臨輕微折價**：當前折價為 {premium_discount:.2f}%，代表市價略低於基金實際淨值，對買方而言性價比相對划算。")
        elif premium_discount > 1.0:
            eval_comments.append(f"🔴 **溢價幅度過高**：當前溢價達 {premium_discount:.2f}%（超過 1.0%），代表追蹤誤差偏大，投資人面臨明顯「買貴」風險，建議等待折溢價收斂後再行布局。")
        else:
            eval_comments.append(f"🟡 **折價幅度偏高**：當前折價達 {premium_discount:.2f}%，代表市場賣壓較重，雖然市價便宜，但應注意追蹤誤差或是否有成分股價格異常之狀況。")
    else:
        eval_comments.append("⚪ **折溢價評估**：未取得淨值資料，無法判定當前折溢價幅度。")

    # (B) 殖利率分析
    if dividend_yield_val is not None:
        if dividend_yield_val >= 5.0:
            eval_comments.append(f"🟢 **配息殖利率優良**：殖利率高達 {dividend_yield_val:.2f}%，能為投資人提供穩健且豐沛的股息現金流收益，非常適合高股息導向的投資組合。")
        elif 3.0 <= dividend_yield_val < 5.0:
            eval_comments.append(f"🟡 **配息殖利率尚可**：殖利率為 {dividend_yield_val:.2f}%，屬於市場平均水準，能提供基本穩定的現金回報。")
        else:
            eval_comments.append(f"🔴 **配息殖利率偏低**：殖利率僅 {dividend_yield_val:.2f}%，對於尋求高息回報的投資人而言吸引力較弱，其投資回報可能更依賴未來淨值上漲的資本利得。")
    else:
        eval_comments.append("⚪ **殖利率評估**：未取得殖利率資料，無法進行配息表現判定。")

    # (C) 流動性分析 (成交量)
    if avg_volume is not None:
        avg_volume_lots = avg_volume / 1000
        if avg_volume_lots >= 5000:
            eval_comments.append(f"🟢 **流動性極佳**：日均成交量達 {avg_volume_lots:,.0f} 張，市場買賣交投熱絡，申購與贖回價差小，投資人可安心隨時進行買賣交易，無流動性風險。")
        elif 1000 <= avg_volume_lots < 5000:
            eval_comments.append(f"🟡 **流動性尚可**：日均成交量為 {avg_volume_lots:,.0f} 張，基本能滿足一般散戶的交易需求，但大筆買賣時建議留意可能存在的些微價差。")
        else:
            eval_comments.append(f"🔴 **流動性偏低**：日均成交量僅 {avg_volume_lots:,.0f} 張（低於 1,000 張），存在流動性風險。容易面臨買賣價差過大，甚至想賣賣不掉的窘境。")
    else:
        eval_comments.append("⚪ **流動性評估**：未取得成交量資料，無法進行流動性判定。")

    # (D) 內扣費用分析
    if expense_ratio is not None:
        if expense_ratio <= 0.4:
            eval_comments.append(f"🟢 **內扣費用低廉**：內扣費用僅 {expense_ratio:.3f}%（低於 0.4%），屬於極具競爭力的低費用率基金，能為投資人最大化保留長期投資回報。")
        elif 0.4 < expense_ratio <= 0.8:
            eval_comments.append(f"🟡 **內扣費用合理**：內扣費用為 {expense_ratio:.3f}%，處於市場平均區間。")
        else:
            eval_comments.append(f"🔴 **內扣費用偏高**：內扣費用達 {expense_ratio:.3f}%（超過 0.8%），這類費用會長期從基金淨值中扣除，對長線投資人的獲利會造成較大的蠶食。")
    else:
        eval_comments.append("⚪ **內扣費用評估**：未取得經理/保管費數據，建議參考基金公開說明書。")

    # 綜合結論判定
    if health_score >= 8:
        card_class = "eval-container"
        rating_title = "🏆 ETF 健康體質健全 (優等)"
        verdict = "該 ETF 在流動性、費用率與追蹤誤差（折溢價）等關鍵健康指標表現卓越，適合做為長期資產配置的優質標的。"
    elif 5 <= health_score < 8:
        card_class = "eval-container-warning"
        rating_title = "⚖️ ETF 健康體質尚可 (中等)"
        verdict = "該 ETF 大部分指標正常，但可能有費用率偏高、流動性尚可或當前折溢價偏大的情況。建議在買入前留意即時折溢價，避免買貴。"
    else:
        card_class = "eval-container-warning"
        rating_title = "⚠️ ETF 健康體質待觀察 (注意風險)"
        verdict = "該 ETF 面臨流動性偏低、內扣費用過高或溢價幅度偏大的風險。流動性不足與偏高費用會嚴重蠶食長期投資回報，建議審慎評估。"
else:
    # (A) 獲利能力分析 (EPS)
    if eps is not None:
        if eps > 0:
            eval_comments.append("🟢 **獲利能力優良**：最近四季 EPS 為正值，顯示公司基本面良好且持續獲利中，能為股東創造實際價值。")
        else:
            eval_comments.append("🔴 **獲利結構虧損**：最近四季 EPS 為负值，表示公司目前處於虧損狀態。此時應深入了解是短期大環境拖累還是長期產業競爭力衰退。")
    else:
        eval_comments.append("⚪ **獲利能力評估**：目前未取得 EPS 歷史數據，無法進行獲利判定。")

    # (B) 估值水位分析 (PE)
    if pe_ratio is not None:
        if pe_ratio < 0:
            eval_comments.append("🔴 **估值評估偏危險**：本益比為負數，反映公司處於虧損。以本益比估值已無太大實質意義，需防範價值陷阱。")
        elif pe_ratio < 15:
            eval_comments.append(f"🟢 **估值相對便宜**：本益比目前為 {pe_ratio:.2f} 倍（低於 15 倍），屬於相對便宜或被低估的階段，防守安全邊際較高。")
        elif 15 <= pe_ratio <= 35:
            eval_comments.append(f"🟡 **估值處於合理區間**：本益比目前為 {pe_ratio:.2f} 倍，落在合理的市場定價範圍。此時股價表現主要取決於未來營收與產業成長動能。")
        else:
            eval_comments.append(f"🔴 **估值明顯偏高**：本益比高達 {pe_ratio:.2f} 倍，市場已給予極高的成長溢價。投資人需審慎評估公司的未來高成長是否真能兌現。")
    else:
        eval_comments.append("⚪ **估值水位評估**：無本益比資料，可能是因為公司暫無獲利或資料缺失。建議參考股價淨值比 (P/B) 來評估估值。")

    # (C) 產品競爭力分析 (毛利率)
    if gross_margin is not None:
        gm_percent = gross_margin * 100
        if gm_percent >= 45:
            eval_comments.append(f"🟢 **產品競爭力極強**：毛利率高達 {gm_percent:.2f}%，說明該企業在其領域擁有強大的定價權、品牌壁壘或高門檻的技術優勢。")
        elif 20 <= gm_percent < 45:
            eval_comments.append(f"🟡 **產品競爭力中等**：毛利率為 {gm_percent:.2f}%，屬於標準製造業或大宗科技產品水平，面臨一定程度的同業競爭壓力。")
        else:
            eval_comments.append(f"🔴 **產品競爭力薄弱**：毛利率僅 {gm_percent:.2f}%，屬於低毛利的薄利多銷模式。極易受到上游原材料上漲或下游殺價競爭影響。")
    else:
        eval_comments.append("⚪ **競爭力評估**：未取得毛利率數據，無法精準評估其產品護城河強度。")

    # (D) 財務防禦力分析 (負債比)
    if debt_to_equity is not None:
        is_financial = "2881" in selected_symbol or "2882" in selected_symbol
        if is_financial:
            eval_comments.append(f"🟡 **金融業財務槓桿**：負債權益比為 {debt_to_equity:.2f}%。由於本標的為金融機構，高負債屬於收取存款並放貸之行業常態。")
        elif debt_to_equity <= 80:
            eval_comments.append(f"🟢 **財務結構極為安全**：負債權益比僅 {debt_to_equity:.2f}%（低於 80%），代表公司負債極低，幾乎無債務違約風險。")
        elif 80 < debt_to_equity <= 150:
            eval_comments.append(f"🟡 **財務結構尚算健康**：負債權益比為 {debt_to_equity:.2f}%，債務槓桿適中。")
        else:
            eval_comments.append(f"🔴 **財務槓桿偏高**：負債權益比高達 {debt_to_equity:.2f}%（超過 150%），財務結構較脆弱。需注意利息支出對利潤的蠶食。")
    else:
        eval_comments.append("⚪ **財務防禦力評估**：未取得負債比數據，建議查詢該公司的最新資產負債表以策安全。")

    # 輸出體質總評
    if health_score >= 8:
        card_class = "eval-container"
        rating_title = "🏆 財務體質健全 (優等)"
        verdict = "該公司目前各項核心財務指標皆在優良水準，具備高競爭力與健康的財務結構，屬於體質相對穩固的標的。"
    elif 5 <= health_score < 8:
        card_class = "eval-container-warning"
        rating_title = "⚖️ 財務體質尚可 (中等)"
        verdict = "該公司多數指標符合標準，但部分指標（如估值偏高或負債偏重）稍有隱憂。投資時需搭配最新季度營收動能進行決策。"
    else:
        card_class = "eval-container-warning"
        rating_title = "⚠️ 財務體質待觀察 (注意風險)"
        verdict = "公司面臨虧損、高估值或債務過重的雙重狀況，基本面護城河較為薄弱，建議謹慎評估或等待體質改善。"

st.markdown(f"""
<div class="{card_class}">
    <div class="eval-header">
        <span>{rating_title}</span>
        <span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 20px; font-size: 0.9rem;">
            健康度評分：{health_score:.1f} / 10
        </span>
    </div>
    <div style="font-size: 1.1rem; line-height: 1.6;">
        <strong>綜合診斷結論：</strong>{verdict}
    </div>
</div>
""", unsafe_allow_html=True)

# 顯示條列白話文說明
st.write("")
for comment in eval_comments:
    st.markdown(comment)

# 頁腳聲明
st.markdown("---")
st.caption("⚠️ 免責聲明：本網站所提供之財務數據與評估結果僅供學術與技術研究參考，不構成任何投資建議。投資人進行投資決策前應自行評估風險。")
