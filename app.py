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
import time
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
# 2. دریافت قیمت‌های بروز
# ==========================================
@st.cache_data(ttl=300)
def get_real_prices():
    prices = {
        'dollar': 188500,
        'gold_18': 0,
        'gold_24': 0,
        'oil': 85,
        'inflation': 35,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'source': 'آفلاین'
    }
    
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            price = data['rates']['IRR'] / 10
            if 180000 < price < 200000:
                prices['dollar'] = int(price)
                prices['source'] = 'آنلاین'
    except:
        pass
    
    try:
        url = "https://api.gold-api.com/price/XAU"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            gold_usd = data.get('price', 2450)
            if gold_usd > 0:
                prices['gold_18'] = int((gold_usd * prices['dollar']) / 9.574)
                prices['gold_24'] = int(prices['gold_18'] / 0.75)
    except:
        prices['gold_18'] = int(prices['dollar'] * 95)
        prices['gold_24'] = int(prices['gold_18'] / 0.75)
    
    prices['oil'] = 85
    prices['inflation'] = 30 + (prices['dollar'] - 188500) / 5000
    prices['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return prices

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
        'future': '🔮 تحلیلگر آینده',
        'economy': '📊 تحلیل اقتصادی',
        'industry_tools': '🛠️ ابزارهای تخصصی'
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
        'future': '🔮 Future Analyst',
        'economy': '📊 Economic Analysis',
        'industry_tools': '🛠️ Industry Tools'
    }
}

# ==========================================
# 5. تم‌ها
# ==========================================
THEMES = {
    "شب تاریک": {
        "bg": "linear-gradient(145deg, #0A1628, #1A2A4A)",
        "card": "rgba(255,255,255,0.03)",
        "text": "#FFFFFF",
        "accent": "#FFD700",
        "border": "rgba(255,215,0,0.1)"
    },
    "آبی آسمان": {
        "bg": "linear-gradient(145deg, #E3F2FD, #BBDEFB)",
        "card": "rgba(255,255,255,0.7)",
        "text": "#0D47A1",
        "accent": "#1565C0",
        "border": "rgba(13,71,161,0.1)"
    },
    "سبز زمردی": {
        "bg": "linear-gradient(145deg, #E8F5E9, #C8E6C9)",
        "card": "rgba(255,255,255,0.7)",
        "text": "#1B5E20",
        "accent": "#2E7D32",
        "border": "rgba(27,94,32,0.1)"
    },
    "طلایی": {
        "bg": "linear-gradient(145deg, #FFF8E1, #FFECB3)",
        "card": "rgba(255,255,255,0.8)",
        "text": "#4E342E",
        "accent": "#F57F17",
        "border": "rgba(245,127,23,0.15)"
    },
    "بنفش سلطنتی": {
        "bg": "linear-gradient(145deg, #F3E5F5, #E1BEE7)",
        "card": "rgba(255,255,255,0.7)",
        "text": "#4A148C",
        "accent": "#6A1B9A",
        "border": "rgba(74,20,140,0.1)"
    },
    "نارنجی غروب": {
        "bg": "linear-gradient(145deg, #FFF3E0, #FFE0B2)",
        "card": "rgba(255,255,255,0.7)",
        "text": "#BF360C",
        "accent": "#E65100",
        "border": "rgba(191,54,12,0.1)"
    },
    "سورمه‌ای": {
        "bg": "linear-gradient(145deg, #FCE4EC, #F8BBD0)",
        "card": "rgba(255,255,255,0.7)",
        "text": "#880E4F",
        "accent": "#AD1457",
        "border": "rgba(136,14,79,0.1)"
    },
    "خاکستری مدرن": {
        "bg": "linear-gradient(145deg, #ECEFF1, #CFD8DC)",
        "card": "rgba(255,255,255,0.8)",
        "text": "#263238",
        "accent": "#455A64",
        "border": "rgba(38,50,56,0.1)"
    }
}

# ==========================================
# 6. انتخاب تم
# ==========================================
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "شب تاریک"

def apply_theme(theme_name):
    theme = THEMES[theme_name]
    st.markdown(f"""
    <style>
        .stApp {{ background: {theme['bg']} !important; color: {theme['text']} !important; transition: all 0.5s ease; }}
        .main-header {{ background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(20px) !important; border: 1px solid {theme['border']} !important; border-radius: 30px !important; padding: 30px 40px !important; box-shadow: 0 20px 60px rgba(0,0,0,0.1) !important; margin-bottom: 30px !important; text-align: center !important; }}
        .main-header h1 {{ background: linear-gradient(135deg, {theme['accent']}, #FFD700) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-size: 2.8rem !important; font-weight: 900 !important; margin: 0 !important; }}
        .main-header p {{ color: {theme['text']} !important; opacity: 0.7 !important; }}
        .main-header .dollar-badge {{ background: rgba(255,215,0,0.08) !important; border: 1px solid rgba(255,215,0,0.1) !important; border-radius: 40px !important; padding: 4px 16px !important; color: {theme['accent']} !important; font-size: 0.75rem !important; display: inline-block !important; margin: 4px !important; }}
        .card {{ background: {theme['card']} !important; backdrop-filter: blur(12px) !important; border: 1px solid {theme['border']} !important; border-radius: 24px !important; padding: 22px 26px !important; margin-bottom: 18px !important; transition: all 0.3s ease !important; color: {theme['text']} !important; }}
        .card:hover {{ border-color: {theme['accent']} !important; transform: translateY(-4px) !important; box-shadow: 0 12px 40px rgba(0,0,0,0.05) !important; }}
        .card-title {{ color: {theme['text']} !important; font-weight: 700 !important; display: flex !important; align-items: center !important; gap: 10px !important; margin-bottom: 10px !important; }}
        .stTabs [data-baseweb="tab-list"] {{ display: flex !important; flex-wrap: wrap !important; gap: 10px !important; background: transparent !important; padding: 0 !important; border: none !important; justify-content: center !important; }}
        .stTabs [data-baseweb="tab"] {{ background: {theme['card']} !important; backdrop-filter: blur(10px) !important; border: 1px solid {theme['border']} !important; border-radius: 50px 15px 50px 15px !important; padding: 10px 24px !important; color: {theme['text']} !important; opacity: 0.6 !important; font-size: 0.85rem !important; transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important; }}
        .stTabs [data-baseweb="tab"]:hover {{ background: {theme['accent']} !important; color: white !important; opacity: 1 !important; transform: translateY(-3px) !important; }}
        .stTabs [aria-selected="true"] {{ background: {theme['accent']} !important; color: white !important; opacity: 1 !important; transform: translateY(-2px) !important; box-shadow: 0 0 30px {theme['accent']}33 !important; }}
        .result-box {{ background: {theme['card']} !important; backdrop-filter: blur(12px) !important; border: 1px solid {theme['border']} !important; border-radius: 30px 15px 30px 15px !important; padding: 28px 32px !important; text-align: center !important; margin-top: 12px !important; }}
        .result-number {{ font-size: 3.2rem !important; font-weight: 900 !important; background: linear-gradient(135deg, {theme['accent']}, #FFD700) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }}
        .result-label {{ color: {theme['text']} !important; opacity: 0.6 !important; font-size: 0.9rem !important; margin-top: 4px !important; }}
        .advisor-box {{ background: {theme['card']} !important; backdrop-filter: blur(12px) !important; border: 1px solid {theme['border']} !important; border-radius: 20px !important; padding: 20px 24px !important; color: {theme['text']} !important; margin-top: 16px !important; }}
        .advisor-box strong {{ color: {theme['accent']} !important; }}
        .future-box {{ background: {theme['card']} !important; backdrop-filter: blur(12px) !important; border: 1px solid {theme['border']} !important; border-radius: 24px !important; padding: 22px 26px !important; color: {theme['text']} !important; margin-top: 16px !important; }}
        .future-box .title {{ color: {theme['accent']} !important; font-weight: 700 !important; font-size: 1.1rem !important; margin-bottom: 10px !important; }}
        .step-item {{ background: {theme['card']} !important; backdrop-filter: blur(8px) !important; border: 1px solid {theme['border']} !important; border-radius: 50px 15px 50px 15px !important; padding: 12px 20px !important; text-align: center !important; min-width: 120px !important; flex: 1 !important; transition: all 0.3s ease !important; }}
        .step-item:hover {{ border-color: {theme['accent']} !important; transform: translateY(-3px) !important; }}
        .step-item .num {{ display: inline-flex !important; align-items: center !important; justify-content: center !important; width: 30px !important; height: 30px !important; border-radius: 50% !important; background: {theme['accent']}33 !important; border: 1px solid {theme['accent']}44 !important; color: {theme['accent']} !important; font-weight: 800 !important; font-size: 0.8rem !important; margin-bottom: 4px !important; }}
        .step-item .text {{ color: {theme['text']} !important; font-weight: 600 !important; font-size: 0.8rem !important; }}
        .step-item .desc {{ color: {theme['text']} !important; opacity: 0.4 !important; font-size: 0.65rem !important; }}
        .stButton > button {{ background: linear-gradient(135deg, {theme['accent']}44, {theme['accent']}11) !important; backdrop-filter: blur(8px) !important; border: 1px solid {theme['accent']}44 !important; border-radius: 50px 15px 50px 15px !important; padding: 12px 32px !important; color: {theme['accent']} !important; font-weight: 600 !important; transition: all 0.3s ease !important; }}
        .stButton > button:hover {{ border-color: {theme['accent']} !important; box-shadow: 0 0 30px {theme['accent']}22 !important; transform: translateY(-3px) !important; }}
        .guide-step {{ background: {theme['card']} !important; backdrop-filter: blur(8px) !important; border: 1px solid {theme['border']} !important; border-radius: 50px 15px 50px 15px !important; padding: 18px 22px !important; margin-bottom: 12px !important; transition: all 0.3s ease !important; }}
        .guide-step:hover {{ border-color: {theme['accent']} !important; }}
        .guide-step h3 {{ color: {theme['text']} !important; font-size: 1rem !important; margin: 0 !important; }}
        .guide-step p {{ color: {theme['text']} !important; opacity: 0.6 !important; font-size: 0.85rem !important; margin-top: 6px !important; }}
        .guide-step .tip {{ background: {theme['accent']}11 !important; padding: 8px 14px !important; border-radius: 10px !important; margin-top: 6px !important; font-size: 0.8rem !important; color: {theme['text']} !important; opacity: 0.8 !important; border-right: 2px solid {theme['accent']}44 !important; }}
        .chat-message {{ padding: 10px 16px !important; border-radius: 14px !important; margin-bottom: 6px !important; max-width: 80% !important; }}
        .chat-user {{ background: {theme['accent']}22 !important; border: 1px solid {theme['accent']}33 !important; color: {theme['text']} !important; margin-right: auto !important; }}
        .chat-bot {{ background: {theme['card']} !important; border: 1px solid {theme['border']} !important; color: {theme['text']} !important; margin-left: auto !important; }}
        .footer {{ text-align: center !important; color: {theme['text']} !important; opacity: 0.2 !important; font-size: 0.65rem !important; margin-top: 40px !important; padding-top: 16px !important; border-top: 1px solid {theme['border']} !important; }}
        ::-webkit-scrollbar {{ width: 4px; }}
        ::-webkit-scrollbar-track {{ background: {theme['border']}; border-radius: 10px; }}
        ::-webkit-scrollbar-thumb {{ background: {theme['accent']}44; border-radius: 10px; }}
        @media (max-width: 768px) {{ .main-header h1 {{ font-size: 2rem !important; }} .stTabs [data-baseweb="tab"] {{ padding: 8px 16px !important; font-size: 0.75rem !important; }} .step-item {{ min-width: 100% !important; }} .result-number {{ font-size: 2.4rem !important; }} .card {{ padding: 16px 18px !important; }} }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 7. انتخاب زبان و تم
# ==========================================
if "lang" not in st.session_state: st.session_state.lang = "fa"
theme_names = list(THEMES.keys())
selected_theme = st.sidebar.selectbox("🎨 انتخاب تم:", theme_names, index=theme_names.index(st.session_state.selected_theme))
if selected_theme != st.session_state.selected_theme:
    st.session_state.selected_theme = selected_theme
    st.rerun()
apply_theme(st.session_state.selected_theme)

lang = st.sidebar.selectbox("🌐 زبان / Language", ["فارسی", "English"])
st.session_state.lang = "fa" if lang == "فارسی" else "en"
t = LANG[st.session_state.lang]

# ==========================================
# 8. صنف‌ها
# ==========================================
industries = [
    "🏪 خواربارفروشی", "🔩 آهن‌آلات و مصالح", "🚗 خودروسازی و لوازم یدکی",
    "👗 پوشاک", "📱 فناوری و مخابرات", "🛒 خرده‌فروشی و آنلاین",
    "🏭 تولید و صنایع", "💰 بانکداری و مالی", "🏥 بهداشت و درمان",
    "🍔 صنایع غذایی", "⛽ پتروشیمی و انرژی", "⚡ برق و نیروگاه‌ها",
    "🎬 سینما و محصولات فرهنگی", "🏭 تولید و صنایع غذایی (تخصصی)",
    "🏢 املاک و مستغلات", "🏗️ ساختمان و پیمانکاری",
    "🏭 تولید سفارشی (Make-to-Order)", "📦 مدیریت موجودی و زنجیره تامین"
]

# ==========================================
# 9. توابع هسته
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
# 10. تحلیلگر آینده
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
        'opportunity': '',
        'dollar_prediction': '',
        'geo_political': '',
        'alert': ''
    }
    
    dollar = prices['dollar']
    gold = prices['gold_18']
    oil = prices['oil']
    inflation = prices['inflation']
    
    if dollar > 190000:
        analysis['geo_political'] = """
🔴 **شرایط کنونی: تنش‌های سیاسی و تحریم‌ها**

بر اساس آخرین تحولات منطقه‌ای و بین‌المللی:

۱. **تحریم‌های نفتی و بانکی** تشدید شده و دسترسی به منابع ارزی را محدود کرده است.
۲. **مذاکرات هسته‌ای** در وضعیت بلاتکلیفی قرار دارد و این نااطمینانی، بازار را تحت تأثیر قرار داده.
۳. **خروج سرمایه** از کشور افزایش یافته و فشار بر منابع ارزی را بیشتر کرده است.
۴. **تنش‌های منطقه‌ای** در خاورمیانه، نگرانی‌هایی درباره امنیت تجارت و حمل‌ونقل ایجاد کرده است.

📈 **پیش‌بینی قیمت دلار:** با توجه به شرایط فوق، دلار **روند صعودی** خواهد داشت و احتمال افزایش ۵ تا ۱۰ درصدی در ماه آینده وجود دارد.
        """
        analysis['dollar_prediction'] = 'صعودی 📈'
        analysis['risk_level'] = 'بالا'
    elif dollar > 180000:
        analysis['geo_political'] = """
⚠️ **شرایط کنونی: نوسانی و متشنج اما کنترل‌شده**

بر اساس آخرین تحولات:

۱. **تحریم‌ها** در وضعیت فعلی باقی مانده و تغییر محسوسی نداشته است.
۲. **انتظار برای تغییرات دیپلماتیک** در ماه‌های آینده وجود دارد.
۳. **بانک مرکزی** با مدیریت منابع ارزی، تلاش دارد نرخ را کنترل کند.
۴. **بازار** با نوسانات روزانه مواجه است اما روند مشخصی ندارد.

📊 **پیش‌بینی قیمت دلار:** دلار در کوتاه‌مدت **نوسانی** خواهد بود اما تمایل به افزایش دارد.
        """
        analysis['dollar_prediction'] = 'نوسانی 📊'
        analysis['risk_level'] = 'متوسط'
    else:
        analysis['geo_political'] = """
✅ **شرایط کنونی: ثبات نسبی در بازار ارز**

بر اساس آخرین تحولات:

۱. **تنش‌های سیاسی** کاهش یافته و فضای دیپلماتیک مساعدتر شده است.
۲. **ورود منابع ارزی** جدید به کشور، فشار را از روی بازار برداشته است.
۳. **بهبود روابط دیپلماتیک** با برخی کشورها، امیدواری‌هایی ایجاد کرده است.
۴. **انتظار ثبات** در کوتاه‌مدت وجود دارد.

📉 **پیش‌بینی قیمت دلار:** با توجه به شرایط، دلار **روند کاهشی یا ثبات** خواهد داشت.
        """
        analysis['dollar_prediction'] = 'کاهشی 📉'
        analysis['risk_level'] = 'کم'
    
    if "خواربار" in صنف or "غذایی" in صنف:
        if dollar > 190000:
            analysis['status'] = '🔴 وضعیت هشدار شدید'
            analysis['trend'] = 'افزایش قیمت مواد اولیه'
            analysis['price_change'] = 15 + (dollar - 190000) / 1000
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بسیار بالا'
            analysis['message'] = f'💰 **قیمت دلار به {dollar:,} تومان رسیده است.**\n\nاین افزایش دلار باعث میشود قیمت مواد اولیه و کالاهای وارداتی شما حدود {analysis["price_change"]:.0f} درصد افزایش پیدا کند.'
            analysis['alert'] = '🚨 **هشدار فوری:** موجودی کالاهای اساسی خود را افزایش دهید.'
            analysis['actions'] = ['🔹 افزایش موجودی کالاهای اساسی', '🔹 قرارداد بلندمدت با تامین‌کنندگان', '🔹 مدیریت قیمت فروش', '🔹 کاهش ضایعات']
            analysis['opportunity'] = '📈 فرصت: افزایش قیمت فروش با مدیریت هزینه‌ها'
        else:
            analysis['status'] = '✅ وضعیت پایدار'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 3
            analysis['impact'] = 'متوسط'
            analysis['message'] = '📊 شرایط فعلی نسبتاً پایدار است.'
            analysis['alert'] = '✅ وضعیت عادی است.'
            analysis['actions'] = ['🔹 حفظ کیفیت محصولات']
            analysis['opportunity'] = '📈 فرصت: جذب مشتری با کیفیت بالا'
    
    elif "ساختمان" in صنف or "پیمانکاری" in صنف or "مصالح" in صنف:
        if dollar > 190000:
            analysis['status'] = '🔴 وضعیت بحرانی'
            analysis['trend'] = 'افزایش شدید هزینه‌ها'
            analysis['price_change'] = 22 + (dollar - 190000) / 800
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بحرانی'
            analysis['message'] = f'🏗️ **قیمت دلار به {dollar:,} تومان رسیده است.**\n\nهزینه مصالح ساختمانی حدود {analysis["price_change"]:.0f} درصد افزایش می‌یابد.'
            analysis['alert'] = '🚨 **هشدار بحرانی:** پروژه‌های جدید را متوقف کنید.'
            analysis['actions'] = ['🔹 خرید فوری مصالح اساسی', '🔹 توقف پروژه‌های جدید', '🔹 بازنگری قیمت قراردادها', '🔹 کاهش نیروی کار موقت']
            analysis['opportunity'] = '📉 فرصت: خرید مصالح با قیمت فعلی'
        else:
            analysis['status'] = '⚠️ وضعیت توجه'
            analysis['trend'] = 'افزایش ملایم'
            analysis['price_change'] = 8
            analysis['impact'] = 'بالا'
            analysis['message'] = '📊 افزایش تدریجی قیمت مصالح قابل پیش‌بینی است.'
            analysis['alert'] = '⚠️ برنامه‌ریزی دقیق پروژه‌ها'
            analysis['actions'] = ['🔹 برنامه‌ریزی دقیق پروژه‌ها']
            analysis['opportunity'] = '📈 فرصت: شروع پروژه‌های جدید'
    
    else:
        analysis['status'] = 'ℹ️ تحلیل'
        analysis['trend'] = 'متغیر'
        analysis['price_change'] = 5
        analysis['impact'] = 'متوسط'
        analysis['message'] = f'📊 تحلیل {صنف} در حال انجام است.'
        analysis['alert'] = 'ℹ️ بررسی دقیق شرایط بازار'
        analysis['actions'] = ['🔹 بررسی دقیق شرایط بازار']
        analysis['opportunity'] = '📈 فرصت: تحلیل دقیق‌تر داده‌ها'
    
    if analysis['risk_level'] == 'بحرانی':
        analysis['status'] = '🔴 بحران'
    elif analysis['risk_level'] == 'بالا':
        analysis['status'] = '⚠️ هشدار'
    elif analysis['risk_level'] == 'متوسط':
        analysis['status'] = '📊 متوسط'
    else:
        analysis['status'] = '✅ پایدار'
    
    return analysis

# ==========================================
# 11. مدل‌ها
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

def sample_data(صنف):
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    if "خواربار" in صنف:
        df = pd.DataFrame({'تاریخ': dates, 'فروش_امروز': np.random.randint(1_000_000, 10_000_000, 200), 'تعداد_مشتریان': np.random.randint(10, 100, 200), 'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)})
    elif "پوشاک" in صنف:
        df = pd.DataFrame({'تاریخ': dates, 'فروش_امروز': np.random.randint(500_000, 5_000_000, 200), 'تعداد_مشتریان': np.random.randint(5, 50, 200), 'فروش_فردا': np.random.randint(500_000, 6_000_000, 200)})
    elif "ساختمان" in صنف:
        df = pd.DataFrame({'تاریخ': dates, 'متراژ': np.random.randint(50, 500, 200), 'تعداد_کارگر': np.random.randint(5, 50, 200), 'فروش_فردا': np.random.randint(1_000_000, 15_000_000, 200)})
    else:
        df = pd.DataFrame({'تاریخ': dates, 'فروش_امروز': np.random.randint(1_000_000, 10_000_000, 200), 'تعداد_مشتریان': np.random.randint(10, 100, 200), 'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)})
    df['تاریخ_شمسی'] = df['تاریخ'].apply(lambda d: jdatetime.datetime.fromgregorian(datetime=d).strftime('%Y/%m/%d'))
    return df

def chatbot_response(user_input, صنف, data, prices):
    user_input = user_input.lower()
    responses = {
        'سلام': "👋 سلام! چطور می‌تونم به شما کمک کنم؟",
        'خوبی': "🙂 ممنون، خوبم! شما چطورید؟",
        'راهنما': f"📖 برای {صنف}، می‌تونم کمک کنم پیش‌بینی فروش داشته باشید.",
        'فروش': f"📊 بر اساس داده‌های {صنف}، فروش شما روند خوبی دارد.",
        'مشتری': f"👥 تعداد مشتریان {صنف} در حال افزایش است.",
        'دلار': f"💰 قیمت دلار امروز: {prices['dollar']:,} تومان",
        'طلا': f"🏅 قیمت طلای ۱۸ عیار: {prices['gold_18']:,} تومان",
        'نفت': f"🛢️ قیمت نفت: {prices['oil']} دلار",
        'تورم': f"📈 نرخ تورم: {prices['inflation']:.1f}%",
        'تخفیف': "💡 تخفیف‌های هدفمند می‌توانند فروش را تا ۲۰٪ افزایش دهند.",
        'داده': f"📋 تعداد رکوردهای شما: {len(data)}",
        'هدف': f"🎯 بهترین ستون هدف برای شما: {suggest_target(data)}",
        'ناهنجاری': "⚠️ ناهنجاری یعنی داده‌هایی که از بقیه خیلی متفاوت هستند.",
        'دقت': "🎯 دقت مدل به تعداد داده‌ها و کیفیت آن بستگی دارد.",
        'تاریخ': f"📅 ستون تاریخ به فرمت شمسی نمایش داده میشود.",
        'آینده': "🔮 تحلیل آینده نشان میدهد شرایط بازار در حال تغییر است.",
        'منبع': f"📡 قیمت‌ها از منابع {prices['source']} دریافت شده است.",
        'ابزار': f"🛠️ برای {صنف}، ابزارهای تخصصی زیادی وجود دارد. از بخش 'ابزارهای تخصصی' استفاده کنید."
    }
    for key, response in responses.items():
        if key in user_input:
            return response
    return f"🤖 سوال شما: '{user_input}'\nلطفاً دقیق‌تر بپرسید یا از کلمات کلیدی استفاده کنید."

def admin_panel(prices):
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🔐</span> پنل مدیریت iHoNoor</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👥 کاربران", "۱,۲۴۵", delta="+۱۲%")
    with col2: st.metric("📊 پیش‌بینی‌ها", "۳,۸۹۰", delta="+۸%")
    with col3: st.metric("🏷️ صنف‌ها", len(industries))
    with col4: st.metric("💰 نرخ دلار", f"{prices['dollar']:,}")
    st.markdown("---")
    st.subheader("📊 وضعیت اقتصادی لحظه‌ای")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 دلار", f"{prices['dollar']:,}")
    with col2: st.metric("🏅 طلای ۱۸ عیار", f"{prices['gold_18']:,}")
    with col3: st.metric("🛢️ نفت", f"{prices['oil']} $")
    with col4: st.metric("📈 تورم", f"{prices['inflation']:.1f}%")
    st.caption(f"📡 {prices['source']} | ⏱️ {prices['date']}")

# ==========================================
# 12. بخش سایدبار
# ==========================================
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "history" not in st.session_state: st.session_state.history = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

with st.sidebar:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,215,0,0.05);border-radius:50px 15px 50px 15px;padding:18px;text-align:center;margin-bottom:18px;">
        <h1 style="font-size:2rem;margin:0;background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">iHo<span style="background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Noor</span></h1>
        <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:0;">✨ v14.2</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ " + t['step1'], industries)
    st.markdown("---")
    st.markdown("### 📊 وضعیت اقتصادی لحظه‌ای")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("💰 دلار", f"{prices['dollar']:,}", delta=f"{((prices['dollar']-188500)/188500*100):.1f}%")
        st.metric("🏅 طلای ۱۸ عیار", f"{prices['gold_18']:,}")
    with col2:
        st.metric("🛢️ نفت", f"{prices['oil']} $")
        st.metric("📈 تورم", f"{prices['inflation']:.1f}%")
    st.caption(f"📡 {prices['source']} | ⏱️ {prices['date']}")
    st.markdown("---")
    فایل = st.file_uploader("📁 " + t['step2'], type=["csv", "xlsx", "xls"])
    st.markdown("---")
    st.markdown("### 🎖️ امتیاز شما")
    col1, col2 = st.sidebar.columns(2)
    with col1: st.metric("⭐", st.session_state.score)
    with col2: st.metric("🔥", f"{st.session_state.streak} روز")

# ==========================================
# 13. بارگذاری دیتا
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
# 14. هدر
# ==========================================
st.markdown(f"""
<div class="main-header">
    <h1><span class="highlight">iHo</span>Noor</h1>
    <p>{t['app_name']} | {t['subtitle']}</p>
    <div>
        <span class="dollar-badge">💰 دلار: {prices['dollar']:,} تومان</span>
        <span class="dollar-badge">🏅 طلای ۱۸ عیار: {prices['gold_18']:,}</span>
        <span class="dollar-badge">🛢️ نفت: {prices['oil']} $</span>
        <span class="source-badge">📡 {prices['source']}</span>
        <span class="source-badge">✨ v14.2</span>
        <span class="source-badge">⏱️ {prices['date']}</span>
    </div>
    <div style="font-size:0.6rem;color:rgba(255,255,255,0.2);margin-top:8px;">
        💡 قیمت‌ها هر ۵ دقیقه به‌روز میشوند
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="steps">
    <div class="step-item"><span class="num">۱</span><div class="text">{t['step1']}</div><div class="desc">از منوی کناری</div></div>
    <div class="step-item"><span class="num">۲</span><div class="text">{t['step2']}</div><div class="desc">Excel یا CSV</div></div>
    <div class="step-item"><span class="num">۳</span><div class="text">{t['step3']}</div><div class="desc">دریافت نتیجه</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 15. تب‌ها
# ==========================================
tab_colors = [
    ("📊 " + t['step3'], "#FF6B6B"),
    ("🛠️ " + t['industry_tools'], "#4ECDC4"),
    ("🔮 " + t['future'], "#45B7D1"),
    ("📊 " + t['economy'], "#96CEB4"),
    ("📖 راهنمای جامع", "#FFEAA7"),
    ("📘 بروشور علمی", "#DDA0DD"),
    ("💬 " + t['chatbot'], "#FF9F43"),
    ("🔐 " + t['admin'], "#F368E0"),
    ("📱 نصب", "#00D2D3"),
    ("📅 تقویم", "#54A0FF"),
    ("🤝 ارجاع", "#FF6B6B"),
    ("👤 داشبورد", "#C0C0C0"),
    ("🏠 خونه‌پرداز", "#4ECDC4"),
    ("📝 تماس", "#45B7D1")
]

tab_names = [t[0] for t in tab_colors]
tab_style = ""
for i, (name, color) in enumerate(tab_colors):
    tab_style += f"""
    .stTabs [data-baseweb="tab"]:nth-child({i+1}) {{ border-color: {color}44 !important; }}
    .stTabs [data-baseweb="tab"]:nth-child({i+1}):hover {{ background: {color}22 !important; border-color: {color} !important; color: {color} !important; }}
    .stTabs [data-baseweb="tab"]:nth-child({i+1})[aria-selected="true"] {{ background: {color} !important; color: white !important; border-color: {color} !important; box-shadow: 0 0 30px {color}44 !important; }}
    """
st.markdown(f"<style>{tab_style}</style>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs(tab_names)

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
    
    st.subheader("📅 بازه زمانی پیش‌بینی")
    forecast_days = st.selectbox(
        "چند روز آینده را پیش‌بینی کنید؟",
        [1, 3, 7, 14, 30],
        format_func=lambda x: f"{x} روز آینده" if x == 1 else f"{x} روز آینده"
    )
    st.caption(f"💡 پیش‌بینی برای {forecast_days} روز آینده انجام میشود.")
    
    if st.button(t['predict_btn'], type="primary", use_container_width=True):
        with st.spinner(f"⏳ در حال پیش‌بینی {forecast_days} روز آینده..."):
            start_time = time.time()
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
                    avg_row = X.mean().values.reshape(1, -1)
                    predictions = []
                    current_row = avg_row.copy()
                    
                    for day in range(forecast_days):
                        pred = model.predict(current_row)[0]
                        predictions.append(pred)
                        if len(X.columns) > 0:
                            current_row[0] = pred
                    
                    st.markdown(f"""
                    <div class="result-box">
                        <span class="result-emoji">📈</span>
                        <div class="result-label">پیش‌بینی {forecast_days} روز آینده</div>
                        <div class="result-number">{predictions[-1]:,.0f}</div>
                        <div class="result-label">{unit} (آخرین روز)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    last_date = data['تاریخ'].iloc[-1] if 'تاریخ' in data.columns else datetime.now()
                    if 'تاریخ' in data.columns:
                        future_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_days, freq='D')
                        future_dates_str = [d.strftime('%Y-%m-%d') for d in future_dates]
                    else:
                        future_dates_str = [f"روز {i+1}" for i in range(forecast_days)]
                    
                    pred_df = pd.DataFrame({
                        'تاریخ': future_dates_str,
                        f'پیش‌بینی {target}': [f"{p:,.0f} {unit}" for p in predictions]
                    })
                    st.dataframe(pred_df, use_container_width=True)
                    
                    st.subheader("📈 روند پیش‌بینی")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=future_dates_str,
                        y=predictions,
                        mode='lines+markers',
                        name=f'پیش‌بینی {target}',
                        line=dict(color='#FFD700', width=3),
                        marker=dict(size=10, color='#FFD700')
                    ))
                    fig.update_layout(
                        title=f'روند پیش‌بینی {target} در {forecast_days} روز آینده',
                        xaxis_title='تاریخ',
                        yaxis_title=unit,
                        height=400,
                        plot_bgcolor='rgba(255,255,255,0.02)',
                        paper_bgcolor='rgba(255,255,255,0.02)',
                        font=dict(color='rgba(255,255,255,0.8)')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.session_state.history.append({
                        'زمان': datetime.now().strftime("%H:%M"),
                        'هدف': target,
                        'بازه': f"{forecast_days} روز",
                        'پیش‌بینی اول': f"{predictions[0]:,.0f} {unit}",
                        'پیش‌بینی آخر': f"{predictions[-1]:,.0f} {unit}",
                        'دقت': f"{best_score:.1%}"
                    })
                    
                    st.success(f"✅ پیش‌بینی {forecast_days} روز آینده با موفقیت انجام شد! (زمان: {time.time()-start_time:.2f} ثانیه)")
                    
            except Exception as e:
                st.error(f"❌ خطا: {e}")

# ==========================================
# تب 2: ابزارهای تخصصی (کاملاً عملی)
# ==========================================
with tab2:
    st.markdown(f"""
    <div class="card" style="background:linear-gradient(135deg,rgba(78,205,196,0.02),rgba(78,205,196,0.01));border:1px solid rgba(78,205,196,0.03);">
        <div class="card-title" style="font-size:1.4rem;">
            <span class="icon">🛠️</span> ابزارهای تخصصی {صنف}
        </div>
        <p style="color:rgba(255,255,255,0.6);">
            <strong style="color:#4ECDC4;">۴ ابزار عملی</strong> برای مدیریت و تحلیل {صنف}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # ۱. خواربارفروشی
    # ==========================================
    if "خواربار" in صنف or "غذایی" in صنف:
        st.subheader("🛒 ابزارهای تخصصی خواربارفروشی")
        
        with st.expander("📦 ۱. مدیریت موجودی و پیش‌بینی نیاز", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("نام کالا", key="grocery_product", placeholder="برنج، روغن، شکر...")
                current_stock = st.number_input("موجودی فعلی (واحد)", min_value=0, step=10, key="grocery_stock", value=100)
            with col2:
                daily_usage = st.number_input("مصرف روزانه (واحد)", min_value=1, step=1, key="grocery_usage", value=10)
                safety_stock = st.number_input("موجودی امن (واحد)", min_value=0, step=5, key="grocery_safety", value=20)
            
            if st.button("📊 تحلیل موجودی", key="grocery_analyze"):
                if product_name:
                    days_left = (current_stock - safety_stock) // daily_usage if daily_usage > 0 else 0
                    reorder_point = safety_stock + (daily_usage * 3)
                    order_qty = (daily_usage * 7) + safety_stock - current_stock
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                        <h4 style="color:#FFD700;">📊 گزارش موجودی {product_name}</h4>
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">روز تا اتمام</p>
                                <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{days_left} روز</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">نقطه سفارش</p>
                                <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{reorder_point}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">مقدار سفارش</p>
                                <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{max(0, order_qty)}</p>
                            </div>
                        </div>
                        <div style="margin-top:10px;padding:10px;border-radius:8px;border-right:3px solid {'#4ECDC4' if current_stock > reorder_point else '#E53E3E'};background:rgba(255,255,255,0.02);">
                            <p style="color:rgba(255,255,255,0.7);font-size:0.9rem;">
                                {'✅ وضعیت موجودی مناسب است.' if current_stock > reorder_point else f'⚠️ هشدار: {order_qty} واحد {product_name} سفارش دهید.'}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with st.expander("📈 ۲. پیش‌بینی فروش روزانه"):
            col1, col2 = st.columns(2)
            with col1:
                last_7_days = st.text_area("فروش ۷ روز گذشته (با کاما جدا کنید)", "10,12,8,15,11,9,13", key="grocery_sales")
            with col2:
                day_of_week = st.selectbox("روز هفته", ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"])
            
            if st.button("📊 پیش‌بینی فروش", key="grocery_forecast"):
                sales_list = [int(x.strip()) for x in last_7_days.split(",") if x.strip()]
                if len(sales_list) == 7:
                    avg = sum(sales_list) / 7
                    max_sales = max(sales_list)
                    min_sales = min(sales_list)
                    day_multiplier = [0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 0.85]
                    day_index = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"].index(day_of_week)
                    prediction = avg * day_multiplier[day_index]
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                        <h4 style="color:#FFD700;">📊 پیش‌بینی فروش</h4>
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">میانگین فروش</p>
                                <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{avg:.0f}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">پیش‌بینی {day_of_week}</p>
                                <p style="color:#4ECDC4;font-size:1.3rem;font-weight:700;">{prediction:.0f}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">محدوده</p>
                                <p style="color:rgba(255,255,255,0.7);font-size:1rem;">{min_sales} - {max_sales}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with st.expander("🧺 ۳. تحلیل سبد خرید"):
            col1, col2 = st.columns(2)
            with col1:
                basket_size = st.number_input("تعداد اقلام در سبد", min_value=1, step=1, key="grocery_basket", value=5)
            with col2:
                avg_price = st.number_input("قیمت متوسط هر قلم (تومان)", min_value=1000, step=1000, key="grocery_price", value=15000)
            
            if st.button("📊 تحلیل سبد", key="grocery_basket_analyze"):
                total_basket = basket_size * avg_price
                discount = 0
                if basket_size > 10:
                    discount = 0.15
                elif basket_size > 5:
                    discount = 0.08
                final_price = total_basket * (1 - discount)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🧺 تحلیل سبد خرید</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">مبلغ کل</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{total_basket:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">تخفیف</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{discount*100:.0f}%</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت نهایی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{final_price:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with st.expander("🏷️ ۴. مدیریت تخفیف‌های هوشمند"):
            col1, col2 = st.columns(2)
            with col1:
                product_price = st.number_input("قیمت محصول (تومان)", min_value=1000, step=1000, key="grocery_product_price", value=50000)
            with col2:
                discount_percent = st.slider("درصد تخفیف", 0, 50, 10, key="grocery_discount")
            
            if st.button("📊 تحلیل تخفیف", key="grocery_discount_analyze"):
                discounted_price = product_price * (1 - discount_percent/100)
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🏷️ تحلیل تخفیف</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت پس از تخفیف</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{discounted_price:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">کاهش قیمت</p>
                            <p style="color:#4ECDC4;font-size:1.3rem;font-weight:700;">{product_price - discounted_price:,.0f}</p>
                        </div>
                    </div>
                    <div style="margin-top:10px;padding:10px;border-radius:8px;background:rgba(78,205,196,0.03);border-right:2px solid #4ECDC4;">
                        <p style="color:rgba(255,255,255,0.7);font-size:0.9rem;">
                            💡 پیشنهاد: برای افزایش فروش، تخفیف {discount_percent}% تا {discount_percent+10}% را امتحان کنید.
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # ۲. ساختمان و پیمانکاری
    # ==========================================
    elif "ساختمان" in صنف or "پیمانکاری" in صنف:
        st.subheader("🏗️ ابزارهای تخصصی ساختمان و پیمانکاری")
        
        with st.expander("📋 ۱. کنترل پروژه و زمان‌بندی", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                project_name = st.text_input("نام پروژه", key="const_project", placeholder="پروژه مسکونی...")
            with col2:
                area_m2 = st.number_input("متراژ (متر مربع)", min_value=10, step=10, key="const_area", value=100)
            with col3:
                workers_count = st.number_input("تعداد کارگر", min_value=1, step=1, key="const_workers", value=5)
            
            col1, col2 = st.columns(2)
            with col1:
                cost_per_m2 = st.number_input("هزینه هر متر مربع (تومان)", min_value=1_000_000, step=100_000, key="const_cost", value=5_000_000)
            with col2:
                duration_days = st.number_input("مدت زمان (روز)", min_value=7, step=7, key="const_duration", value=90)
            
            if st.button("📊 محاسبه پروژه", key="const_calc"):
                if project_name:
                    total_cost = area_m2 * cost_per_m2
                    daily_cost = total_cost / duration_days
                    workers_cost = workers_count * 500_000 * duration_days
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                        <h4 style="color:#FFD700;">📊 خلاصه پروژه {project_name}</h4>
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه کل</p>
                                <p style="color:#FFD700;font-size:1.1rem;font-weight:700;">{total_cost:,.0f}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه روزانه</p>
                                <p style="color:#FFD700;font-size:1.1rem;font-weight:700;">{daily_cost:,.0f}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه کارگر</p>
                                <p style="color:#FFD700;font-size:1.1rem;font-weight:700;">{workers_cost:,.0f}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with st.expander("💰 ۲. برآورد هزینه مصالح"):
            materials = {
                "سیمان (تن)": 1_500_000,
                "فولاد (تن)": 20_000_000,
                "آجر (هزار عدد)": 2_500_000,
                "شن و ماسه (تن)": 800_000,
                "بلوک (عدد)": 15_000
            }
            
            col1, col2 = st.columns(2)
            with col1:
                selected_material = st.selectbox("نوع مصالح", list(materials.keys()), key="const_material")
            with col2:
                quantity = st.number_input("مقدار", min_value=1, step=1, key="const_quantity", value=10)
            
            if st.button("📊 برآورد هزینه", key="const_cost_est"):
                unit_price = materials[selected_material]
                total = unit_price * quantity
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">💰 برآورد هزینه {selected_material}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت واحد</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{unit_price:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه کل</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{total:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📐 ۳. مدیریت متراژ و مساحت"):
            col1, col2 = st.columns(2)
            with col1:
                length = st.number_input("طول (متر)", min_value=1, step=1, key="const_length", value=10)
            with col2:
                width = st.number_input("عرض (متر)", min_value=1, step=1, key="const_width", value=8)
            
            if st.button("📐 محاسبه مساحت", key="const_area_calc"):
                area = length * width
                perimeter = 2 * (length + width)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📐 محاسبات متراژ</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">مساحت</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{area} متر مربع</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">محیط</p>
                            <p style="color:#4ECDC4;font-size:1.3rem;font-weight:700;">{perimeter} متر</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("👷 ۴. مدیریت نیروی کار"):
            col1, col2 = st.columns(2)
            with col1:
                total_workers = st.number_input("تعداد کل کارگران", min_value=1, step=1, key="const_total_workers", value=10)
            with col2:
                shift_hours = st.number_input("ساعت کاری روزانه", min_value=4, step=1, key="const_shift", value=8)
            
            if st.button("📊 تحلیل نیروی کار", key="const_workers_analyze"):
                weekly_hours = total_workers * shift_hours * 6
                monthly_hours = weekly_hours * 4
                total_cost = total_workers * 500_000 * 25  # ۵۰۰ هزار تومان حقوق روزانه
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">👷 تحلیل نیروی کار</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">ساعت کار هفتگی</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{weekly_hours}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">ساعت کار ماهانه</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{monthly_hours}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه ماهانه</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{total_cost:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # ۳. پوشاک
    # ==========================================
    elif "پوشاک" in صنف or "لباس" in صنف:
        st.subheader("👗 ابزارهای تخصصی پوشاک")
        
        with st.expander("🎨 ۱. تحلیل ترند و رنگ", expanded=True):
            colors = ["سفید", "مشکی", "آبی", "قرمز", "سبز", "طلایی", "نقره‌ای", "بنفش", "صورتی", "زرد"]
            col1, col2 = st.columns(2)
            with col1:
                selected_color = st.selectbox("رنگ مورد نظر", colors, key="fashion_color")
            with col2:
                season = st.selectbox("فصل", ["بهار", "تابستان", "پاییز", "زمستان"], key="fashion_season")
            
            if st.button("🔍 تحلیل ترند", key="fashion_trend"):
                popularity = np.random.randint(40, 95)
                trend = "صعودی" if popularity > 70 else "ثابت" if popularity > 50 else "نزولی"
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🎨 تحلیل رنگ {selected_color}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">محبوبیت</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{popularity}%</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">روند</p>
                            <p style="color:{"#38A169" if trend == "صعودی" else "#F5A623" if trend == "ثابت" else "#E53E3E"};font-size:1.3rem;font-weight:700;">{trend}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">فصل مناسب</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{season}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📏 ۲. مدیریت سایزها"):
            sizes = ["XS", "S", "M", "L", "XL", "XXL"]
            col1, col2 = st.columns(2)
            with col1:
                size = st.selectbox("سایز", sizes, key="fashion_size")
            with col2:
                stock_count = st.number_input("تعداد موجودی", min_value=0, step=1, key="fashion_stock", value=50)
            
            if st.button("📊 تحلیل سایز", key="fashion_size_analyze"):
                demand = np.random.randint(20, 80)
                status = "کافی" if stock_count > demand else "نیاز به افزایش"
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📏 تحلیل سایز {size}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">تقاضا</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{demand} واحد</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">وضعیت</p>
                            <p style="color:{"#38A169" if status == "کافی" else "#E53E3E"};font-size:1.3rem;font-weight:700;">{status}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("💰 ۳. تحلیل قیمت‌گذاری"):
            col1, col2 = st.columns(2)
            with col1:
                cost_price = st.number_input("قیمت تمام شده (تومان)", min_value=1000, step=1000, key="fashion_cost", value=100000)
            with col2:
                markup = st.slider("درصد سود", 10, 200, 50, key="fashion_markup")
            
            if st.button("📊 تحلیل قیمت", key="fashion_price_analyze"):
                selling_price = cost_price * (1 + markup/100)
                profit = selling_price - cost_price
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">💰 تحلیل قیمت‌گذاری</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت فروش</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{selling_price:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">سود هر واحد</p>
                            <p style="color:#4ECDC4;font-size:1.3rem;font-weight:700;">{profit:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📊 ۴. پیش‌بینی فروش فصلی"):
            col1, col2 = st.columns(2)
            with col1:
                last_season_sales = st.number_input("فروش فصل گذشته", min_value=0, step=1, key="fashion_last", value=1000)
            with col2:
                growth_rate = st.slider("نرخ رشد پیش‌بینی (%)", -20, 50, 10, key="fashion_growth")
            
            if st.button("📊 پیش‌بینی فروش", key="fashion_forecast"):
                next_season = last_season_sales * (1 + growth_rate/100)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📊 پیش‌بینی فروش فصل آینده</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">فروش پیش‌بینی</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{next_season:.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">تغییرات</p>
                            <p style="color:{"#38A169" if growth_rate > 0 else "#E53E3E"};font-size:1.3rem;font-weight:700;">{growth_rate:+.1f}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # ۴. خودرو و لوازم یدکی
    # ==========================================
    elif "خودرو" in صنف or "یدکی" in صنف:
        st.subheader("🚗 ابزارهای تخصصی خودرو و لوازم یدکی")
        
        with st.expander("🔩 ۱. مدیریت قطعات یدکی", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                part_name = st.text_input("نام قطعه", key="auto_part", placeholder="لنت ترمز، فیلتر روغن...")
            with col2:
                part_life = st.number_input("عمر مفید (کیلومتر)", min_value=1000, step=1000, key="auto_life", value=20000)
            
            col1, col2 = st.columns(2)
            with col1:
                current_km = st.number_input("کیلومتر فعلی", min_value=0, step=1000, key="auto_km", value=5000)
            with col2:
                part_price = st.number_input("قیمت قطعه (تومان)", min_value=1000, step=1000, key="auto_price", value=500000)
            
            if st.button("📊 تحلیل قطعه", key="auto_analyze"):
                if part_name:
                    remaining = max(0, part_life - current_km)
                    status = "مناسب" if remaining > 5000 else "نیاز به تعویض" if remaining > 1000 else "بحرانی"
                    cost_per_km = part_price / part_life
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                        <h4 style="color:#FFD700;">🔩 تحلیل قطعه {part_name}</h4>
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">کیلومتر باقیمانده</p>
                                <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{remaining:,}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">وضعیت</p>
                                <p style="color:{"#38A169" if status == "مناسب" else "#F5A623" if status == "نیاز به تعویض" else "#E53E3E"};font-size:1.2rem;font-weight:700;">{status}</p>
                            </div>
                            <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                                <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه هر کیلومتر</p>
                                <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{cost_per_km:.1f}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with st.expander("🛠️ ۲. مدیریت تعمیرات"):
            col1, col2 = st.columns(2)
            with col1:
                repair_type = st.selectbox("نوع تعمیر", ["دوره‌ای", "اضطراری", "بازسازی"], key="auto_repair_type")
            with col2:
                repair_cost = st.number_input("هزینه تعمیر (تومان)", min_value=1000, step=1000, key="auto_repair_cost", value=200000)
            
            if st.button("📊 تحلیل تعمیرات", key="auto_repair_analyze"):
                yearly_cost = repair_cost * 4  # ۴ تعمیر در سال
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🛠️ تحلیل هزینه تعمیرات</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه هر تعمیر</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{repair_cost:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه سالانه تعمیرات</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{yearly_cost:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📊 ۳. تحلیل قیمت روز"):
            car_models = ["پراید", "تیبا", "دنا", "شاهین", "تارا", "پژو ۲۰۶", "پژو ۲۰۷"]
            col1, col2 = st.columns(2)
            with col1:
                car_model = st.selectbox("مدل خودرو", car_models, key="auto_model")
            with col2:
                car_year = st.number_input("سال ساخت", min_value=1380, max_value=1404, step=1, key="auto_year", value=1400)
            
            if st.button("📊 تحلیل قیمت", key="auto_price_analyze"):
                base_price = {"پراید": 350_000_000, "تیبا": 450_000_000, "دنا": 650_000_000, 
                             "شاهین": 750_000_000, "تارا": 850_000_000, "پژو ۲۰۶": 500_000_000, "پژو ۲۰۷": 600_000_000}
                price = base_price.get(car_model, 500_000_000)
                depreciation = (1404 - car_year) * 15_000_000
                final_price = max(price - depreciation, price * 0.4)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📊 تحلیل قیمت {car_model}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت فعلی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{final_price:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">کاهش قیمت از سال ۱۴۰۴</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{depreciation:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("🔧 ۴. مدیریت خدمات پس از فروش"):
            col1, col2 = st.columns(2)
            with col1:
                service_type = st.selectbox("نوع خدمات", ["گارانتی", "تعویض روغن", "سیستم ترمز", "سیستم تعلیق"], key="auto_service")
            with col2:
                service_interval = st.number_input("دوره سرویس (کیلومتر)", min_value=1000, step=1000, key="auto_interval", value=10000)
            
            if st.button("📊 تحلیل خدمات", key="auto_service_analyze"):
                yearly_service = 20000 // service_interval
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🔧 تحلیل خدمات {service_type}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">دفعات سرویس در سال</p>
                            <p style="color:#FFD700;font-size:1.3rem;font-weight:700;">{yearly_service}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">کیلومتر بین سرویس‌ها</p>
                            <p style="color:#4ECDC4;font-size:1.3rem;font-weight:700;">{service_interval:,}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # ۵. فناوری و مخابرات
    # ==========================================
    elif "فناوری" in صنف or "مخابرات" in صنف:
        st.subheader("📱 ابزارهای تخصصی فناوری و مخابرات")
        
        with st.expander("👥 ۱. تحلیل رشد کاربران", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                current_users = st.number_input("کاربران فعلی", min_value=0, step=100, key="tech_users", value=1000)
            with col2:
                growth_rate = st.number_input("نرخ رشد ماهانه (%)", min_value=0.0, step=0.5, key="tech_growth", value=5.0)
            
            months = st.number_input("تعداد ماه‌های آینده", min_value=1, step=1, key="tech_months", value=12)
            
            if st.button("📊 پیش‌بینی رشد", key="tech_forecast"):
                projected = []
                for i in range(months + 1):
                    projected.append(current_users * ((1 + growth_rate / 100) ** i))
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📊 پیش‌بینی رشد کاربران</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">پس از ۱ ماه</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{projected[1]:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">پس از ۶ ماه</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{projected[6]:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">پس از {months} ماه</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{projected[-1]:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📊 ۲. تحلیل درآمد"):
            col1, col2 = st.columns(2)
            with col1:
                revenue_per_user = st.number_input("درآمد هر کاربر (تومان)", min_value=1000, step=1000, key="tech_revenue", value=50000)
            with col2:
                churn_rate = st.slider("نرخ ریزش کاربران (%)", 0, 20, 5, key="tech_churn")
            
            if st.button("📊 تحلیل درآمد", key="tech_revenue_analyze"):
                total_revenue = current_users * revenue_per_user
                lost_revenue = total_revenue * (churn_rate / 100)
                net_revenue = total_revenue - lost_revenue
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📊 تحلیل درآمد</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">درآمد کل</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{total_revenue:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">درآمد از دست رفته</p>
                            <p style="color:#E53E3E;font-size:1.2rem;font-weight:700;">{lost_revenue:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">درآمد خالص</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{net_revenue:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📲 ۳. مدیریت اشتراک‌ها"):
            plan_types = ["ماهانه", "سالانه", "شش ماهه"]
            col1, col2 = st.columns(2)
            with col1:
                plan = st.selectbox("نوع اشتراک", plan_types, key="tech_plan")
            with col2:
                plan_price = st.number_input("قیمت اشتراک (تومان)", min_value=1000, step=1000, key="tech_plan_price", value=100000)
            
            if st.button("📊 تحلیل اشتراک", key="tech_plan_analyze"):
                if plan == "ماهانه":
                    yearly = plan_price * 12
                    discount = 0
                elif plan == "سالانه":
                    yearly = plan_price
                    discount = 20
                else:
                    yearly = plan_price * 2
                    discount = 10
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📲 تحلیل اشتراک {plan}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">هزینه سالانه</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{yearly:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">تخفیف</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{discount}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("🌐 ۴. مدیریت پهنای باند"):
            col1, col2 = st.columns(2)
            with col1:
                bandwidth = st.number_input("پهنای باند فعلی (Mbps)", min_value=1, step=1, key="tech_bandwidth", value=100)
            with col2:
                users_count = st.number_input("تعداد کاربران", min_value=1, step=1, key="tech_users_count", value=1000)
            
            if st.button("📊 تحلیل پهنای باند", key="tech_bandwidth_analyze"):
                per_user = (bandwidth * 1024) / users_count
                status = "مناسب" if per_user > 1 else "نیاز به افزایش"
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🌐 تحلیل پهنای باند</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">پهنای باند هر کاربر</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{per_user:.2f} Kbps</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">وضعیت</p>
                            <p style="color:{"#38A169" if status == "مناسب" else "#E53E3E"};font-size:1.2rem;font-weight:700;">{status}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # ۶. املاک
    # ==========================================
    elif "املاک" in صنف or "مستغلات" in صنف:
        st.subheader("🏠 ابزارهای تخصصی املاک")
        
        with st.expander("🏠 ۱. برآورد قیمت ملک", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                area_estate = st.number_input("متراژ ملک", min_value=10, step=10, key="estate_area", value=80)
            with col2:
                room_count = st.number_input("تعداد اتاق", min_value=1, step=1, key="estate_rooms", value=2)
            
            col1, col2 = st.columns(2)
            with col1:
                year_built = st.number_input("سال ساخت", min_value=1360, step=1, key="estate_year", value=1400)
            with col2:
                location = st.selectbox("موقعیت", ["مرکزی", "شمال", "جنوب", "شرق", "غرب"], key="estate_location")
            
            if st.button("📊 برآورد قیمت", key="estate_price"):
                base_price = 20_000_000 * area_estate
                room_bonus = room_count * 50_000_000
                age_discount = (1404 - year_built) * 5_000_000
                location_bonus = {"مرکزی": 30_000_000, "شمال": 50_000_000, "جنوب": 0, "شرق": 15_000_000, "غرب": 10_000_000}
                estimated_price = base_price + room_bonus - age_discount + location_bonus.get(location, 0)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">🏠 برآورد قیمت ملک</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت نهایی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{estimated_price:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت هر متر</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{estimated_price / area_estate:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">موقعیت</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{location}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📊 ۲. تحلیل بازار اجاره"):
            col1, col2 = st.columns(2)
            with col1:
                rent_price = st.number_input("اجاره ماهانه (تومان)", min_value=100000, step=100000, key="estate_rent", value=5_000_000)
            with col2:
                deposit = st.number_input("رهن (تومان)", min_value=100000, step=100000, key="estate_deposit", value=50_000_000)
            
            if st.button("📊 تحلیل اجاره", key="estate_rent_analyze"):
                yearly_rent = rent_price * 12
                roi = (yearly_rent / deposit) * 100 if deposit > 0 else 0
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📊 تحلیل اجاره</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">اجاره سالانه</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{yearly_rent:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">بازدهی رهن</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{roi:.1f}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📈 ۳. پیش‌بینی قیمت منطقه"):
            regions = ["منطقه ۱", "منطقه ۲", "منطقه ۳", "منطقه ۴", "منطقه ۵"]
            col1, col2 = st.columns(2)
            with col1:
                region = st.selectbox("منطقه", regions, key="estate_region")
            with col2:
                current_price = st.number_input("قیمت فعلی هر متر (تومان)", min_value=1000, step=1000, key="estate_current_price", value=20_000_000)
            
            if st.button("📊 پیش‌بینی قیمت", key="estate_forecast"):
                growth = np.random.randint(5, 20)
                future_price = current_price * (1 + growth/100)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">📈 پیش‌بینی قیمت {region}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">قیمت پیش‌بینی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{future_price:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">رشد پیش‌بینی</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{growth}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("💰 ۴. مدیریت سرمایه‌گذاری"):
            col1, col2 = st.columns(2)
            with col1:
                investment = st.number_input("سرمایه اولیه (تومان)", min_value=100000, step=100000, key="estate_invest", value=500_000_000)
            with col2:
                years = st.number_input("مدت زمان (سال)", min_value=1, step=1, key="estate_years", value=5)
            
            if st.button("📊 تحلیل سرمایه‌گذاری", key="estate_invest_analyze"):
                roi = np.random.randint(15, 30)
                final_value = investment * ((1 + roi/100) ** years)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;">
                    <h4 style="color:#FFD700;">💰 تحلیل سرمایه‌گذاری</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">ارزش نهایی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{final_value:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.4);font-size:0.7rem;">بازدهی سالانه</p>
                            <p style="color:#4ECDC4;font-size:1.2rem;font-weight:700;">{roi}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # ۷. سایر صنف‌ها
    # ==========================================
    else:
        st.info(f"""
        📌 **ابزارهای تخصصی برای {صنف} در حال توسعه است.**
        
        اما میتوانید از ابزارهای زیر استفاده کنید:
        - 📊 تحلیل داده‌های خود در تب پیش‌بینی
        - 🔮 تحلیل اقتصادی در تب تحلیلگر آینده
        - 💬 سوالات خود را از چتبات بپرسید
        """)

# ==========================================
# تب 3: تحلیلگر آینده
# ==========================================
with tab3:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🔮</span> تحلیلگر هوشمند آینده iHoNoor</div>
        <p>تحلیل جامع اقتصادی، ژئوپولیتیک و تأثیر آن بر صنف شما</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 وضعیت اقتصادی لحظه‌ای")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 دلار", f"{prices['dollar']:,}", delta=f"{((prices['dollar']-188500)/188500*100):.1f}%")
    with col2: st.metric("🏅 طلای ۱۸ عیار", f"{prices['gold_18']:,}")
    with col3: st.metric("🛢️ نفت", f"{prices['oil']} $")
    with col4: st.metric("📈 تورم", f"{prices['inflation']:.1f}%")
    st.caption(f"📡 {prices['source']} | ⏱️ {prices['date']}")
    
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
            <span style="margin-right:10px;background:rgba(255,215,0,0.05);padding:2px 12px;border-radius:20px;font-size:0.75rem;">{analysis['dollar_prediction']}</span>
        </div>
        <p style="font-size:1.1rem;margin-top:10px;"><strong>روند:</strong> {analysis['trend']}</p>
        <p><strong>تأثیر بر صنف:</strong> {analysis['impact']}</p>
        <p><strong>تغییر قیمت پیش‌بینی شده:</strong> {analysis['price_change']:.1f}%</p>
        <p><strong>سطح ریسک:</strong> {analysis['risk_level']}</p>
        <div style="background:rgba(255,255,255,0.03);padding:12px;border-radius:10px;margin-top:10px;">
            <p style="margin:0;font-weight:600;color:#FFD700;">📌 پیام:</p>
            <p style="margin:4px 0;white-space:pre-line;">{analysis['message']}</p>
        </div>
        <div style="background:rgba(255,215,0,0.03);padding:12px;border-radius:10px;margin-top:10px;border-right:3px solid #FFD700;">
            <p style="margin:0;font-weight:600;color:#FFD700;">🚨 هشدار اختصاصی:</p>
            <p style="margin:4px 0;">{analysis['alert']}</p>
        </div>
        <div style="margin-top:10px;">
            <strong>🔹 راهکارهای پیشنهادی:</strong>
            <ul style="margin-top:5px;">{''.join([f'<li>{action}</li>' for action in analysis['actions']])}</ul>
        </div>
        <div style="margin-top:10px;background:rgba(78,205,196,0.05);padding:12px;border-radius:10px;border-right:3px solid #4ECDC4;">
            <strong style="color:#4ECDC4;">{analysis['opportunity']}</strong>
        </div>
        <div style="margin-top:10px;background:rgba(255,255,255,0.02);padding:12px;border-radius:10px;">
            <p style="margin:0;font-weight:600;color:#45B7D1;">🌍 تحلیل ژئوپولیتیک:</p>
            <p style="margin:4px 0;white-space:pre-line;font-size:0.85rem;">{analysis['geo_political']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 4: تحلیل اقتصادی
# ==========================================
with tab4:
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,rgba(69,183,209,0.02),rgba(69,183,209,0.01));border:1px solid rgba(69,183,209,0.03);">
        <div class="card-title" style="font-size:1.4rem;">
            <span class="icon">📊</span> تحلیل اقتصادی لحظه‌ای
        </div>
        <p style="color:rgba(255,255,255,0.6);">
            <strong style="color:#45B7D1;">وضعیت اقتصادی ایران و جهان</strong> بر اساس داده‌های لحظه‌ای
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;text-align:center;">
            <p style="font-size:1.5rem;margin:0;">💰</p>
            <p style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin:4px 0;">قیمت دلار آزاد</p>
            <p style="color:#FFD700;font-size:1.4rem;font-weight:700;margin:0;">{prices['dollar']:,}</p>
            <p style="color:rgba(255,255,255,0.3);font-size:0.65rem;">تومان</p>
        </div>
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;text-align:center;">
            <p style="font-size:1.5rem;margin:0;">🏅</p>
            <p style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin:4px 0;">طلای ۱۸ عیار</p>
            <p style="color:#FFD700;font-size:1.4rem;font-weight:700;margin:0;">{prices['gold_18']:,}</p>
            <p style="color:rgba(255,255,255,0.3);font-size:0.65rem;">تومان</p>
        </div>
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;text-align:center;">
            <p style="font-size:1.5rem;margin:0;">🛢️</p>
            <p style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin:4px 0;">قیمت نفت</p>
            <p style="color:#FFD700;font-size:1.4rem;font-weight:700;margin:0;">{prices['oil']}</p>
            <p style="color:rgba(255,255,255,0.3);font-size:0.65rem;">دلار هر بشکه</p>
        </div>
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:16px;text-align:center;">
            <p style="font-size:1.5rem;margin:0;">📈</p>
            <p style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin:4px 0;">نرخ تورم</p>
            <p style="color:#FFD700;font-size:1.4rem;font-weight:700;margin:0;">{prices['inflation']:.1f}%</p>
            <p style="color:rgba(255,255,255,0.3);font-size:0.65rem;">درصد سالانه</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 5: راهنمای جامع
# ==========================================
with tab5:
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,rgba(255,215,0,0.02),rgba(255,165,0,0.01));border:1px solid rgba(255,215,0,0.03);">
        <div class="card-title" style="font-size:1.4rem;">
            <span class="icon">📖</span> راهنمای جامع iHoNoor
        </div>
        <p style="color:rgba(255,255,255,0.6);">
            با <strong style="color:#FFD700;">۴ گام ساده</strong> از iHoNoor استفاده کنید.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-step">
        <h3>📌 گام ۱: صنف خود را انتخاب کنید</h3>
        <p>از منوی سمت راست، صنف خود را انتخاب کنید.</p>
        <div class="tip">💡 <strong>مثال:</strong> فروشگاه مواد غذایی → "خواربارفروشی"</div>
    </div>
    <div class="guide-step">
        <h3>📌 گام ۲: فایل خود را آپلود کنید</h3>
        <p>فایل Excel یا CSV خود را آپلود کنید.</p>
        <div class="warning">⚠️ فایل باید حداقل شامل ستون‌های "تاریخ" و یک ستون عددی باشد.</div>
        <div class="tip">💡 حداقل ۵۰ روز داده برای پیش‌بینی قابل اعتماد.</div>
    </div>
    <div class="guide-step">
        <h3>📌 گام ۳: ستون هدف را انتخاب کنید</h3>
        <p>ستونی که میخواهید پیش‌بینی کنید را انتخاب کنید.</p>
        <div class="success">✅ از گزینه <strong>"💡 پیشنهاد iHoNoor"</strong> استفاده کنید.</div>
    </div>
    <div class="guide-step">
        <h3>📌 گام ۴: پیش‌بینی را دریافت کنید</h3>
        <p>تعداد روزهای آینده را انتخاب کنید و روی <strong>"🚀 پیش‌بینی کن"</strong> کلیک کنید.</p>
        <div class="tip">📊 خروجی: جدول پیش‌بینی، نمودار روند و آمار</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 6: بروشور علمی
# ==========================================
with tab6:
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,rgba(0,200,150,0.02),rgba(0,200,150,0.01));border:1px solid rgba(0,200,150,0.03);">
        <div class="card-title" style="font-size:1.4rem;">
            <span class="icon">📘</span> بروشور علمی iHoNoor
        </div>
        <p style="color:rgba(255,255,255,0.6);">
            <strong style="color:#4ECDC4;">پیش‌بینی هوشمند فروش</strong> با استفاده از <strong style="color:#4ECDC4;">یادگیری ماشین</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:24px;padding:24px 28px;margin-bottom:16px;">
        <h3 style="color:#4ECDC4;">🧠 یادگیری ماشین چیست؟</h3>
        <p style="color:rgba(255,255,255,0.7);">
            <strong>یادگیری ماشین (Machine Learning)</strong> شاخه‌ای از هوش مصنوعی است که به کامپیوترها امکان میدهد 
            بدون برنامه‌ریزی مستقیم، از داده‌ها <strong>یاد بگیرند</strong> و <strong>الگوها</strong> را شناسایی کنند.
        </p>
        <div style="background:rgba(78,205,196,0.05);padding:12px 18px;border-radius:12px;border-right:3px solid #4ECDC4;margin-top:8px;">
            💡 iHoNoor مانند یک <strong>مشاور فروش هوشمند</strong> عمل میکند.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 7: چتبات
# ==========================================
with tab7:
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
    user_msg = st.text_input("✏️ سوال خود را بنویسید...", placeholder="مثلاً: ابزارهای تخصصی خواربارفروشی چیست؟")
    if st.button("📨 ارسال") and user_msg:
        st.session_state.chat_history.append({'role': 'user', 'content': user_msg})
        response = chatbot_response(user_msg, صنف, data, prices)
        st.session_state.chat_history.append({'role': 'bot', 'content': response})
        st.rerun()
    if st.button("🗑️ پاک کردن تاریخچه چت"):
        st.session_state.chat_history = []
        st.rerun()

# ==========================================
# تب 8: پنل مدیریت
# ==========================================
with tab8:
    if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False
    if not st.session_state.admin_logged_in:
        st.markdown("""
        <div style="text-align:center;padding:40px 0;">
            <h2 style="color:#FFD700;">🔐 ورود به پنل مدیریت</h2>
            <p style="color:rgba(255,255,255,0.3);">لطفاً اطلاعات خود را وارد کنید</p>
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
# تب 9: نصب
# ==========================================
with tab9:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📱</span> نصب روی گوشی</div>
        <p style="color:rgba(255,255,255,0.6);">در کروم: ⋮ → Add to Home screen</p>
        <p style="color:rgba(255,255,255,0.6);">در سافاری: اشتراک‌گذاری → Add to Home Screen</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 10: تقویم
# ==========================================
with tab10:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">📅</span> تقویم شمسی</div>', unsafe_allow_html=True)
    today = jdatetime.date.today()
    st.info(f"📌 امروز: {today.strftime('%A %d %B %Y')}")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 11: ارجاع
# ==========================================
with tab11:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">🤝</span> سیستم ارجاع</div>', unsafe_allow_html=True)
    code = f"iHN-{str(uuid.uuid4())[:8].upper()}"
    st.success(f"🔑 کد ارجاع شما: **{code}**")
    if st.button("📨 ثبت ارجاع"):
        st.session_state.score += 10
        st.success("✅ +۱۰ امتیاز!")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 12: داشبورد
# ==========================================
with tab12:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">👤</span> داشبورد</div>', unsafe_allow_html=True)
    st.metric("📊 تعداد رکوردها", len(data))
    st.metric("🏷️ صنف", صنف)
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history))
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 13: خونه‌پرداز
# ==========================================
with tab13:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">🏠</span> خونه‌پرداز</div>', unsafe_allow_html=True)
    st.info("💰 درآمد و هزینه‌های خود را مدیریت کنید.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 14: تماس
# ==========================================
with tab14:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">📝</span> تماس</div>', unsafe_allow_html=True)
    st.info("📬 ha2021alipur@gmail.com | 📱 09019470509")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# فوتر
# ==========================================
st.markdown(f"""
<div class="footer">
    ✨ iHoNoor v14.2 | {t['app_name']} | دلار: {prices['dollar']:,} تومان | 📡 {prices['source']} | ha2021alipur@gmail.com
</div>
""", unsafe_allow_html=True)خ
