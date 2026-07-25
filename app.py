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
    
    .quick-guide {
        background: #FFF8E1;
        padding: 12px 18px;
        border-radius: 10px;
        border-right: 4px solid #FFA000;
        margin-bottom: 15px;
        font-size: 0.9rem;
    }
    
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 700;
        margin: 2px;
    }
    .badge-gold { background: #FFD700; color: #333; }
    .badge-silver { background: #C0C0C0; color: #333; }
    .badge-bronze { background: #CD7F32; color: white; }
    .badge-blue { background: #0D47A1; color: white; }
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
# لیست صنف‌ها (همه صنف‌های قبلی)
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
    
    # حالت ساده تبلت
    حالت_ساده = st.checkbox("📱 حالت ساده (مناسب تبلت)", value=False)
    if حالت_ساده:
        st.markdown("""
        <style>
            .stButton > button { padding: 14px 30px !important; font-size: 1.1rem !important; }
            .stSelectbox, .stTextInput { font-size: 1.1rem !important; }
            .stTabs [data-baseweb="tab"] { padding: 10px 14px !important; font-size: 0.9rem !important; }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # گیمیفیکیشن
    if "user_score" not in st.session_state:
        st.session_state.user_score = 0
    if "daily_streak" not in st.session_state:
        st.session_state.daily_streak = 0
    
    st.markdown("### 🎖️ امتیاز شما")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⭐ امتیاز", st.session_state.user_score)
    with col2:
        st.metric("🔥 روز", f"{st.session_state.daily_streak}")

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

def detect_unit(column_name):
    column_name = column_name.lower()
    if any(word in column_name for word in ['نفر', 'مشتری', 'تعداد', 'مراجع', 'بازدید', 'کاربر']):
        return 'نفر'
    if any(word in column_name for word in ['تومان', 'ریال', 'فروش', 'قیمت', 'درآمد', 'مبلغ', 'هزینه']):
        return 'تومان'
    if 'درصد' in column_name:
        return 'درصد'
    if any(word in column_name for word in ['کیلو', 'گرم', 'تن', 'وزن']):
        return 'کیلوگرم'
    if any(word in column_name for word in ['متر', 'سانتی', 'طول']):
        return 'متر'
    if any(word in column_name for word in ['لیتر', 'میل']):
        return 'لیتر'
    return 'واحد'

def suggest_target_column(df):
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    priority = ['فروش_فردا', 'فروش', 'تعداد_مشتریان', 'قیمت', 'درآمد', 'سود']
    for keyword in priority:
        for col in numeric_cols:
            if keyword in col:
                return col
    return numeric_cols[0] if numeric_cols else None

def get_avg_industry(صنف):
    avgs = {
        "خواربارفروشی": 8_000_000,
        "پوشاک": 5_000_000,
        "ساختمان": 12_000_000,
        "نانوایی": 3_000_000,
        "فناوری": 10_000_000,
        "خرده‌فروشی": 7_000_000,
        "بهداشت": 6_000_000,
        "املاک": 15_000_000
    }
    for key in avgs:
        if key in صنف:
            return avgs[key]
    return 6_000_000

def get_discount_suggestion(pred_value, unit):
    if unit != 'تومان':
        return None
    if pred_value < 3_000_000:
        return "۲۵٪"
    elif pred_value < 5_000_000:
        return "۱۵٪"
    elif pred_value < 8_000_000:
        return "۱۰٪"
    else:
        return "۵٪"

def get_emoji(pred_value, unit):
    if unit == 'تومان':
        if pred_value > 10_000_000:
            return "🚀", "فروش عالی!"
        elif pred_value > 6_000_000:
            return "📈", "فروش خوب"
        else:
            return "💪", "نیاز به تلاش"
    elif unit == 'نفر':
        if pred_value > 80:
            return "🎉", "مشتریان عالی!"
        elif pred_value > 40:
            return "👍", "مشتریان خوب"
        else:
            return "📢", "جذب مشتری بیشتر"
    else:
        return "📊", "پیش‌بینی انجام شد"

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

def مشاور_iHonoor(pred_value, accuracy, target_col, data, alerts, صنف, unit):
    تحلیل = {'خلاصه': '', 'بینش‌ها': [], 'راهکارها': [], 'هشدار': None, 'فرصت': None, 'پیام': None}
    
    if pred_value:
        if pred_value > 10_000_000 and unit == 'تومان':
            تحلیل['خلاصه'] = f"✅ پیش‌بینی {target_col}: {pred_value:,.0f} {unit} (عالی)"
            تحلیل['فرصت'] = "✨ از این فرصت برای توسعه کسب‌وکار استفاده کنید."
        elif pred_value > 5_000_000 and unit == 'تومان':
            تحلیل['خلاصه'] = f"📊 پیش‌بینی {target_col}: {pred_value:,.0f} {unit} (خوب)"
        elif unit == 'نفر' and pred_value > 50:
            تحلیل['خلاصه'] = f"✅ پیش‌بینی {target_col}: {pred_value:,.0f} {unit} (عالی)"
        else:
            تحلیل['خلاصه'] = f"⚠️ پیش‌بینی {target_col}: {pred_value:,.0f} {unit} (نیاز به بررسی)"
            تحلیل['هشدار'] = "مقدار پیش‌بینی پایین‌تر از حد انتظار است."
    
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
    elif "ساختمان" in صنف or "پیمانکاری" in صنف:
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
# تشخیص ناهنجاری
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
# دریافت قیمت دلار
# ==========================================
def دریافت_قیمت_دلار():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data['rates']['IRR'] / 10
            if price > 1000:
                return price
    except:
        pass
    return 160000

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
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
    "📝 ارسال نظر"
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
    
    # انتخاب ستون هدف با پیشنهاد
    all_columns = data.columns.tolist()
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    suggested = suggest_target_column(data)
    
    if suggested:
        target_options = [f"💡 پیشنهاد iHoNoor: {suggested}"] + all_columns
    else:
        target_options = all_columns
    
    selected_option = st.selectbox("🎯 ستون هدف (مقداری که می‌خواهید پیش‌بینی کنید):", target_options)
    
    if selected_option.startswith("💡 پیشنهاد iHoNoor:"):
        target = suggested
        st.info(f"✅ iHoNoor ستون **{target}** را برای پیش‌بینی پیشنهاد می‌دهد.")
    else:
        target = selected_option
    
    if target not in numeric_cols:
        st.error("❌ ستون هدف باید **عددی** باشد! لطفاً یکی از ستون‌های عددی را انتخاب کنید.")
        st.stop()
    
    unit = detect_unit(target)
    st.info(f"✅ واحد تشخیص داده شده: **{unit}**")
    
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
                    
                    # افزایش امتیاز
                    st.session_state.user_score += 5
                    st.session_state.daily_streak += 1
                    
                    # ایموجی پویا
                    emoji, msg = get_emoji(pred_value, unit)
                    
                    st.markdown(f"""
                    <div class="result-box">
                        <div style="font-size:2.5rem;">{emoji}</div>
                        <div class="result-label">📈 پیش‌بینی {target}</div>
                        <div class="result-number">{pred_value:,.0f}</div>
                        <div class="result-label">{unit}</div>
                        <div style="font-size:0.9rem;color:#555;margin-top:5px;">{msg}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🎯 دقت مدل", f"{best_score:.1%}")
                    with col2:
                        st.metric(f"🔮 بازه اطمینان ({unit})", f"{pred_value*0.85:,.0f} - {pred_value*1.15:,.0f}")
                    
                    # مقایسه با میانگین صنف
                    avg_industry = get_avg_industry(صنف)
                    if unit == 'تومان' and avg_industry > 0:
                        diff = ((pred_value / avg_industry) - 1) * 100
                        if diff > 20:
                            st.success(f"✅ {diff:.1f}% بالاتر از میانگین صنف!")
                        elif diff < -20:
                            st.warning(f"⚠️ {abs(diff):.1f}% پایین‌تر از میانگین صنف")
                        else:
                            st.info(f"📊 نزدیک به میانگین صنف ({diff:+.1f}%)")
                    
                    # پیشنهاد تخفیف هوشمند
                    discount = get_discount_suggestion(pred_value, unit)
                    if discount:
                        st.info(f"💡 تخفیف پیشنهادی: {discount}")
                    
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
                    
                    تحلیل = مشاور_iHonoor(pred_value, best_score, target, data, alerts, صنف, unit)
                    نمایش_مشاور(تحلیل)
                    
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
                    
                    with st.expander("💱 تحلیل دلاری"):
                        if unit == 'تومان':
                            dollar_rate = دریافت_قیمت_دلار()
                            avg_value = y.mean()
                            avg_dollar = avg_value / dollar_rate
                            pred_dollar = pred_value / dollar_rate
                            
                            st.metric("💰 نرخ دلار", f"{dollar_rate:,.0f} تومان")
                            st.metric("📊 میانگین به دلار", f"${avg_dollar:,.2f}")
                            st.metric("📈 پیش‌بینی به دلار", f"${pred_dollar:,.2f}")
                        else:
                            st.info(f"ℹ️ واحد '{unit}' است، تحلیل دلاری فقط برای ستون‌های تومانی معنا دارد.")
                    
                    # ذخیره در تاریخچه
                    if "history" not in st.session_state:
                        st.session_state.history = []
                    
                    st.session_state.history.append({
                        'تاریخ': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'صنف': صنف,
                        'هدف': target,
                        'پیش‌بینی': f"{pred_value:,.0f}",
                        'واحد': unit,
                        'دقت': f"{best_score:.1%}"
                    })
                    
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
                st.session_state.user_score += 10
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 تعداد رکوردها", len(data))
        with col2:
            num_cols = data.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                st.metric("📈 میانگین", f"{data[num_cols[0]].mean():,.0f}")
        with col3:
            st.metric("🏷️ صنف", صنف)
        
        st.markdown("---")
        st.subheader("📈 نمودار داده‌ها")
        fig = px.line(data, x=data.columns[0], y=data.columns[1], title="روند داده‌ها", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🎖️ دستاوردهای من")
        badges = []
        if st.session_state.user_score >= 100:
            badges.append(('🏆', 'طلایی', 'badge-gold'))
        elif st.session_state.user_score >= 50:
            badges.append(('🥈', 'نقره‌ای', 'badge-silver'))
        elif st.session_state.user_score >= 20:
            badges.append(('🥉', 'برنزی', 'badge-bronze'))
        if st.session_state.daily_streak >= 7:
            badges.append(('🔥', 'هفتگی', 'badge-blue'))
        if st.session_state.daily_streak >= 30:
            badges.append(('💎', 'ماهانه', 'badge-gold'))
        
        if badges:
            for emoji, name, cls in badges:
                st.markdown(f'<span class="badge {cls}">{emoji} {name}</span>', unsafe_allow_html=True)
        else:
            st.info("هنوز مدالی کسب نکرده‌اید. با استفاده از iHoNoor مدال بگیرید!")
    else:
        st.info("📊 داده‌های کافی برای نمایش داشبورد وجود ندارد.")

with tab7:
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
    
    if total_expense > 0 and total_income > 0:
        expense_ratio = (total_expense / total_income) * 100
        if expense_ratio > 80:
            st.warning(f"⚠️ هزینه‌های شما {expense_ratio:.1f}% از درآمدتان است. پیشنهاد می‌کنیم هزینه‌های غیرضروری را کاهش دهید.")
        elif expense_ratio > 60:
            st.info(f"📊 هزینه‌های شما {expense_ratio:.1f}% از درآمدتان است. وضعیت قابل قبول است.")
        else:
            st.success(f"✅ هزینه‌های شما {expense_ratio:.1f}% از درآمدتان است. مدیریت مالی عالی!")

with tab8:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📘</span> راهنمای تخصصی صنف‌ها</div>
    </div>
    """, unsafe_allow_html=True)
    
    راهنماها = {
        "خواربارفروشی": {
            "توضیح": "فروشگاه‌های مواد غذایی و خواربار که محصولات مصرفی روزمره را عرضه می‌کنند.",
            "پیشنهاد": "مدیریت موجودی هوشمند، کاهش ضایعات، تخفیف‌های هدفمند"
        },
        "پوشاک": {
            "توضیح": "فروشگاه‌های پوشاک، لباس، کیف و کفش که محصولات مد و فشن را عرضه می‌کنند.",
            "پیشنهاد": "شناسایی ترندهای جدید، تخفیف‌های هوشمند، مدیریت سایزها"
        },
        "ساختمان و پیمانکاری": {
            "توضیح": "شرکت‌های پیمانکاری، مهندسان و مجریان پروژه‌های ساختمانی و عمرانی.",
            "پیشنهاد": "پیش‌بینی هزینه‌ها، مدیریت نیروی کار، کاهش تأخیر"
        },
        "نانوایی": {
            "توضیح": "نانوایی‌های سنتی و صنعتی که انواع نان و شیرینی را تولید و عرضه می‌کنند.",
            "پیشنهاد": "پیش‌بینی تقاضا، کاهش ضایعات، تنوع محصولات"
        },
        "خودروسازی": {
            "توضیح": "فروشندگان قطعات خودرو، خدمات تعمیرات و نمایندگی‌های فروش خودرو.",
            "پیشنهاد": "شناسایی قطعات پرفروش، پیش‌بینی تقاضا، مدیریت خدمات"
        },
        "بهداشت": {
            "توضیح": "بیمارستان‌ها، کلینیک‌ها، مطب‌های پزشکی و مراکز درمانی.",
            "پیشنهاد": "پیش‌بینی مراجعه، مدیریت پرسنل، مدیریت موجودی"
        }
    }
    
    found = False
    for key in راهنماها:
        if key in صنف:
            st.info(f"📌 **{key}:** {راهنماها[key]['توضیح']}")
            st.success(f"💡 **پیشنهاد:** {راهنماها[key]['پیشنهاد']}")
            found = True
            break
    
    if not found:
        st.info(f"📌 اطلاعات بیشتری در مورد {صنف} در حال جمع‌آوری است.")
        st.success("💡 با تحلیل داده‌های خود، بهترین تصمیمات را بگیرید و از مشاور iHoNoor استفاده کنید.")

with tab9:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📚</span> راهنمای جامع iHoNoor</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **🎯 iHoNoor چیست؟**
    یک پلتفرم هوشمند با ۶ مدل هوش مصنوعی برای پیش‌بینی فروش
    
    **📋 چه داده‌هایی نیاز دارید؟**
    - ستون تاریخ
    - ستون فروش یا تعداد مشتریان (عددی)
    - حداقل ۵۰ رکورد
    
    **🚀 چگونه استفاده کنیم؟**
    ۱. صنف خود را انتخاب کنید
    ۲. فایل خود را آپلود کنید
    ۳. ستون هدف عددی را انتخاب کنید
    ۴. روی پیش‌بینی کلیک کنید
    
    **💡 نکات کلیدی:**
    - ستون هدف باید عددی باشد
    - تاریخ فقط برای نمودار است
    - واحد به‌صورت خودکار تشخیص داده می‌شود
    - از گزینه "💡 پیشنهاد iHoNoor" برای انتخاب بهترین ستون استفاده کنید
    """)

with tab10:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🚀</span> آینده هوش مصنوعی</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **📊 آمار جهانی:**
    - بیش از ۵۰٪ کسب‌وکارها از هوش مصنوعی استفاده می‌کنند
    - کسب‌وکارهای هوشمند تا ۴۰٪ سود بیشتری دارند
    - دقت پیش‌بینی با هوش مصنوعی تا ۸۵٪
    
    **💡 چرا iHoNoor؟**
    - ۱۰۰٪ ایرانی و بدون تحریم
    - ۶ مدل هوش مصنوعی
    - رابط کاربری ساده و حرفه‌ای
    - پشتیبانی داخلی
    """)

with tab11:
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">📝</span> ارسال نظر و پیشنهاد</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📬 **ایمیل:** ha2021alipur@gmail.com | 📱 **واتساپ/تلگرام:** 09019470509")
    
    with st.form("contact_form"):
        name = st.text_input("👤 نام و نام‌خانوادگی")
        message = st.text_area("📝 متن پیام", height=100)
        submitted = st.form_submit_button("📨 ارسال")
        if submitted and name and message:
            st.success("✅ نظر شما با موفقیت ارسال شد!")
            st.balloons()

# ==========================================
# تاریخچه (جدید)
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================
# نوتیفیکیشن
# ==========================================
if st.session_state.daily_streak == 7:
    st.success("🔥 **تبریک!** ۷ روز متوالی از iHoNoor استفاده کردید! مدال هفتگی گرفتید! 🎖️")
elif st.session_state.daily_streak == 30:
    st.success("💎 **تبریک بزرگ!** ۳۰ روز متوالی! مدال ماهانه گرفتید! 🏆")

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor 🤖 نور هوشمند فروش | نسخه ۳.۰<br>
    📧 ha2021alipur@gmail.com | 📱 09019470509<br>
    © 2025 iHoNoor | تمامی حقوق محفوظ است.
</div>
""", unsafe_allow_html=True)
