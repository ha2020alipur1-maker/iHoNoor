import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, r2_score
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
import os
import jdatetime
import uuid
import requests
import json
import io
warnings.filterwarnings('ignore')

# ==========================================
# 1. تنظیمات اولیه
# ==========================================
st.set_page_config(
    page_title="iHoNoor | نور هوشمند کسب‌وکار",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. دریافت قیمت‌های واقعی از API
# ==========================================
@st.cache_data(ttl=300)  # هر ۵ دقیقه آپدیت میشه
def get_real_prices():
    """دریافت قیمت‌های واقعی از API"""
    prices = {
        'dollar': 195000,
        'gold': 0,
        'oil': 85,
        'steel': 1200,
        'inflation': 35,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'source': 'آفلاین'
    }
    
    # ۱. دریافت قیمت دلار
    try:
        url1 = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url1, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data['rates']['IRR'] / 10
            if price > 1000:
                prices['dollar'] = int(price)
                prices['source'] = 'آنلاین'
    except:
        pass
    
    # ۲. دریافت قیمت طلا
    try:
        url2 = "https://api.gold-api.com/price/XAU"
        response = requests.get(url2, timeout=5)
        if response.status_code == 200:
            data = response.json()
            gold_usd = data.get('price', 0)
            if gold_usd > 0:
                prices['gold'] = int(gold_usd * prices['dollar'] / 31.1)
    except:
        # تخمین طلا از روی دلار
        prices['gold'] = int(prices['dollar'] * 180)
    
    # ۳. قیمت نفت (از API)
    try:
        url3 = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url3, timeout=5)
        if response.status_code == 200:
            # تخمین قیمت نفت بر اساس دلار
            prices['oil'] = int(75 + (prices['dollar'] - 195000) / 2000)
    except:
        prices['oil'] = 85
    
    # ۴. قیمت فولاد
    try:
        # تخمین قیمت فولاد بر اساس دلار
        prices['steel'] = int(1100 + (prices['dollar'] - 195000) / 100)
    except:
        prices['steel'] = 1200
    
    # ۵. نرخ تورم
    try:
        prices['inflation'] = 30 + (prices['dollar'] - 195000) / 5000
    except:
        prices['inflation'] = 35
    
    return prices

# دریافت قیمت‌ها
prices = get_real_prices()

# ==========================================
# 3. تنظیمات ادمین
# ==========================================
ADMIN_USERNAME = "ihonoor_admin"
ADMIN_PASSWORD = "iHoNoor@1404"

# ==========================================
# 4. چندزبانه
# ==========================================
LANG = {
    'fa': {
        'app_name': 'نور هوشمند کسب‌وکار',
        'subtitle': 'با یاری الهی، مسیر موفقیت را روشن کن',
        'step1': 'انتخاب صنف',
        'step2': 'آپلود فایل',
        'step3': 'پیش‌بینی',
        'target': 'ستون هدف (چی رو پیش‌بینی کنم؟)',
        'suggest': '💡 پیشنهاد iHoNoor',
        'unit': 'واحد تشخیص داده شده',
        'predict_btn': '🚀 پیش‌بینی کن',
        'accuracy': 'دقت مدل',
        'confidence': 'بازه اطمینان',
        'dollar_label': 'تحلیل دلاری',
        'anomaly_label': 'تشخیص ناهنجاری',
        'feature_importance': 'اهمیت ویژگی‌ها',
        'health': 'سلامت داده‌ها',
        'advisor': '✨ مشاور iHoNoor',
        'chatbot': '💬 چتبات هوشمند',
        'admin': '🔐 پنل مدیریت',
        'future': '🔮 تحلیلگر آینده'
    },
    'en': {
        'app_name': 'Smart Business Light',
        'subtitle': 'With Divine Help, Illuminate Your Success Path',
        'step1': 'Select Industry',
        'step2': 'Upload File',
        'step3': 'Predict',
        'target': 'Target Column (What to predict?)',
        'suggest': '💡 iHoNoor Suggestion',
        'unit': 'Detected Unit',
        'predict_btn': '🚀 Predict',
        'accuracy': 'Model Accuracy',
        'confidence': 'Confidence Interval',
        'dollar_label': 'Dollar Analysis',
        'anomaly_label': 'Anomaly Detection',
        'feature_importance': 'Feature Importance',
        'health': 'Data Health',
        'advisor': '✨ iHoNoor Advisor',
        'chatbot': '💬 Smart Chatbot',
        'admin': '🔐 Admin Panel',
        'future': '🔮 Future Analyst'
    }
}

# ==========================================
# 5. استایل حرفه‌ای
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', 'Vazirmatn', sans-serif;
        direction: rtl;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #F9FAFB;
    }
    
    .main-header {
        background: linear-gradient(105deg, #0A2540 0%, #1A3A5C 100%);
        padding: 28px 35px;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 28px;
        box-shadow: 0 15px 40px -10px rgba(10, 37, 64, 0.25);
        border: 1px solid rgba(255,255,255,0.06);
    }
    .main-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .main-header h1 .highlight {
        color: #F5A623;
        text-shadow: 0 0 30px rgba(245, 166, 35, 0.2);
    }
    .main-header p {
        font-size: 1rem;
        font-weight: 300;
        opacity: 0.8;
        margin-top: 6px;
        letter-spacing: 0.3px;
    }
    .main-header .badge-version {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(4px);
        padding: 4px 16px;
        border-radius: 40px;
        font-size: 0.7rem;
        display: inline-block;
        margin-top: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .main-header .dollar-badge {
        background: rgba(245, 166, 35, 0.15);
        backdrop-filter: blur(4px);
        padding: 4px 16px;
        border-radius: 40px;
        font-size: 0.75rem;
        display: inline-block;
        margin-top: 8px;
        margin-right: 8px;
        border: 1px solid rgba(245, 166, 35, 0.2);
        color: #F5A623;
    }
    .main-header .source-badge {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(4px);
        padding: 2px 12px;
        border-radius: 40px;
        font-size: 0.6rem;
        display: inline-block;
        margin-top: 8px;
        margin-right: 8px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #94A9C2;
    }

    .card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 22px 26px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
        margin-bottom: 18px;
        transition: all 0.25s ease;
    }
    .card:hover {
        box-shadow: 0 12px 40px rgba(10, 37, 64, 0.08);
        transform: translateY(-2px);
    }
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0A2540;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card-title .icon {
        font-size: 1.3rem;
    }

    .stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 12px 32px !important;
        border: none !important;
        transition: all 0.2s ease !important;
        background: #0A2540 !important;
        color: white !important;
        box-shadow: 0 6px 18px rgba(10, 37, 64, 0.12);
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 28px rgba(10, 37, 64, 0.25);
        background: #143D5E !important;
    }

    .result-box {
        background: linear-gradient(135deg, #EBF4FF, #D6E8FF);
        padding: 28px 30px;
        border-radius: 24px;
        border: 1px solid rgba(10, 37, 64, 0.06);
        text-align: center;
        margin-top: 16px;
        box-shadow: inset 0 1px 4px rgba(255,255,255,0.8);
    }
    .result-number {
        font-size: 3rem;
        font-weight: 800;
        color: #0A2540;
        letter-spacing: -1px;
    }
    .result-label {
        font-size: 0.95rem;
        font-weight: 400;
        color: #3D5A78;
        margin-top: 4px;
    }
    .result-emoji {
        font-size: 2.8rem;
        margin-bottom: 6px;
    }

    .advisor-box {
        background: linear-gradient(105deg, #0A2540, #1A3A5C);
        padding: 22px 28px;
        border-radius: 20px;
        color: white;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .advisor-box strong {
        color: #F5A623;
        font-weight: 700;
    }

    .future-box {
        background: linear-gradient(135deg, #1A3A5C, #0A2540);
        padding: 22px 28px;
        border-radius: 20px;
        color: white;
        margin-top: 20px;
        border: 1px solid rgba(245, 166, 35, 0.2);
        box-shadow: 0 0 30px rgba(245, 166, 35, 0.05);
    }
    .future-box .title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #F5A623;
        margin-bottom: 10px;
    }
    .future-box .status-badge {
        display: inline-block;
        padding: 4px 16px;
        border-radius: 40px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .future-box .status-badge.critical { background: #E53E3E; color: white; }
    .future-box .status-badge.warning { background: #F5A623; color: #0A2540; }
    .future-box .status-badge.stable { background: #38A169; color: white; }

    .steps {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .step-item {
        flex: 1;
        min-width: 130px;
        background: white;
        padding: 12px 16px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .step-item .num {
        background: #0A2540;
        color: white;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        margin-bottom: 4px;
    }
    .step-item .text { font-weight: 600; color: #0A2540; font-size: 0.85rem; }
    .step-item .desc { font-size: 0.65rem; color: #6B85A0; }

    .footer {
        text-align: center;
        color: #94A9C2;
        font-size: 0.75rem;
        margin-top: 50px;
        padding-top: 18px;
        border-top: 1px solid #E2E8F0;
    }

    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 40px;
        font-size: 0.7rem;
        font-weight: 700;
        margin: 3px;
    }
    .badge-gold { background: #F5A623; color: #0A2540; }
    .badge-silver { background: #C0C8D4; color: #0A2540; }
    .badge-bronze { background: #CD7F32; color: white; }
    .badge-blue { background: #0A2540; color: white; }

    .chat-message {
        padding: 12px 18px;
        border-radius: 14px;
        margin-bottom: 8px;
        max-width: 80%;
    }
    .chat-user {
        background: #0A2540;
        color: white;
        margin-right: auto;
    }
    .chat-bot {
        background: #E8F0F8;
        color: #0A2540;
        margin-left: auto;
    }

    .guide-step {
        background: white;
        padding: 20px 24px;
        border-radius: 16px;
        margin-bottom: 16px;
        border-right: 5px solid #0A2540;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }
    .guide-step:hover {
        box-shadow: 0 4px 16px rgba(10, 37, 64, 0.08);
        transform: translateX(-4px);
    }
    .guide-step h3 {
        color: #0A2540;
        margin: 0;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .guide-step p {
        color: #3D5A78;
        margin-top: 8px;
        margin-bottom: 0;
    }
    .guide-step .tip {
        background: #F0F7FF;
        padding: 10px 16px;
        border-radius: 10px;
        margin-top: 8px;
        font-size: 0.9rem;
    }
    .guide-step .warning {
        background: #FFF5F5;
        padding: 10px 16px;
        border-radius: 10px;
        margin-top: 8px;
        font-size: 0.9rem;
        border-right: 3px solid #E53E3E;
    }
    .guide-step .success {
        background: #F0FFF4;
        padding: 10px 16px;
        border-radius: 10px;
        margin-top: 8px;
        font-size: 0.9rem;
        border-right: 3px solid #38A169;
    }

    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.8rem; }
        .steps { flex-direction: column; }
        .step-item { min-width: 100%; }
        .result-number { font-size: 2.2rem; }
        .guide-step { padding: 16px; }
        .chat-message { max-width: 95%; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. انتخاب زبان
# ==========================================
if "lang" not in st.session_state:
    st.session_state.lang = "fa"

lang = st.sidebar.selectbox("🌐 زبان / Language", ["فارسی", "English"])
if lang == "English":
    st.session_state.lang = "en"
else:
    st.session_state.lang = "fa"

t = LANG[st.session_state.lang]

# ==========================================
# 7. صنف‌ها
# ==========================================
industries = [
    "🏪 خواربارفروشی", "🔩 آهن‌آلات و مصالح", "🚗 خودروسازی و لوازم یدکی",
    "👗 پوشاک", "🍞 نانوایی", "📱 فناوری و مخابرات", "🛒 خرده‌فروشی و آنلاین",
    "🏭 تولید و صنایع", "💰 بانکداری و مالی", "🏥 بهداشت و درمان",
    "🍔 صنایع غذایی", "⛽ پتروشیمی و انرژی", "⚡ برق و نیروگاه‌ها",
    "🎬 سینما و محصولات فرهنگی", "🏭 تولید و صنایع غذایی (تخصصی)",
    "🏢 املاک و مستغلات", "🏗️ ساختمان و پیمانکاری",
    "🏭 تولید سفارشی (Make-to-Order)", "📦 مدیریت موجودی و زنجیره تامین"
]

# ==========================================
# 8. توابع هسته
# ==========================================
def detect_unit(col):
    col = col.lower()
    if any(w in col for w in ['نفر', 'مشتری', 'تعداد', 'کاربر']): return 'نفر'
    if any(w in col for w in ['تومان', 'ریال', 'فروش', 'قیمت', 'درآمد']): return 'تومان'
    if 'درصد' in col: return 'درصد'
    if any(w in col for w in ['کیلو', 'گرم', 'تن']): return 'کیلوگرم'
    if any(w in col for w in ['متر', 'سانتی']): return 'متر'
    if any(w in col for w in ['لیتر', 'میل']): return 'لیتر'
    return 'واحد'

def suggest_target(df):
    nums = df.select_dtypes(include=['number']).columns.tolist()
    for k in ['فروش_فردا', 'فروش', 'تعداد_مشتریان', 'قیمت', 'درآمد']:
        for c in nums:
            if k in c: return c
    return nums[0] if nums else None

def get_emoji(val, unit):
    if unit == 'تومان':
        if val > 10_000_000: return "🚀", "فروش عالی!"
        if val > 6_000_000: return "📈", "فروش خوب"
        return "💪", "نیاز به تلاش"
    if unit == 'نفر':
        if val > 80: return "🎉", "مشتریان عالی!"
        if val > 40: return "👍", "مشتریان خوب"
        return "📢", "جذب مشتری بیشتر"
    return "📊", "پیش‌بینی انجام شد"

# ==========================================
# 9. تحلیلگر آینده
# ==========================================
def future_analyst(صنف, prices):
    analysis = {
        'status': 'پایدار',
        'trend': 'ثابت',
        'impact': 'متوسط',
        'price_change': 0,
        'message': '',
        'actions': [],
        'risk_level': 'متوسط',
        'opportunity': ''
    }
    
    dollar = prices['dollar']
    gold = prices['gold']
    oil = prices['oil']
    steel = prices['steel']
    inflation = prices['inflation']
    
    if "خواربار" in صنف or "غذایی" in صنف or "نانوایی" in صنف:
        if dollar > 200000:
            analysis['status'] = '⚠️ هشدار'
            analysis['trend'] = 'افزایش قیمت'
            analysis['price_change'] = 15 + (dollar - 195000) / 1000
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بالا'
            analysis['message'] = f'💰 با افزایش دلار به {dollar:,} تومان، قیمت مواد اولیه {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['actions'].append('🔹 موجودی کالاهای اساسی را افزایش دهید')
            analysis['actions'].append('🔹 قراردادهای بلندمدت با تامین‌کنندگان منعقد کنید')
            analysis['opportunity'] = '📈 فرصت: افزایش قیمت فروش با مدیریت هزینه‌ها'
        else:
            analysis['status'] = '✅ پایدار'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 3
            analysis['impact'] = 'متوسط'
            analysis['message'] = '📊 شرایط فعلی نسبتاً پایدار است.'
            analysis['actions'].append('🔹 حفظ کیفیت محصولات')
            analysis['opportunity'] = '📈 فرصت: جذب مشتری با کیفیت بالا'
    
    elif "ساختمان" in صنف or "پیمانکاری" in صنف or "مصالح" in صنف:
        if steel > 1300:
            analysis['status'] = '⚠️ هشدار شدید'
            analysis['trend'] = 'افزایش شدید قیمت'
            analysis['price_change'] = 20 + (steel - 1200) / 5
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بسیار بالا'
            analysis['message'] = f'🏗️ قیمت فولاد به {steel} دلار رسیده و هزینه‌های ساخت {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['actions'].append('🔹 خرید مصالح را به امروز موکول کنید')
            analysis['actions'].append('🔹 پروژه‌های جدید را با احتیاط شروع کنید')
            analysis['opportunity'] = '📉 فرصت: سرمایه‌گذاری در پروژه‌های کوچکتر'
        else:
            analysis['status'] = '⚠️ توجه'
            analysis['trend'] = 'افزایش ملایم'
            analysis['price_change'] = 8
            analysis['impact'] = 'بالا'
            analysis['message'] = '📊 افزایش تدریجی قیمت مصالح قابل پیش‌بینی است.'
            analysis['actions'].append('🔹 برنامه‌ریزی دقیق پروژه‌ها')
            analysis['opportunity'] = '📈 فرصت: شروع پروژه‌های جدید'
    
    elif "پوشاک" in صنف or "لباس" in صنف:
        if dollar > 200000:
            analysis['status'] = '⚠️ هشدار'
            analysis['trend'] = 'افزایش قیمت'
            analysis['price_change'] = 12 + (dollar - 195000) / 1500
            analysis['impact'] = 'بالا'
            analysis['risk_level'] = 'بالا'
            analysis['message'] = f'👗 با افزایش دلار، قیمت پارچه و مواد اولیه {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['actions'].append('🔹 خرید مواد اولیه را پیش‌بینی کنید')
            analysis['actions'].append('🔹 استفاده از تولیدات داخلی را افزایش دهید')
            analysis['opportunity'] = '📈 فرصت: تولید با مواد داخلی'
        else:
            analysis['status'] = '✅ مناسب'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 4
            analysis['impact'] = 'متوسط'
            analysis['message'] = '📊 شرایط برای تولید و فروش مناسب است.'
            analysis['actions'].append('🔹 افزایش تنوع محصولات')
            analysis['opportunity'] = '📈 فرصت: توسعه برند'
    
    elif "خودرو" in صنف or "یدکی" in صنف:
        if dollar > 210000:
            analysis['status'] = '🔴 بحران'
            analysis['trend'] = 'افزایش شدید'
            analysis['price_change'] = 25 + (dollar - 195000) / 1000
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بحرانی'
            analysis['message'] = f'🚗 افزایش شدید دلار و تحریم‌ها قیمت خودرو را {analysis["price_change"]:.0f}% بالا می‌برد.'
            analysis['actions'].append('🔹 فروش را به تعویق نیندازید')
            analysis['actions'].append('🔹 قطعات یدکی استراتژیک خریداری کنید')
            analysis['opportunity'] = '📈 فرصت: فروش در شرایط افزایش قیمت'
        else:
            analysis['status'] = '⚠️ هشدار'
            analysis['trend'] = 'افزایش ملایم'
            analysis['price_change'] = 10
            analysis['impact'] = 'بالا'
            analysis['message'] = '📊 افزایش قیمت خودرو ادامه دارد.'
            analysis['actions'].append('🔹 مدیریت موجودی قطعات')
            analysis['opportunity'] = '📉 فرصت: خرید در قیمت‌های فعلی'
    
    elif "بهداشت" in صنف or "درمان" in صنف:
        if inflation > 40:
            analysis['status'] = '⚠️ توجه'
            analysis['trend'] = 'افزایش هزینه'
            analysis['price_change'] = 8 + (inflation - 35) / 2
            analysis['impact'] = 'متوسط'
            analysis['risk_level'] = 'متوسط'
            analysis['message'] = f'🏥 با تورم {inflation:.0f}%، هزینه‌های درمانی {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['actions'].append('🔹 قیمت خدمات را بازبینی کنید')
            analysis['actions'].append('🔹 قراردادهای بیمه را بهبود دهید')
            analysis['opportunity'] = '📈 فرصت: توسعه خدمات تخصصی'
        else:
            analysis['status'] = '✅ پایدار'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 3
            analysis['impact'] = 'کم'
            analysis['message'] = '📊 شرایط برای فعالیت درمانی مطلوب است.'
            analysis['actions'].append('🔹 بهبود کیفیت خدمات')
            analysis['opportunity'] = '📈 فرصت: جذب بیماران بیشتر'
    
    elif "املاک" in صنف or "مستغلات" in صنف:
        if dollar > 200000:
            analysis['status'] = '📈 رشد'
            analysis['trend'] = 'افزایش قیمت ملک'
            analysis['price_change'] = 18 + (dollar - 195000) / 1000
            analysis['impact'] = 'بالا'
            analysis['risk_level'] = 'متوسط'
            analysis['message'] = f'🏠 قیمت ملک با افزایش دلار {analysis["price_change"]:.0f}% رشد می‌کند.'
            analysis['actions'].append('🔹 خرید ملک برای سرمایه‌گذاری')
            analysis['actions'].append('🔹 اجاره‌ها را به‌روزرسانی کنید')
            analysis['opportunity'] = '📈 فرصت: سرمایه‌گذاری در ملک'
        else:
            analysis['status'] = '✅ پایدار'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 5
            analysis['impact'] = 'متوسط'
            analysis['message'] = '📊 بازار ملک در وضعیت عادی است.'
            analysis['actions'].append('🔹 بررسی فرصت‌های سرمایه‌گذاری')
            analysis['opportunity'] = '📈 فرصت: خرید ملک برای اجاره'
    
    elif "فناوری" in صنف or "مخابرات" in صنف:
        if dollar > 200000:
            analysis['status'] = '⚠️ هشدار'
            analysis['trend'] = 'افزایش هزینه'
            analysis['price_change'] = 10 + (dollar - 195000) / 1500
            analysis['impact'] = 'بالا'
            analysis['risk_level'] = 'بالا'
            analysis['message'] = f'📱 هزینه تجهیزات فناوری {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['actions'].append('🔹 خرید تجهیزات را به تعویق نیندازید')
            analysis['actions'].append('🔹 استفاده از خدمات ابری داخلی')
            analysis['opportunity'] = '📈 فرصت: توسعه نرم‌افزارهای داخلی'
        else:
            analysis['status'] = '✅ مناسب'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 3
            analysis['impact'] = 'متوسط'
            analysis['message'] = '📊 شرایط برای سرمایه‌گذاری در فناوری مناسب است.'
            analysis['actions'].append('🔹 توسعه خدمات دیجیتال')
            analysis['opportunity'] = '📈 فرصت: نوآوری در خدمات'
    
    else:
        analysis['status'] = 'ℹ️ تحلیل'
        analysis['trend'] = 'متغیر'
        analysis['price_change'] = 5
        analysis['impact'] = 'متوسط'
        analysis['message'] = f'📊 تحلیل {صنف} در حال انجام است.'
        analysis['actions'].append('🔹 بررسی دقیق شرایط بازار')
        analysis['opportunity'] = '📈 فرصت: تحلیل دقیق‌تر داده‌ها'
    
    if analysis['risk_level'] == 'بحرانی':
        analysis['status'] = '🔴 وضعیت بحرانی'
    elif analysis['risk_level'] == 'بالا':
        analysis['status'] = '⚠️ وضعیت هشدار'
    
    return analysis

# ==========================================
# 10. مدل‌ها
# ==========================================
models_dict = {
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "Linear Regression": LinearRegression(),
}

def train_models(X_train, y_train, X_test, y_test):
    results = {}
    for name, model in models_dict.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            results[name] = {'model': model, 'r2': r2_score(y_test, y_pred)}
        except:
            results[name] = {'error': 'خطا'}
    return results

# ==========================================
# 11. تولید دیتای نمونه
# ==========================================
def sample_data(صنف):
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    
    if "خواربار" in صنف:
        df = pd.DataFrame({
            'تاریخ': dates,
            'فروش_امروز': np.random.randint(1_000_000, 10_000_000, 200),
            'تعداد_مشتریان': np.random.randint(10, 100, 200),
            'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)
        })
    elif "پوشاک" in صنف:
        df = pd.DataFrame({
            'تاریخ': dates,
            'فروش_امروز': np.random.randint(500_000, 5_000_000, 200),
            'تعداد_مشتریان': np.random.randint(5, 50, 200),
            'فروش_فردا': np.random.randint(500_000, 6_000_000, 200)
        })
    elif "ساختمان" in صنف:
        df = pd.DataFrame({
            'تاریخ': dates,
            'متراژ': np.random.randint(50, 500, 200),
            'تعداد_کارگر': np.random.randint(5, 50, 200),
            'فروش_فردا': np.random.randint(1_000_000, 15_000_000, 200)
        })
    else:
        df = pd.DataFrame({
            'تاریخ': dates,
            'فروش_امروز': np.random.randint(1_000_000, 10_000_000, 200),
            'تعداد_مشتریان': np.random.randint(10, 100, 200),
            'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)
        })
    
    df['تاریخ_شمسی'] = df['تاریخ'].apply(lambda d: jdatetime.datetime.fromgregorian(datetime=d).strftime('%Y/%m/%d'))
    return df

# ==========================================
# 12. چتبات
# ==========================================
def chatbot_response(user_input, صنف, data, prices):
    user_input = user_input.lower()
    
    responses = {
        'سلام': "👋 سلام! چطور می‌تونم به شما کمک کنم؟",
        'خوبی': "🙂 ممنون، خوبم! شما چطورید؟",
        'راهنما': f"📖 برای {صنف}، می‌تونم کمک کنم پیش‌بینی فروش داشته باشید.",
        'فروش': f"📊 بر اساس داده‌های {صنف}، فروش شما روند خوبی دارد.",
        'مشتری': f"👥 تعداد مشتریان {صنف} در حال افزایش است.",
        'دلار': f"💰 قیمت دلار امروز: {prices['dollar']:,} تومان",
        'طلا': f"🏅 قیمت طلا: {prices['gold']:,} تومان",
        'نفت': f"🛢️ قیمت نفت: {prices['oil']} دلار",
        'فولاد': f"🔩 قیمت فولاد: {prices['steel']} دلار هر تن",
        'تورم': f"📈 نرخ تورم: {prices['inflation']:.1f}%",
        'تخفیف': "💡 تخفیف‌های هدفمند می‌توانند فروش را تا ۲۰٪ افزایش دهند.",
        'داده': f"📋 تعداد رکوردهای شما: {len(data)}",
        'هدف': f"🎯 بهترین ستون هدف برای شما: {suggest_target(data)}",
        'ناهنجاری': "⚠️ ناهنجاری یعنی داده‌هایی که از بقیه خیلی متفاوت هستند.",
        'دقت': "🎯 دقت مدل به تعداد داده‌ها و کیفیت آن بستگی دارد.",
        'تاریخ': f"📅 ستون تاریخ به فرمت شمسی نمایش داده میشود.",
        'آینده': "🔮 تحلیل آینده نشان میدهد شرایط بازار در حال تغییر است.",
        'منبع': f"📡 قیمت‌ها از منابع {prices['source']} دریافت شده است."
    }
    
    for key, response in responses.items():
        if key in user_input:
            return response
    
    return f"🤖 سوال شما: '{user_input}'\nلطفاً دقیق‌تر بپرسید یا از کلمات کلیدی مثل: سلام، راهنما، فروش، مشتری، دلار، طلا، نفت، فولاد، تورم، تخفیف، داده، هدف، ناهنجاری، دقت، تاریخ، آینده، منبع استفاده کنید."

# ==========================================
# 13. پنل مدیریت
# ==========================================
def admin_panel(prices):
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🔐</span> پنل مدیریت iHoNoor</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 کاربران", "۱,۲۴۵", delta="+۱۲%")
    with col2:
        st.metric("📊 پیش‌بینی‌ها", "۳,۸۹۰", delta="+۸%")
    with col3:
        st.metric("🏷️ صنف‌ها", len(industries))
    with col4:
        st.metric("💰 نرخ دلار", f"{prices['dollar']:,}")
    
    st.markdown("---")
    st.subheader("📊 وضعیت اقتصادی لحظه‌ای")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("💰 دلار", f"{prices['dollar']:,}")
    with col2:
        st.metric("🏅 طلا", f"{prices['gold']:,}")
    with col3:
        st.metric("🛢️ نفت", f"{prices['oil']} $")
    with col4:
        st.metric("🔩 فولاد", f"{prices['steel']} $")
    with col5:
        st.metric("📈 تورم", f"{prices['inflation']:.1f}%")
    
    st.caption(f"📡 منبع: {prices['source']} | آخرین بروزرسانی: {prices['date']}")
    
    st.markdown("---")
    st.subheader("👥 مدیریت کاربران")
    users_data = pd.DataFrame({
        'نام': ['علی رضایی', 'مریم احمدی', 'محمد کریمی', 'سارا حسینی'],
        'ایمیل': ['ali@example.com', 'maryam@example.com', 'mohammad@example.com', 'sara@example.com'],
        'صنف': ['خواربارفروشی', 'پوشاک', 'ساختمان', 'نانوایی'],
        'وضعیت': ['فعال', 'فعال', 'غیرفعال', 'فعال']
    })
    st.dataframe(users_data, use_container_width=True)

# ==========================================
# 14. بخش سایدبار
# ==========================================
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "history" not in st.session_state: st.session_state.history = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

with st.sidebar:
    st.markdown("""
    <div style="background:#0A2540;color:white;padding:18px;border-radius:18px;text-align:center;margin-bottom:18px;">
        <h1 style="font-size:2rem;margin:0;"><span style="color:#F5A623;">iHo</span>Noor</h1>
        <p style="font-size:0.75rem;opacity:0.7;margin:0;">✨ v6.1</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ " + t['step1'], industries)
    
    st.markdown("---")
    st.markdown("### 📊 وضعیت اقتصادی لحظه‌ای")
    st.metric("💰 دلار", f"{prices['dollar']:,} تومان", delta=f"{((prices['dollar']-195000)/195000*100):.1f}%")
    st.metric("🏅 طلا", f"{prices['gold']:,} تومان")
    st.metric("🛢️ نفت", f"{prices['oil']} دلار")
    st.metric("🔩 فولاد", f"{prices['steel']} دلار")
    st.caption(f"📡 {prices['source']} | {prices['date']}")
    
    st.markdown("---")
    فایل = st.file_uploader("📁 " + t['step2'], type=["csv", "xlsx", "xls"])
    
    حالت_ساده = st.checkbox("📱 حالت ساده (تبلت)", value=False)
    if حالت_ساده:
        st.markdown("<style>.stButton>button{padding:16px 32px!important;font-size:1.1rem!important;}</style>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### 🎖️ امتیاز شما")
    c1, c2 = st.columns(2)
    c1.metric("⭐", st.session_state.score)
    c2.metric("🔥", f"{st.session_state.streak} روز")

# ==========================================
# 15. بارگذاری دیتا
# ==========================================
data = None
if فایل:
    try:
        data = pd.read_csv(فایل) if فایل.name.endswith('.csv') else pd.read_excel(فایل)
        st.success(f"✅ {len(data)} رکورد بارگذاری شد.")
    except Exception as e:
        st.error(f"❌ خطا در خواندن فایل: {e}")

if data is None:
    data = sample_data(صنف)
    st.info(f"📊 داده‌های نمونه برای {صنف}")

# ==========================================
# 16. هدر
# ==========================================
st.markdown(f"""
<div class="main-header">
    <h1><span class="highlight">iHo</span>Noor</h1>
    <p>{t['app_name']} | {t['subtitle']}</p>
    <div>
        <span class="badge-version">✨ نسخه ۶.۱ | پیش‌بینی هوشمند</span>
        <span class="dollar-badge">💰 دلار: {prices['dollar']:,} تومان</span>
        <span class="dollar-badge">🏅 طلا: {prices['gold']:,}</span>
        <span class="source-badge">📡 {prices['source']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="steps">
    <div class="step-item"><div class="num">۱</div><div class="text">{t['step1']}</div><div class="desc">از منوی کناری</div></div>
    <div class="step-item"><div class="num">۲</div><div class="text">{t['step2']}</div><div class="desc">Excel یا CSV</div></div>
    <div class="step-item"><div class="num">۳</div><div class="text">{t['step3']}</div><div class="desc">دریافت نتیجه</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 17. تب‌ها
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "📊 " + t['step3'],
    "🔮 " + t['future'],
    "📖 راهنما",
    "💬 " + t['chatbot'],
    "🔐 " + t['admin'],
    "📱 نصب",
    "📅 تقویم",
    "🤝 ارجاع",
    "👤 داشبورد",
    "🏠 خونه‌پرداز",
    "📝 تماس"
])

# ==========================================
# تب 1: پیش‌بینی
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><div class="card-title"><span class="icon">📋</span> نمونه داده</div>', unsafe_allow_html=True)
        st.dataframe(data.head(5))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><div class="card-title"><span class="icon">📊</span> خلاصه</div>', unsafe_allow_html=True)
        st.dataframe(data.describe())
        st.markdown('</div>', unsafe_allow_html=True)
    
    all_cols = data.columns.tolist()
    nums = data.select_dtypes(include=['number']).columns.tolist()
    suggested = suggest_target(data)
    
    opts = [f"{t['suggest']}: {suggested}"] + all_cols if suggested else all_cols
    selected = st.selectbox(t['target'], opts)
    
    if selected.startswith(t['suggest']):
        target = suggested
        st.info(f"✅ iHoNoor ستون **{target}** را پیشنهاد میکند.")
    else:
        target = selected
    
    if target not in nums:
        st.error("❌ ستون هدف باید عددی باشد!")
        st.stop()
    
    unit = detect_unit(target)
    st.info(f"✅ {t['unit']}: **{unit}**")
    
    if st.button(t['predict_btn'], type="primary", use_container_width=True):
        with st.spinner("⏳ در حال تحلیل..."):
            try:
                le = LabelEncoder()
                d = data.copy()
                for col in d.select_dtypes(include=['object']).columns:
                    if col != target:
                        try:
                            d[col] = le.fit_transform(d[col].astype(str))
                        except:
                            pass
                
                X = d.drop(columns=[target]).select_dtypes(include=['number'])
                y = d[target]
                
                if len(X.columns) == 0:
                    st.error("❌ ویژگی عددی کافی نیست.")
                    st.stop()
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                results = train_models(X_train, y_train, X_test, y_test)
                
                best = None
                best_score = -1
                for name, res in results.items():
                    if 'error' not in res and res['r2'] > best_score:
                        best_score = res['r2']
                        best = name
                
                if best:
                    model = results[best]['model']
                    pred = model.predict(X.mean().values.reshape(1, -1))[0]
                    
                    st.session_state.score += 5
                    st.session_state.streak += 1
                    
                    emoji, msg = get_emoji(pred, unit)
                    
                    st.markdown(f"""
                    <div class="result-box">
                        <div class="result-emoji">{emoji}</div>
                        <div class="result-label">{msg}</div>
                        <div class="result-number">{pred:,.0f}</div>
                        <div class="result-label">{unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric(t['accuracy'], f"{best_score:.1%}")
                    c2.metric(t['confidence'], f"{pred*0.85:,.0f} - {pred*1.15:,.0f}")
                    c3.metric("🏆 مدل", best)
                    
                    with st.expander("📊 " + t['feature_importance']):
                        if hasattr(model, 'feature_importances_'):
                            imp = pd.DataFrame({'ویژگی': X.columns, 'اهمیت': model.feature_importances_}).sort_values('اهمیت', ascending=False)
                            st.dataframe(imp)
                            fig = px.bar(imp, x='اهمیت', y='ویژگی', orientation='h', height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("ℹ️ این مدل اهمیت ویژگی‌ها را پشتیبانی نمیکند.")
                    
                    with st.expander("💱 " + t['dollar_label']):
                        st.markdown(f"💰 **نرخ دلار لحظه‌ای:** {prices['dollar']:,} تومان")
                        if unit == 'تومان':
                            dollar_value = pred / prices['dollar']
                            st.metric("💵 پیش‌بینی به دلار", f"${dollar_value:,.2f}")
                        else:
                            st.info(f"ℹ️ واحد '{unit}' است. تحلیل دلاری برای ستون‌های تومانی انجام میشود.")
                    
                    st.markdown(f"""
                    <div class="advisor-box">
                        <strong>✨ {t['advisor']}</strong>
                        <p style="font-size:0.9rem;opacity:0.9;margin-top:8px;">
                            با توجه به پیش‌بینی، موجودی خود را مدیریت کنید.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state.history.append({
                        'زمان': datetime.now().strftime("%H:%M"),
                        'هدف': target,
                        'پیش‌بینی': f"{pred:,.0f} {unit}",
                        'دقت': f"{best_score:.1%}"
                    })
                    
            except Exception as e:
                st.error(f"❌ خطا: {e}")

# ==========================================
# تب 2: تحلیلگر آینده
# ==========================================
with tab2:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🔮</span> تحلیلگر هوشمند آینده iHoNoor</div>
        <p>تحلیل شرایط اقتصادی و تأثیر آن بر صنف شما</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 وضعیت اقتصادی لحظه‌ای")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("💰 دلار", f"{prices['dollar']:,}", delta=f"{((prices['dollar']-195000)/195000*100):.1f}%")
    with col2:
        st.metric("🏅 طلا", f"{prices['gold']:,}", delta=f"{((prices['gold']-35000000)/35000000*100):.1f}%")
    with col3:
        st.metric("🛢️ نفت", f"{prices['oil']} $", delta=f"{((prices['oil']-85)/85*100):.1f}%")
    with col4:
        st.metric("🔩 فولاد", f"{prices['steel']} $", delta=f"{((prices['steel']-1200)/1200*100):.1f}%")
    with col5:
        st.metric("📈 تورم", f"{prices['inflation']:.1f}%", delta=f"{((prices['inflation']-35)/35*100):.1f}%")
    
    st.caption(f"📡 منبع: {prices['source']} | آخرین بروزرسانی: {prices['date']}")
    
    st.markdown("---")
    st.subheader(f"🔮 تحلیل آینده برای {صنف}")
    
    analysis = future_analyst(صنف, prices)
    
    status_color = "stable"
    if "بحران" in analysis['status'] or "بحرانی" in analysis['status']:
        status_color = "critical"
    elif "هشدار" in analysis['status']:
        status_color = "warning"
    
    st.markdown(f"""
    <div class="future-box">
        <div class="title">🔮 تحلیلگر آینده iHoNoor</div>
        <div>
            <span class="status-badge {status_color}">{analysis['status']}</span>
        </div>
        <p style="font-size:1.1rem;margin-top:10px;">
            <strong>روند:</strong> {analysis['trend']}
        </p>
        <p>
            <strong>تأثیر بر صنف:</strong> {analysis['impact']}
        </p>
        <p>
            <strong>تغییر قیمت پیش‌بینی شده:</strong> {analysis['price_change']:.1f}%
        </p>
        <p>
            <strong>سطح ریسک:</strong> {analysis['risk_level']}
        </p>
        <p style="background:rgba(255,255,255,0.05);padding:12px;border-radius:10px;margin-top:10px;">
            {analysis['message']}
        </p>
        <div style="margin-top:10px;">
            <strong>🔹 راهکارهای پیشنهادی:</strong>
            <ul style="margin-top:5px;">
                {''.join([f'<li>{action}</li>' for action in analysis['actions']])}
            </ul>
        </div>
        <div style="margin-top:10px;background:rgba(245,166,35,0.1);padding:12px;border-radius:10px;border-right:3px solid #F5A623;">
            <strong>{analysis['opportunity']}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📊 جزئیات تحلیل و نحوه محاسبه"):
        st.markdown("""
        **🔍 تحلیلگر آینده چگونه کار میکند؟**
        
        این ابزار با ترکیب **۴ عامل کلیدی** وضعیت آینده صنف شما را پیش‌بینی میکند:
        
        1. **قیمت دلار**: تأثیر مستقیم بر واردات و قیمت مواد اولیه
        2. **قیمت طلا**: شاخص تورم و ارزش پول
        3. **قیمت نفت**: تأثیر بر هزینه‌های انرژی و حمل و نقل
        4. **قیمت فولاد**: تأثیر بر صنایع ساختمانی و تولیدی
        5. **نرخ تورم**: تأثیر بر قدرت خرید و هزینه‌ها
        
        **📌 هر صنف چه تأثیری می‌پذیرد؟**
        
        | صنف | تأثیرپذیری | عامل اصلی |
        |-----|------------|-----------|
        | خواربارفروشی | بالا | دلار و تورم |
        | ساختمان | بسیار بالا | فولاد و دلار |
        | پوشاک | بالا | دلار |
        | خودرو | بسیار بالا | دلار و تحریم‌ها |
        | بهداشت | متوسط | تورم |
        | فناوری | بالا | دلار |
        | املاک | بالا | تورم و دلار |
        """)

# ==========================================
# تب 3: راهنمای کامل (کاربرپسند)
# ==========================================
with tab3:
    st.markdown("""
    <div class="card" style="background: linear-gradient(135deg, #EBF4FF, #D6E8FF); border: none;">
        <div class="card-title" style="font-size:1.4rem;">
            <span class="icon">📖</span> راهنمای کامل iHoNoor
        </div>
        <p style="font-size:1.1rem; color:#0A2540;">
            با <strong>۴ گام ساده</strong> از iHoNoor استفاده کنید و فروش خود را پیش‌بینی کنید.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== گام ۱ =====
    st.markdown("""
    <div class="guide-step">
        <h3>📌 گام ۱: صنف خود را انتخاب کنید</h3>
        <p>از منوی سمت راست، صنف خود را انتخاب کنید. iHoNoor برای هر صنف، تحلیل مخصوص خود را دارد.</p>
        <div class="tip">
            💡 <strong>مثال:</strong> اگر فروشگاه مواد غذایی دارید، "خواربارفروشی" را انتخاب کنید.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== گام ۲ =====
    st.markdown("""
    <div class="guide-step">
        <h3>📌 گام ۲: فایل خود را آپلود کنید</h3>
        <p>فایل Excel یا CSV خود را در بخش آپلود بارگذاری کنید.</p>
        <div class="warning">
            ⚠️ <strong>نکته مهم:</strong> فایل شما باید حداقل شامل دو ستون باشد:
            <ul style="margin:4px 0;padding-right:20px;">
                <li><strong>📅 تاریخ:</strong> روزهای مختلف (مثلاً ۱۴۰۳/۰۱/۰۱)</li>
                <li><strong>💰 فروش:</strong> مقدار فروش در آن روز (عددی)</li>
            </ul>
        </div>
        <div class="tip">
            💡 <strong>تعداد رکوردهای توصیه شده:</strong> حداقل ۵۰ روز برای پیش‌بینی قابل اعتماد.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== گام ۳ =====
    st.markdown("""
    <div class="guide-step">
        <h3>📌 گام ۳: ستون هدف را انتخاب کنید</h3>
        <p>ستونی که میخواهید پیش‌بینی کنید را انتخاب کنید.</p>
        <div class="success">
            ✅ <strong>پیشنهاد iHoNoor:</strong> اگر مطمئن نیستید، گزینه <strong>"💡 پیشنهاد iHoNoor"</strong> را انتخاب کنید تا بهترین ستون به شما پیشنهاد شود.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== گام ۴ =====
    st.markdown("""
    <div class="guide-step">
        <h3>📌 گام ۴: پیش‌بینی را دریافت کنید</h3>
        <p>روی دکمه <strong>"🚀 پیش‌بینی کن"</strong> کلیک کنید و نتیجه را مشاهده کنید.</p>
        <div class="tip">
            📊 <strong>خروجی‌ها:</strong>
            <ul style="margin:4px 0;padding-right:20px;">
                <li><strong>عدد پیش‌بینی:</strong> مقدار مورد انتظار برای فردا</li>
                <li><strong>دقت مدل:</strong> نشان میدهد چقدر میتوانید به نتیجه اعتماد کنید</li>
                <li><strong>بازه اطمینان:</strong> محدوده احتمالی فروش</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== نکات کلیدی =====
    st.markdown("""
    <div style="background:linear-gradient(105deg, #0A2540, #1A3A5C);padding:22px 28px;border-radius:20px;color:white;margin-top:16px;">
        <h3 style="color:#F5A623;margin:0;">💡 نکات کلیدی برای بهترین نتیجه</h3>
        <ul style="margin-top:10px;line-height:2;">
            <li>📊 <strong>حداقل ۵۰ روز داده</strong> داشته باشید</li>
            <li>📅 داده‌های خود را <strong>هر هفته آپدیت</strong> کنید</li>
            <li>🎯 ستون هدف حتماً <strong>عددی</strong> باشد</li>
            <li>🔄 هر بار که داده جدید دارید، پیش‌بینی را <strong>تکرار</strong> کنید</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== پشتیبانی =====
    st.markdown("""
    <div style="background:#FFF8E1;padding:16px 22px;border-radius:16px;border-right:4px solid #F5A623;margin-top:16px;">
        <strong>📞 نیاز به کمک دارید؟</strong>
        <p style="margin:4px 0;">با ما در ارتباط باشید:</p>
        <ul style="margin:4px 0;padding-right:20px;">
            <li>📧 <strong>ایمیل:</strong> ha2021alipur@gmail.com</li>
            <li>📱 <strong>واتساپ/تلگرام:</strong> 09019470509</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 4: چتبات
# ==========================================
with tab4:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">💬</span> چتبات هوشمند iHoNoor</div>
        <p>از چتبات بپرسید تا به شما کمک کند.</p>
    </div>
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history[-20:]:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-message chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    user_msg = st.text_input("✏️ سوال خود را بنویسید...", placeholder="مثلاً: آینده صنف من چطوره؟")
    if st.button("📨 ارسال") and user_msg:
        st.session_state.chat_history.append({'role': 'user', 'content': user_msg})
        response = chatbot_response(user_msg, صنف, data, prices)
        st.session_state.chat_history.append({'role': 'bot', 'content': response})
        st.rerun()
    
    if st.button("🗑️ پاک کردن تاریخچه چت"):
        st.session_state.chat_history = []
        st.rerun()

# ==========================================
# تب 5: پنل مدیریت
# ==========================================
with tab5:
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        st.markdown("""
        <div style="text-align:center;padding:40px 0;">
            <h2 style="color:#0A2540;">🔐 ورود به پنل مدیریت</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("👤 نام کاربری")
            password = st.text_input("🔑 رمز عبور", type="password")
            if st.button("🚪 ورود", type="primary", use_container_width=True):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("✅ با موفقیت وارد شدید!")
                    st.rerun()
                else:
                    st.error("❌ نام کاربری یا رمز عبور اشتباه است.")
    else:
        admin_panel(prices)
        if st.button("🚪 خروج از سیستم"):
            st.session_state.admin_logged_in = False
            st.rerun()

# ==========================================
# تب‌های دیگر
# ==========================================
with tab6:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📱</span> نصب روی گوشی</div>
        <p>در کروم: ⋮ → Add to Home screen</p>
        <p>در سافاری: اشتراک‌گذاری → Add to Home Screen</p>
    </div>
    """, unsafe_allow_html=True)

with tab7:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">📅</span> تقویم شمسی</div>', unsafe_allow_html=True)
    today = jdatetime.date.today()
    st.info(f"📌 امروز: {today.strftime('%A %d %B %Y')}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab8:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">🤝</span> سیستم ارجاع</div>', unsafe_allow_html=True)
    code = f"iHN-{str(uuid.uuid4())[:8].upper()}"
    st.success(f"🔑 کد ارجاع شما: **{code}**")
    if st.button("📨 ثبت ارجاع"):
        st.session_state.score += 10
        st.success("✅ +۱۰ امتیاز!")
    st.markdown('</div>', unsafe_allow_html=True)

with tab9:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">👤</span> داشبورد</div>', unsafe_allow_html=True)
    st.metric("📊 تعداد رکوردها", len(data))
    st.metric("🏷️ صنف", صنف)
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history))
    st.markdown('</div>', unsafe_allow_html=True)

with tab10:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">🏠</span> خونه‌پرداز</div>', unsafe_allow_html=True)
    st.info("💰 درآمد و هزینه‌های خود را مدیریت کنید.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab11:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">📝</span> تماس</div>', unsafe_allow_html=True)
    st.info("📬 ha2021alipur@gmail.com | 📱 09019470509")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# فوتر
# ==========================================
st.markdown(f"""
<div class="footer">
    ✨ iHoNoor v6.1 | {t['app_name']} | دلار: {prices['dollar']:,} تومان | 📡 {prices['source']} | ha2021alipur@gmail.com
</div>
""", unsafe_allow_html=True)
