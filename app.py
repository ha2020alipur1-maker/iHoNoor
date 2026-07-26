import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import random
warnings.filterwarnings('ignore')

# ==========================================
# تنظیمات اولیه
# ==========================================
st.set_page_config(
    page_title="iHoNoor Pro | هوش مصنوعی فروش",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# استایل حرفه‌ای
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * { direction: rtl; font-family: 'Inter', 'Vazirmatn', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0A0E1A 0%, #141B2D 50%, #1A2340 100%); }
    
    .main-header {
        background: linear-gradient(135deg, #0A1628, #1A2A5C, #0A1628);
        padding: 30px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid rgba(255,215,0,0.08);
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        position: relative; overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,215,0,0.03), transparent 60%);
        animation: rotateGlow 30s linear infinite;
        pointer-events: none;
    }
    @keyframes rotateGlow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .main-header h1 {
        font-size: 3rem; font-weight: 800; margin: 0;
        background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: goldShine 4s ease-in-out infinite alternate;
    }
    @keyframes goldShine { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }
    .main-header p { opacity: 0.7; margin-top: 5px; color: rgba(255,255,255,0.6); }
    .main-header .badge {
        background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.1);
        padding: 4px 16px; border-radius: 40px; font-size: 0.7rem; display: inline-block; margin: 4px; color: #FFD700;
    }
    .main-header .status-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        background: #4CAF50; margin-right: 6px; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } 100% { opacity: 1; transform: scale(1); } }
    
    .card {
        background: rgba(255,255,255,0.02); backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.04); border-radius: 16px;
        padding: 20px 24px; margin-bottom: 16px; color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; overflow: hidden;
    }
    .card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
        opacity: 0; transition: opacity 0.3s ease;
    }
    .card:hover::before { opacity: 1; }
    .card:hover { border-color: rgba(255,215,0,0.08); transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.3); }
    .card-title { font-size: 1rem; font-weight: 700; color: #FFD700; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
    
    .result-box {
        background: linear-gradient(135deg, rgba(255,215,0,0.03), rgba(255,165,0,0.01));
        border: 1px solid rgba(255,215,0,0.06); border-radius: 16px;
        padding: 25px 30px; text-align: center; margin-top: 12px; position: relative; overflow: hidden;
    }
    .result-box::after {
        content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #FFD700, #FFA500);
    }
    .result-number {
        font-size: 3.2rem; font-weight: 900;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: numberPulse 3s infinite ease-in-out;
    }
    @keyframes numberPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
    .result-label { color: rgba(255,255,255,0.4); font-size: 0.9rem; margin-top: 4px; }
    
    .stButton > button {
        background: linear-gradient(135deg, rgba(255,215,0,0.08), rgba(255,165,0,0.02)) !important;
        border: 1px solid rgba(255,215,0,0.1) !important; border-radius: 12px !important;
        padding: 12px 32px !important; color: #FFD700 !important; font-weight: 600 !important;
        width: 100% !important; transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        border-color: rgba(255,215,0,0.2) !important;
        box-shadow: 0 0 40px rgba(255,215,0,0.03) !important; transform: translateY(-2px);
    }
    
    .metric-card {
        background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px; padding: 14px 18px; text-align: center; color: white;
        transition: all 0.3s ease; position: relative; overflow: hidden;
    }
    .metric-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #FFD700, transparent); opacity: 0; transition: opacity 0.3s ease;
    }
    .metric-card:hover::before { opacity: 1; }
    .metric-card:hover { background: rgba(255,255,255,0.04); transform: translateY(-2px); }
    .metric-card .value { font-size: 1.8rem; font-weight: 700; color: #FFD700; letter-spacing: -0.5px; }
    .metric-card .label { font-size: 0.7rem; color: rgba(255,255,255,0.3); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .step-item {
        background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px; padding: 12px 16px; text-align: center; flex: 1; min-width: 80px;
        transition: all 0.3s ease;
    }
    .step-item:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,215,0,0.05); }
    .step-item .num {
        display: inline-block; width: 28px; height: 28px;
        background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.05);
        border-radius: 50%; line-height: 28px; color: #FFD700; font-weight: 700; font-size: 0.8rem;
    }
    .step-item:hover .num { background: rgba(255,215,0,0.15); border-color: rgba(255,215,0,0.1); }
    .step-item .text { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 4px; }
    .steps { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
    
    .sidebar-logo {
        background: linear-gradient(135deg, rgba(10,22,40,0.8), rgba(26,42,92,0.6));
        padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 16px;
        border: 1px solid rgba(255,215,0,0.03); backdrop-filter: blur(10px);
    }
    .sidebar-logo h1 { font-size: 1.8rem; margin: 0; background: linear-gradient(135deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sidebar-logo p { color: rgba(255,255,255,0.15); font-size: 0.7rem; margin: 0; letter-spacing: 2px; }
    
    .chat-message { padding: 10px 16px; border-radius: 12px; margin-bottom: 6px; max-width: 80%; animation: fadeInUp 0.3s ease-out; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .chat-user { background: rgba(255,215,0,0.04); border: 1px solid rgba(255,215,0,0.03); margin-right: auto; color: white; }
    .chat-bot { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.02); margin-left: auto; color: rgba(255,255,255,0.6); }
    
    .agent-box {
        background: linear-gradient(135deg, rgba(76,175,80,0.03), rgba(33,150,243,0.02));
        border: 1px solid rgba(76,175,80,0.05); border-radius: 16px; padding: 18px 22px; margin-top: 12px;
    }
    .agent-box .agent-title { color: #4CAF50; font-weight: 700; display: flex; align-items: center; gap: 10px; }
    .agent-box .agent-task { color: rgba(255,255,255,0.5); font-size: 0.85rem; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.02); }
    
    .what-if-box {
        background: linear-gradient(135deg, rgba(255,152,0,0.03), rgba(255,215,0,0.02));
        border: 1px solid rgba(255,152,0,0.05); border-radius: 16px; padding: 18px 22px; margin-top: 12px;
    }
    .what-if-box .what-if-title { color: #FF9800; font-weight: 700; display: flex; align-items: center; gap: 10px; }
    
    .footer { text-align: center; color: rgba(255,255,255,0.05); font-size: 0.65rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.01); letter-spacing: 1px; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.05); border-radius: 10px; }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .result-number { font-size: 2.4rem; }
        .metric-card .value { font-size: 1.4rem; }
        .steps { flex-direction: column; }
        .step-item { min-width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# هدر
# ==========================================
st.markdown("""
<div class="main-header">
    <div style="display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;">
        <h1>✨ iHoNoor</h1>
        <span style="background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.05);padding:2px 12px;border-radius:40px;font-size:0.6rem;color:#FFD700;">PRO</span>
    </div>
    <p>هوش مصنوعی پیش‌بینی و تحلیل فروش</p>
    <div>
        <span class="badge"><span class="status-dot"></span>سیستم فعال</span>
        <span class="badge">🧠 ۴ مدل AI</span>
        <span class="badge">🤖 دستیار هوشمند</span>
        <span class="badge">📊 تحلیل سرنخ‌ها</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# مراحل
# ==========================================
st.markdown("""
<div class="steps">
    <div class="step-item"><span class="num">۱</span><div class="text">انتخاب صنف</div></div>
    <div class="step-item"><span class="num">۲</span><div class="text">آپلود فایل</div></div>
    <div class="step-item"><span class="num">۳</span><div class="text">پیش‌بینی</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# صنف‌ها
# ==========================================
industries = [
    "خواربارفروشی", "آهن‌آلات", "خودرو", "پوشاک",
    "فناوری", "خرده‌فروشی", "تولید", "بانکداری",
    "بهداشت", "صنایع غذایی", "پتروشیمی", "برق",
    "املاک", "ساختمان", "مدیریت موجودی"
]

# ==========================================
# سایدبار
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>iHo<span style="color:#FFD700;">Noor</span></h1>
        <p>✨ هوش مصنوعی فروش</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ انتخاب صنف", industries)
    
    st.markdown("---")
    
    فایل = st.file_uploader("📁 آپلود فایل", type=["csv", "xlsx", "xls"])
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:10px;padding:12px;text-align:center;">
        <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;margin:0;">
            ⚡ وضعیت: <span style="color:#4CAF50;">فعال</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تولید داده نمونه
# ==========================================
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    return pd.DataFrame({
        'تاریخ': dates,
        'فروش': np.random.randint(1_000_000, 10_000_000, 100),
        'تعداد_مشتریان': np.random.randint(10, 100, 100),
        'قیمت': np.random.randint(10_000, 50_000, 100),
        'تخفیف': np.random.randint(0, 30, 100)
    })

# ==========================================
# بارگذاری داده
# ==========================================
data = None

if فایل:
    try:
        data = pd.read_csv(فایل) if فایل.name.endswith('.csv') else pd.read_excel(فایل)
        st.success(f"✅ {len(data)} رکورد بارگذاری شد.")
    except:
        st.error("❌ خطا در خواندن فایل")

if data is None:
    data = generate_sample_data()
    st.info("📊 داده‌های نمونه بارگذاری شد.")

# ==========================================
# نمایش داده
# ==========================================
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><div class="card-title">📋 نمونه داده</div>', unsafe_allow_html=True)
    st.dataframe(data.head(5), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 خلاصه آمار</div>', unsafe_allow_html=True)
    st.dataframe(data.describe(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# انتخاب ستون هدف
# ==========================================
numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
all_cols = data.columns.tolist()

suggested = "فروش" if "فروش" in all_cols else numeric_cols[0] if numeric_cols else None

options = [f"💡 پیشنهاد: {suggested}"] + all_cols if suggested else all_cols
selected = st.selectbox("🎯 ستون هدف (چی رو پیش‌بینی کنم؟)", options)

if selected.startswith("💡 پیشنهاد:"):
    target = suggested
    st.info(f"✅ iHoNoor ستون **{target}** را پیشنهاد میکند.")
else:
    target = selected

if target not in numeric_cols:
    st.error("❌ ستون هدف باید عددی باشد!")
    st.stop()

def detect_unit(col):
    col = col.lower()
    if any(w in col for w in ['نفر', 'مشتری', 'تعداد']): return 'نفر'
    if any(w in col for w in ['تومان', 'ریال', 'فروش', 'قیمت', 'درآمد']): return 'تومان'
    if 'درصد' in col: return 'درصد'
    return 'واحد'

unit = detect_unit(target)
st.info(f"✅ واحد تشخیص داده شده: **{unit}**")

# ==========================================
# داشبورد مدیریتی
# ==========================================
st.subheader("📊 داشبورد مدیریتی")

total_records = len(data)
numeric_columns = len(numeric_cols)
avg_target = data[target].mean() if target in data else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{total_records:,}</div>
        <div class="label">تعداد رکوردها</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{numeric_columns}</div>
        <div class="label">ستون‌های عددی</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{avg_target:,.0f}</div>
        <div class="label">میانگین {target}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{صنف}</div>
        <div class="label">صنف انتخابی</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# انتخاب مدل
# ==========================================
st.subheader("🧠 انتخاب مدل")

models = {
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "Linear Regression": LinearRegression()
}
selected_model_name = st.selectbox("انتخاب مدل:", list(models.keys()))

# ==========================================
# بازه زمانی
# ==========================================
forecast_days = st.selectbox(
    "📅 چند روز آینده؟",
    [1, 3, 7, 14, 30],
    format_func=lambda x: f"{x} روز"
)

# ==========================================
# دکمه پیش‌بینی
# ==========================================
if st.button("🚀 پیش‌بینی", type="primary", use_container_width=True):
    with st.spinner("⏳ در حال تحلیل..."):
        start_time = time.time()
        try:
            le = LabelEncoder()
            scaler = StandardScaler()
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
            
            X_scaled = scaler.fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            
            model = models[selected_model_name]
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            avg_row = X.mean().values.reshape(1, -1)
            predictions = []
            current_row = avg_row.copy()
            
            for day in range(forecast_days):
                pred = model.predict(current_row)[0]
                predictions.append(pred)
                if len(X.columns) > 0:
                    current_row[0] = pred
            
            # نمایش نتیجه
            st.markdown(f"""
            <div class="result-box">
                <div class="result-label">پیش‌بینی {forecast_days} روز آینده</div>
                <div class="result-number">{predictions[-1]:,.0f}</div>
                <div class="result-label">{unit} (آخرین روز)</div>
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.2);margin-top:6px;">⏱️ {time.time()-start_time:.2f} ثانیه</div>
            </div>
            """, unsafe_allow_html=True)
            
            # نمایش دقت
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🎯 دقت (R²)", f"{score:.1%}")
            with col2:
                st.metric("📊 خطای مطلق", f"{mae:,.0f} {unit}")
            
            # جدول پیش‌بینی
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
            
            # نمودار
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
                title='روند پیش‌بینی',
                xaxis_title='تاریخ',
                yaxis_title=unit,
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.success("✅ پیش‌بینی با موفقیت انجام شد!")
            
        except Exception as e:
            st.error(f"❌ خطا: {e}")

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor Pro | هوش مصنوعی فروش | ha2021alipur@gmail.com | 09019470509
</div>
""", unsafe_allow_html=True)
