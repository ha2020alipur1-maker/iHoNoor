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
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
warnings.filterwarnings('ignore')

# ==========================================
# تنظیمات اولیه
# ==========================================
st.set_page_config(
    page_title="iHoNoor | نور هوشمند کسب‌وکار",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# استایل ساده و کاربرپسند
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    * { font-family: 'Inter', 'Vazirmatn', sans-serif; direction: rtl; }
    .stApp { background: #F5F7FA; }
    
    .main-header {
        background: linear-gradient(135deg, #0D47A1, #1A237E);
        padding: 20px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 900; margin: 0; }
    .main-header h1 .highlight { color: #FFD700; }
    .main-header p { font-size: 1rem; opacity: 0.9; margin-top: 5px; }
    
    .card {
        background: white;
        padding: 18px 22px;
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 15px;
        border: 1px solid #f0f0f0;
    }
    .card-title { font-size: 1rem; font-weight: 700; color: #0D47A1; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
    
    .result-box {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        padding: 20px 25px;
        border-radius: 14px;
        border-right: 5px solid #FFD700;
        text-align: center;
        margin-top: 12px;
    }
    .result-number { font-size: 2.5rem; font-weight: 900; color: #0D47A1; }
    .result-label { font-size: 0.9rem; color: #555; margin-top: 3px; }
    
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 8px 24px !important;
        border: none !important;
    }
    .stButton > button:first-child {
        background: linear-gradient(135deg, #0D47A1, #1A237E) !important;
        color: white !important;
    }
    
    .advisor-box {
        background: linear-gradient(135deg, #0D47A1, #1A237E);
        padding: 15px 20px;
        border-radius: 14px;
        color: white;
        margin-top: 15px;
    }
    
    .quick-guide {
        background: #FFF8E1;
        padding: 12px 18px;
        border-radius: 10px;
        border-right: 4px solid #FFA000;
        margin-bottom: 15px;
        font-size: 0.9rem;
    }
    
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.75rem;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #eee;
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
    
    .steps {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        flex-wrap: wrap;
    }
    .step-item {
        flex: 1;
        min-width: 120px;
        background: white;
        padding: 10px 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    .step-item .num {
        background: #0D47A1;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        margin-bottom: 4px;
    }
    .step-item .text { font-weight: 600; color: #333; font-size: 0.8rem; }
    .step-item .desc { font-size: 0.65rem; color: #888; }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.6rem; }
        .steps { flex-direction: column; }
        .step-item { min-width: 100%; }
        .result-number { font-size: 2rem; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# نقشه صنف‌ها
# ==========================================
INDUSTRY_TITLES = {
    "🏪 خواربارفروشی": "پیش‌بینی فروش خواربارفروشی",
    "🔩 آهن‌آلات و مصالح": "پیش‌بینی قیمت مصالح",
    "🚗 خودروسازی": "پیش‌بینی تقاضای قطعات",
    "👗 پوشاک": "پیش‌بینی فروش پوشاک",
    "🍞 نانوایی": "پیش‌بینی تعداد مشتریان",
    "📱 فناوری": "پیش‌بینی فروش فناوری",
    "🛒 خرده‌فروشی": "پیش‌بینی فروش آنلاین",
    "🏭 تولید و صنایع": "پیش‌بینی تولید صنعتی",
    "💰 بانکداری": "پیش‌بینی تراکنش‌ها",
    "🏥 بهداشت": "پیش‌بینی مراجعه بیماران",
    "🍔 صنایع غذایی": "پیش‌بینی فروش غذایی",
    "⛽ پتروشیمی": "پیش‌بینی قیمت انرژی",
    "⚡ برق": "پیش‌بینی مصرف برق",
    "🏢 املاک": "پیش‌بینی قیمت ملک",
    "🏗️ ساختمان": "پیش‌بینی هزینه پروژه",
    "📦 مدیریت موجودی": "پیش‌بینی موجودی انبار"
}

industries = list(INDUSTRY_TITLES.keys())

def get_industry_title(صنف):
    return INDUSTRY_TITLES.get(صنف, "پیش‌بینی هوشمند")

# ==========================================
# توابع اصلی
# ==========================================
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
    if any(word in column_name for word in ['گالون', 'gallon']):
        return 'گالون'
    if any(word in column_name for word in ['دلار', 'dollar']):
        return 'دلار'
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
    """میانگین ساختگی برای مقایسه صنف"""
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

# ==========================================
# مدل‌ها
# ==========================================
models_dict = {
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "Linear Regression": LinearRegression(),
}

model_names_fa = {
    "Random Forest": "جنگل تصادفی",
    "XGBoost": "ایکس‌جی‌بوست",
    "Gradient Boosting": "گرادیان بوستینگ",
    "Linear Regression": "رگرسیون خطی"
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
        except:
            results[name] = {'error': 'خطا'}
    return results

# ==========================================
# تولید داده نمونه
# ==========================================
def sample_data(صنف):
    np.random.seed(42)
    dates = pd.date_range('1403-01-01', periods=150, freq='D')
    
    base = {
        'تاریخ': dates,
        'فروش_روزانه_تومان': np.random.randint(2_000_000, 15_000_000, 150),
        'تعداد_مشتریان': np.random.randint(20, 120, 150),
        'قیمت_میانگین': np.random.randint(50_000, 200_000, 150),
        'تخفیف_درصد': np.random.randint(0, 30, 150),
    }
    
    if "خواربار" in صنف:
        base['فروش_فردا'] = base['فروش_روزانه_تومان'] + np.random.randint(-2_000_000, 3_000_000, 150)
    elif "پوشاک" in صنف:
        base['فروش_فردا'] = base['فروش_روزانه_تومان'] * np.random.uniform(0.8, 1.3, 150)
    elif "نانوایی" in صنف:
        base['تعداد_مشتریان'] = np.random.randint(50, 200, 150)
        base['فروش_فردا'] = base['فروش_روزانه_تومان'] + np.random.randint(-1_000_000, 2_000_000, 150)
    else:
        base['فروش_فردا'] = base['فروش_روزانه_تومان'] + np.random.randint(-2_000_000, 3_000_000, 150)
    
    base['فروش_فردا'] = np.maximum(base['فروش_فردا'], 500_000)
    return pd.DataFrame(base)

# ==========================================
# سایدبار
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="background:#0D47A1;color:white;padding:15px;border-radius:12px;text-align:center;margin-bottom:15px;">
        <h1 style="font-size:2rem;margin:0;"><span style="color:#FFD700;">iHo</span>Noor</h1>
        <p style="font-size:0.8rem;opacity:0.9;margin:0;">✨ نور هوشمند</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ صنف خود را انتخاب کنید:", industries)
    
    st.markdown("---")
    
    فایل = st.file_uploader("📁 آپلود فایل", type=["csv", "xlsx", "xls"])
    
    # ===== ویژگی جدید: حالت ساده تبلت =====
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
    
    # ===== گیمیفیکیشن ساده =====
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
# بارگذاری داده
# ==========================================
data = None
source = ""

if فایل is not None:
    try:
        data = pd.read_csv(فایل) if فایل.name.endswith('.csv') else pd.read_excel(فایل)
        source = "فایل شما"
        st.success(f"✅ {len(data)} رکورد بارگذاری شد.")
    except:
        st.error("❌ خطا در خواندن فایل")

if data is None:
    data = sample_data(صنف)
    source = "داده‌های نمونه"
    st.info(f"📊 داده‌های نمونه برای {صنف}")

# ==========================================
# هدر اصلی
# ==========================================
industry_title = get_industry_title(صنف)

st.markdown(f"""
<div class="main-header">
    <h1><span class="highlight">iHo</span>Noor</h1>
    <p>✨ {industry_title}</p>
</div>
""", unsafe_allow_html=True)

# ===== راهنمای سریع (ویژگی جدید) =====
st.markdown("""
<div class="quick-guide">
    🚀 <strong>چگونه کار کنیم؟</strong>
    صنف ← آپلود فایل ← انتخاب ستون هدف ← کلیک پیش‌بینی
</div>
""", unsafe_allow_html=True)

# ==========================================
# قدم‌های راهنما
# ==========================================
st.markdown("""
<div class="steps">
    <div class="step-item"><div class="num">۱</div><div class="text">انتخاب صنف</div><div class="desc">از منوی کناری</div></div>
    <div class="step-item"><div class="num">۲</div><div class="text">آپلود فایل</div><div class="desc">Excel یا CSV</div></div>
    <div class="step-item"><div class="num">۳</div><div class="text">پیش‌بینی</div><div class="desc">دریافت نتیجه</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# تب‌های ساده
# ==========================================
tab1, tab2 = st.tabs(["📊 تحلیل و پیش‌بینی", "📜 تاریخچه"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><div class="card-title">📋 نمونه داده</div>', unsafe_allow_html=True)
        st.dataframe(data.head(5))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><div class="card-title">📊 خلاصه</div>', unsafe_allow_html=True)
        st.dataframe(data.describe())
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== انتخاب ستون هدف با پیشنهاد =====
    all_columns = data.columns.tolist()
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    suggested = suggest_target_column(data)
    
    if suggested:
        target_options = [f"💡 پیشنهاد: {suggested}"] + all_columns
    else:
        target_options = all_columns
    
    selected_option = st.selectbox("🎯 ستون هدف (چی رو پیش‌بینی کنم؟)", target_options)
    
    if selected_option.startswith("💡 پیشنهاد:"):
        target = suggested
        st.info(f"✅ ستون **{target}** پیشنهاد میشود.")
    else:
        target = selected_option
    
    if target not in numeric_cols:
        st.error("❌ ستون هدف باید عددی باشد!")
        st.stop()
    
    unit = detect_unit(target)
    st.info(f"✅ واحد: **{unit}**")
    
    # ===== دکمه‌های پیش‌بینی =====
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 پیش‌بینی کن", type="primary", use_container_width=True):
            with st.spinner("⏳ در حال پیش‌بینی..."):
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
                        st.error("❌ ویژگی عددی کافی نیست.")
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
                        
                        # ===== ایموجی پویا (ویژگی جدید) =====
                        emoji, msg = get_emoji(pred_value, unit)
                        
                        st.markdown(f"""
                        <div class="result-box">
                            <div style="font-size:2.5rem;">{emoji}</div>
                            <div class="result-label">{msg}</div>
                            <div class="result-number">{pred_value:,.0f}</div>
                            <div class="result-label">{unit}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎯 دقت", f"{best_score:.1%}")
                        with col2:
                            st.metric(f"🔮 بازه", f"{pred_value*0.85:,.0f} - {pred_value*1.15:,.0f}")
                        with col3:
                            st.metric("🏆 مدل", model_names_fa.get(best_model, best_model))
                        
                        # ===== مقایسه با میانگین صنف (ویژگی جدید) =====
                        avg_industry = get_avg_industry(صنف)
                        if unit == 'تومان' and avg_industry > 0:
                            diff = ((pred_value / avg_industry) - 1) * 100
                            if diff > 20:
                                st.success(f"✅ {diff:.1f}% بالاتر از میانگین صنف!")
                            elif diff < -20:
                                st.warning(f"⚠️ {abs(diff):.1f}% پایین‌تر از میانگین صنف")
                            else:
                                st.info(f"📊 نزدیک به میانگین صنف ({diff:+.1f}%)")
                        
                        # ===== پیشنهاد تخفیف هوشمند (ویژگی جدید) =====
                        discount = get_discount_suggestion(pred_value, unit)
                        if discount:
                            st.info(f"💡 تخفیف پیشنهادی: {discount}")
                        
                        # ===== اهمیت ویژگی‌ها =====
                        if hasattr(model, 'feature_importances_'):
                            with st.expander("📊 اهمیت ویژگی‌ها"):
                                imp_df = pd.DataFrame({
                                    'ویژگی': X.columns,
                                    'اهمیت': model.feature_importances_
                                }).sort_values('اهمیت', ascending=False)
                                st.dataframe(imp_df)
                        
                        # ===== مشاور iHoNoor =====
                        st.markdown("""
                        <div class="advisor-box">
                            <strong>✨ مشاور iHoNoor</strong>
                            <p style="font-size:0.9rem;opacity:0.9;margin-top:5px;">
                                با توجه به پیش‌بینی، موجودی خود را مدیریت کنید و برای روزهای آینده برنامه‌ریزی داشته باشید.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # ===== ذخیره در تاریخچه (ویژگی جدید) =====
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
    
    with col2:
        if st.button("⚡ پیش‌بینی خودکار", use_container_width=True):
            # خودکار: انتخاب بهترین ستون و بهترین مدل
            auto_target = suggest_target_column(data)
            if auto_target:
                st.info(f"✅ ستون انتخاب شد: {auto_target}")
                # دوباره اجرا با ستون پیشنهادی
                # (این بخش ساده شده)

with tab2:
    st.markdown("""
    <div class="card">
        <div class="card-title">📜 تاریخچه پیش‌بینی‌ها</div>
    </div>
    """, unsafe_allow_html=True)
    
    if "history" not in st.session_state or len(st.session_state.history) == 0:
        st.info("📭 هنوز پیش‌بینی انجام نداده‌اید.")
    else:
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)
        
        if st.button("🗑️ پاک کردن تاریخچه"):
            st.session_state.history = []
            st.rerun()

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor | ha2021alipur@gmail.com | 09019470509
</div>
""", unsafe_allow_html=True)
