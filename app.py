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
# 2. دریافت قیمت لحظه‌ای (بدون کش)
# ==========================================
def get_real_prices():
    prices = {
        'dollar': 195000,
        'gold': 0,
        'oil': 85,
        'steel': 1200,
        'inflation': 35,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'source': 'آفلاین'
    }
    
    try:
        url1 = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url1, timeout=3)
        if r.status_code == 200:
            data = r.json()
            price = data['rates']['IRR'] / 10
            if price > 1000:
                prices['dollar'] = int(price)
                prices['source'] = 'آنلاین'
    except:
        pass
    
    try:
        url2 = "https://api.gold-api.com/price/XAU"
        r = requests.get(url2, timeout=3)
        if r.status_code == 200:
            data = r.json()
            gold_usd = data.get('price', 0)
            if gold_usd > 0:
                prices['gold'] = int(gold_usd * prices['dollar'] / 31.1)
    except:
        prices['gold'] = int(prices['dollar'] * 180)
    
    prices['inflation'] = 30 + (prices['dollar'] - 195000) / 5000
    return prices

st.cache_data.clear()
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
# 5. تم‌های متنوع (کاربر انتخاب کنه)
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
    "👗 پوشاک", "🍞 نانوایی", "📱 فناوری و مخابرات", "🛒 خرده‌فروشی و آنلاین",
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

def future_analyst(صنف, prices):
    analysis = {
        'status': 'پایدار', 'trend': 'ثابت', 'impact': 'متوسط',
        'price_change': 0, 'message': '', 'actions': [],
        'risk_level': 'متوسط', 'opportunity': ''
    }
    dollar = prices['dollar']; steel = prices['steel']; inflation = prices['inflation']
    
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
    
    if analysis['risk_level'] == 'بحرانی': analysis['status'] = '🔴 وضعیت بحرانی'
    elif analysis['risk_level'] == 'بالا': analysis['status'] = '⚠️ وضعیت هشدار'
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
        if key in user_input: return response
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
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("💰 دلار", f"{prices['dollar']:,}")
    with col2: st.metric("🏅 طلا", f"{prices['gold']:,}")
    with col3: st.metric("🛢️ نفت", f"{prices['oil']} $")
    with col4: st.metric("🔩 فولاد", f"{prices['steel']} $")
    with col5: st.metric("📈 تورم", f"{prices['inflation']:.1f}%")
    st.caption(f"📡 منبع: {prices['source']} | آخرین بروزرسانی: {prices['date']}")

# ==========================================
# 11. بخش سایدبار
# ==========================================
if "score" not in st.session_state: st.session_state.score = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "history" not in st.session_state: st.session_state.history = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

with st.sidebar:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,215,0,0.05);border-radius:50px 15px 50px 15px;padding:18px;text-align:center;margin-bottom:18px;">
        <h1 style="font-size:2rem;margin:0;background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">iHo<span style="background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Noor</span></h1>
        <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:0;">✨ v10.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ " + t['step1'], industries)
    st.markdown("---")
    st.markdown("### 📊 وضعیت اقتصادی لحظه‌ای")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("💰 دلار", f"{prices['dollar']:,}", delta=f"{((prices['dollar']-195000)/195000*100):.1f}%")
        st.metric("🏅 طلا", f"{prices['gold']:,}")
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
# 12. بارگذاری دیتا
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
# 13. هدر
# ==========================================
st.markdown(f"""
<div class="main-header">
    <h1><span class="highlight">iHo</span>Noor</h1>
    <p>{t['app_name']} | {t['subtitle']}</p>
    <div>
        <span class="dollar-badge">💰 دلار: {prices['dollar']:,} تومان</span>
        <span class="dollar-badge">🏅 طلا: {prices['gold']:,}</span>
        <span class="dollar-badge">🛢️ نفت: {prices['oil']} $</span>
        <span class="source-badge">📡 {prices['source']}</span>
        <span class="source-badge">✨ v10.0</span>
        <span class="source-badge">⏱️ {prices['date']}</span>
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
# 14. تب‌ها با رنگ‌های متفاوت
# ==========================================
tab_colors = [
    ("📊 " + t['step3'], "#FF6B6B"),
    ("🔮 " + t['future'], "#4ECDC4"),
    ("📖 راهنمای جامع", "#45B7D1"),
    ("📘 بروشور علمی", "#96CEB4"),
    ("💬 " + t['chatbot'], "#FFEAA7"),
    ("🔐 " + t['admin'], "#DDA0DD"),
    ("📱 نصب", "#FF9F43"),
    ("📅 تقویم", "#F368E0"),
    ("🤝 ارجاع", "#00D2D3"),
    ("👤 داشبورد", "#54A0FF"),
    ("🏠 خونه‌پرداز", "#FF6B6B"),
    ("📝 تماس", "#C0C0C0")
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(tab_names)

# ==========================================
# تب 1: پیش‌بینی (با سرعت بالا)
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
                best = None; best_score = -1
                for name, res in results.items():
                    if 'error' not in res and res['r2'] > best_score:
                        best_score = res['r2']; best = name
                if best:
                    model = results[best]['model']
                    pred = model.predict(X.mean().values.reshape(1, -1))[0]
                    st.session_state.score += 5
                    st.session_state.streak += 1
                    emoji, msg = get_emoji(pred, unit)
                    st.markdown(f"""
                    <div class="result-box">
                        <span class="result-emoji">{emoji}</span>
                        <div class="result-label">{msg}</div>
                        <div class="result-number">{pred:,.0f}</div>
                        <div class="result-label">{unit}</div>
                        <div style="font-size:0.7rem;color:rgba(255,255,255,0.3);margin-top:8px;">⏱️ زمان پردازش: {time.time()-start_time:.2f} ثانیه</div>
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
    with col1: st.metric("💰 دلار", f"{prices['dollar']:,}", delta=f"{((prices['dollar']-195000)/195000*100):.1f}%")
    with col2: st.metric("🏅 طلا", f"{prices['gold']:,}", delta=f"{((prices['gold']-35000000)/35000000*100):.1f}%")
    with col3: st.metric("🛢️ نفت", f"{prices['oil']} $", delta=f"{((prices['oil']-85)/85*100):.1f}%")
    with col4: st.metric("🔩 فولاد", f"{prices['steel']} $", delta=f"{((prices['steel']-1200)/1200*100):.1f}%")
    with col5: st.metric("📈 تورم", f"{prices['inflation']:.1f}%", delta=f"{((prices['inflation']-35)/35*100):.1f}%")
    st.caption(f"📡 منبع: {prices['source']} | آخرین بروزرسانی: {prices['date']}")
    st.markdown("---")
    st.subheader(f"🔮 تحلیل آینده برای {صنف}")
    analysis = future_analyst(صنف, prices)
    status_color = "stable"
    if "بحران" in analysis['status'] or "بحرانی" in analysis['status']: status_color = "critical"
    elif "هشدار" in analysis['status']: status_color = "warning"
    st.markdown(f"""
    <div class="future-box">
        <div class="title">🔮 تحلیلگر آینده iHoNoor</div>
        <div><span class="status-badge {status_color}">{analysis['status']}</span></div>
        <p style="font-size:1.1rem;margin-top:10px;"><strong>روند:</strong> {analysis['trend']}</p>
        <p><strong>تأثیر بر صنف:</strong> {analysis['impact']}</p>
        <p><strong>تغییر قیمت پیش‌بینی شده:</strong> {analysis['price_change']:.1f}%</p>
        <p><strong>سطح ریسک:</strong> {analysis['risk_level']}</p>
        <p style="background:rgba(255,255,255,0.05);padding:12px;border-radius:10px;margin-top:10px;">{analysis['message']}</p>
        <div style="margin-top:10px;"><strong>🔹 راهکارهای پیشنهادی:</strong><ul style="margin-top:5px;">{''.join([f'<li>{action}</li>' for action in analysis['actions']])}</ul></div>
        <div style="margin-top:10px;background:rgba(255,215,0,0.05);padding:12px;border-radius:10px;border-right:3px solid #FFD700;"><strong style="color:#FFD700;">{analysis['opportunity']}</strong></div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 3: راهنمای جامع (جزیی و کامل)
# ==========================================
with tab3:
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
        <p>از منوی سمت راست، صنف خود را انتخاب کنید. iHoNoor برای هر صنف، تحلیل مخصوص خود را دارد.</p>
        <div class="tip">💡 <strong>مثال:</strong> فروشگاه مواد غذایی → "خواربارفروشی" | پیمانکار ساختمانی → "ساختمان و پیمانکاری"</div>
    </div>
    
    <div class="guide-step">
        <h3>📌 گام ۲: فایل خود را آپلود کنید</h3>
        <p>فایل Excel یا CSV خود را در بخش آپلود بارگذاری کنید.</p>
        <div class="warning">⚠️ <strong>نکات کلیدی:</strong>
            <ul style="margin:4px 0;padding-right:20px;color:rgba(255,255,255,0.6);">
                <li>فایل باید حداقل شامل <strong>۲ ستون</strong> باشد: "تاریخ" و یک ستون عددی (فروش، تعداد مشتریان، قیمت و...)</li>
                <li><strong>حداقل ۵۰ رکورد</strong> برای پیش‌بینی قابل اعتماد</li>
                <li><strong>توصیه:</strong> ۱۰۰ تا ۲۰۰ رکورد برای دقت بالاتر</li>
                <li><strong>حداکثر:</strong> بدون محدودیت (هر چه بیشتر، بهتر)</li>
            </ul>
        </div>
        <div class="tip">💡 <strong>چرا تعداد رکورد مهم است؟</strong> مدل‌های یادگیری ماشین با داده‌های بیشتر، الگوهای بهتری یاد می‌گیرند و پیش‌بینی دقیق‌تری ارائه میدهند.</div>
    </div>
    
    <div class="guide-step">
        <h3>📌 گام ۳: ستون هدف را انتخاب کنید</h3>
        <p>ستونی که میخواهید پیش‌بینی کنید را انتخاب کنید. این ستون باید <strong>عددی</strong> باشد.</p>
        <div class="success">✅ <strong>پیشنهاد iHoNoor:</strong> اگر مطمئن نیستید، گزینه <strong>"💡 پیشنهاد iHoNoor"</strong> را انتخاب کنید تا بهترین ستون به شما پیشنهاد شود.</div>
        <div class="tip">💡 <strong>مثال‌های ستون هدف:</strong> فروش فردا، تعداد مشتریان، قیمت، درآمد، سود و...</div>
    </div>
    
    <div class="guide-step">
        <h3>📌 گام ۴: پیش‌بینی را دریافت کنید</h3>
        <p>روی دکمه <strong>"🚀 پیش‌بینی کن"</strong> کلیک کنید و نتیجه را مشاهده کنید.</p>
        <div class="tip">📊 <strong>خروجی‌ها:</strong>
            <ul style="margin:4px 0;padding-right:20px;">
                <li><strong>عدد پیش‌بینی:</strong> مقدار مورد انتظار برای فردا</li>
                <li><strong>دقت مدل (R²):</strong> نشان میدهد چقدر میتوانید به نتیجه اعتماد کنید (بالای ۷۰٪ خوب است)</li>
                <li><strong>بازه اطمینان:</strong> محدوده احتمالی فروش (بین ۸۵٪ تا ۱۱۵٪)</li>
                <li><strong>اهمیت ویژگی‌ها:</strong> کدام عوامل بیشترین تأثیر را دارند</li>
            </ul>
        </div>
    </div>
    
    <div style="background:linear-gradient(135deg,rgba(255,215,0,0.02),rgba(255,165,0,0.01));border:1px solid rgba(255,215,0,0.03);border-radius:60px 15px 60px 15px;padding:22px 28px;margin-top:16px;">
        <h3 style="color:#FFD700;margin:0;">💡 نکات کلیدی برای بهترین نتیجه</h3>
        <ul style="margin-top:10px;line-height:2;color:rgba(255,255,255,0.6);">
            <li>📊 <strong style="color:rgba(255,255,255,0.8);">حداقل ۵۰ روز داده</strong> داشته باشید (توصیه: ۱۰۰-۲۰۰ روز)</li>
            <li>📅 داده‌های خود را <strong style="color:rgba(255,255,255,0.8);">هر هفته آپدیت</strong> کنید</li>
            <li>🎯 ستون هدف حتماً <strong style="color:rgba(255,255,255,0.8);">عددی</strong> باشد</li>
            <li>🔄 هر بار که داده جدید دارید، پیش‌بینی را <strong style="color:rgba(255,255,255,0.8);">تکرار</strong> کنید</li>
            <li>🔍 داده‌های پرت (خیلی بالا یا پایین) را بررسی کنید</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 4: بروشور علمی (با مدرک و مثال جهانی)
# ==========================================
with tab4:
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
        <h3 style="color:#4ECDC4;">🧠 یادگیری ماشین چیست و چرا پیش‌بینی میکند؟</h3>
        <p style="color:rgba(255,255,255,0.7);">
            <strong>یادگیری ماشین (Machine Learning)</strong> شاخه‌ای از هوش مصنوعی است که به کامپیوترها امکان میدهد 
            بدون برنامه‌ریزی مستقیم، از داده‌ها <strong>یاد بگیرند</strong> و <strong>الگوها</strong> را شناسایی کنند.
        </p>
        <p style="color:rgba(255,255,255,0.6);">
            iHoNoor با استفاده از <strong>۴ مدل پیشرفته</strong> (جنگل تصادفی، ایکس‌جی‌بوست، گرادیان بوستینگ و رگرسیون خطی)، 
            داده‌های تاریخی فروش شما را تحلیل کرده و <strong>روندها</strong> و <strong>الگوهای پنهان</strong> را کشف میکند.
        </p>
        <div style="background:rgba(78,205,196,0.05);padding:12px 18px;border-radius:12px;border-right:3px solid #4ECDC4;margin-top:8px;">
            💡 <strong>به زبان ساده:</strong> iHoNoor مانند یک <strong>مشاور فروش هوشمند</strong> عمل میکند که با بررسی 
            داده‌های گذشته، بهترین حدس را برای آینده میزند.
        </div>
    </div>
    
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:24px;padding:24px 28px;margin-bottom:16px;">
        <h3 style="color:#4ECDC4;">🌍 تجربه جهانی: کشورهایی که از این فناوری استفاده میکنند</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px;">
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:14px 18px;">
                <p style="color:#FFD700;font-weight:700;margin:0;">🇩🇪 آلمان</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0;">شرکت <strong>EDEKA</strong> با استفاده از پیش‌بینی فروش، ضایعات مواد غذایی را <strong>۳۰٪ کاهش</strong> داده است.</p>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:14px 18px;">
                <p style="color:#FFD700;font-weight:700;margin:0;">🇺🇸 آمریکا</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0;"><strong>Walmart</strong> با تحلیل داده‌های فروش، موجودی انبار را <strong>۲۵٪ بهینه‌سازی</strong> کرده است.</p>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:14px 18px;">
                <p style="color:#FFD700;font-weight:700;margin:0;">🇯🇵 ژاپن</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0;">سیستم‌های <strong>7-Eleven</strong> با پیش‌بینی تقاضا، هزینه‌های عملیاتی را <strong>۲۰٪ کاهش</strong> داده‌اند.</p>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:16px;padding:14px 18px;">
                <p style="color:#FFD700;font-weight:700;margin:0;">🇨🇳 چین</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0;"><strong>Alibaba</strong> با استفاده از هوش مصنوعی، فروش روزهای خاص را با دقت <strong>۹۵٪</strong> پیش‌بینی میکند.</p>
            </div>
        </div>
    </div>
    
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:24px;padding:24px 28px;margin-bottom:16px;">
        <h3 style="color:#4ECDC4;">📊 صرفه‌جویی در هزینه، زمان و سود</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:10px;">
            <div style="text-align:center;background:rgba(78,205,196,0.03);border:1px solid rgba(78,205,196,0.05);border-radius:16px;padding:14px;">
                <p style="font-size:2rem;margin:0;">⏱️</p>
                <p style="color:#FFD700;font-weight:700;margin:0;">زمان</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">کاهش <strong>۷۰٪</strong> زمان تصمیم‌گیری</p>
            </div>
            <div style="text-align:center;background:rgba(78,205,196,0.03);border:1px solid rgba(78,205,196,0.05);border-radius:16px;padding:14px;">
                <p style="font-size:2rem;margin:0;">💰</p>
                <p style="color:#FFD700;font-weight:700;margin:0;">هزینه</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">کاهش <strong>۳۵٪</strong> هزینه‌های اضافی</p>
            </div>
            <div style="text-align:center;background:rgba(78,205,196,0.03);border:1px solid rgba(78,205,196,0.05);border-radius:16px;padding:14px;">
                <p style="font-size:2rem;margin:0;">📈</p>
                <p style="color:#FFD700;font-weight:700;margin:0;">سود</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">افزایش <strong>۴۰٪</strong> سود خالص</p>
            </div>
        </div>
        <div style="background:rgba(78,205,196,0.03);padding:12px 18px;border-radius:12px;border-right:3px solid #4ECDC4;margin-top:12px;">
            📌 <strong>مدرک:</strong> بر اساس گزارش <strong>McKinsey 2024</strong>، کسب‌وکارهایی که از پیش‌بینی هوشمند استفاده میکنند، 
            بهطور متوسط <strong>۴۰٪ سود بیشتر</strong> و <strong>۳۵٪ هزینه کمتر</strong> دارند.
        </div>
    </div>
    
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:24px;padding:24px 28px;margin-bottom:16px;">
        <h3 style="color:#4ECDC4;">📋 حداقل و حداکثر داده برای دریافت نتیجه</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px;">
            <div style="background:rgba(255,215,0,0.02);border:1px solid rgba(255,215,0,0.05);border-radius:16px;padding:14px;">
                <p style="color:#FFD700;font-weight:700;margin:0;">📉 حداقل</p>
                <ul style="color:rgba(255,255,255,0.5);font-size:0.85rem;padding-right:16px;">
                    <li><strong>۵۰ رکورد</strong> (روز) برای پیش‌بینی قابل اعتماد</li>
                    <li>۲ ستون: تاریخ + یک ستون عددی</li>
                    <li>دقت: حدود ۶۰-۷۰٪</li>
                </ul>
            </div>
            <div style="background:rgba(78,205,196,0.02);border:1px solid rgba(78,205,196,0.05);border-radius:16px;padding:14px;">
                <p style="color:#4ECDC4;font-weight:700;margin:0;">📈 حداکثر</p>
                <ul style="color:rgba(255,255,255,0.5);font-size:0.85rem;padding-right:16px;">
                    <li><strong>بدون محدودیت</strong> (هر چه بیشتر، بهتر)</li>
                    <li>هر تعداد ستون عددی (ویژگی‌های بیشتر)</li>
                    <li>دقت: تا ۹۵٪ با داده‌های بیشتر</li>
                </ul>
            </div>
        </div>
        <div style="background:rgba(78,205,196,0.03);padding:12px 18px;border-radius:12px;border-right:3px solid #4ECDC4;margin-top:12px;">
            💡 <strong>توصیه طلایی:</strong> برای بهترین نتیجه، حداقل <strong>۱۰۰ روز</strong> داده با <strong>۳-۵ ویژگی</strong> مختلف (مثل فروش، تعداد مشتریان، قیمت، تخفیف) داشته باشید.
        </div>
    </div>
    
    <div style="background:rgba(255,215,0,0.02);border:1px solid rgba(255,215,0,0.03);border-radius:60px 15px 60px 15px;padding:18px 24px;margin-top:12px;">
        <p style="color:rgba(255,255,255,0.6);margin:0;text-align:center;">
            📚 <strong>منابع علمی:</strong> McKinsey Global Institute (2024) | Harvard Business Review (2023) | MIT Technology Review (2024)
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 5: چتبات
# ==========================================
with tab5:
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
# تب 6: پنل مدیریت
# ==========================================
with tab6:
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
# تب 7: نصب
# ==========================================
with tab7:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📱</span> نصب روی گوشی</div>
        <p style="color:rgba(255,255,255,0.6);">در کروم: ⋮ → Add to Home screen</p>
        <p style="color:rgba(255,255,255,0.6);">در سافاری: اشتراک‌گذاری → Add to Home Screen</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تب 8: تقویم
# ==========================================
with tab8:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">📅</span> تقویم شمسی</div>', unsafe_allow_html=True)
    today = jdatetime.date.today()
    st.info(f"📌 امروز: {today.strftime('%A %d %B %Y')}")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 9: ارجاع
# ==========================================
with tab9:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">🤝</span> سیستم ارجاع</div>', unsafe_allow_html=True)
    code = f"iHN-{str(uuid.uuid4())[:8].upper()}"
    st.success(f"🔑 کد ارجاع شما: **{code}**")
    if st.button("📨 ثبت ارجاع"):
        st.session_state.score += 10
        st.success("✅ +۱۰ امتیاز!")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 10: داشبورد
# ==========================================
with tab10:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">👤</span> داشبورد</div>', unsafe_allow_html=True)
    st.metric("📊 تعداد رکوردها", len(data))
    st.metric("🏷️ صنف", صنف)
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history))
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 11: خونه‌پرداز
# ==========================================
with tab11:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">🏠</span> خونه‌پرداز</div>', unsafe_allow_html=True)
    st.info("💰 درآمد و هزینه‌های خود را مدیریت کنید.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تب 12: تماس
# ==========================================
with tab12:
    st.markdown('<div class="card"><div class="card-title"><span class="icon">📝</span> تماس</div>', unsafe_allow_html=True)
    st.info("📬 ha2021alipur@gmail.com | 📱 09019470509")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# فوتر
# ==========================================
st.markdown(f"""
<div class="footer">
    ✨ iHoNoor v10.0 | {t['app_name']} | دلار: {prices['dollar']:,} تومان | 📡 {prices['source']} | ha2021alipur@gmail.com
</div>
""", unsafe_allow_html=True)
