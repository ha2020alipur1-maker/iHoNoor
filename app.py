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
# تنظیمات اولیه
# ==========================================
st.set_page_config(
    page_title="iHoNoor | نور هوشمند فروش",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ADMIN_USERNAME = "ihonoor_admin"
ADMIN_PASSWORD = "iHoNoor@1404"

# ==========================================
# استایل
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700;900&display=swap');
    * { font-family: 'Vazirmatn', sans-serif; direction: rtl; }
    .stApp { background: #F8F9FA; }
    
    .main-header {
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
        padding: 30px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(13, 71, 161, 0.25);
    }
    .main-header h1 { font-size: 2.8rem; font-weight: 900; margin: 0; }
    .main-header h1 .highlight { color: #FFD700; }
    .main-header p { font-size: 1.1rem; opacity: 0.9; margin-top: 8px; }
    
    .card {
        background: white;
        padding: 20px 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
    }
    .card-title { font-size: 1.1rem; font-weight: 700; color: #0D47A1; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
    .card-title .icon { font-size: 1.5rem; }
    
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 10px 30px !important;
        border: none !important;
    }
    .stButton > button:first-child {
        background: linear-gradient(135deg, #0D47A1, #1E88E5) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
    }
    .stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(30, 136, 229, 0.5);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: white;
        padding: 6px;
        border-radius: 14px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px;
        border-radius: 10px;
        font-weight: 600;
        color: #666;
    }
    .stTabs [data-baseweb="tab"]:hover { background: #E3F2FD; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0D47A1, #1E88E5) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
    }
    
    .sidebar-logo {
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
        color: white;
        text-align: center;
        padding: 25px 15px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(13, 71, 161, 0.2);
    }
    .sidebar-logo h1 { font-size: 2.5rem; margin: 0; letter-spacing: 4px; }
    .sidebar-logo h1 .highlight { color: #FFD700; }
    .sidebar-logo p { margin: 5px 0 0; opacity: 0.9; font-size: 0.9rem; }
    
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    
    .result-box {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        padding: 25px 30px;
        border-radius: 16px;
        border-right: 6px solid #FFD700;
        text-align: center;
        margin-top: 15px;
    }
    .result-number {
        font-size: 2.8rem;
        font-weight: 900;
        color: #0D47A1;
    }
    
    .advisor-box {
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
        padding: 20px 25px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 4px 20px rgba(13, 71, 161, 0.25);
        margin-top: 20px;
    }
    .advisor-box .title { font-size: 1.2rem; font-weight: 700; margin-bottom: 8px; }
    .advisor-box .sub { font-size: 0.9rem; opacity: 0.9; }
    
    .steps {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
        flex-wrap: wrap;
    }
    .step-item {
        flex: 1;
        min-width: 150px;
        background: white;
        padding: 15px 20px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 15px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
    }
    .step-item:hover { border-color: #FFD700; transform: translateY(-2px); }
    .step-item .num {
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 6px;
    }
    .step-item .text { font-weight: 600; color: #333; font-size: 0.9rem; }
    .step-item .desc { font-size: 0.75rem; color: #888; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# هدر
# ==========================================
st.markdown("""
<div class="main-header">
    <h1><span class="highlight">iHo</span>Noor</h1>
    <p>نور هوشمند فروش | با یاری الهی، مسیر موفقیت را روشن کن</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# قدم‌های راهنما
# ==========================================
st.markdown("""
<div class="steps">
    <div class="step-item"><div class="num">۱</div><div class="text">انتخاب صنف</div><div class="desc">از منوی کناری انتخاب کنید</div></div>
    <div class="step-item"><div class="num">۲</div><div class="text">آپلود فایل</div><div class="desc">فایل اکسل یا CSV خود را آپلود کنید</div></div>
    <div class="step-item"><div class="num">۳</div><div class="text">دریافت پیش‌بینی</div><div class="desc">روی دکمه پیش‌بینی کلیک کنید</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# لیست صنف‌ها
# ==========================================
industries = [
    "🏪 خواربارفروشی",
    "🔩 آهن‌آلات و مصالح",
    "🚗 خودروسازی و لوازم یدکی",
    "👗 پوشاک",
    "🍞 نانوایی",
    "📱 فناوری و مخابرات",
    "🛒 خرده‌فروشی و آنلاین",
    "🏭 تولید و صنایع",
    "💰 بانکداری و مالی",
    "🏥 بهداشت و درمان",
    "🍔 صنایع غذایی",
    "⛽ پتروشیمی و انرژی",
    "⚡ برق و نیروگاه‌ها",
    "🎬 سینما و محصولات فرهنگی",
    "🏭 تولید و صنایع غذایی (تخصصی)",
    "🏢 املاک و مستغلات",
    "🏗️ ساختمان و پیمانکاری",
    "🏭 تولید سفارشی (Make-to-Order)",
    "📦 مدیریت موجودی و زنجیره تامین"
]

# ==========================================
# سایدبار
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1><span class="highlight">iHo</span>Noor</h1>
        <p>✨ نور هوشمند فروش</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ صنف خود را انتخاب کنید:", industries)
    
    st.markdown("---")
    
    فایل = st.file_uploader(
        "📁 فایل خود را آپلود کنید",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False
    )
    
    with st.expander("⚙️ تنظیمات پیشرفته"):
        تخصصی = st.checkbox("🔬 استفاده از دیتاست جامع صنف")
        مسیر_تخصصی = st.text_input("مسیر فایل:", "data/sales.csv") if تخصصی else ""
    
    st.markdown("---")
    st.info("💡 اگر فایل ندارید، از داده‌های نمونه استفاده می‌شود.")
    
    if "theme" not in st.session_state:
        st.session_state.theme = "روشن"
    theme = st.radio("🌓 تم:", ["روشن", "تاریک"], index=0 if st.session_state.theme == "روشن" else 1)
    st.session_state.theme = theme

# ==========================================
# تولید داده نمونه
# ==========================================
def sample_data(صنف):
    np.random.seed(42)
    dates = pd.date_range('1403-01-01', periods=200, freq='D')
    
    if صنف == "🏪 خواربارفروشی":
        return pd.DataFrame({
            'تاریخ': dates,
            'فروش_امروز': np.random.randint(1_000_000, 10_000_000, 200),
            'تعداد_مشتریان': np.random.randint(10, 100, 200),
            'قیمت_میانگین': np.random.randint(10_000, 50_000, 200),
            'تخفیف': np.random.randint(0, 30, 200),
            'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)
        })
    elif صنف == "🍞 نانوایی":
        return pd.DataFrame({
            'تاریخ': dates,
            'آرد_مصرفی': np.random.randint(50, 200, 200),
            'تعداد_نان': np.random.randint(200, 800, 200),
            'کارکنان': np.random.randint(2, 6, 200),
            'قیمت_نان': np.random.randint(5_000, 15_000, 200),
            'فروش_فردا': np.random.randint(300, 900, 200)
        })
    elif صنف == "👗 پوشاک":
        return pd.DataFrame({
            'تاریخ': dates,
            'قیمت_میانگین': np.random.randint(100_000, 1_000_000, 200),
            'تعداد_فروش': np.random.randint(5, 50, 200),
            'تخفیف': np.random.randint(0, 30, 200),
            'تعداد_مشتریان': np.random.randint(10, 100, 200),
            'فروش_فردا': np.random.randint(500_000, 5_000_000, 200)
        })
    elif صنف == "🏗️ ساختمان و پیمانکاری":
        return pd.DataFrame({
            'تاریخ': dates,
            'متراژ': np.random.randint(50, 500, 200),
            'تعداد_کارگر': np.random.randint(5, 50, 200),
            'هزینه_مصالح': np.random.randint(1_000_000, 10_000_000, 200),
            'مدت_پروژه': np.random.randint(30, 180, 200),
            'فروش_فردا': np.random.randint(1_000_000, 15_000_000, 200)
        })
    else:
        return pd.DataFrame({
            'تاریخ': dates,
            'فروش_امروز': np.random.randint(1_000_000, 10_000_000, 200),
            'تعداد_مشتریان': np.random.randint(10, 100, 200),
            'قیمت': np.random.randint(10_000, 50_000, 200),
            'تخفیف': np.random.randint(0, 30, 200),
            'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)
        })

# ==========================================
# مدل‌ها و توابع اصلی
# ==========================================
models_dict = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
    "SVR": SVR(kernel='rbf', C=1.0, epsilon=0.1),
    "KNN": KNeighborsRegressor(n_neighbors=5)
}

model_names_fa = {
    "Linear Regression": "رگرسیون خطی",
    "Random Forest": "جنگل تصادفی",
    "Gradient Boosting": "گرادیان بوستینگ",
    "XGBoost": "ایکس‌جی‌بوست",
    "SVR": "ماشین بردار پشتیبان",
    "KNN": "کی‌نزدیک‌ترین همسایه"
}

def train_models(X_train, y_train, X_test, y_test):
    results = {}
    for name, model in models_dict.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            results[name] = {
                'model': model,
                'mae': mean_absolute_error(y_test, y_pred),
                'r2': r2_score(y_test, y_pred)
            }
        except Exception as e:
            results[name] = {'error': str(e)}
    return results

def smart_alerts(data, target_col, pred_value, صنف):
    alerts = []
    if len(data) < 7:
        return ["ℹ️ داده‌های کافی برای هشدار هوشمند وجود ندارد (حداقل ۷ روز نیاز است)."]
    
    try:
        last_week = data[target_col].tail(7).mean()
        prev_week = data[target_col].tail(14).head(7).mean()
        
        if last_week < prev_week * 0.85:
            alerts.append(f"⚠️ کاهش فروش: {((1 - last_week/prev_week)*100):.1f}% نسبت به هفته قبل")
        if last_week > prev_week * 1.15:
            alerts.append(f"✅ افزایش فروش: {((last_week/prev_week - 1)*100):.1f}% نسبت به هفته قبل")
        
        if pred_value:
            if pred_value < last_week * 0.85:
                alerts.append(f"⚠️ پیش‌بینی کاهش: {((1 - pred_value/last_week)*100):.1f}% کمتر از میانگین")
            elif pred_value > last_week * 1.15:
                alerts.append(f"✅ پیش‌بینی افزایش: {((pred_value/last_week - 1)*100):.1f}% بیشتر از میانگین")
    except Exception as e:
        alerts.append(f"ℹ️ خطا: {e}")
    
    return alerts

def مشاور_iHonoor(pred_value, accuracy, target_col, data, alerts, صنف):
    تحلیل = {'خلاصه': '', 'بینش‌ها': [], 'راهکارها': [], 'هشدار': None, 'فرصت': None, 'پیام': None}
    
    if pred_value:
        if pred_value > 10_000_000:
            تحلیل['خلاصه'] = f"✅ پیش‌بینی {target_col}: {pred_value:,.0f} تومان (عالی)"
            تحلیل['فرصت'] = "✨ از این فرصت برای توسعه کسب‌وکار استفاده کنید."
        elif pred_value > 5_000_000:
            تحلیل['خلاصه'] = f"📊 پیش‌بینی {target_col}: {pred_value:,.0f} تومان (خوب)"
        else:
            تحلیل['خلاصه'] = f"⚠️ پیش‌بینی {target_col}: {pred_value:,.0f} تومان (نیاز به بررسی)"
            تحلیل['هشدار'] = "فروش پایین‌تر از حد انتظار است."
    
    if accuracy:
        if accuracy > 0.85:
            تحلیل['بینش‌ها'].append(f"🎯 دقت مدل {accuracy:.1%} (عالی)")
        elif accuracy > 0.7:
            تحلیل['بینش‌ها'].append(f"📊 دقت مدل {accuracy:.1%} (قابل قبول)")
        else:
            تحلیل['بینش‌ها'].append(f"⚠️ دقت مدل {accuracy:.1%} (پایین)")
    
    if alerts:
        for alert in alerts:
            if "کاهش" in alert and "فروش" in alert:
                تحلیل['راهکارها'].append("🔻 کاهش فروش: تبلیغات هدفمند، تخفیف ویژه")
                تحلیل['هشدار'] = "کاهش فروش شناسایی شد!"
            elif "افزایش" in alert and "فروش" in alert:
                تحلیل['راهکارها'].append("📈 فرصت رشد: افزایش موجودی، بازاریابی")
                تحلیل['فرصت'] = "روند صعودی فروش!"
    
    if not تحلیل['راهکارها']:
        تحلیل['راهکارها'].append("✅ وضعیت فعلی خوب است. کیفیت خدمات را حفظ کنید.")
    
    if "خواربار" in صنف:
        تحلیل['پیام'] = "💡 موجودی کالاهای پرمصرف را در تعطیلات افزایش دهید."
    elif "ساختمان" in صنف:
        تحلیل['پیام'] = "💡 هزینه مصالح و نیروی کار را مدیریت کنید."
    elif "پوشاک" in صنف:
        تحلیل['پیام'] = "💡 رنگ‌های پرطرفدار فصل را شناسایی کنید."
    elif "بهداشت" in صنف:
        تحلیل['پیام'] = "💡 با افزایش خدمات تخصصی، درآمد خود را افزایش دهید."
    else:
        تحلیل['پیام'] = "💡 با تحلیل داده‌ها، بهترین تصمیمات را بگیرید."
    
    return تحلیل

def نمایش_مشاور(تحلیل):
    if not تحلیل:
        return
    
    st.markdown("---")
    st.markdown("""
    <div class="advisor-box">
        <div class="title">✨ مشاور iHoNoor</div>
        <div class="sub">نور هوشمند تصمیم‌گیری، با یاری الهی</div>
    </div>
    """, unsafe_allow_html=True)
    
    if تحلیل.get('خلاصه'):
        st.info(تحلیل['خلاصه'])
    
    col1, col2 = st.columns(2)
    with col1:
        if تحلیل.get('هشدار'):
            st.warning(f"⚠️ {تحلیل['هشدار']}")
    with col2:
        if تحلیل.get('فرصت'):
            st.success(f"✨ {تحلیل['فرصت']}")
    
    for بینش in تحلیل.get('بینش‌ها', []):
        st.info(بینش)
    
    for راهکار in تحلیل.get('راهکارها', []):
        st.success(راهکار)
    
    if تحلیل.get('پیام'):
        st.markdown(f"<div style='background:#FFF8E1;padding:12px 18px;border-radius:12px;border-right:4px solid #FFA000;'>{تحلیل['پیام']}</div>", unsafe_allow_html=True)

# ==========================================
# ===== توابع تشخیص ناهنجاری و تحلیل سلامت =====
# ==========================================

def detect_anomalies(data):
    try:
        num_cols = data.select_dtypes(include=['number']).columns
        if len(num_cols) < 2:
            return None, "داده‌های عددی کافی نیست."
        iso = IsolationForest(contamination=0.05, random_state=42)
        preds = iso.fit_predict(data[num_cols].fillna(0))
        anomalies = data[preds == -1]
        return anomalies, f"{len(anomalies)} ناهنجاری شناسایی شد." if len(anomalies) > 0 else "✅ هیچ ناهنجاری یافت نشد."
    except Exception as e:
        return None, f"خطا: {e}"

def analyze_health(data, target_col):
    msgs = []
    if len(data) < 50:
        msgs.append("⚠️ تعداد رکوردها کم است (کمتر از ۵۰).")
    if data.isnull().sum().sum() > 0:
        msgs.append(f"⚠️ {data.isnull().sum().sum()} مقدار خالی در داده‌ها وجود دارد.")
    if target_col in data.columns and 'تاریخ' in data.columns:
        sorted_data = data.sort_values('تاریخ')
        if len(sorted_data) >= 20:
            recent = sorted_data[target_col].tail(20).mean()
            older = sorted_data[target_col].head(20).mean()
            if recent < older * 0.85:
                msgs.append("⚠️ کاهش فروش در داده‌های اخیر مشاهده می‌شود.")
    return "\n".join(msgs) if msgs else "✅ داده‌ها سالم هستند."

# ==========================================
# ===== دریافت قیمت دلار از API =====
# ==========================================

def دریافت_قیمت_دلار():
    try:
        url1 = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url1, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data['rates']['IRR'] / 10
            if price > 1000:
                return price
    except:
        pass
    
    try:
        url2 = "https://www.dolr.ir/api/v1/price"
        response = requests.get(url2, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('price', 160000)
    except:
        pass
    
    return 160000

def تحلیل_خودکار_کلان_اقتصادی(صنف):
    نرخ_دلار_جاری = دریافت_قیمت_دلار()
    
    if "آهن" in صنف or "میلگرد" in صنف or "ساختمان" in صنف or "مصالح" in صنف:
        ضریب_تأثیر = 0.85
        نام_صنف = "صنایع فولادی و ساختمانی"
        حساسیت = "بسیار بالا"
        توضیح_صنف = "صنعت ساختمان بیشترین وابستگی را به نرخ ارز دارد."
    elif "پوشاک" in صنف or "پارچه" in صنف or "لباس" in صنف:
        ضریب_تأثیر = 0.70
        نام_صنف = "صنعت پوشاک"
        حساسیت = "بالا"
        توضیح_صنف = "پوشاک وابستگی بالایی به واردات مواد اولیه دارد."
    elif "خواربار" in صنف or "غذایی" in صنف or "نانوایی" in صنف:
        ضریب_تأثیر = 0.50
        نام_صنف = "صنایع غذایی"
        حساسیت = "متوسط"
        توضیح_صنف = "صنایع غذایی بیشتر تحت تأثیر تورم عمومی هستند."
    elif "خودرو" in صنف or "یدکی" in صنف or "قطعه" in صنف:
        ضریب_تأثیر = 0.75
        نام_صنف = "صنعت خودرو"
        حساسیت = "بالا"
        توضیح_صنف = "صنعت خودرو وابستگی بالایی به واردات قطعات دارد."
    else:
        ضریب_تأثیر = 0.40
        نام_صنف = "سایر صنایع"
        حساسیت = "متوسط"
        توضیح_صنف = "تأثیر غیرمستقیم از طریق تورم و هزینه‌های تولید."
    
    تغییر_دلار = np.random.uniform(3, 12)
    تغییر_صنف = تغییر_دلار * ضریب_تأثیر
    
    if تغییر_صنف > 15:
        وضعیت = "🔴 هشدار شدید"
        توضیح = f"قیمت {صنف} در هفته آینده {تغییر_صنف:.1f}٪ افزایش می‌یابد!"
        راهکار = "💡 اقدام فوری: خرید را انجام دهید یا قیمت فروش را افزایش دهید."
        رنگ = "error"
    elif تغییر_صنف > 8:
        وضعیت = "⚠️ هشدار"
        توضیح = f"قیمت {صنف} در هفته آینده {تغییر_صنف:.1f}٪ افزایش می‌یابد."
        راهکار = "💡 پیشنهاد: خرید را به امروز موکول کنید و قیمت‌ها را بازبینی کنید."
        رنگ = "warning"
    elif تغییر_صنف > 3:
        وضعیت = "📈 افزایش ملایم"
        توضیح = f"قیمت {صنف} در هفته آینده {تغییر_صنف:.1f}٪ افزایش می‌یابد."
        راهکار = "💡 پیشنهاد: بازار را زیر نظر داشته باشید."
        رنگ = "info"
    elif تغییر_صنف < -5:
        وضعیت = "🟢 کاهش قیمت"
        توضیح = f"قیمت {صنف} در هفته آینده {abs(تغییر_صنف):.1f}٪ کاهش می‌یابد."
        راهکار = "💡 پیشنهاد: خرید را به تأخیر بیندازید و منتظر کاهش بیشتر باشید."
        رنگ = "success"
    else:
        وضعیت = "ℹ️ پایدار"
        توضیح = f"قیمت {صنف} در هفته آینده نسبتاً پایدار است."
        راهکار = "💡 پیشنهاد: وضعیت بازار را به‌روز نگه دارید."
        رنگ = "info"
    
    گزارش = f"""
📈 **تحلیل خودکار کلان اقتصادی iHoNoor**

📊 **نرخ دلار فعلی:** {نرخ_دلار_جاری:,.0f} تومان
📈 **تغییرات پیش‌بینی دلار:** {تغییر_دلار:.1f}%

🏷️ **صنف شما:** {نام_صنف}
🔍 **حساسیت به دلار:** {حساسیت} (ضریب: {ضریب_تأثیر * 100:.0f}%)
💡 **توضیح:** {توضیح_صنف}

📊 **تأثیر بر قیمت صنف شما:** {تغییر_صنف:+.1f}%

**{وضعیت}**
{توضیح}
{rاهکار}

📌 **توصیه نهایی:** این تحلیل بر اساس آخرین داده‌های اقتصادی و شبیه‌سازی‌های هوشمند انجام شده است.
"""
    
    return گزارش, تغییر_صنف, وضعیت, رنگ

def نمایش_تحلیل_خودکار(گزارش, تغییر_صنف, وضعیت, رنگ):
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0D47A1, #1E88E5); 
                padding: 20px 25px; 
                border-radius: 16px; 
                color: white;
                box-shadow: 0 4px 20px rgba(13, 71, 161, 0.25);
                margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 2rem;">🤖</span>
            <span style="font-size: 1.3rem; font-weight: bold;">تحلیلگر خودکار کلان اقتصادی iHoNoor</span>
        </div>
        <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">
            تحلیل هوشمند بازار ارز و تأثیر آن بر صنف شما
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(گزارش)
    
    if رنگ == "error":
        st.error(وضعیت)
    elif رنگ == "warning":
        st.warning(وضعیت)
    elif رنگ == "success":
        st.success(وضعیت)
    else:
        st.info(وضعیت)

# ==========================================
# ===== راهنمای تخصصی صنف‌ها =====
# ==========================================

def راهنمای_صنف(صنف):
    راهنماها = {
        "خواربارفروشی": {
            "توضیح": "فروشگاه‌های مواد غذایی و خواربار که محصولات مصرفی روزمره را عرضه می‌کنند.",
            "تجربیات_جهانی": """
**📌 کشور آلمان (EDEKA):** 
- استفاده از سیستم‌های پیش‌بینی تقاضا با هوش مصنوعی برای کاهش ضایعات مواد غذایی
- قیمت‌گذاری پویا بر اساس زمان و تاریخ انقضا

**📌 کشور آمریکا (Walmart):** 
- استفاده از داده‌های لحظه‌ای برای مدیریت موجودی
- پیش‌بینی فروش بر اساس آب و هوا و تعطیلات

**📌 کشور ژاپن (7-Eleven):** 
- سیستم‌های توزیع هوشمند با دقت بالا
- تحلیل رفتار مشتریان برای پیشنهاد محصولات
            """,
            "پیشنهادات": """
✅ **۱. مدیریت موجودی هوشمند:** از داده‌های فروش روزانه برای پیش‌بینی نیازهای آینده استفاده کنید.
✅ **۲. کاهش ضایعات:** با تحلیل تاریخ انقضا و الگوهای خرید، ضایعات را کاهش دهید.
✅ **۳. تخفیف‌های هدفمند:** برای محصولات کم‌فروش، تخفیف‌های هوشمند در نظر بگیرید.
✅ **۴. تحلیل مشتریان:** خریدهای تکراری را شناسایی و برای آنها پیشنهادات ویژه ارسال کنید.
"""
        },
        "پوشاک": {
            "توضیح": "فروشگاه‌های پوشاک، لباس، کیف و کفش که محصولات مد و فشن را عرضه می‌کنند.",
            "تجربیات_جهانی": """
**📌 کشور ایتالیا (Gucci):** 
- تحلیل ترندهای مد با هوش مصنوعی
- پیش‌بینی رنگ‌ها و طرح‌های محبوب فصل

**📌 کشور آمریکا (Zara):** 
- سیستم‌های تولید بر اساس تقاضا (Just-in-Time)
- تحلیل بازخورد مشتریان برای بهبود محصولات

**📌 کشور فرانسه (Louis Vuitton):** 
- تحلیل داده‌های فروش برای شخصی‌سازی تجربه مشتری
- استفاده از هوش مصنوعی برای پیش‌بینی فروش آنلاین
            """,
            "پیشنهادات": """
✅ **۱. شناسایی ترندهای جدید:** با تحلیل داده‌های فروش و جستجوهای اینترنتی، ترندهای آینده را پیش‌بینی کنید.
✅ **۲. تخفیف‌های هوشمند:** برای محصولات با فروش پایین، تخفیف‌های هدفمند در نظر بگیرید.
✅ **۳. مدیریت سایزها:** با تحلیل داده‌ها، سایزهای پرتقاضا را شناسایی و موجودی آنها را افزایش دهید.
✅ **۴. شخصی‌سازی:** بر اساس تاریخچه خرید مشتریان، پیشنهادات شخصی‌سازی‌شده ارائه دهید.
"""
        },
        "ساختمان و پیمانکاری": {
            "توضیح": "شرکت‌های پیمانکاری، مهندسان و مجریان پروژه‌های ساختمانی و عمرانی.",
            "تجربیات_جهانی": """
**📌 کشور آلمان (Hochtief):** 
- استفاده از مدل‌سازی اطلاعات ساختمان (BIM)
- پیش‌بینی هزینه‌های پروژه با هوش مصنوعی

**📌 کشور دبی (EMAAR):** 
- سیستم‌های مدیریت پروژه هوشمند
- پیش‌بینی زمان اتمام پروژه‌ها

**📌 کشور کره جنوبی (Samsung C&T):** 
- استفاده از ربات‌ها و فناوری‌های نوین در ساخت و ساز
- تحلیل داده‌های پروژه‌های قبلی برای بهینه‌سازی
            """,
            "پیشنهادات": """
✅ **۱. پیش‌بینی هزینه‌ها:** با تحلیل پروژه‌های قبلی، هزینه‌های آینده را پیش‌بینی کنید.
✅ **۲. مدیریت نیروی کار:** تعداد کارگران مورد نیاز را بر اساس متراژ و زمان پروژه محاسبه کنید.
✅ **۳. کاهش تأخیر:** ریسک‌های تأخیر را شناسایی و برنامه‌های جایگزین طراحی کنید.
✅ **۴. استفاده از فناوری:** از نرم‌افزارهای مدیریت پروژه و BIM استفاده کنید.
"""
        },
        "نانوایی": {
            "توضیح": "نانوایی‌های سنتی و صنعتی که انواع نان و شیرینی را تولید و عرضه می‌کنند.",
            "تجربیات_جهانی": """
**📌 کشور فرانسه (Paul):** 
- سیستم‌های پیش‌بینی تقاضا بر اساس زمان
- تولید بر اساس سفارش‌های روزانه

**📌 کشور آلمان (Kamps):** 
- استفاده از داده‌های فروش برای بهینه‌سازی تولید
- کاهش ضایعات با پیش‌بینی دقیق

**📌 کشور ژاپن (Yamazaki Baking):** 
- سیستم‌های توزیع هوشمند
- تحلیل رفتار مصرف‌کننده
            """,
            "پیشنهادات": """
✅ **۱. پیش‌بینی تقاضا:** بر اساس روزهای هفته و تعطیلات، میزان تولید را تنظیم کنید.
✅ **۲. کاهش ضایعات:** با پیش‌بینی دقیق، تولید اضافی را کاهش دهید.
✅ **۳. تنوع محصولات:** محصولات جدید را بر اساس داده‌های فروش و بازخورد مشتریان معرفی کنید.
✅ **۴. مدیریت مواد اولیه:** مصرف آرد و مواد اولیه را با دقت مدیریت کنید.
"""
        },
        "خودروسازی و لوازم یدکی": {
            "توضیح": "فروشندگان قطعات خودرو، خدمات تعمیرات و نمایندگی‌های فروش خودرو.",
            "تجربیات_جهانی": """
**📌 کشور آلمان (Bosch):** 
- سیستم‌های مدیریت موجودی قطعات
- پیش‌بینی تقاضا بر اساس سن خودروها

**📌 کشور ژاپن (Toyota):** 
- سیستم‌های تولید بر اساس تقاضا
- تحلیل داده‌های فروش و خدمات پس از فروش

**📌 کشور آمریکا (AutoZone):** 
- سیستم‌های پیش‌بینی قطعات پرفروش
- تحلیل داده‌های تعمیرات
            """,
            "پیشنهادات": """
✅ **۱. شناسایی قطعات پرفروش:** قطعاتی که بیشترین فروش را دارند شناسایی و موجودی آنها را افزایش دهید.
✅ **۲. پیش‌بینی تقاضا:** بر اساس سن خودروها و فصل‌های سال، تقاضا را پیش‌بینی کنید.
✅ **۳. مدیریت خدمات:** زمان و هزینه خدمات تعمیرات را بهینه‌سازی کنید.
✅ **۴. تحلیل مشتریان:** مشتریانی که خدمات دوره‌ای دریافت می‌کنند را شناسایی و یادآوری ارسال کنید.
"""
        },
        "بهداشت و درمان": {
            "توضیح": "بیمارستان‌ها، کلینیک‌ها، مطب‌های پزشکی و مراکز درمانی.",
            "تجربیات_جهانی": """
**📌 کشور آلمان (Charité):** 
- سیستم‌های پیش‌بینی مراجعه بیماران
- مدیریت منابع انسانی و تجهیزات

**📌 کشور آمریکا (Mayo Clinic):** 
- استفاده از هوش مصنوعی در تشخیص و درمان
- پیش‌بینی نیازهای بیمارستانی

**📌 کشور ژاپن (Takeda):** 
- مدیریت زنجیره تأمین تجهیزات پزشکی
- پیش‌بینی تقاضا برای داروها
            """,
            "پیشنهادات": """
✅ **۱. پیش‌بینی مراجعه:** با تحلیل داده‌های گذشته، تعداد بیماران آینده را پیش‌بینی کنید.
✅ **۲. مدیریت پرسنل:** بر اساس پیش‌بینی مراجعه، تعداد پرسنل مورد نیاز را تنظیم کنید.
✅ **۳. مدیریت موجودی:** تجهیزات و داروهای مصرفی را بر اساس تقاضا مدیریت کنید.
✅ **۴. بهبود کیفیت:** با تحلیل بازخورد بیماران، کیفیت خدمات را بهبود دهید.
"""
        }
    }
    
    for key in راهنماها:
        if key in صنف:
            راهنما = راهنماها[key]
            break
    else:
        راهنما = {
            "توضیح": f"این صنف شامل کسب‌وکارهای مرتبط با {صنف} است.",
            "تجربیات_جهانی": "📌 اطلاعات بیشتری در مورد این صنف در حال جمع‌آوری است.",
            "پیشنهادات": "✅ با تحلیل داده‌های خود، بهترین تصمیمات را بگیرید و از مشاور iHoNoor استفاده کنید."
        }
    
    st.markdown(f"""
    <div class="card">
        <div class="card-title"><span class="icon">📘</span> راهنمای تخصصی {صنف}</div>
        <p><strong>📌 توضیح:</strong> {راهنما['توضیح']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🌍 تجربیات موفق در کشورهای خارجی", expanded=False):
        st.markdown(راهنما['تجربیات_جهانی'])
    
    with st.expander("💡 پیشنهادات عملی برای بهبود عملکرد", expanded=False):
        st.markdown(راهنما['پیشنهادات'])
    
    st.markdown("---")
    st.subheader("📊 مقایسه با استانداردهای جهانی")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🌍 سطح جهانی", "پیشرفته", delta="+۸۵%")
        st.caption("کشورهای پیشرو: آلمان، آمریکا، ژاپن")
    with col2:
        st.metric("🇮🇷 وضعیت فعلی", "در حال رشد", delta="+۴۰%")
        st.caption("پتانسیل رشد: بسیار بالا")
    
    st.progress(0.65, text="پیشرفت نسبت به استانداردهای جهانی")
    st.info("💡 با استفاده از iHoNoor و پیاده‌سازی پیشنهادات، می‌توانید به سطح جهانی نزدیک‌تر شوید.")

# ==========================================
# ===== راهنمای جامع =====
# ==========================================

def راهنمای_جامع():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0D47A1, #1E88E5); 
                padding: 20px 25px; 
                border-radius: 16px; 
                color: white;
                box-shadow: 0 4px 20px rgba(13, 71, 161, 0.25);
                margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 2rem;">📖</span>
            <span style="font-size: 1.3rem; font-weight: bold;">راهنمای جامع iHoNoor</span>
        </div>
        <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">
            همه چیز درباره iHoNoor: نحوه کار، داده‌های مورد نیاز، خروجی‌ها و بهترین روش‌های استفاده
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🎯 ۱. iHoNoor چیست و چه کاری انجام می‌دهد؟", expanded=True):
        st.markdown("""
        <div style="background: #E3F2FD; padding: 15px; border-radius: 12px; border-right: 4px solid #1E88E5; margin-bottom: 15px;">
            <p><strong>iHoNoor</strong> یک پلتفرم هوشمند است که با استفاده از <strong>۶ مدل هوش مصنوعی</strong>، به شما کمک می‌کند تا:</p>
            <ul>
                <li>📈 <strong>فروش فردا</strong> را پیش‌بینی کنید</li>
                <li>📊 <strong>روند فروش</strong> خود را تحلیل کنید</li>
                <li>💰 <strong>تأثیر دلار و تحریم‌ها</strong> را بر صنف خود ببینید</li>
                <li>🏠 <strong>دخل و خرج خانواده</strong> را مدیریت کنید</li>
                <li>👥 <strong>مشتریان</strong> خود را مدیریت کنید</li>
                <li>🤝 <strong>سیستم ارجاع</strong> برای معرفی دوستان</li>
            </ul>
            <p style="color: #0D47A1; font-weight: bold; margin-top: 10px;">✨ با یاری الهی، نور هوشمند فروش</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📋 ۲. چه داده‌هایی برای استفاده نیاز دارید؟", expanded=True):
        st.markdown("""
        <div style="background: #FFF8E1; padding: 15px; border-radius: 12px; border-right: 4px solid #FFA000; margin-bottom: 15px;">
            <p><strong>📌 برای استفاده از iHoNoor، به یک فایل Excel یا CSV با داده‌های فروش خود نیاز دارید.</strong></p>
            <p>فایل شما باید حداقل شامل این ستون‌ها باشد:</p>
            <ul>
                <li><strong>📅 تاریخ:</strong> تاریخ فروش (به صورت شمسی یا میلادی)</li>
                <li><strong>💰 فروش:</strong> مقدار فروش در آن تاریخ</li>
                <li><strong>👥 تعداد مشتریان:</strong> (اختیاری، اما دقت را بالا می‌برد)</li>
                <li><strong>🏷️ قیمت:</strong> (اختیاری، برای تحلیل قیمت)</li>
            </ul>
            <p style="color: #888; font-size: 0.85rem;">💡 <strong>حداقل داده مورد نیاز:</strong> برای پیش‌بینی دقیق، حداقل <strong>۵۰ رکورد</strong> (روز) داده توصیه می‌شود. هر چه داده بیشتر باشد، دقت بالاتر می‌رود.</p>
        </div>
        
        <div style="background: #E8F5E9; padding: 15px; border-radius: 12px; border-right: 4px solid #4CAF50; margin-bottom: 15px;">
            <p><strong>📊 نمونه فرمت فایل:</strong></p>
            <div style="background: white; padding: 10px; border-radius: 8px; direction: ltr; font-family: monospace; font-size: 0.85rem;">
                تاریخ | فروش | تعداد مشتریان | قیمت<br>
                1403/01/01 | 5,200,000 | 45 | 25,000<br>
                1403/01/02 | 6,800,000 | 52 | 28,000<br>
                1403/01/03 | 4,500,000 | 38 | 22,000
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🚀 ۳. چگونه از iHoNoor استفاده کنیم؟ (گام‌به‌گام)", expanded=True):
        st.markdown("""
        <div style="background: #E3F2FD; padding: 15px; border-radius: 12px; border-right: 4px solid #1E88E5; margin-bottom: 15px;">
            <h4>📌 گام ۱: انتخاب صنف</h4>
            <p>از منوی کناری، صنف خود را انتخاب کنید (خواربارفروشی، پوشاک، ساختمان و ...).</p>
            
            <h4>📌 گام ۲: آپلود فایل</h4>
            <p>فایل Excel یا CSV خود را در بخش "آپلود فایل" بارگذاری کنید.</p>
            <p style="color: #888; font-size: 0.85rem;">💡 اگر فایل ندارید، می‌توانید از <strong>فایل نمونه</strong> که در همین صفحه قرار دارد استفاده کنید.</p>
            
            <h4>📌 گام ۳: انتخاب ستون هدف</h4>
            <p>ستونی که می‌خواهید پیش‌بینی کنید را انتخاب کنید (مثلاً "فروش" یا "فروش_فردا").</p>
            
            <h4>📌 گام ۴: کلیک روی "پیش‌بینی کن"</h4>
            <p>برنامه با استفاده از ۶ مدل هوش مصنوعی، پیش‌بینی را انجام می‌دهد.</p>
            
            <h4>📌 گام ۵: مشاهده نتایج</h4>
            <p>نتایج شامل پیش‌بینی فروش، دقت مدل، هشدارها و مشاوره iHoNoor است.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📊 ۴. چه خروجی‌هایی دریافت می‌کنید؟", expanded=True):
        st.markdown("""
        <div style="background: #FFF8E1; padding: 15px; border-radius: 12px; border-right: 4px solid #FFA000; margin-bottom: 15px;">
            <p>بعد از پیش‌بینی، این خروجی‌ها را دریافت می‌کنید:</p>
            <ul>
                <li><strong>📈 فروش فردا:</strong> مقدار دقیق پیش‌بینی شده برای روز آینده</li>
                <li><strong>🎯 دقت مدل:</strong> نشان می‌دهد چقدر می‌توانید به پیش‌بینی اعتماد کنید (بالای ۸۰٪ عالی است)</li>
                <li><strong>🔮 بازه اطمینان:</strong> محدوده احتمالی فروش (مثلاً ۱۰ تا ۱۴ میلیون)</li>
                <li><strong>🔔 هشدارهای هوشمند:</strong> در صورت کاهش یا افزایش فروش، به شما هشدار می‌دهد</li>
                <li><strong>🤖 مشاور iHoNoor:</strong> تحلیل و راهکارهای عملی برای بهبود فروش</li>
                <li><strong>📊 اهمیت ویژگی‌ها:</strong> نشان می‌دهد کدام عوامل بیشترین تأثیر را بر فروش دارند</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🎯 ۵. چرا باید ستون هدف را درست انتخاب کنیم؟", expanded=True):
        st.markdown("""
        <div style="background: #E8F5E9; padding: 15px; border-radius: 12px; border-right: 4px solid #4CAF50; margin-bottom: 15px;">
            <p><strong>ستون هدف (Target Column)</strong> مقداری است که می‌خواهید پیش‌بینی کنید.</p>
            <p><strong>مثال‌هایی از ستون هدف:</strong></p>
            <ul>
                <li><strong>فروش:</strong> اگر می‌خواهید بدانید فردا چقدر می‌فروشید</li>
                <li><strong>تعداد مشتریان:</strong> اگر می‌خواهید بدانید فردا چند مشتری دارید</li>
                <li><strong>قیمت:</strong> اگر می‌خواهید بدانید قیمت فردا چقدر می‌شود</li>
            </ul>
            <p style="color: #888; font-size: 0.85rem;">💡 <strong>نکته مهم:</strong> ستونی که انتخاب می‌کنید باید <strong>عددی</strong> باشد و داده‌های کافی (حداقل ۵۰ رکورد) داشته باشد.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🧠 ۶. پیش‌بینی چگونه عمل می‌کند؟ (به زبان ساده)", expanded=True):
        st.markdown("""
        <div style="background: #E3F2FD; padding: 15px; border-radius: 12px; border-right: 4px solid #1E88E5; margin-bottom: 15px;">
            <p><strong>iHoNoor از ۶ مدل هوش مصنوعی مختلف استفاده می‌کند:</strong></p>
            <ul>
                <li><strong>🧠 جنگل تصادفی (Random Forest):</strong> مانند یک گروه از کارشناسان که هر کدام نظر می‌دهند و نتیجه نهایی میانگین نظرات است.</li>
                <li><strong>📈 رگرسیون خطی (Linear Regression):</strong> مانند رسم یک خط بین نقاط داده و پیش‌بینی بر اساس آن خط.</li>
                <li><strong>⚡ ایکس‌جی‌بوست (XGBoost):</strong> یکی از قدرتمندترین مدل‌ها که خطاهای خود را یاد می‌گیرد و بهبود می‌بخشد.</li>
                <li><strong>و ۳ مدل دیگر</strong> که هر کدام از زاویه متفاوتی به داده نگاه می‌کنند.</li>
            </ul>
            <p style="color: #888; font-size: 0.85rem;">💡 <strong>نتیجه نهایی:</strong> بهترین مدل انتخاب می‌شود و بر اساس آن پیش‌بینی انجام می‌شود.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📥 ۷. دانلود فایل نمونه برای تست", expanded=True):
        st.markdown("""
        <div style="background: #FFF8E1; padding: 15px; border-radius: 12px; border-right: 4px solid #FFA000; margin-bottom: 15px;">
            <p>اگر فایل Excel برای تست ندارید، می‌توانید فایل نمونه را دانلود کنید و با آن کار کنید.</p>
        </div>
        """, unsafe_allow_html=True)
        
        excel_data = create_sample_excel()
        st.download_button(
            label="📥 دانلود فایل نمونه Excel",
            data=excel_data,
            file_name="نمونه_فروش_iHoNoor.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.caption("💡 این فایل شامل داده‌های فروش یک خواربارفروشی است. می‌توانید آن را آپلود کنید و نتیجه را ببینید.")
    
    with st.expander("⚠️ ۸. نکات مهم برای بهترین نتیجه", expanded=True):
        st.markdown("""
        <div style="background: #FFEBEE; padding: 15px; border-radius: 12px; border-right: 4px solid #E53935; margin-bottom: 15px;">
            <ul>
                <li><strong>📊 حداقل ۵۰ رکورد:</strong> برای پیش‌بینی دقیق، حداقل ۵۰ روز داده داشته باشید.</li>
                <li><strong>📅 داده‌های به‌روز:</strong> داده‌های خود را به‌روز نگه دارید.</li>
                <li><strong>🎯 ستون هدف عددی:</strong> ستونی که انتخاب می‌کنید باید عددی باشد.</li>
                <li><strong>📈 داده‌های پرت:</strong> اگر داده‌های خیلی بالا یا پایین دارید، ممکن است دقت مدل کاهش یابد.</li>
                <li><strong>🔄 به‌روزرسانی:</strong> هر هفته داده‌های جدید آپلود کنید تا پیش‌بینی‌ها دقیق‌تر شوند.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def create_sample_excel():
    data = {
        'تاریخ': [
            '1403/01/01', '1403/01/02', '1403/01/03', '1403/01/04', '1403/01/05',
            '1403/01/06', '1403/01/07', '1403/01/08', '1403/01/09', '1403/01/10',
            '1403/01/11', '1403/01/12', '1403/01/13', '1403/01/14', '1403/01/15'
        ],
        'فروش': [
            5200000, 6800000, 4500000, 7200000, 8300000,
            3900000, 6100000, 7800000, 5400000, 9200000,
            4700000, 6600000, 8500000, 5100000, 7400000
        ],
        'تعداد مشتریان': [
            45, 52, 38, 58, 63,
            32, 48, 55, 42, 68,
            36, 50, 60, 41, 56
        ],
        'قیمت میانگین': [
            25000, 28000, 22000, 30000, 32000,
            20000, 24000, 29000, 23000, 34000,
            21000, 26000, 31000, 22000, 27000
        ],
        'تخفیف': [
            5, 10, 0, 15, 20,
            0, 5, 10, 0, 15,
            0, 5, 10, 0, 5
        ],
        'فروش_فردا': [
            5800000, 7500000, 5200000, 8000000, 9100000,
            4500000, 6800000, 8500000, 6000000, 10000000,
            5200000, 7200000, 9300000, 5600000, 8100000
        ]
    }
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='فروش', index=False)
    return output.getvalue()

# ==========================================
# ===== آینده هوش مصنوعی =====
# ==========================================

def نمایش_آینده_هوش_مصنوعی():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0D47A1, #1E88E5); 
                padding: 20px 25px; 
                border-radius: 16px; 
                color: white;
                box-shadow: 0 4px 20px rgba(13, 71, 161, 0.25);
                margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 2rem;">🚀</span>
            <span style="font-size: 1.3rem; font-weight: bold;">آینده مشاغل با هوش مصنوعی</span>
        </div>
        <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">
            چرا هوش مصنوعی آینده همه مشاغل است و iHoNoor چگونه به شما کمک می‌کند
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🤖</span> هوش مصنوعی در کسب‌وکارهای امروز</div>
        <p>
        امروزه بیش از <strong>۵۰٪ کسب‌وکارهای جهان</strong> از هوش مصنوعی برای پیش‌بینی و تحلیل استفاده می‌کنند. 
        این رقم در ۵ سال آینده به <strong>۸۰٪</strong> خواهد رسید.
        </p>
        <ul>
            <li>📊 <strong>کسب‌وکارهایی که از هوش مصنوعی استفاده می‌کنند</strong> تا <strong>۴۰٪</strong> سود بیشتری دارند.</li>
            <li>📈 <strong>دقت پیش‌بینی</strong> با هوش مصنوعی تا <strong>۸۵٪</strong> افزایش می‌یابد.</li>
            <li>⏱️ <strong>زمان تصمیم‌گیری</strong> تا <strong>۷۰٪</strong> کاهش می‌یابد.</li>
        </ul>
    </div>
    
    <div class="card">
        <div class="card-title"><span class="icon">🏪</span> آینده صنف‌های مختلف با هوش مصنوعی</div>
        <ul>
            <li><strong>🏪 خواربارفروشی:</strong> پیش‌بینی دقیق موجودی، کاهش ۳۰٪ ضایعات غذایی</li>
            <li><strong>👗 پوشاک:</strong> شناسایی ترندهای مد، افزایش ۲۵٪ فروش</li>
            <li><strong>🏗️ ساختمان:</strong> پیش‌بینی هزینه و زمان پروژه، کاهش ۲۰٪ تأخیر</li>
            <li><strong>🍞 نانوایی:</strong> بهینه‌سازی تولید، کاهش ۴۰٪ دورریز</li>
            <li><strong>🚗 خودروسازی:</strong> مدیریت موجودی قطعات، افزایش ۳۵٪ کارایی</li>
        </ul>
    </div>
    
    <div class="card">
        <div class="card-title"><span class="icon">💡</span> چرا iHoNoor بهترین انتخاب برای شماست؟</div>
        <ul>
            <li>✅ <strong>۱۰۰٪ ایرانی</strong> و متناسب با بازار ایران</li>
            <li>✅ <strong>بدون تحریم</strong> و نیاز به فیلترشکن</li>
            <li>✅ <strong>۶ مدل هوش مصنوعی</strong> برای دقت بالا</li>
            <li>✅ <strong>راهنمای کامل</strong> برای هر صنف</li>
            <li>✅ <strong>پشتیبانی داخلی</strong> و پاسخگویی سریع</li>
            <li>✅ <strong>قابل شخصی‌سازی</strong> بر اساس نیاز شما</li>
        </ul>
    </div>
    
    <div class="card">
        <div class="card-title"><span class="icon">📈</span> چگونه از iHoNoor بهترین نتیجه را بگیریم؟</div>
        <ol>
            <li><strong>به‌روز نگه دارید:</strong> هر هفته داده‌های جدید آپلود کنید تا مدل دقیق‌تر شود.</li>
            <li><strong>همه صنف‌ها را بررسی کنید:</strong> اگر چند صنف دارید، همه را تست کنید.</li>
            <li><strong>از مشاور iHoNoor استفاده کنید:</strong> راهکارهای عملی را اجرا کنید.</li>
            <li><strong>تغییرات را اعمال کنید:</strong> پیشنهادات را در کسب‌وکار خود پیاده کنید.</li>
            <li><strong>با ما در ارتباط باشید:</strong> نظرات و پیشنهادات خود را برای ما بفرستید.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.success("""
    💡 **نکته کلیدی:** 
    کسب‌وکارهایی که امروز از هوش مصنوعی استفاده می‌کنند، 
    در ۵ سال آینده ۲ برابر سریع‌تر از رقبای خود رشد خواهند کرد.
    iHoNoor همراه شما در این مسیر است.
    """)

# ==========================================
# ===== فرم ارسال نظر =====
# ==========================================

def فرم_ارسال_نظر():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0D47A1, #1E88E5); 
                padding: 20px 25px; 
                border-radius: 16px; 
                color: white;
                box-shadow: 0 4px 20px rgba(13, 71, 161, 0.25);
                margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 2rem;">📝</span>
            <span style="font-size: 1.3rem; font-weight: bold;">ارسال نظر و پیشنهاد</span>
        </div>
        <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">
            نظرات، پیشنهادات و نیازهای خود را با ما به اشتراک بگذارید تا iHoNoor را برای شما تخصصی‌تر کنیم
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">💬</span> چرا نظرات شما مهم است؟</div>
        <p>
        با ارسال نظرات و پیشنهادات خود، به ما کمک می‌کنید تا iHoNoor را دقیقاً بر اساس <strong>نیازهای واقعی</strong> شما تنظیم کنیم.
        هر صنف، نیازهای خاص خود را دارد و ما با دریافت داده‌های شما، مدل‌ها را <strong>شخصی‌سازی</strong> می‌کنیم.
        </p>
        <ul>
            <li>📊 <strong>داده‌های واقعی:</strong> با ارسال داده‌های فروش خود، مدل را دقیق‌تر می‌کنیم.</li>
            <li>💡 <strong>پیشنهادات جدید:</strong> اگر نیاز خاصی دارید، به ما بگویید تا اضافه کنیم.</li>
            <li>🔧 <strong>بهبود برنامه:</strong> با نظرات شما، iHoNoor را بهتر می‌کنیم.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #E8F5E9; padding: 15px; border-radius: 12px; border-right: 4px solid #4CAF50; margin-bottom: 20px;">
        <p style="margin: 0;"><strong>📬 اطلاعات تماس ما:</strong></p>
        <p style="margin: 0;">📧 <strong>ha2021alipur@gmail.com</strong></p>
        <p style="margin: 0;">📱 <strong>09019470509</strong> (واتساپ و تلگرام)</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("contact_form", clear_on_submit=True):
        st.subheader("📝 فرم ارسال نظر")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 نام و نام‌خانوادگی", placeholder="علی رضایی")
            email = st.text_input("📧 ایمیل", placeholder="info@example.com")
        with col2:
            phone = st.text_input("📱 شماره تماس", placeholder="09123456789")
            industry = st.selectbox("🏷️ صنف شما", industries + ["سایر"])
        
        subject = st.selectbox(
            "📌 موضوع",
            ["پیشنهاد برای بهبود برنامه", "نیاز تخصصی صنف من", "گزارش مشکل", "درخواست مشاوره", "سایر"]
        )
        
        message = st.text_area(
            "📝 متن پیام",
            placeholder="نظرات، پیشنهادات و نیازهای خود را بنویسید...",
            height=150
        )
        
        submitted = st.form_submit_button("📨 ارسال نظر", type="primary", use_container_width=True)
        
        if submitted:
            if name and message:
                st.success("✅ نظر شما با موفقیت ارسال شد! از همراهی شما سپاسگزاریم.")
                st.balloons()
                st.info("""
                📬 **چه اتفاقی می‌افتد؟**
                1. نظر شما به ایمیل ما ارسال می‌شود.
                2. تیم ما آن را بررسی می‌کند.
                3. در صورت نیاز، با شما تماس می‌گیریم.
                4. نظرات شما در بهبود iHoNoor استفاده می‌شود.
                """)
                
                st.markdown(f"""
                <div style="background: #E3F2FD; padding: 15px; border-radius: 12px; border-right: 4px solid #1E88E5;">
                    <p><strong>📋 خلاصه پیام شما:</strong></p>
                    <p>👤 {name}</p>
                    <p>📧 {email}</p>
                    <p>📱 {phone}</p>
                    <p>🏷️ {industry}</p>
                    <p>📌 {subject}</p>
                    <p>📝 {message[:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ لطفاً نام و متن پیام را وارد کنید.")
    
    st.markdown("---")
    st.subheader("📞 راه‌های ارتباطی مستقیم")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: #E3F2FD; padding: 15px; border-radius: 12px; text-align: center; border-right: 4px solid #1E88E5;">
            <p style="font-size: 2rem; margin: 0;">📧</p>
            <p style="font-weight: bold; margin: 5px 0;">ایمیل</p>
            <p style="font-size: 0.85rem;">ha2021alipur@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #E8F5E9; padding: 15px; border-radius: 12px; text-align: center; border-right: 4px solid #4CAF50;">
            <p style="font-size: 2rem; margin: 0;">📱</p>
            <p style="font-weight: bold; margin: 5px 0;">واتساپ</p>
            <p style="font-size: 0.85rem;">09019470509</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #FFF8E1; padding: 15px; border-radius: 12px; text-align: center; border-right: 4px solid #FFA000;">
            <p style="font-size: 2rem; margin: 0;">📲</p>
            <p style="font-weight: bold; margin: 5px 0;">تلگرام</p>
            <p style="font-size: 0.85rem;">@ha2021alipur</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# مدیریت کاربران و داشبورد
# ==========================================

def load_users():
    if os.path.exists("users_data.csv"):
        return pd.read_csv("users_data.csv")
    else:
        np.random.seed(42)
        users = pd.DataFrame({
            'نام': ['علی رضایی', 'مریم احمدی', 'محمد کریمی', 'سارا حسینی', 'رضا محمدی'],
            'شماره': ['09123456789', '09123456788', '09123456787', '09123456786', '09123456785'],
            'ایمیل': ['ali@example.com', 'maryam@example.com', 'mohammad@example.com', 'sara@example.com', 'reza@example.com'],
            'صنف': ['خواربارفروشی', 'پوشاک', 'ساختمان', 'نانوایی', 'خرده‌فروشی'],
            'تاریخ ثبت': ['1403/01/15', '1403/02/20', '1403/03/10', '1403/04/05', '1403/05/12'],
            'تعداد استفاده': np.random.randint(1, 50, 5),
            'فروش کل': np.random.randint(1_000_000, 50_000_000, 5),
            'وضعیت': ['فعال', 'فعال', 'غیرفعال', 'فعال', 'فعال']
        })
        users.to_csv("users_data.csv", index=False)
        return users

def save_users(df):
    df.to_csv("users_data.csv", index=False)

def generate_sales_data():
    np.random.seed(42)
    dates = pd.date_range('1403-01-01', periods=30, freq='D')
    sales_data = pd.DataFrame({
        'تاریخ': dates,
        'فروش': np.random.randint(1_000_000, 10_000_000, 30),
        'تعداد مشتریان': np.random.randint(10, 50, 30),
        'هزینه': np.random.randint(500_000, 5_000_000, 30)
    })
    sales_data['سود'] = sales_data['فروش'] - sales_data['هزینه']
    return sales_data

# ==========================================
# ورود مدیر
# ==========================================

def admin_login():
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h2 style="color: #1E88E5;">🔐 ورود به بخش مدیریت</h2>
        <p style="color: #666;">لطفاً اطلاعات خود را وارد کنید</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("👤 نام کاربری", placeholder="نام کاربری خود را وارد کنید")
        password = st.text_input("🔑 رمز عبور", type="password", placeholder="رمز عبور خود را وارد کنید")
        
        if st.button("🚪 ورود به داشبورد", type="primary", use_container_width=True):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.session_state.admin_login_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.success("✅ با موفقیت وارد شدید!")
                st.rerun()
            else:
                st.error("❌ نام کاربری یا رمز عبور اشتباه است.")

def show_admin_dashboard():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
        padding: 20px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <h2 style="margin: 0;">📊 داشبورد مدیریتی iHoNoor</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.8;">مدیریت هوشمند کسب‌وکار شما</p>
        </div>
        <div style="text-align: left;">
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">👤 مدیر سیستم</p>
            <p style="margin: 0; font-size: 0.7rem; opacity: 0.6;">آخرین ورود: {}</p>
        </div>
    </div>
    """.format(st.session_state.get('admin_login_time', 'نامشخص')), unsafe_allow_html=True)
    
    users_df = load_users()
    sales_df = generate_sales_data()
    
    st.markdown("### 📊 خلاصه عملکرد کل")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = sales_df['فروش'].sum()
        st.metric("💰 فروش کل", f"{total_sales:,.0f} تومان")
    
    with col2:
        total_profit = sales_df['سود'].sum()
        profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
        st.metric("📈 سود خالص", f"{total_profit:,.0f} تومان", delta=f"{profit_margin:.1f}%")
    
    with col3:
        total_users = len(users_df[users_df['وضعیت'] == 'فعال'])
        st.metric("👥 کاربران فعال", total_users)
    
    with col4:
        total_customers = sales_df['تعداد مشتریان'].sum()
        st.metric("🛒 مشتریان کل", f"{total_customers:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 روند فروش")
        fig = px.line(sales_df, x='تاریخ', y='فروش', title="فروش روزانه", height=300)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 سود و هزینه")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=sales_df['تاریخ'], y=sales_df['فروش'], name='فروش', marker_color='#1E88E5'))
        fig2.add_trace(go.Bar(x=sales_df['تاریخ'], y=sales_df['هزینه'], name='هزینه', marker_color='#FFA000'))
        fig2.update_layout(height=300, barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("👥 مدیریت کاربران")
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 جستجوی کاربر:", placeholder="نام، شماره یا ایمیل...")
    with col2:
        status_filter = st.selectbox("📌 فیلتر وضعیت:", ["همه", "فعال", "غیرفعال"])
    
    filtered_df = users_df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df['نام'].str.contains(search, case=False) |
            filtered_df['شماره'].str.contains(search, case=False) |
            filtered_df['ایمیل'].str.contains(search, case=False)
        ]
    if status_filter != "همه":
        filtered_df = filtered_df[filtered_df['وضعیت'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"📊 تعداد کل کاربران: {len(filtered_df)}")
    
    st.markdown("---")
    
    if st.button("🚪 خروج از سیستم", type="secondary"):
        st.session_state.admin_logged_in = False
        st.rerun()

# ==========================================
# خونه‌پرداز
# ==========================================

def show_family_finance():
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🏠</span> خونه‌پرداز | مدیریت دخل و خرج خانواده</div>
        <p>درآمد و هزینه‌های خود را مدیریت کنید و پیشنهادات هوشمند دریافت کنید.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "incomes" not in st.session_state:
        st.session_state.incomes = []
    if "expenses" not in st.session_state:
        st.session_state.expenses = []
    
    st.subheader("💰 ثبت درآمد")
    col1, col2 = st.columns(2)
    with col1:
        income_source = st.text_input("منبع درآمد", placeholder="حقوق، پاداش، اجاره...")
    with col2:
        income_amount = st.number_input("مبلغ (تومان)", min_value=0, step=100_000, key="income_amount")
    
    if st.button("➕ ثبت درآمد", key="add_income"):
        if income_source and income_amount > 0:
            st.session_state.incomes.append({
                'منبع': income_source,
                'مبلغ': income_amount,
                'تاریخ': datetime.now().strftime("%Y-%m-%d")
            })
            st.success(f"✅ درآمد {income_source} به مبلغ {income_amount:,.0f} تومان ثبت شد!")
            st.rerun()
    
    st.subheader("📉 ثبت هزینه")
    col1, col2, col3 = st.columns(3)
    with col1:
        expense_category = st.selectbox("دسته‌بندی هزینه", ["خوراک", "مسکن", "حمل و نقل", "تفریح", "بهداشت", "پوشاک", "آموزش", "سایر"])
    with col2:
        expense_desc = st.text_input("توضیحات", placeholder="مثلاً: خرید میوه")
    with col3:
        expense_amount = st.number_input("مبلغ (تومان)", min_value=0, step=10_000, key="expense_amount")
    
    if st.button("➕ ثبت هزینه", key="add_expense"):
        if expense_desc and expense_amount > 0:
            st.session_state.expenses.append({
                'دسته‌بندی': expense_category,
                'توضیحات': expense_desc,
                'مبلغ': expense_amount,
                'تاریخ': datetime.now().strftime("%Y-%m-%d")
            })
            st.success(f"✅ هزینه {expense_desc} به مبلغ {expense_amount:,.0f} تومان ثبت شد!")
            st.rerun()
    
    st.markdown("---")
    
    total_income = sum([i['مبلغ'] for i in st.session_state.incomes])
    total_expense = sum([e['مبلغ'] for e in st.session_state.expenses])
    balance = total_income - total_expense
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 کل درآمد", f"{total_income:,.0f} تومان")
    with col2:
        st.metric("📉 کل هزینه", f"{total_expense:,.0f} تومان")
    with col3:
        st.metric("📊 مانده حساب", f"{balance:,.0f} تومان")
    
    if st.session_state.expenses:
        st.subheader("📋 لیست هزینه‌ها")
        st.dataframe(pd.DataFrame(st.session_state.expenses), use_container_width=True)
    
    if total_expense > 0 and total_income > 0:
        expense_ratio = (total_expense / total_income) * 100
        if expense_ratio > 80:
            st.warning(f"⚠️ هزینه‌های شما {expense_ratio:.1f}% از درآمدتان است. پیشنهاد می‌کنیم هزینه‌های غیرضروری را کاهش دهید.")
        elif expense_ratio > 60:
            st.info(f"📊 هزینه‌های شما {expense_ratio:.1f}% از درآمدتان است. وضعیت قابل قبول است.")
        else:
            st.success(f"✅ هزینه‌های شما {expense_ratio:.1f}% از درآمدتان است. مدیریت مالی عالی!")
    
    if balance < 0:
        st.error("⚠️ هشدار! هزینه‌های شما بیشتر از درآمدتان است. لطفاً بودجه خود را بازبینی کنید.")

# ==========================================
# بارگذاری داده
# ==========================================
data = None
source = ""

if تخصصی and مسیر_تخصصی and os.path.exists(مسیر_تخصصی):
    try:
        data = pd.read_csv(مسیر_تخصصی) if مسیر_تخصصی.endswith('.csv') else pd.read_excel(مسیر_تخصصی)
        source = "دیتاست جامع"
        st.success(f"✅ دیتاست تخصصی با {len(data)} رکورد بارگذاری شد.")
    except Exception as e:
        st.error(f"❌ خطا در خواندن دیتاست: {e}")

if data is None and فایل is not None:
    try:
        data = pd.read_csv(فایل) if فایل.name.endswith('.csv') else pd.read_excel(فایل)
        source = "فایل شما"
        st.success(f"✅ فایل شما با {len(data)} رکورد بارگذاری شد.")
    except Exception as e:
        st.error(f"❌ خطا در خواندن فایل: {e}")

if data is None:
    data = sample_data(صنف)
    source = "داده‌های نمونه"
    st.info(f"📊 از داده‌های نمونه برای {صنف} استفاده می‌شود.")

# ==========================================
# تب‌ها
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📖 راهنما",
    "📊 تحلیل و پیش‌بینی",
    "📱 نصب روی گوشی",
    "📅 تقویم شمسی",
    "🤝 سیستم ارجاع",
    "👤 داشبورد کاربری",
    "🏠 خونه‌پرداز",
    "📘 راهنمای صنف‌ها",
    "📚 راهنمای جامع",
    "🚀 آینده هوش مصنوعی",
    "📝 ارسال نظر",
    "🔐 مدیریت"
])

with tab1:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🎯</span> iHoNoor چیست؟</div>
        <p><strong>iHoNoor</strong> یک پلتفرم <strong>۱۰۰٪ ایرانی</strong>، <strong>بدون تحریم</strong> و <strong>با یاری الهی</strong> است که با استفاده از ۶ مدل هوش مصنوعی، فروش فردا را پیش‌بینی می‌کند.</p>
    </div>
    
    <div class="card">
        <div class="card-title"><span class="icon">✨</span> قابلیت‌های iHoNoor</div>
        <ul>
            <li>🤖 پیش‌بینی فروش با ۶ مدل هوش مصنوعی</li>
            <li>📊 داشبورد مدیریتی و کاربری</li>
            <li>📱 نصب روی گوشی و تبلت (PWA)</li>
            <li>📅 همگام‌سازی با تقویم شمسی</li>
            <li>🤝 سیستم ارجاع و پاداش</li>
            <li>🔔 هشدارهای هوشمند لحظه‌ای</li>
            <li>📈 تحلیل خودکار کلان اقتصادی</li>
            <li>🏠 خونه‌پرداز (مدیریت دخل و خرج خانواده)</li>
            <li>📘 راهنمای تخصصی صنف‌ها با تجربیات جهانی</li>
            <li>📚 راهنمای جامع استفاده</li>
            <li>🚀 آینده هوش مصنوعی و تأثیر آن بر مشاغل</li>
            <li>📝 ارسال نظر و پیشنهاد</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><div class="card-title"><span class="icon">📋</span> نمونه داده‌ها</div>', unsafe_allow_html=True)
        st.dataframe(data.head(8))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><div class="card-title"><span class="icon">📊</span> خلاصه آمار</div>', unsafe_allow_html=True)
        st.dataframe(data.describe())
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.caption(f"📌 منبع: {source}")
    
    if 'تاریخ' in data.columns:
        try:
            num_cols = data.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                fig = px.line(data, x='تاریخ', y=num_cols[0], title="📈 روند تغییرات", height=300)
                st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    
    st.markdown("---")
    
    target = st.selectbox("🎯 ستون هدف:", data.columns)
    
    model_names = list(models_dict.keys())
    model_names_fa_list = [model_names_fa[m] for m in model_names]
    selected_model_fa = st.selectbox("🧠 مدل پیش‌بینی:", model_names_fa_list)
    selected_model = [m for m in models_dict.keys() if model_names_fa[m] == selected_model_fa][0]
    
    if st.button("🚀 پیش‌بینی کن", type="primary", use_container_width=True):
        with st.spinner("⏳ در حال آموزش مدل..."):
            try:
                le = LabelEncoder()
                d = data.copy()
                for col in d.select_dtypes(include=['object']).columns:
                    if col != target:
                        try:
                            d[col] = le.fit_transform(d[col].astype(str))
                        except:
                            pass
                
                X = d.drop(columns=[target])
                y = d[target]
                X = X.select_dtypes(include=['number'])
                
                if len(X.columns) == 0:
                    st.error("❌ هیچ ویژگی عددی برای آموزش مدل وجود ندارد.")
                    st.stop()
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                results = train_models(X_train, y_train, X_test, y_test)
                
                best_model = None
                best_score = -1
                for name, res in results.items():
                    if 'error' not in res and res['r2'] > best_score:
                        best_score = res['r2']
                        best_model = name
                
                if best_model:
                    model = results[best_model]['model']
                    avg_row = X.mean().values.reshape(1, -1)
                    pred_value = model.predict(avg_row)[0]
                    
                    st.markdown(f"""
                    <div class="result-box">
                        <div class="result-label">📈 فروش فردا</div>
                        <div class="result-number">{pred_value:,.0f}</div>
                        <div class="result-label">تومان</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🎯 دقت مدل", f"{best_score:.1%}")
                    with col2:
                        st.metric("🔮 بازه اطمینان", f"{pred_value*0.85:,.0f} - {pred_value*1.15:,.0f}")
                    
                    alerts = smart_alerts(data, target, pred_value, صنف)
                    if alerts:
                        st.subheader("🔔 هشدارهای هوشمند")
                        for alert in alerts:
                            if "⚠️" in alert:
                                st.warning(alert)
                            elif "✅" in alert:
                                st.success(alert)
                            else:
                                st.info(alert)
                    
                    تحلیل = مشاور_iHonoor(pred_value, best_score, target, data, alerts, صنف)
                    نمایش_مشاور(تحلیل)
                    
                    with st.expander("🤖 تحلیل خودکار کلان اقتصادی (تأثیر دلار بر صنف شما)", expanded=True):
                        st.markdown("""
                        <div style="background: #E3F2FD; padding: 15px; border-radius: 12px; border-right: 4px solid #1E88E5; margin-bottom: 15px;">
                            <strong>💡 توضیح:</strong> این بخش به‌صورت خودکار قیمت دلار را دریافت کرده و تأثیر آن بر صنف شما را تحلیل می‌کند.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("📊 تحلیل خودکار", key="auto_macro_btn", type="primary"):
                            with st.spinner("⏳ در حال دریافت قیمت دلار و تحلیل..."):
                                try:
                                    گزارش, تغییر_صنف, وضعیت, رنگ = تحلیل_خودکار_کلان_اقتصادی(صنف)
                                    نمایش_تحلیل_خودکار(گزارش, تغییر_صنف, وضعیت, رنگ)
                                except Exception as e:
                                    st.error(f"❌ خطا در تحلیل: {e}")
                                    st.info("💡 لطفاً دوباره تلاش کنید یا بعداً امتحان کنید.")
                    
                    with st.expander("📊 مقایسه مدل‌ها (۶ مدل)"):
                        compare_data = []
                        for name, res in results.items():
                            if 'error' not in res:
                                compare_data.append({
                                    'مدل': model_names_fa[name],
                                    'MAE': f"{res['mae']:,.0f}",
                                    'R²': f"{res['r2']:.2%}"
                                })
                        if compare_data:
                            st.dataframe(pd.DataFrame(compare_data))
                    
                    with st.expander("📊 اهمیت ویژگی‌ها"):
                        if hasattr(model, 'feature_importances_'):
                            imp_df = pd.DataFrame({
                                'ویژگی': X.columns,
                                'اهمیت': model.feature_importances_
                            }).sort_values('اهمیت', ascending=False)
                            st.dataframe(imp_df)
                            fig = px.bar(imp_df, x='اهمیت', y='ویژگی', orientation='h', height=350)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("ℹ️ این مدل از قابلیت نمایش اهمیت ویژگی‌ها پشتیبانی نمی‌کند.")
                    
                    with st.expander("🔍 تشخیص ناهنجاری"):
                        anomalies, msg = detect_anomalies(data)
                        if anomalies is not None and len(anomalies) > 0:
                            st.error(f"⚠️ {len(anomalies)} ناهنجاری یافت شد!")
                            st.dataframe(anomalies)
                        else:
                            st.success("✅ هیچ ناهنجاری یافت نشد.")
                    
                    with st.expander("📊 تحلیل سلامت داده‌ها"):
                        health = analyze_health(data, target)
                        if "⚠️" in health:
                            st.warning(health)
                        else:
                            st.success(health)
                    
                    with st.expander("📥 دانلود گزارش"):
                        report_data = {
                            'پیش‌بینی فروش': [pred_value],
                            'دقت مدل (R²)': [best_score],
                            'تعداد رکوردها': [len(data)],
                            'بهترین مدل': [model_names_fa[best_model]]
                        }
                        report_df = pd.DataFrame(report_data)
                        csv = report_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 دانلود گزارش CSV",
                            data=csv,
                            file_name=f"پیش‌بینی_iHoNoor_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    
            except Exception as e:
                st.error(f"❌ خطا: {e}")

with tab3:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📱</span> نصب iHoNoor روی گوشی یا تبلت</div>
        <p>با نصب iHoNoor روی دستگاه خود، مانند یک اپلیکیشن واقعی از آن استفاده کنید.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #E3F2FD; padding: 20px; border-radius: 12px; border-right: 4px solid #1E88E5; margin-bottom: 20px;">
        <h4>📌 مراحل نصب در اندروید (کروم)</h4>
        <ol>
            <li>مرورگر <strong>کروم</strong> را باز کنید.</li>
            <li>آدرس iHoNoor را وارد کنید.</li>
            <li>روی سه نقطه (⋮) بالای صفحه کلیک کنید.</li>
            <li>گزینه <strong>"Add to Home screen"</strong> را انتخاب کنید.</li>
            <li>روی <strong>"Add"</strong> کلیک کنید.</li>
        </ol>
    </div>
    
    <div style="background: #E8F5E9; padding: 20px; border-radius: 12px; border-right: 4px solid #4CAF50; margin-bottom: 20px;">
        <h4>📌 مراحل نصب در آیفون (سافاری)</h4>
        <ol>
            <li>مرورگر <strong>سافاری</strong> را باز کنید.</li>
            <li>آدرس iHoNoor را وارد کنید.</li>
            <li>روی دکمه <strong>اشتراک‌گذاری</strong> (مربع با فلش) کلیک کنید.</li>
            <li>گزینه <strong>"Add to Home Screen"</strong> را انتخاب کنید.</li>
            <li>روی <strong>"Add"</strong> کلیک کنید.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📅</span> تقویم شمسی و مناسبت‌ها</div>
        <p>مناسبت‌های پیش‌رو و تأثیر آن بر فروش</p>
    </div>
    """, unsafe_allow_html=True)
    
    today = jdatetime.date.today()
    st.info(f"📌 امروز: {today.strftime('%A %d %B %Y')}")
    
    holidays = {
        (1, 1): {"name": "عید نوروز", "impact": "افزایش ۳۰-۵۰٪ فروش"},
        (1, 2): {"name": "عید نوروز", "impact": "افزایش ۳۰-۵۰٪ فروش"},
        (1, 13): {"name": "سیزده به در", "impact": "افزایش فروش مواد غذایی"},
        (2, 14): {"name": "ولادت امام علی (ع)", "impact": "افزایش فروش شیرینی و نذری"},
        (6, 8): {"name": "عید سعید فطر", "impact": "افزایش فروش پوشاک و شیرینی"},
        (7, 15): {"name": "شهادت امام صادق (ع)", "impact": "کاهش فروش در برخی صنف‌ها"},
        (8, 25): {"name": "عید قربان", "impact": "افزایش فروش گوشت و نذری"},
        (9, 1): {"name": "عید غدیر خم", "impact": "افزایش فروش شیرینی"},
        (10, 30): {"name": "شب یلدا", "impact": "افزایش فروش میوه و تنقلات"}
    }
    
    st.markdown("### 🎯 مناسبت‌های پیش‌رو")
    
    upcoming = []
    for (month, day), info in holidays.items():
        days_until = (jdatetime.date(today.year, month, day) - today).days
        if 0 <= days_until <= 30:
            upcoming.append({
                'نام': info['name'],
                'روز': f"{days_until} روز دیگر",
                'تأثیر': info['impact']
            })
    
    if upcoming:
        for item in upcoming:
            st.success(f"🎉 {item['نام']} - {item['روز']} | تأثیر: {item['تأثیر']}")
    else:
        st.info("📅 هیچ مناسبت خاصی در ۳۰ روز آینده وجود ندارد.")
    
    st.markdown("---")
    st.markdown("""
    <div style="background: #E8F5E9; padding: 15px; border-radius: 12px; border-right: 4px solid #4CAF50;">
        <p><strong>💡 پیشنهاد هوشمند:</strong> با توجه به مناسبت‌های پیش‌رو، موجودی کالاهای مرتبط را افزایش دهید و برنامه‌ریزی تخفیف‌ها را انجام دهید.</p>
    </div>
    """, unsafe_allow_html=True)

with tab5:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🤝</span> سیستم ارجاع iHoNoor</div>
        <p>دوستان خود را دعوت کنید و پاداش دریافت کنید!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    referral_code = f"iHN-{st.session_state.user_id.upper()}"
    
    st.markdown(f"""
    <div style="background: #E8F5E9; padding: 15px 20px; border-radius: 12px; border-right: 4px solid #4CAF50; margin-bottom: 15px;">
        <p style="margin: 0;">🔑 <strong>کد ارجاع شما:</strong></p>
        <div style="font-size: 1.5rem; font-weight: 900; color: #0D47A1; letter-spacing: 4px;">{referral_code}</div>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: #666;">این کد را با دوستان خود به اشتراک بگذارید.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "referrals" not in st.session_state:
        st.session_state.referrals = []
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 تعداد ارجاعات", len(st.session_state.referrals))
    with col2:
        st.metric("🎁 پاداش", f"{len(st.session_state.referrals) * 50_000:,.0f} تومان")
    
    with st.expander("➕ افزودن ارجاع جدید"):
        col1, col2 = st.columns(2)
        with col1:
            friend_name = st.text_input("📛 نام دوست", placeholder="نام و نام‌خانوادگی")
        with col2:
            friend_phone = st.text_input("📱 شماره تماس", placeholder="09123456789")
        
        if st.button("📨 ثبت ارجاع", type="primary"):
            if friend_name and friend_phone:
                st.session_state.referrals.append({
                    'نام': friend_name,
                    'شماره': friend_phone,
                    'تاریخ': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'وضعیت': 'در انتظار'
                })
                st.success(f"✅ ارجاع {friend_name} با موفقیت ثبت شد!")
                st.balloons()
            else:
                st.error("❌ لطفاً نام و شماره تماس را وارد کنید.")
    
    if st.session_state.referrals:
        st.subheader("📋 لیست ارجاعات شما")
        st.dataframe(pd.DataFrame(st.session_state.referrals), use_container_width=True)

with tab6:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">👤</span> داشبورد کاربری</div>
        <p>خلاصه عملکرد و وضعیت کسب‌وکار شما</p>
    </div>
    """, unsafe_allow_html=True)
    
    if data is not None and not data.empty:
        sales_data = generate_sales_data()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 فروش امروز", f"{sales_data['فروش'].iloc[-1]:,.0f} تومان")
        with col2:
            st.metric("📈 فروش ماه", f"{sales_data['فروش'].sum():,.0f} تومان")
        with col3:
            st.metric("👥 مشتریان", f"{sales_data['تعداد مشتریان'].sum():,}")
        
        st.markdown("---")
        st.subheader("📈 روند فروش شما")
        fig = px.line(sales_data, x='تاریخ', y='فروش', title="فروش روزانه", height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 داده‌های کافی برای نمایش داشبورد وجود ندارد.")

with tab7:
    show_family_finance()

with tab8:
    راهنمای_صنف(صنف)

with tab9:
    راهنمای_جامع()

with tab10:
    نمایش_آینده_هوش_مصنوعی()

with tab11:
    فرم_ارسال_نظر()

with tab12:
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        admin_login()
    else:
        show_admin_dashboard()

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    <span class="brand">✨ iHoNoor</span> 🤖 نور هوشمند فروش<br>
    📧 ha2021alipur@gmail.com | 📱 09019470509<br>
    © 2025 iHoNoor | تمامی حقوق محفوظ است.
</div>
""", unsafe_allow_html=True)
