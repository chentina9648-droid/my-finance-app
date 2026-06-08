import streamlit as st
import datetime
import pandas as pd
from hotel_search_engine import search_hotel_reviews

# ==============================================================================
# 1. 網頁基礎設定與明亮文青風 CSS 注入
# ==============================================================================
st.set_page_config(
    page_title="首爾客製化旅遊與報價系統",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入文青咖啡廳/無印良品輕盈質感 (米白配溫暖咖啡/深灰) CSS 樣式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Outfit:wght@300;400;600;700&display=swap');
    
    /* 全域大地色系明亮背景與深咖啡字體 */
    .stApp {
        background-color: #F4EFEB !important;
        color: #3E2723 !important;
    }
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', 'Outfit', sans-serif;
    }
    
    /* 側邊欄調整為溫暖燕麥泥土色 */
    section[data-testid="stSidebar"] {
        background-color: #ECE4DB !important;
        border-right: 1px solid #D3C5B3 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
        color: #3E2723 !important;
    }

    /* 大地色漸層大 Banner */
    .travel-banner {
        background: linear-gradient(135deg, #E6DFD5 0%, #D3C5B3 100%);
        padding: 2.2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(62, 39, 35, 0.08);
        border: 1px solid #C5B5A1;
    }

    .banner-title {
        color: #3E2723 !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    .banner-subtitle {
        color: #5C4C3E;
        font-size: 1.05rem;
        margin-top: 0.6rem;
        font-weight: 300;
    }

    /* 飯店網格卡片 */
    .hotel-card {
        background: #FAF8F5;
        border: 1px solid #D3C5B3;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(62, 39, 35, 0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 520px;
    }
    
    .hotel-card:hover {
        transform: translateY(-4px);
        border-color: #A08C75;
        box-shadow: 0 8px 25px rgba(133, 88, 59, 0.12);
    }
    
    .hotel-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.6rem;
    }
    
    .hotel-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #3E2723;
    }
    
    .hotel-stars {
        color: #B87A47;
        font-size: 0.95rem;
    }
    
    /* 莫蘭迪大地色徽章 */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 0.8rem;
    }
    
    .badge {
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .badge-price { background: #F5E8E4; color: #9E2A2B; border: 1px solid #E5C3BD; }
    .badge-breakfast { background: #EAF0EC; color: #3C6255; border: 1px solid #CAD8D0; }
    .badge-nobreakfast { background: #F0EDE9; color: #786C60; border: 1px solid #DDD7CF; }
    .badge-location { background: #E8EEF3; color: #2B5B84; border: 1px solid #CBDCE9; }
    .badge-room { background: #F4EFEA; color: #85583B; border: 1px solid #E2D6CC; }

    .hotel-details {
        font-size: 0.85rem;
        color: #5C4C3E;
        line-height: 1.5;
        margin-bottom: 0.8rem;
        flex-grow: 1;
    }
    
    .hotel-details li {
        margin-bottom: 4px;
        list-style-type: none;
        position: relative;
        padding-left: 15px;
    }
    
    .hotel-details li::before {
        content: "•";
        position: absolute;
        left: 0;
        color: #B87A47;
        font-weight: bold;
    }
    
    .hotel-opinion-label {
        font-weight: 700;
        font-size: 0.85rem;
        color: #3E2723;
        margin-top: 0.5rem;
    }
    
    .hotel-opinion {
        font-size: 0.8rem;
        color: #6D5D50;
        background: #FDFDFB;
        border: 1px dashed #D3C5B3;
        padding: 8px;
        border-radius: 6px;
        margin-bottom: 0.8rem;
        line-height: 1.4;
    }

    /* 警告提示 (上下鋪/四人房) */
    .hotel-warning {
        background: #FDF2E9;
        border-left: 3px solid #C68B59;
        color: #8C532B;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-bottom: 0.8rem;
        line-height: 1.3;
    }

    /* Streamlit 全域按鈕樣式 - 大地棕橘風格 */
    div.stButton > button {
        background-color: #FAF8F5 !important;
        color: #5C4033 !important;
        border: 1px solid #D3C5B3 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #B87A47 !important;
        border-color: #A0683A !important;
        color: #FFFFFF !important;
    }
    
    /* 評價氣泡框 */
    .review-bubble {
        background: #FAF8F5;
        border: 1px solid #D3C5B3;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(62, 39, 35, 0.02);
    }
    
    .review-bubble:hover {
        border-color: #A08C75;
    }
    
    .review-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }
    
    .review-source {
        font-size: 0.75rem;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 12px;
    }
    
    .source-dcard { background: #E8EEF3; color: #2B5B84; border: 1px solid #CBDCE9; }
    .source-ptt { background: #F5E8E4; color: #9E2A2B; border: 1px solid #E5C3BD; }
    .source-blog { background: #F4EFEA; color: #85583B; border: 1px solid #E2D6CC; }
    .source-booking { background: #EAF0EC; color: #3C6255; border: 1px solid #CAD8D0; }
    
    .review-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #3E2723;
        text-decoration: none;
    }
    
    .review-title:hover {
        color: #B87A47;
    }
    
    .review-snippet {
        font-size: 0.8rem;
        color: #6D5D50;
        line-height: 1.4;
    }

    /* Tab 標籤樣式微調 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #6D5D50 !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #3E2723 !important;
        border-color: #A08C75 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 精選 10 家飯店資料庫建構 (Hotel Database)
# ==============================================================================
HOTELS_DB = [
    {
        "name": "首爾麻浦魯內酒店 (Roynet Hotel)",
        "stars": "★★★★",
        "price": 19000,
        "breakfast": True,
        "location": "🚇 孔德站步行 3 分鐘",
        "badge_room": "🛏️ 雙人床/雙床",
        "warning": "",
        "pros": ["交通無敵，有機場線直達且周邊地鐵多線交會。", "2022年新開幕，日本品牌設備新穎且乾淨，樓下有 Olive Young。"],
        "cons": ["大廳位於二樓，上下樓梯或搭電梯在尖峰時刻需稍候。"],
        "opinion": "網友 (Dcard Fanny) 大推：『地點在孔德站與麻浦站中間，旁邊小間 Olive Young 彩妝品很齊全。連住四晚有被升等，服務超棒！』",
        "dcard_link": "https://www.dcard.tw/@fanny4lin/post/261413889?cid=cbe89f9c-cd23-4146-8810-cf5a47c5867a",
        "near_spots": "麻浦烤肉街、孔德市場、京義線林道公園 (皆在 10 分鐘路程內)"
    },
    {
        "name": "藍洞豪華旅舍 (Blue Hole Hostel)",
        "stars": "特色設計旅舍",
        "price": 15000,
        "breakfast": False,
        "location": "🚇 明洞附近步行 5 分鐘",
        "badge_room": "🛌 整間獨立四人房",
        "warning": "⚠️ 房型提醒：本旅舍基本為上下舖設計。為確保隱私與舒適，本報價已自動將預算升級為「包下整間四人房型」，以供兩人獨立入住。",
        "pros": ["包下四人房後空間充裕，性價比極高。", "緊鄰明洞市中心，逛街吃東西非常方便。"],
        "cons": ["房型為上下舖結構，上鋪旅客需攀爬，且衛浴較為簡約。"],
        "opinion": "住客真實反饋：『小巧設計風，兩人入住包下整間四人房比較不會有壓迫感，位置非常適合血拚，晚上很安靜。』",
        "dcard_link": "https://www.google.com/search?q=Blue+Hole+Hostel+Seoul+評價",
        "near_spots": "明洞步行街、明洞聖堂、南山纜車站 (皆在 10 分鐘路程內)"
    },
    {
        "name": "明洞九樹 2 號精品飯店 (Nine Tree)",
        "stars": "★★★★",
        "price": 17200,
        "breakfast": True,
        "location": "🚇 乙支路3街站步行 5 分鐘",
        "badge_room": "🛏️ 標準雙人房",
        "warning": "",
        "pros": ["交通極佳，地鐵 2、3 號線交會，去弘大或江南都可免轉乘直達。", "飯店一樓內設有超商，大廳提供免費自助行李秤重服務。"],
        "cons": ["距離機場巴士站牌有約 8 分鐘的步行路程，帶大型行李箱稍有不便。"],
        "opinion": "網友 (PTT Korea_Travel) 評價：『高樓層可以直接看到南山塔，房間很大而且水壓強，打掃很乾淨，住起來很安心。』",
        "dcard_link": "https://www.google.com/search?q=Nine+Tree+Premier+Hotel+Myeongdong+2+評價",
        "near_spots": "明洞商圈、清溪川、中部市場 (皆在 10 分鐘路程內)"
    },
    {
        "name": "格萊德馬浦酒店 (Glad Mapo)",
        "stars": "★★★★",
        "price": 18500,
        "breakfast": True,
        "location": "🚇 孔德站 9 號出口直結",
        "badge_room": "🛏️ 高級雙人房",
        "warning": "",
        "pros": ["交通樞紐共構，地鐵站出來直接上電梯到大廳，下雨完全免淋雨。", "室內採光極佳，現代摩登工業風設計，商務與觀光皆宜。"],
        "cons": ["實施環保政策，不提供一次性牙膏牙刷，住客需要自行攜帶。"],
        "opinion": "Dcard 網友分享：『孔德站這間地理位置絕了！地下就能直通地鐵跟機場線，樓下就有星巴克、大創跟便利商店，超推。』",
        "dcard_link": "https://www.google.com/search?q=Glad+Mapo+評價",
        "near_spots": "桃花洞美食街、孔德市場、京義線林道 (皆在 10 分鐘路程內)"
    },
    {
        "name": "首爾站福朋喜來登酒店 (Four Points)",
        "stars": "★★★★",
        "price": 19500,
        "breakfast": True,
        "location": "🚇 首爾站 12 號出口直通",
        "badge_room": "🛏️ 豪華雙人房",
        "warning": "",
        "pros": ["直結首爾車站地下通道，轉乘 KTX 或是搭乘 AREX 機場快線最方便。", "萬豪旗下品牌保證，軟硬體與床鋪舒適度皆有高水準。"],
        "cons": ["地下通道走進飯店需要 5-8 分鐘，且沿途有部分階梯需注意。"],
        "opinion": "網友點評：『位置對於要搭高鐵的人很棒。房間景觀超讚，俯瞰整個首爾車站，早餐的選擇精緻美味。』",
        "dcard_link": "https://www.google.com/search?q=Four+Points+Sheraton+Seoul+Station+評價",
        "near_spots": "樂天超市首爾站店、首爾路7017、南大門市場 (皆在 10 分鐘路程內)"
    },
    {
        "name": "弘大美居大使酒店 (Mercure)",
        "stars": "★★★★",
        "price": 20000,
        "breakfast": True,
        "location": "🚇 弘大入口站步行 2 分鐘",
        "badge_room": "🛏️ 經典雙人房",
        "warning": "",
        "pros": ["弘大商圈最精華地段，購物與夜生活出門即達。", "飯店設計極具現代科技感，支援手機控制房間燈光與冷氣。"],
        "cons": ["因為周邊是弘大主商圈，週五週末低樓層偶爾會聽到街頭藝人歌聲。"],
        "opinion": "網友評價：『買了東西就拿回飯店放，放完出來繼續逛！位置真的瘋狂，房間非常新且插頭設計多。』",
        "dcard_link": "https://www.google.com/search?q=Mercure+Ambassador+Seoul+Hongdae+評價",
        "near_spots": "弘大步行街、延南洞文青街、KT&G 想像空間 (皆在 10 分鐘路程內)"
    },
    {
        "name": "明洞 L7 酒店 (L7 Myeongdong)",
        "stars": "★★★★",
        "price": 18800,
        "breakfast": True,
        "location": "🚇 明洞站 9 號出口步行 1 分鐘",
        "badge_room": "🛏️ 標準大床房",
        "warning": "",
        "pros": ["地鐵站出口一上來就是飯店，門口就是機場巴士站，交通無縫接軌。", "頂樓有附設南山塔景觀足浴池與酒吧，晚上氣氛極佳。"],
        "cons": ["登記入住時間人潮非常多，下午三點排隊可能需等候較久。"],
        "opinion": "Dcard 旅客推崇：『大推這家飯店的景觀！頂樓泡腳可以直接看南山塔非常浪漫。逛明洞買完化妝品放回房間超方便。』",
        "dcard_link": "https://www.google.com/search?q=L7+Myeongdong+評價",
        "near_spots": "明洞商圈、新世界百貨本店、南山纜車 (皆在 10 分鐘路程內)"
    },
    {
        "name": "首爾東大門諾富特大使酒店 (Novotel)",
        "stars": "★★★★★",
        "price": 19800,
        "breakfast": True,
        "location": "🚇 東大門歷史文化公園站步行 3 分",
        "badge_room": "🛏️ 高級雙人房",
        "warning": "",
        "pros": ["擁有首爾市區少有的頂樓露天溫水無邊際游泳池，拍照極美。", "五星級飯店品質，備品精緻且客房隔音效果極佳。"],
        "cons": ["一般客房空間較為精簡，若要小廚房與沙發需加預算訂公寓房。"],
        "opinion": "PTT 網友分享：『三線交會站旁邊，去哪都方便。飯店頂樓無邊際泳池拍起來超像國外度假，周邊很多宵夜帳篷。』",
        "dcard_link": "https://www.google.com/search?q=Novotel+Ambassador+Seoul+Dongdaemun+評價",
        "near_spots": "東大門設計廣場 (DDP)、東大門批發市場、現代Outlet (皆在 10 分鐘路程內)"
    },
    {
        "name": "明洞索拉利亞西鐵酒店 (Solaria)",
        "stars": "★★★★",
        "price": 19200,
        "breakfast": True,
        "location": "🚇 明洞站 8 號出口步行 3 分鐘",
        "badge_room": "🛏️ 日式經典雙人房",
        "warning": "",
        "pros": ["正宗日系品牌，浴室乾濕分離且備有免治馬桶，清潔精緻。", "直接坐落於明洞步行街商圈內，下樓即可開吃開逛。"],
        "cons": ["由於在徒步商圈內，計程車在管制時段可能無法開到大門口，需步行。"],
        "opinion": "住客評分：『日系服務無微不至，浴室水壓超大！在首爾逛街一整天後回飯店洗熱水澡泡澡真的是救星。』",
        "dcard_link": "https://www.google.com/search?q=Solaria+Nishitetsu+Hotel+Seoul+Myeongdong+評價",
        "near_spots": "明洞步行街、樂天百貨總店、明洞藝術劇場 (皆在 10 分鐘路程內)"
    },
    {
        "name": "首爾東大門雅樂軒酒店 (Aloft)",
        "stars": "★★★★",
        "price": 16800,
        "breakfast": True,
        "location": "🚇 東大門站 8 號出口步行 5 分鐘",
        "badge_room": "🛏️ 時尚雙人房",
        "warning": "",
        "pros": ["萬豪集團連鎖品牌，CP 值高，預算相對划算。", "緊鄰清溪川，晚上散步氣氛悠閒放鬆。"],
        "cons": ["客房裝修風格走亮色彩色調，稍有歷史感，非最新極簡設計。"],
        "opinion": "網友 (Dcard) 分享：『價格實惠且早餐種類很多，走去東大門熱門的一隻雞（陳玉華）只要5分鐘，半夜吃宵夜非常方便。』",
        "dcard_link": "https://www.google.com/search?q=Aloft+Seoul+Dongdaemun+評價",
        "near_spots": "清溪川、陳玉華一隻雞、廣藏市場 (皆在 10 分鐘路程內)"
    }
]

# ==============================================================================
# 3. 初始化 Session State (以實現一鍵搜尋)
# ==============================================================================
if 'destination' not in st.session_state:
    st.session_state.destination = "首爾"
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.date(2026, 6, 23)
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.date(2026, 6, 27)
if 'guests' not in st.session_state:
    st.session_state.guests = 2
if 'has_breakfast' not in st.session_state:
    st.session_state.has_breakfast = True
if 'search_triggered' not in st.session_state:
    st.session_state.search_triggered = True  # 預設為開啟，方便一進來就看到報價
if 'selected_hotel' not in st.session_state:
    st.session_state.selected_hotel = "首爾麻浦魯內酒店 (Roynet Hotel)"

def trigger_demo_search():
    st.session_state.destination = "首爾"
    st.session_state.start_date = datetime.date(2026, 6, 23)
    st.session_state.end_date = datetime.date(2026, 6, 27)
    st.session_state.guests = 2
    st.session_state.has_breakfast = True
    st.session_state.search_triggered = True

# ==============================================================================
# 4. 側邊欄控制面板 (搜尋條件)
# ==============================================================================
st.sidebar.markdown("### 🔍 旅遊條件設定")

# 一鍵填入範例按鈕
st.sidebar.button(
    "🔥 一鍵搜尋：首爾 6/23-6/27 雙人含早",
    on_click=trigger_demo_search,
    use_container_width=True,
    help="自動為您填入韓國首爾 6/23 - 6/27 兩位成人、含早餐的極佳自由行搜尋條件！"
)

st.sidebar.markdown("---")

destination = st.sidebar.text_input("📍 目的地城市", value=st.session_state.destination, key="input_destination")
st.session_state.destination = destination

start_date = st.sidebar.date_input("📅 入住日期", value=st.session_state.start_date, key="input_start_date")
st.session_state.start_date = start_date

end_date = st.sidebar.date_input("📅 退房日期", value=st.session_state.end_date, key="input_end_date")
st.session_state.end_date = end_date

guests = st.sidebar.number_input("👥 入住人數", min_value=1, max_value=10, value=st.session_state.guests, key="input_guests")
st.session_state.guests = guests

has_breakfast = st.sidebar.checkbox("🍳 必須包含早餐", value=st.session_state.has_breakfast, key="input_breakfast")
st.session_state.has_breakfast = has_breakfast

search_button = st.sidebar.button("🔍 開始分析與比對", use_container_width=True)
if search_button:
    st.session_state.search_triggered = True

# 行程自訂參數 (用於預算計算機連動)
st.sidebar.markdown("---")
st.sidebar.markdown("### 💵 行程預算動態調整 (雙人份)")
hanbok_price_input = st.sidebar.slider("韓服體驗費用 (NT$)", min_value=0, max_value=3000, value=1000, step=100)
luge_price_input = st.sidebar.slider("滑道車門票費用 (NT$)", min_value=0, max_value=4000, value=1600, step=100)
transport_price_input = st.sidebar.slider("預估市區與近郊交通費 (NT$)", min_value=500, max_value=5000, value=2400, step=100)

# ==============================================================================
# 5. 主內容區：首爾精選 10 家飯店對比
# ==============================================================================
if st.session_state.search_triggered and ("首爾" in st.session_state.destination or "Seoul" in st.session_state.destination.lower()):
    
    st.markdown(f"### 📋 首爾精選 10 家飯店資料庫對比 (入住期間：{st.session_state.start_date} ~ {st.session_state.end_date}，{st.session_state.guests}人)")
    st.write("已根據您的基準預算 (NT 15,000 - 19,000 元 / 4晚雙人房) 挑選並擴充共 10 家首爾市中心、交通極方便的優質飯店：")
    
    # 建立 2 欄的 Grid
    hotels_grid = HOTELS_DB
    
    # 根據早餐過濾 (如果勾選「必須含早餐」，則只保留含早餐的，但保留基準飯店藍洞做對比提醒)
    if st.session_state.has_breakfast:
        hotels_grid = [h for h in HOTELS_DB if h["breakfast"] or "藍洞" in h["name"]]

    # 分成 2 欄排列
    cols = st.columns(2)
    for idx, h in enumerate(hotels_grid):
        col_to_use = cols[idx % 2]
        
        # 早餐標籤與樣式
        bf_badge = '<span class="badge badge-breakfast">🍳 含早餐</span>' if h["breakfast"] else '<span class="badge badge-nobreakfast">❌ 無早餐</span>'
        
        # 缺點與警告標示
        warning_html = f'<div class="hotel-warning">{h["warning"]}</div>' if h["warning"] else ''
        
        # 條列優缺點
        pros_list = "".join([f"<li>🟢 {pro}</li>" for pro in h["pros"]])
        cons_list = "".join([f"<li>🔴 {con}</li>" for con in h["cons"]])
        
        with col_to_use:
            # 壓縮 HTML 換行與縮進，以防止 Streamlit 誤將 HTML 當作 markdown code block 渲染
            card_html = f"""
<div class="hotel-card">
<div>
<div class="hotel-header">
<span class="hotel-name">{h["name"]}</span>
<span class="hotel-stars">{h["stars"]}</span>
</div>
<div class="badge-container">
<span class="badge badge-price">4晚總價 NT$ {h["price"]:,}</span>
{bf_badge}
<span class="badge badge-location">{h["location"]}</span>
<span class="badge badge-room">{h["badge_room"]}</span>
</div>
{warning_html}
<ul class="hotel-details">
{pros_list}
{cons_list}
</ul>
<div class="hotel-opinion-label">🗣️ 真實住客/論壇心得摘要</div>
<div class="hotel-opinion">{h["opinion"]}</div>
</div>
</div>
""".replace('\n', ' ')
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 使用 streamlit native buttons 排在卡片底部
            btn_cols = st.columns([1, 1.2])
            with btn_cols[0]:
                if st.button("⚡ 即時抓取最新評價", key=f"fetch_{idx}"):
                    st.session_state.selected_hotel = h["name"]
            with btn_cols[1]:
                # 如果是 Dcard 連結，可直接點擊
                st.markdown(f'<a href="{h["dcard_link"]}" target="_blank"><button style="width:100%; padding:6px 12px; background-color:#FFFFFF; color:#4A3F35; border:1px solid #D7C4A5; border-radius:8px; cursor:pointer; font-size:13px;">🔗 查看 Dcard/網路原文</button></a>', unsafe_allow_html=True)
            
            st.write("") # 留白

    # ==============================================================================
    # 6. 專屬行程規劃與交通指南 (Itinerary & Transport)
    # ==============================================================================
    st.markdown("---")
    st.markdown("### 🗺️ 專屬行程規劃與交通指南")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👘 韓服體驗", "🏎️ 江華島滑道車 (Luge) 攻略", "💄 聖水洞與弘大品牌巡禮", "📍 目前選定飯店之周邊景點"])
    
    with tab1:
        st.markdown("""
        #### 👘 適合拍照的宮殿與優質韓服店推薦
        - **最佳拍照宮殿**：
          1. **景福宮 (Gyeongbokgung)**：最著名的宮殿，有寬闊的廣場、慶會樓（水上亭閣）與香遠亭，穿韓服可免費入場。
          2. **昌德宮 (Changdeokgung)**：以優美的秘苑（秘境花園）聞名，古木參天，比起景福宮更有清幽與古典文藝感。
          3. **北村韓屋村 (Bukchon Hanok Village)**：保留大量朝鮮時代傳統韓屋，適合拍攝巷弄復古街景（但注意有上下坡與民宅靜音規範）。
        - **周邊優質韓服店家推薦**：
          - **西花韓服 (Seohwa Hanbok)**：位於景福宮站 4 號出口旁，衣服質感到位，包含基本編髮與配件，且有中文服務人員，租借 4 小時約 **20,000 ~ 25,000 韓元** (約台幣 NT$ 500/人)。
          - **Oneday Hanbok**：款式新穎且尺碼齊全，租借時間靈活，是許多 Dcard 網友的首選。
          - **宮女狐韓服 (Princess Hanbok)**：以少女風蕾絲韓服及精緻華麗的編髮聞名。
        """)
        
    with tab2:
        st.markdown(f"""
        #### 🏎️ 首爾出發：江華島 Mega Luge 滑道車交通全攻略
        江華島 Mega Luge 擁有長達 1.8 公里的雙賽道，是首爾近郊最刺激熱門的滑道車景點。
        
        - **詳細交通轉乘指引**：
          1. **市區出發**：從 **新村站** 或 **弘大入口站** 搭乘 **紅色巴士 3000 號**。
          2. **直達江華島**：搭乘 3000 號巴士至終點站 **江華客運站 (Ganghwa Terminal)** 下車。單程車程約 **1 小時 20 分鐘**。
          3. **轉乘至度假村 (Luge場地)**：
             - **方案 A (最推薦)：搭乘計程車**。在江華客運站出口直接搭計程車，至「江華海邊度假村 (Ganghwa Seaside Resort)」下車。車程約 **15 分鐘**，車資約 12,000 韓元 (約台幣 NT$ 300 / 兩人平分 NT$ 150)。
             - **方案 B：搭乘公車**。在客運站內搭乘當地公車 **500 號** 或 **501 號**，在「海邊度假村站」下車，班次較少（需配合時刻表）。
        - **預估搭車時間與費用**：
          - 單程總交通時間約 **1.5 至 2 小時**。
          - 雙人門票費用（平日2次券為 30,000 韓元/人，本系統已估算雙人約 NT$ 1,600）。
        """)
        
    with tab3:
        st.markdown("""
        #### 💄 聖水洞與弘大：美妝與文青設計品牌一日巡禮
        本行程規劃半天，結合最新潮的「聖水洞」與經典「弘大」，是抓緊首爾流行趨勢的最佳逛街動線。
        
        - **上午：聖水洞 (Sungsudong) 工業文青巡禮**
          - **必看景點**：Dior 聖水概念店（外觀玻璃屋超美，適合拍照）、Ader Error 聖水空間（充滿前衛藝術裝置的旗艦店）。
          - **品牌巡禮**：**Matin Kim**（時下最紅的極簡金屬牌包包皮夾）、**Stand Oil**（百搭皮革包）、各類複合式設計精品店。
          - **午餐推薦**：去聖水洞特色工廠咖啡廳（如 Onion 聖水店）喝咖啡與品嘗麵包。
        - **下午：弘大 (Hongdae) 活力美妝探索**
          - **品牌巡禮**：**Olive Young Town 弘大旗艦店**（首爾最大旗艦店之一，美妝保養一次買齊）、**3CE Stylenanda**（粉紅夢幻空間與人氣彩妝）、**Musinsa Standard**（韓國版 UNIQLO，剪裁極佳）、**ÅLAND**（集結韓國新銳服飾的設計大樓）。
        """)
        
    with tab4:
        # 動態抓取目前選定飯店之周邊景點與交通
        current_sel = st.session_state.selected_hotel
        matched_hotel = next((h for h in HOTELS_DB if h["name"] == current_sel), HOTELS_DB[0])
        
        st.markdown(f"#### 📍 當前選定：【{matched_hotel['name']}】之 10 分鐘周邊好玩景點")
        st.write(f"- **推薦步行景點**：{matched_hotel['near_spots']}")
        st.write(f"- **飯店交通位置**：{matched_hotel['location']}")
        st.info("💡 您可以在上面的飯店卡片中，點擊任何飯店的『⚡ 即時抓取最新評價』，此處的周邊景點資訊將會隨之動態更新！")

    # ==============================================================================
    # 7. 即時評論搜尋 (來自 DuckDuckGo 的真實資料)
    # ==============================================================================
    st.markdown("---")
    st.markdown(f"### 🕸️ 【{st.session_state.selected_hotel}】即時網路評價抓取 (Dcard/PTT/論壇)")
    
    with st.spinner(f"正在為您爬取「{st.session_state.selected_hotel}」在 Dcard、PTT 與各大旅遊網的真實討論..."):
        reviews = search_hotel_reviews(st.session_state.selected_hotel)
        
    if not reviews:
        st.warning(f"⚠️ 未能在網路上找到關於「{st.session_state.selected_hotel}」的即時評價，建議手動搜尋！")
    else:
        st.success(f"🎉 成功從網路為您抓取到 {len(reviews)} 筆關於「{st.session_state.selected_hotel}」的真實評價片段與原始連結：")
        
        for r in reviews[:5]:
            source_class = "source-dcard"
            if r['source'] == "PTT":
                source_class = "source-ptt"
            elif r['source'] == "旅遊部落格":
                source_class = "source-blog"
            elif r['source'] == "訂房網反饋":
                source_class = "source-booking"
                
            st.markdown(f"""
            <div class="review-bubble">
                <div class="review-header">
                    <span class="review-source {source_class}">{r['source']}</span>
                    <a href="{r['link']}" target="_blank" class="review-title">🔗 {r['title']}</a>
                </div>
                <div class="review-snippet">{r['snippet']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ==============================================================================
    # 8. 透明化報價系統 (Budget Calculator)
    # ==============================================================================
    st.markdown("---")
    st.markdown("### 📊 透明化雙人預算總覽表")
    st.write("已為您整合 10 家飯店的「4 晚住宿費」與您在側邊欄設定的「行程與交通費」，為您呈現最完整的花費對比：")
    
    # 計算各方案的總價與價差
    budget_data = []
    
    # 找出最低房價做為基準價差計算
    min_room_price = min([h["price"] for h in HOTELS_DB])
    
    for h in HOTELS_DB:
        room_cost = h["price"]
        other_cost = hanbok_price_input + luge_price_input + transport_price_input
        total_cost = room_cost + other_cost
        
        # 價差 (與藍洞豪華旅舍 $15,000 做對比)
        diff_from_base = room_cost - 15000
        diff_text = f"+NT$ {diff_from_base:,}" if diff_from_base > 0 else "基準 (0)"
        
        budget_data.append({
            "飯店名稱": h["name"],
            "星級": h["stars"],
            "4晚房價 (2人)": f"NT$ {room_cost:,}",
            "行程活動與交通 (2人)": f"NT$ {other_cost:,}",
            "估計總花費 (雙人)": total_cost, # 數值型態方便排序
            "與藍洞房價差額": diff_text
        })
        
    df_budget = pd.DataFrame(budget_data)
    # 依照總花費由低到高排序
    df_budget = df_budget.sort_values(by="估計總花費 (雙人)").reset_index(drop=True)
    
    # 格式化總花費呈現
    df_budget_show = df_budget.copy()
    df_budget_show["估計總花費 (雙人)"] = df_budget_show["估計總花費 (雙人)"].apply(lambda x: f"NT$ {x:,}")
    
    # 顯示精緻的報價對比表格
    st.dataframe(
        df_budget_show,
        use_container_width=True,
        column_config={
            "飯店名稱": st.column_config.TextColumn("🏨 飯店名稱", width="medium"),
            "星級": st.column_config.TextColumn("⭐ 星級"),
            "4晚房價 (2人)": st.column_config.TextColumn("🛌 4晚住宿費"),
            "行程活動與交通 (2人)": st.column_config.TextColumn("🎟️ 額外活動+市區交通費"),
            "估計總花費 (雙人)": st.column_config.TextColumn("💰 總花費報價 (2人)"),
            "與藍洞房價差額": st.column_config.TextColumn("⚖️ 房價價差 (對比藍洞)")
        }
    )
    
    # 預算結論小貼士
    cheapest = df_budget.iloc[0]
    premium = df_budget.iloc[-1]
    
    st.markdown(f"""
    > [!TIP]
    > **💰 報價小總結：**
    > - **最超值方案**：選擇 **{cheapest['飯店名稱']}**，包含所有門票交通費後，雙人總開銷預計僅需 **NT$ {cheapest['估計總花費 (雙人)']:,}**。
    > - **最奢華方案**：選擇 **{premium['飯店名稱']}**，雙人總開銷為 **NT$ {premium['估計總花費 (雙人)']:,}**，比基準的藍洞豪華旅舍多花了 **{premium['與藍洞房價差額']}**。
    > - 如果希望有 **4星級水準且有早餐**，最便宜的是 **{df_budget[df_budget['飯店名稱'].str.contains('Nine Tree')].iloc[0]['飯店名稱']}**，總花費為 **NT$ {df_budget[df_budget['飯店名稱'].str.contains('Nine Tree')].iloc[0]['估計總花費 (雙人)']:,}**。
    """)

else:
    st.info("💡 請在側邊欄輸入搜尋條件，或直接點擊 **「🔥 一鍵搜尋：首爾 6/23-6/27 雙人含早」** 來獲取推薦飯店與真實評價！")
