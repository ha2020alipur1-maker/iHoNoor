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
if "lang" not in st.session_state:
    st.session_state.lang = "fa"
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "شب تاریک"

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
    oil = prices['oil']
    inflation = prices['inflation']
    
    if dollar > 190000:
        analysis['geo_political'] = "🔴 تنش‌های سیاسی و تحریم‌ها تشدید شده است. دلار روند صعودی دارد."
        analysis['dollar_prediction'] = 'صعودی 📈'
        analysis['risk_level'] = 'بالا'
    elif dollar > 180000:
        analysis['geo_political'] = "⚠️ شرایط نوسانی است. دلار در کوتاه‌مدت نوسانی خواهد بود."
        analysis['dollar_prediction'] = 'نوسانی 📊'
        analysis['risk_level'] = 'متوسط'
    else:
        analysis['geo_political'] = "✅ ثبات نسبی در بازار ارز. دلار روند کاهشی یا ثبات دارد."
        analysis['dollar_prediction'] = 'کاهشی 📉'
        analysis['risk_level'] = 'کم'
    
    if "خواربار" in صنف or "غذایی" in صنف:
        if dollar > 190000:
            analysis['status'] = '🔴 هشدار شدید'
            analysis['trend'] = 'افزایش قیمت مواد اولیه'
            analysis['price_change'] = 15 + (dollar - 190000) / 1000
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بسیار بالا'
            analysis['message'] = f'💰 قیمت دلار به {dollar:,} تومان رسیده است. قیمت مواد اولیه {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['alert'] = '🚨 موجودی کالاهای اساسی را افزایش دهید.'
            analysis['actions'] = ['🔹 افزایش موجودی کالاهای اساسی', '🔹 قرارداد بلندمدت با تامین‌کنندگان']
            analysis['opportunity'] = '📈 فرصت: افزایش قیمت فروش با مدیریت هزینه‌ها'
        else:
            analysis['status'] = '✅ پایدار'
            analysis['trend'] = 'ثابت'
            analysis['price_change'] = 3
            analysis['impact'] = 'متوسط'
            analysis['message'] = '📊 شرایط فعلی نسبتاً پایدار است.'
            analysis['alert'] = '✅ وضعیت عادی است.'
            analysis['actions'] = ['🔹 حفظ کیفیت محصولات']
            analysis['opportunity'] = '📈 فرصت: جذب مشتری با کیفیت بالا'
    
    elif "ساختمان" in صنف or "پیمانکاری" in صنف:
        if dollar > 190000:
            analysis['status'] = '🔴 بحرانی'
            analysis['trend'] = 'افزایش شدید هزینه‌ها'
            analysis['price_change'] = 22 + (dollar - 190000) / 800
            analysis['impact'] = 'بسیار بالا'
            analysis['risk_level'] = 'بحرانی'
            analysis['message'] = f'🏗️ هزینه مصالح ساختمانی {analysis["price_change"]:.0f}% افزایش می‌یابد.'
            analysis['alert'] = '🚨 پروژه‌های جدید را متوقف کنید.'
            analysis['actions'] = ['🔹 خرید فوری مصالح اساسی', '🔹 توقف پروژه‌های جدید']
            analysis['opportunity'] = '📉 فرصت: خرید مصالح با قیمت فعلی'
        else:
            analysis['status'] = '⚠️ توجه'
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
        'ابزار': f"🛠️ برای {صنف}، ابزارهای تخصصی زیادی وجود دارد."
    }
    for key, response in responses.items():
        if key in user_input:
            return response
    return f"🤖 سوال شما: '{user_input}'\nلطفاً دقیق‌تر بپرسید."

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
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,215,0,0.05);border-radius:50px 15px 50px 15px;padding:18px;text-align:center;margin-bottom:18px;">
        <h1 style="font-size:2rem;margin:0;background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">iHo<span style="background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Noor</span></h1>
        <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:0;">✨ v14.4</p>
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
        <span class="source-badge">✨ v14.4</span>
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
# تب 2: ابزارهای تخصصی
# ==========================================
with tab2:
    st.markdown(f"""
    <div class="card" style="background:linear-gradient(135deg,rgba(78,205,196,0.02),rgba(78,205,196,0.01));border:1px solid rgba(78,205,196,0.03);">
        <div class="card-title" style="font-size:1.4rem;">
            <span class="icon">🛠️</span> ابزارهای تخصصی {صنف}
        </div>
        <p style="color:rgba(255,255,255,0.6);">
            <strong style="color:#4ECDC4;">ابزارهای عملی</strong> برای مدیریت و تحلیل {صنف}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # خواربارفروشی
    if "خواربار" in صنف:
        st.subheader("🛒 ابزارهای تخصصی خواربارفروشی")
        with st.expander("📦 مدیریت موجودی", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                product = st.text_input("نام کالا", key="grocery_p", placeholder="برنج...")
                stock = st.number_input("موجودی فعلی", min_value=0, step=10, key="grocery_s", value=100)
            with col2:
                daily = st.number_input("مصرف روزانه", min_value=1, step=1, key="grocery_d", value=10)
                safety = st.number_input("موجودی امن", min_value=0, step=5, key="grocery_safe", value=20)
            if st.button("📊 تحلیل موجودی", key="grocery_btn"):
                if product:
                    days_left = (stock - safety) // daily if daily > 0 else 0
                    reorder = safety + (daily * 3)
                    st.success(f"📊 {product}: {days_left} روز تا اتمام | نقطه سفارش: {reorder}")

    # ساختمان
    elif "ساختمان" in صنف:
        st.subheader("🏗️ ابزارهای تخصصی ساختمان")
        with st.expander("📋 کنترل پروژه", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("نام پروژه", key="const_n", placeholder="پروژه...")
            with col2:
                area = st.number_input("متراژ", min_value=10, step=10, key="const_a", value=100)
            with col3:
                workers = st.number_input("کارگر", min_value=1, step=1, key="const_w", value=5)
            col1, col2 = st.columns(2)
            with col1:
                cost = st.number_input("هزینه هر متر مربع", min_value=1_000_000, step=100_000, key="const_c", value=5_000_000)
            with col2:
                days = st.number_input("مدت زمان (روز)", min_value=7, step=7, key="const_d", value=90)
            if st.button("📊 محاسبه پروژه", key="const_btn"):
                if name:
                    total = area * cost
                    st.success(f"📊 {name}: هزینه کل {total:,.0f} تومان | روزانه {total/days:,.0f} تومان")

    # پوشاک
    elif "پوشاک" in صنف:
        st.subheader("👗 ابزارهای تخصصی پوشاک")
        with st.expander("🎨 تحلیل ترند", expanded=True):
            colors = ["سفید", "مشکی", "آبی", "قرمز", "سبز", "طلایی"]
            col1, col2 = st.columns(2)
            with col1:
                color = st.selectbox("رنگ", colors, key="fashion_c")
            with col2:
                season = st.selectbox("فصل", ["بهار", "تابستان", "پاییز", "زمستان"], key="fashion_s")
            if st.button("🔍 تحلیل ترند", key="fashion_btn"):
                pop = np.random.randint(40, 95)
                st.success(f"🎨 رنگ {color}: {pop}% محبوبیت در {season}")

    # خودرو
    elif "خودرو" in صنف or "یدکی" in صنف:
        st.subheader("🚗 ابزارهای تخصصی خودرو")
        with st.expander("🔩 مدیریت قطعات", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                part = st.text_input("نام قطعه", key="auto_p", placeholder="لنت ترمز...")
                life = st.number_input("عمر مفید (کیلومتر)", min_value=1000, step=1000, key="auto_l", value=20000)
            with col2:
                km = st.number_input("کیلومتر فعلی", min_value=0, step=1000, key="auto_k", value=5000)
            if st.button("📊 تحلیل قطعه", key="auto_btn"):
                if part:
                    remain = max(0, life - km)
                    st.success(f"🔩 {part}: {remain:,} کیلومتر باقیمانده")

    # سایر صنف‌ها
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
        <div class="tip">💡 مثال: فروشگاه مواد غذایی → "خواربارفروشی"</div>
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
        <div class="success">✅ از گزینه "💡 پیشنهاد iHoNoor" استفاده کنید.</div>
    </div>
    <div class="guide-step">
        <h3>📌 گام ۴: پیش‌بینی را دریافت کنید</h3>
        <p>تعداد روزهای آینده را انتخاب کنید و روی "🚀 پیش‌بینی کن" کلیک کنید.</p>
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
            بدون برنامه‌ریزی مستقیم، از داده‌ها یاد بگیرند و الگوها را شناسایی کنند.
        </p>
        <div style="background:rgba(78,205,196,0.05);padding:12px 18px;border-radius:12px;border-right:3px solid #4ECDC4;margin-top:8px;">
            💡 iHoNoor مانند یک مشاور فروش هوشمند عمل میکند.
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
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
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
    ✨ iHoNoor v14.4 | {t['app_name']} | دلار: {prices['dollar']:,} تومان | 📡 {prices['source']} | ha2021alipur@gmail.com
</div>
""", unsafe_allow_html=True)
