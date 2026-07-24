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

# ==========================================
# تنظیمات مدیر
# ==========================================
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
    
    .dashboard-card {
        background: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
        text-align: center;
    }
    .dashboard-card .number { font-size: 2rem; font-weight: 900; color: #0D47A1; }
    .dashboard-card .label { font-size: 0.85rem; color: #666; margin-top: 5px; }
    
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
    
    .referral-box {
        background: #E8F5E9;
        padding: 15px 20px;
        border-radius: 12px;
        border-right: 4px solid #4CAF50;
        margin-bottom: 15px;
    }
    .referral-box .code {
        font-size: 1.5rem;
        font-weight: 900;
        color: #0D47A1;
        letter-spacing: 4px;
    }
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
    "🏪 خواربارفروشی", "🔩 آهن‌آلات و مصالح", "🚗 خودروسازی و لوازم یدکی",
    "👗 پوشاک", "🍞 نانوایی", "📱 فناوری و مخابرات",
    "🛒 خرده‌فروشی و آنلاین", "🏭 تولید و صنایع", "💰 بانکداری و مالی",
    "🏥 بهداشت و درمان", "🍔 صنایع غذایی", "⛽ پتروشیمی و انرژی",
    "⚡ برق و نیروگاه‌ها", "🎬 سینما و محصولات فرهنگی",
    "🏭 تولید و صنایع غذایی (تخصصی)", "🏢 املاک و مستغلات",
    "🏗️ ساختمان و پیمانکاری", "🏭 تولید سفارشی (Make-to-Order)",
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
            'فروش': np.random.randint(1_000_000, 10_000_000, 200),
            'مشتریان': np.random.randint(10, 100, 200),
            'قیمت': np.random.randint(10_000, 50_000, 200),
            'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)
        })
    elif صنف == "🏗️ ساختمان و پیمانکاری":
        return pd.DataFrame({
            'تاریخ': dates,
            'فروش': np.random.randint(5_000_000, 20_000_000, 200),
            'مشتریان': np.random.randint(5, 30, 200),
            'قیمت': np.random.randint(100_000, 500_000, 200),
            'فروش_فردا': np.random.randint(5_000_000, 25_000_000, 200)
        })
    else:
        return pd.DataFrame({
            'تاریخ': dates,
            'فروش': np.random.randint(1_000_000, 10_000_000, 200),
            'مشتریان': np.random.randint(10, 100, 200),
            'قیمت': np.random.randint(10_000, 50_000, 200),
            'فروش_فردا': np.random.randint(1_000_000, 12_000_000, 200)
        })

# ==========================================
# مدل‌ها
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
# ===== ورود مدیر =====
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

# ==========================================
# ===== مدیریت کاربران =====
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
# ===== داشبورد مدیریتی =====
# ==========================================

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
# ===== PWA نصب روی گوشی =====
# ==========================================

def show_pwa_install():
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
    
    <div style="background: #FFF8E1; padding: 15px; border-radius: 12px; border-right: 4px solid #FFA000;">
        <p><strong>💡 نکته:</strong> پس از نصب، آیکون iHoNoor روی صفحه اصلی دستگاه شما ظاهر می‌شود و مانند یک اپلیکیشن واقعی باز می‌شود.</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ===== تقویم شمسی =====
# ==========================================

def show_shamsi_calendar():
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

# ==========================================
# ===== سیستم ارجاع =====
# ==========================================

def generate_referral_code():
    if "user_id" not in st.session_state:
        import uuid
        st.session_state.user_id = str(uuid.uuid4())[:8]
    return f"iHN-{st.session_state.user_id.upper()}"

def show_referral_system():
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="icon">🤝</span> سیستم ارجاع iHoNoor</div>
        <p>دوستان خود را دعوت کنید و پاداش دریافت کنید!</p>
    </div>
    """, unsafe_allow_html=True)
    
    referral_code = generate_referral_code()
    
    st.markdown(f"""
    <div class="referral-box">
        <p style="margin: 0;">🔑 <strong>کد ارجاع شما:</strong></p>
        <div class="code">{referral_code}</div>
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
    
    st.markdown("""
    <div style="background: #F5F5F5; padding: 15px; border-radius: 12px; margin-top: 15px;">
        <p style="margin: 0;"><strong>📤 اشتراک‌گذاری:</strong></p>
        <p style="margin: 5px 0; font-size: 0.9rem; color: #666;">کد ارجاع خود را در شبکه‌های اجتماعی به اشتراک بگذارید.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📖 راهنما",
    "📊 تحلیل و پیش‌بینی",
    "📱 نصب روی گوشی",
    "📅 تقویم شمسی",
    "🤝 سیستم ارجاع",
    "👤 داشبورد کاربری",
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
    show_pwa_install()

with tab4:
    show_shamsi_calendar()

with tab5:
    show_referral_system()

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
