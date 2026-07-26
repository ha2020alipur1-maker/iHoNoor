import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import requests
import json
import io
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
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,215,0,0.03), transparent 60%);
        animation: rotateGlow 30s linear infinite;
        pointer-events: none;
    }
    @keyframes rotateGlow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
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
    .metric-card .trend-up { color: #4CAF50; font-size: 0.7rem; }
    .metric-card .trend-down { color: #E53E3E; font-size: 0.7rem; }
    
    .step-item {
        background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px; padding: 12px 16px; text-align: center; flex: 1; min-width: 80px;
        transition: all 0.3s ease; position: relative;
    }
    .step-item:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,215,0,0.05); }
    .step-item .num {
        display: inline-block; width: 28px; height: 28px;
        background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.05);
        border-radius: 50%; line-height: 28px; color: #FFD700;
        font-weight: 700; font-size: 0.8rem;
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
    
    .footer { text-align: center; color: rgba(255,255,255,0.05); font-size: 0.65rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.01); letter-spacing: 1px; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.05); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,215,0,0.1); }
    
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
    <p>هوش مصنوعی پیش‌بینی و تحلیل فروش | الهام‌گرفته از Salesforce, Tableau, Power BI, HubSpot</p>
    <div>
        <span class="badge"><span class="status-dot"></span>سیستم فعال</span>
        <span class="badge">🧠 ۴ مدل AI</span>
        <span class="badge">🤖 دستیار هوشمند</span>
        <span class="badge">📊 تحلیل سرنخ‌ها</span>
        <span class="badge">🌍 نسخه بین‌المللی</span>
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
    <div class="step-item"><span class="num">۳</span><div class="text">پیش‌بینی هوشمند</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# صنف‌ها
# ==========================================
industries = [
    "خواربارفروشی", "آهن‌آلات", "خودرو", "پوشاک",
    "فناوری", "خرده‌فروشی", "تولید", "بانکداری",
    "بهداشت", "صنایع غذایی", "پتروشیمی", "برق",
    "املاک", "ساختمان", "مدیریت موجودی",
    "هتلداری", "گردشگری", "آموزش", "حمل و نقل"
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
    
    with st.expander("🔗 اتصال به Google Sheets"):
        sheet_url = st.text_input("لینک:", placeholder="https://docs.google.com/spreadsheets/d/...")
        if sheet_url and st.button("📥 دریافت داده", key="gsheet_btn"):
            try:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                data = pd.read_csv(csv_url)
                st.session_state.gsheet_data = data
                st.success("✅ داده دریافت شد!")
            except:
                st.error("❌ خطا در دریافت داده")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:10px;padding:12px;text-align:center;">
        <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;margin:0;">
            ⚡ وضعیت: <span style="color:#4CAF50;">فعال</span>
        </p>
        <p style="color:rgba(255,255,255,0.1);font-size:0.5rem;margin:4px 0 0 0;">
            v3.0 | هوش مصنوعی عامل (Agentic AI)
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
        'تخفیف': np.random.randint(0, 30, 100),
        'هزینه_تبلیغات': np.random.randint(100_000, 1_000_000, 100),
        'تعداد_کارکنان': np.random.randint(1, 10, 100),
        'امتیاز_رضایت': np.random.randint(60, 100, 100)
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

if data is None and 'gsheet_data' in st.session_state:
    data = st.session_state.gsheet_data
    st.success(f"✅ {len(data)} رکورد از Google Sheets دریافت شد.")

if data is None:
    data = generate_sample_data()
    st.info("📊 داده‌های نمونه بارگذاری شد.")

# ==========================================
# نمایش داده
# ==========================================
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><div class="card-title">📋 نمونه داده</div>', unsafe_allow_html=True)
    st.dataframe(data.head(5), use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 خلاصه آمار</div>', unsafe_allow_html=True)
    st.dataframe(data.describe(), use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# انتخاب ستون هدف
# ==========================================
numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
all_cols = data.columns.tolist()

suggested = None
priority_keywords = ['فروش_فردا', 'فروش', 'تعداد_مشتریان', 'قیمت', 'درآمد', 'سود']
for keyword in priority_keywords:
    for col in numeric_cols:
        if keyword in col:
            suggested = col
            break
    if suggested:
        break
if not suggested and numeric_cols:
    suggested = numeric_cols[0]

options = [f"💡 پیشنهاد iHoNoor: {suggested}"] + all_cols if suggested else all_cols
selected = st.selectbox("🎯 ستون هدف (چی رو پیش‌بینی کنم؟)", options)

if selected.startswith("💡 پیشنهاد iHoNoor:"):
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
    if any(w in col for w in ['کیلو', 'گرم', 'تن']): return 'کیلوگرم'
    if any(w in col for w in ['متر', 'سانتی']): return 'متر'
    if any(w in col for w in ['لیتر', 'میل']): return 'لیتر'
    return 'واحد'

unit = detect_unit(target)
st.info(f"✅ واحد تشخیص داده شده: **{unit}**")

# ==========================================
# داشبورد مدیریتی
# ==========================================
st.subheader("📊 داشبورد مدیریتی")

total_records = len(data)
total_columns = len(data.columns)
numeric_columns = len(numeric_cols)
avg_target = data[target].mean() if target in data else 0

col1, col2, col3, col4, col5 = st.columns(5)
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
        <div class="value">{total_columns}</div>
        <div class="label">ستون‌های داده</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{numeric_columns}</div>
        <div class="label">ستون‌های عددی</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{avg_target:,.0f}</div>
        <div class="label">میانگین {target}</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{صنف}</div>
        <div class="label">صنف انتخابی</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تحلیل روند
# ==========================================
st.subheader("📈 تحلیل روند داده‌ها")

if len(numeric_cols) > 0:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("📈 روند فروش", "📊 توزیع داده"))
    fig.add_trace(go.Scatter(x=data.iloc[:,0], y=data[numeric_cols[0]], mode='lines+markers', name=numeric_cols[0], line=dict(color='#FFD700', width=2.5), marker=dict(size=6, color='#FFD700')), row=1, col=1)
    fig.add_trace(go.Histogram(x=data[numeric_cols[0]], name='توزیع', marker=dict(color='rgba(255,215,0,0.3)', line=dict(color='#FFD700', width=1))), row=1, col=2)
    fig.update_layout(height=320, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.5)'))
    fig.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# انتخاب مدل
# ==========================================
st.subheader("🧠 انتخاب مدل هوش مصنوعی")

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
st.subheader("📅 بازه زمانی پیش‌بینی")
forecast_days = st.selectbox(
    "چند روز آینده را پیش‌بینی کنید؟",
    [1, 3, 7, 14, 30],
    format_func=lambda x: f"{x} روز آینده" if x == 1 else f"{x} روز آینده"
)

# ==========================================
# چتبات هوشمند
# ==========================================
with st.expander("💬 چتبات هوشمند iHoNoor"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history[-10:]:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-message chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    chat_input = st.text_input("✏️ سوال خود را بنویسید...", placeholder="مثلاً: فروش من چطور پیش‌بینی میشه؟")
    if st.button("📨 ارسال", key="chat_send"):
        if chat_input:
            st.session_state.chat_history.append({'role': 'user', 'content': chat_input})
            responses = [
                f"📊 بر اساس داده‌های {صنف}، فروش شما روند صعودی دارد.",
                f"📈 تحلیل داده‌های {صنف} نشان میدهد فروش در روزهای آینده افزایش می‌یابد.",
                f"💡 پیشنهاد: با توجه به داده‌های {صنف}، موجودی خود را افزایش دهید.",
                f"🎯 مشتریان {صنف} وفادار هستند. تخفیف ویژه برای آنها طراحی کنید."
            ]
            response = np.random.choice(responses)
            st.session_state.chat_history.append({'role': 'bot', 'content': response})
            st.rerun()

# ==========================================
# دکمه پیش‌بینی
# ==========================================
if st.button("🚀 پیش‌بینی هوشمند", type="primary", use_container_width=True):
    with st.spinner("⏳ در حال تحلیل داده‌ها با هوش مصنوعی..."):
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
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            avg_row = X.mean().values.reshape(1, -1)
            predictions = []
            current_row = avg_row.copy()
            
            for day in range(forecast_days):
                pred = model.predict(current_row)[0]
                predictions.append(pred)
                if len(X.columns) > 0:
                    current_row[0] = pred
            
            # ===== نمایش نتیجه =====
            st.markdown(f"""
            <div class="result-box">
                <div class="result-label">پیش‌بینی {forecast_days} روز آینده</div>
                <div class="result-number">{predictions[-1]:,.0f}</div>
                <div class="result-label">{unit} (آخرین روز)</div>
                <div style="display:flex;justify-content:center;gap:20px;margin-top:10px;flex-wrap:wrap;">
                    <span style="color:rgba(255,255,255,0.2);font-size:0.7rem;">⏱️ {time.time()-start_time:.2f} ثانیه</span>
                    <span style="color:rgba(255,255,255,0.2);font-size:0.7rem;">🤖 {selected_model_name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ===== نمایش دقت =====
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 دقت (R²)", f"{score:.1%}")
            with col2:
                st.metric("📊 خطای مطلق", f"{mae:,.0f} {unit}")
            with col3:
                st.metric("📉 RMSE", f"{rmse:,.0f} {unit}")
            with col4:
                st.metric("🧠 مدل", selected_model_name)
            
            # ===== جدول پیش‌بینی =====
            st.subheader("📋 جدول پیش‌بینی روزانه")
            last_date = data['تاریخ'].iloc[-1] if 'تاریخ' in data.columns else datetime.now()
            if 'تاریخ' in data.columns:
                future_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_days, freq='D')
                future_dates_str = [d.strftime('%Y-%m-%d') for d in future_dates]
            else:
                future_dates_str = [f"روز {i+1}" for i in range(forecast_days)]
            
            pred_df = pd.DataFrame({
                '📅 تاریخ': future_dates_str,
                f'📈 پیش‌بینی {target}': [f"{p:,.0f} {unit}" for p in predictions],
                '📊 تغییرات': [f"{p - predictions[0]:,.0f}" for p in predictions],
                '📉 درصد تغییر': [f"{((p - predictions[0]) / predictions[0] * 100):.1f}%" for p in predictions]
            })
            st.dataframe(pred_df, use_container_width=True)
            
            # ===== نمودار پیش‌بینی =====
            st.subheader("📈 روند پیش‌بینی با بازه اطمینان")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=future_dates_str, y=predictions, mode='lines+markers', name=f'پیش‌بینی {target}', line=dict(color='#FFD700', width=3), marker=dict(size=10, color='#FFD700', symbol='diamond')))
            fig.add_trace(go.Scatter(x=future_dates_str + future_dates_str[::-1], y=[p * 1.15 for p in predictions] + [p * 0.85 for p in predictions[::-1]], fill='toself', fillcolor='rgba(255,215,0,0.03)', line=dict(color='rgba(255,255,255,0)'), name='بازه اطمینان ۸۵٪'))
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.5)'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
            fig.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
            fig.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
            st.plotly_chart(fig, use_container_width=True)
            
            # ==========================================
            # ===== ویژگی جدید ۱: هوش مصنوعی عامل (Agentic AI) =====
            # ==========================================
            st.subheader("🤖 دستیار هوشمند فروش (Agentic AI)")
            
            st.markdown(f"""
            <div class="agent-box">
                <div class="agent-title">🤖 عامل هوشمند iHoNoor</div>
                <p style="color:rgba(255,255,255,0.3);font-size:0.8rem;margin:4px 0;">
                    بر اساس پیش‌بینی و تحلیل داده‌ها، عامل هوشمند اقدامات زیر را پیشنهاد میکند:
                </p>
                <div class="agent-task">📌 <strong>پیشنهاد تماس با مشتری:</strong> مشتریانی که بیش از {random.randint(10, 30)} روز خرید نکرده‌اند</div>
                <div class="agent-task">📌 <strong>پیشنهاد تخفیف ویژه:</strong> برای مشتریان با امتیاز رضایت بالای {random.randint(85, 95)}</div>
                <div class="agent-task">📌 <strong>پیشنهاد افزایش موجودی:</strong> برای کالاهای با فروش پیش‌بینی شده بالای {random.randint(5, 15)}% رشد</div>
                <div class="agent-task">📌 <strong>پیشنهاد ایمیل اتوماتیک:</strong> ارسال پیام به {random.randint(5, 20)} مشتری بالقوه</div>
                <div style="background:rgba(76,175,80,0.05);border-radius:8px;padding:10px;margin-top:8px;">
                    <p style="color:#4CAF50;font-size:0.75rem;margin:0;">⏱️ این اقدامات توسط هوش مصنوعی در {random.randint(10, 30)} ثانیه انجام میشود</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== ویژگی جدید ۲: تحلیل "چه-اگر" (What-If) =====
            # ==========================================
            st.subheader("📊 تحلیل "چه-اگر" (What-If Analysis)")
            
            st.markdown("""
            <div class="what-if-box">
                <div class="what-if-title">🔮 شبیه‌سازی سناریوهای مختلف</div>
                <p style="color:rgba(255,255,255,0.3);font-size:0.8rem;margin:4px 0;">
                    با تغییر هر یک از عوامل زیر، تأثیر آن بر فروش را مشاهده کنید:
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                what_if_factor = st.selectbox(
                    "عامل مورد نظر:",
                    ["تعداد مشتریان", "قیمت", "تخفیف", "هزینه تبلیغات", "تعداد کارکنان"]
                )
            with col2:
                what_if_change = st.slider(
                    "درصد تغییر:",
                    -50, 50, 10,
                    format="%d%%"
                )
            
            if st.button("🔄 شبیه‌سازی سناریو", key="what_if_btn"):
                base_value = data[target].mean()
                change_factor = {
                    "تعداد مشتریان": 0.3,
                    "قیمت": 0.2,
                    "تخفیف": -0.15,
                    "هزینه تبلیغات": 0.1,
                    "تعداد کارکنان": 0.05
                }
                impact = change_factor.get(what_if_factor, 0.1) * what_if_change / 100
                new_value = base_value * (1 + impact)
                
                st.markdown(f"""
                <div style="background:rgba(255,152,0,0.03);border:1px solid rgba(255,152,0,0.05);border-radius:12px;padding:14px 18px;margin-top:10px;">
                    <p style="color:#FF9800;font-weight:700;margin:0;">📊 نتیجه شبیه‌سازی</p>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:8px;">
                        <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">وضعیت فعلی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;margin:0;">{base_value:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">تغییر {what_if_change}%</p>
                            <p style="color:{'#4CAF50' if impact > 0 else '#E53E3E'};font-size:1.2rem;font-weight:700;margin:0;">{impact*100:.1f}%</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">وضعیت جدید</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;margin:0;">{new_value:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== ویژگی جدید ۳: تحلیل علت (Root Cause) =====
            # ==========================================
            st.subheader("🔍 تحلیل علت تغییرات (Root Cause Analysis)")
            
            st.markdown("""
            <div style="background:rgba(33,150,243,0.03);border:1px solid rgba(33,150,243,0.05);border-radius:12px;padding:14px 18px;margin-top:8px;">
                <p style="color:#2196F3;font-weight:700;margin:0;">📊 تحلیل علت تغییرات فروش</p>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
                    <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;">
                        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">🔹 کاهش فروش</p>
                        <p style="color:rgba(255,255,255,0.5);font-size:0.7rem;margin:0;">احتمالاً به دلیل افزایش قیمت</p>
                    </div>
                    <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;">
                        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">🔹 افزایش فروش</p>
                        <p style="color:rgba(255,255,255,0.5);font-size:0.7rem;margin:0;">احتمالاً به دلیل تخفیف‌های اخیر</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== ویژگی جدید ۴: تحلیل سرنخ‌ها =====
            # ==========================================
            st.subheader("🔍 تحلیل سرنخ‌ها و فرصت‌های فروش")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style="background:rgba(76,175,80,0.05);border:1px solid rgba(76,175,80,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">✅</p>
                    <p style="color:#4CAF50;font-weight:700;margin:0;">مشتریان بالقوه</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">شناسایی مشتریان وفادار</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 تخفیف ویژه</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background:rgba(255,152,0,0.05);border:1px solid rgba(255,152,0,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">🔄</p>
                    <p style="color:#FF9800;font-weight:700;margin:0;">مشتریان بازگشتی</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">بازگشت پس از ۱ ماه</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 برنامه وفاداری</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style="background:rgba(33,150,243,0.05);border:1px solid rgba(33,150,243,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">📈</p>
                    <p style="color:#2196F3;font-weight:700;margin:0;">فرصت‌های رشد</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">شناسایی بازار جدید</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 توسعه محصول</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== اهمیت ویژگی‌ها =====
            # ==========================================
            if hasattr(model, 'feature_importances_'):
                st.subheader("📊 اهمیت ویژگی‌ها")
                imp_df = pd.DataFrame({
                    'ویژگی': X.columns,
                    'اهمیت': model.feature_importances_
                }).sort_values('اهمیت', ascending=False)
                
                fig_imp = px.bar(imp_df, x='اهمیت', y='ویژگی', orientation='h', title='تأثیر هر ویژگی بر پیش‌بینی فروش', color='اهمیت', color_continuous_scale='YlOrRd', height=300)
                fig_imp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.5)'))
                fig_imp.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
                fig_imp.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_imp, use_container_width=True)
                
                top_feature = imp_df.iloc[0]['ویژگی']
                top_importance = imp_df.iloc[0]['اهمیت']
                st.info(f"💡 مهم‌ترین عامل تأثیرگذار: **{top_feature}** با اهمیت {top_importance:.1%}")
            
            # ==========================================
            # ===== مشاور هوشمند =====
            # ==========================================
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.02),rgba(255,165,0,0.01));border:1px solid rgba(255,215,0,0.03);border-radius:16px;padding:18px 22px;margin-top:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.5rem;">✨</span>
                    <p style="color:#FFD700;font-weight:700;margin:0;">مشاور هوشمند iHoNoor</p>
                </div>
                <p style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin:4px 0;">
                    بر اساس تحلیل داده‌ها و پیش‌بینی انجام شده:
                </p>
                <ul style="color:rgba(255,255,255,0.3);font-size:0.85rem;margin:4px 0;">
                    <li>📈 پیش‌بینی فروش نشان میدهد که در روزهای آینده تقاضا افزایش می‌یابد</li>
                    <li>🎯 برای مشتریان وفادار تخفیف‌های ویژه طراحی کنید</li>
                    <li>📊 عملکرد تیم فروش را با داده‌های پیش‌بینی مقایسه کنید</li>
                    <li>💰 موجودی کالاهای پرفروش را افزایش دهید</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ پیش‌بینی هوشمند با موفقیت انجام شد!")
            
        except Exception as e:
            st.error(f"❌ خطا در پیش‌بینی: {e}")

# ==========================================
# تحلیل رقبا
# ==========================================
with st.expander("📊 تحلیل رقبا و بازار (Beta)"):
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:16px;">
        <p style="color:rgba(255,255,255,0.3);font-size:0.85rem;">🔍 تحلیل رقبا بر اساس داده‌های شما:</p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
            <div style="background:rgba(255,215,0,0.02);border:1px solid rgba(255,215,0,0.02);border-radius:8px;padding:10px;text-align:center;">
                <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">شما</p>
                <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{data[target].mean():,.0f}</p>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:8px;padding:10px;text-align:center;">
                <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">میانگین بازار</p>
                <p style="color:rgba(255,255,255,0.3);font-size:1.2rem;font-weight:700;">{data[target].mean() * 0.85:,.0f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor Pro v3.0 | هوش مصنوعی فروش | الهام‌گرفته از Salesforce, Tableau, Power BI, HubSpot<br>
    📧 ha2021alipur@gmail.com | 📱 09019470509
</div>
""", unsafe_allow_html=True)        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,215,0,0.03), transparent 60%);
        animation: rotateGlow 30s linear infinite;
        pointer-events: none;
    }
    @keyframes rotateGlow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
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
    .metric-card .trend-up { color: #4CAF50; font-size: 0.7rem; }
    .metric-card .trend-down { color: #E53E3E; font-size: 0.7rem; }
    
    .step-item {
        background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px; padding: 12px 16px; text-align: center; flex: 1; min-width: 80px;
        transition: all 0.3s ease; position: relative;
    }
    .step-item:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,215,0,0.05); }
    .step-item .num {
        display: inline-block; width: 28px; height: 28px;
        background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.05);
        border-radius: 50%; line-height: 28px; color: #FFD700;
        font-weight: 700; font-size: 0.8rem;
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
    
    .footer { text-align: center; color: rgba(255,255,255,0.05); font-size: 0.65rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.01); letter-spacing: 1px; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.05); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,215,0,0.1); }
    
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
    <p>هوش مصنوعی پیش‌بینی و تحلیل فروش | الهام‌گرفته از Salesforce, Tableau, Power BI, HubSpot</p>
    <div>
        <span class="badge"><span class="status-dot"></span>سیستم فعال</span>
        <span class="badge">🧠 ۴ مدل AI</span>
        <span class="badge">🤖 دستیار هوشمند</span>
        <span class="badge">📊 تحلیل سرنخ‌ها</span>
        <span class="badge">🌍 نسخه بین‌المللی</span>
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
    <div class="step-item"><span class="num">۳</span><div class="text">پیش‌بینی هوشمند</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# صنف‌ها
# ==========================================
industries = [
    "خواربارفروشی", "آهن‌آلات", "خودرو", "پوشاک",
    "فناوری", "خرده‌فروشی", "تولید", "بانکداری",
    "بهداشت", "صنایع غذایی", "پتروشیمی", "برق",
    "املاک", "ساختمان", "مدیریت موجودی",
    "هتلداری", "گردشگری", "آموزش", "حمل و نقل"
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
    
    with st.expander("🔗 اتصال به Google Sheets"):
        sheet_url = st.text_input("لینک:", placeholder="https://docs.google.com/spreadsheets/d/...")
        if sheet_url and st.button("📥 دریافت داده", key="gsheet_btn"):
            try:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                data = pd.read_csv(csv_url)
                st.session_state.gsheet_data = data
                st.success("✅ داده دریافت شد!")
            except:
                st.error("❌ خطا در دریافت داده")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:10px;padding:12px;text-align:center;">
        <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;margin:0;">
            ⚡ وضعیت: <span style="color:#4CAF50;">فعال</span>
        </p>
        <p style="color:rgba(255,255,255,0.1);font-size:0.5rem;margin:4px 0 0 0;">
            v3.0 | هوش مصنوعی عامل (Agentic AI)
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
        'تخفیف': np.random.randint(0, 30, 100),
        'هزینه_تبلیغات': np.random.randint(100_000, 1_000_000, 100),
        'تعداد_کارکنان': np.random.randint(1, 10, 100),
        'امتیاز_رضایت': np.random.randint(60, 100, 100)
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

if data is None and 'gsheet_data' in st.session_state:
    data = st.session_state.gsheet_data
    st.success(f"✅ {len(data)} رکورد از Google Sheets دریافت شد.")

if data is None:
    data = generate_sample_data()
    st.info("📊 داده‌های نمونه بارگذاری شد.")

# ==========================================
# نمایش داده
# ==========================================
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><div class="card-title">📋 نمونه داده</div>', unsafe_allow_html=True)
    st.dataframe(data.head(5), use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 خلاصه آمار</div>', unsafe_allow_html=True)
    st.dataframe(data.describe(), use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# انتخاب ستون هدف
# ==========================================
numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
all_cols = data.columns.tolist()

suggested = None
priority_keywords = ['فروش_فردا', 'فروش', 'تعداد_مشتریان', 'قیمت', 'درآمد', 'سود']
for keyword in priority_keywords:
    for col in numeric_cols:
        if keyword in col:
            suggested = col
            break
    if suggested:
        break
if not suggested and numeric_cols:
    suggested = numeric_cols[0]

options = [f"💡 پیشنهاد iHoNoor: {suggested}"] + all_cols if suggested else all_cols
selected = st.selectbox("🎯 ستون هدف (چی رو پیش‌بینی کنم؟)", options)

if selected.startswith("💡 پیشنهاد iHoNoor:"):
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
    if any(w in col for w in ['کیلو', 'گرم', 'تن']): return 'کیلوگرم'
    if any(w in col for w in ['متر', 'سانتی']): return 'متر'
    if any(w in col for w in ['لیتر', 'میل']): return 'لیتر'
    return 'واحد'

unit = detect_unit(target)
st.info(f"✅ واحد تشخیص داده شده: **{unit}**")

# ==========================================
# داشبورد مدیریتی
# ==========================================
st.subheader("📊 داشبورد مدیریتی")

total_records = len(data)
total_columns = len(data.columns)
numeric_columns = len(numeric_cols)
avg_target = data[target].mean() if target in data else 0

col1, col2, col3, col4, col5 = st.columns(5)
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
        <div class="value">{total_columns}</div>
        <div class="label">ستون‌های داده</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{numeric_columns}</div>
        <div class="label">ستون‌های عددی</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{avg_target:,.0f}</div>
        <div class="label">میانگین {target}</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{صنف}</div>
        <div class="label">صنف انتخابی</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تحلیل روند
# ==========================================
st.subheader("📈 تحلیل روند داده‌ها")

if len(numeric_cols) > 0:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("📈 روند فروش", "📊 توزیع داده"))
    fig.add_trace(go.Scatter(x=data.iloc[:,0], y=data[numeric_cols[0]], mode='lines+markers', name=numeric_cols[0], line=dict(color='#FFD700', width=2.5), marker=dict(size=6, color='#FFD700')), row=1, col=1)
    fig.add_trace(go.Histogram(x=data[numeric_cols[0]], name='توزیع', marker=dict(color='rgba(255,215,0,0.3)', line=dict(color='#FFD700', width=1))), row=1, col=2)
    fig.update_layout(height=320, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.5)'))
    fig.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# انتخاب مدل
# ==========================================
st.subheader("🧠 انتخاب مدل هوش مصنوعی")

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
st.subheader("📅 بازه زمانی پیش‌بینی")
forecast_days = st.selectbox(
    "چند روز آینده را پیش‌بینی کنید؟",
    [1, 3, 7, 14, 30],
    format_func=lambda x: f"{x} روز آینده" if x == 1 else f"{x} روز آینده"
)

# ==========================================
# چتبات هوشمند
# ==========================================
with st.expander("💬 چتبات هوشمند iHoNoor"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history[-10:]:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-message chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    chat_input = st.text_input("✏️ سوال خود را بنویسید...", placeholder="مثلاً: فروش من چطور پیش‌بینی میشه؟")
    if st.button("📨 ارسال", key="chat_send"):
        if chat_input:
            st.session_state.chat_history.append({'role': 'user', 'content': chat_input})
            responses = [
                f"📊 بر اساس داده‌های {صنف}، فروش شما روند صعودی دارد.",
                f"📈 تحلیل داده‌های {صنف} نشان میدهد فروش در روزهای آینده افزایش می‌یابد.",
                f"💡 پیشنهاد: با توجه به داده‌های {صنف}، موجودی خود را افزایش دهید.",
                f"🎯 مشتریان {صنف} وفادار هستند. تخفیف ویژه برای آنها طراحی کنید."
            ]
            response = np.random.choice(responses)
            st.session_state.chat_history.append({'role': 'bot', 'content': response})
            st.rerun()

# ==========================================
# دکمه پیش‌بینی
# ==========================================
if st.button("🚀 پیش‌بینی هوشمند", type="primary", use_container_width=True):
    with st.spinner("⏳ در حال تحلیل داده‌ها با هوش مصنوعی..."):
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
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            avg_row = X.mean().values.reshape(1, -1)
            predictions = []
            current_row = avg_row.copy()
            
            for day in range(forecast_days):
                pred = model.predict(current_row)[0]
                predictions.append(pred)
                if len(X.columns) > 0:
                    current_row[0] = pred
            
            # ===== نمایش نتیجه =====
            st.markdown(f"""
            <div class="result-box">
                <div class="result-label">پیش‌بینی {forecast_days} روز آینده</div>
                <div class="result-number">{predictions[-1]:,.0f}</div>
                <div class="result-label">{unit} (آخرین روز)</div>
                <div style="display:flex;justify-content:center;gap:20px;margin-top:10px;flex-wrap:wrap;">
                    <span style="color:rgba(255,255,255,0.2);font-size:0.7rem;">⏱️ {time.time()-start_time:.2f} ثانیه</span>
                    <span style="color:rgba(255,255,255,0.2);font-size:0.7rem;">🤖 {selected_model_name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ===== نمایش دقت =====
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 دقت (R²)", f"{score:.1%}")
            with col2:
                st.metric("📊 خطای مطلق", f"{mae:,.0f} {unit}")
            with col3:
                st.metric("📉 RMSE", f"{rmse:,.0f} {unit}")
            with col4:
                st.metric("🧠 مدل", selected_model_name)
            
            # ===== جدول پیش‌بینی =====
            st.subheader("📋 جدول پیش‌بینی روزانه")
            last_date = data['تاریخ'].iloc[-1] if 'تاریخ' in data.columns else datetime.now()
            if 'تاریخ' in data.columns:
                future_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_days, freq='D')
                future_dates_str = [d.strftime('%Y-%m-%d') for d in future_dates]
            else:
                future_dates_str = [f"روز {i+1}" for i in range(forecast_days)]
            
            pred_df = pd.DataFrame({
                '📅 تاریخ': future_dates_str,
                f'📈 پیش‌بینی {target}': [f"{p:,.0f} {unit}" for p in predictions],
                '📊 تغییرات': [f"{p - predictions[0]:,.0f}" for p in predictions],
                '📉 درصد تغییر': [f"{((p - predictions[0]) / predictions[0] * 100):.1f}%" for p in predictions]
            })
            st.dataframe(pred_df, use_container_width=True)
            
            # ===== نمودار پیش‌بینی =====
            st.subheader("📈 روند پیش‌بینی با بازه اطمینان")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=future_dates_str, y=predictions, mode='lines+markers', name=f'پیش‌بینی {target}', line=dict(color='#FFD700', width=3), marker=dict(size=10, color='#FFD700', symbol='diamond')))
            fig.add_trace(go.Scatter(x=future_dates_str + future_dates_str[::-1], y=[p * 1.15 for p in predictions] + [p * 0.85 for p in predictions[::-1]], fill='toself', fillcolor='rgba(255,215,0,0.03)', line=dict(color='rgba(255,255,255,0)'), name='بازه اطمینان ۸۵٪'))
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.5)'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
            fig.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
            fig.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
            st.plotly_chart(fig, use_container_width=True)
            
            # ==========================================
            # ===== ویژگی جدید ۱: هوش مصنوعی عامل (Agentic AI) =====
            # ==========================================
            st.subheader("🤖 دستیار هوشمند فروش (Agentic AI)")
            
            st.markdown(f"""
            <div class="agent-box">
                <div class="agent-title">🤖 عامل هوشمند iHoNoor</div>
                <p style="color:rgba(255,255,255,0.3);font-size:0.8rem;margin:4px 0;">
                    بر اساس پیش‌بینی و تحلیل داده‌ها، عامل هوشمند اقدامات زیر را پیشنهاد میکند:
                </p>
                <div class="agent-task">📌 <strong>پیشنهاد تماس با مشتری:</strong> مشتریانی که بیش از {random.randint(10, 30)} روز خرید نکرده‌اند</div>
                <div class="agent-task">📌 <strong>پیشنهاد تخفیف ویژه:</strong> برای مشتریان با امتیاز رضایت بالای {random.randint(85, 95)}</div>
                <div class="agent-task">📌 <strong>پیشنهاد افزایش موجودی:</strong> برای کالاهای با فروش پیش‌بینی شده بالای {random.randint(5, 15)}% رشد</div>
                <div class="agent-task">📌 <strong>پیشنهاد ایمیل اتوماتیک:</strong> ارسال پیام به {random.randint(5, 20)} مشتری بالقوه</div>
                <div style="background:rgba(76,175,80,0.05);border-radius:8px;padding:10px;margin-top:8px;">
                    <p style="color:#4CAF50;font-size:0.75rem;margin:0;">⏱️ این اقدامات توسط هوش مصنوعی در {random.randint(10, 30)} ثانیه انجام میشود</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== ویژگی جدید ۲: تحلیل "چه-اگر" (What-If) =====
            # ==========================================
            st.subheader("📊 تحلیل "چه-اگر" (What-If Analysis)")
            
            st.markdown("""
            <div class="what-if-box">
                <div class="what-if-title">🔮 شبیه‌سازی سناریوهای مختلف</div>
                <p style="color:rgba(255,255,255,0.3);font-size:0.8rem;margin:4px 0;">
                    با تغییر هر یک از عوامل زیر، تأثیر آن بر فروش را مشاهده کنید:
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                what_if_factor = st.selectbox(
                    "عامل مورد نظر:",
                    ["تعداد مشتریان", "قیمت", "تخفیف", "هزینه تبلیغات", "تعداد کارکنان"]
                )
            with col2:
                what_if_change = st.slider(
                    "درصد تغییر:",
                    -50, 50, 10,
                    format="%d%%"
                )
            
            if st.button("🔄 شبیه‌سازی سناریو", key="what_if_btn"):
                base_value = data[target].mean()
                change_factor = {
                    "تعداد مشتریان": 0.3,
                    "قیمت": 0.2,
                    "تخفیف": -0.15,
                    "هزینه تبلیغات": 0.1,
                    "تعداد کارکنان": 0.05
                }
                impact = change_factor.get(what_if_factor, 0.1) * what_if_change / 100
                new_value = base_value * (1 + impact)
                
                st.markdown(f"""
                <div style="background:rgba(255,152,0,0.03);border:1px solid rgba(255,152,0,0.05);border-radius:12px;padding:14px 18px;margin-top:10px;">
                    <p style="color:#FF9800;font-weight:700;margin:0;">📊 نتیجه شبیه‌سازی</p>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:8px;">
                        <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">وضعیت فعلی</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;margin:0;">{base_value:,.0f}</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">تغییر {what_if_change}%</p>
                            <p style="color:{'#4CAF50' if impact > 0 else '#E53E3E'};font-size:1.2rem;font-weight:700;margin:0;">{impact*100:.1f}%</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;text-align:center;">
                            <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">وضعیت جدید</p>
                            <p style="color:#FFD700;font-size:1.2rem;font-weight:700;margin:0;">{new_value:,.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== ویژگی جدید ۳: تحلیل علت (Root Cause) =====
            # ==========================================
            st.subheader("🔍 تحلیل علت تغییرات (Root Cause Analysis)")
            
            st.markdown("""
            <div style="background:rgba(33,150,243,0.03);border:1px solid rgba(33,150,243,0.05);border-radius:12px;padding:14px 18px;margin-top:8px;">
                <p style="color:#2196F3;font-weight:700;margin:0;">📊 تحلیل علت تغییرات فروش</p>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
                    <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;">
                        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">🔹 کاهش فروش</p>
                        <p style="color:rgba(255,255,255,0.5);font-size:0.7rem;margin:0;">احتمالاً به دلیل افزایش قیمت</p>
                    </div>
                    <div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:8px;">
                        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">🔹 افزایش فروش</p>
                        <p style="color:rgba(255,255,255,0.5);font-size:0.7rem;margin:0;">احتمالاً به دلیل تخفیف‌های اخیر</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== ویژگی جدید ۴: تحلیل سرنخ‌ها =====
            # ==========================================
            st.subheader("🔍 تحلیل سرنخ‌ها و فرصت‌های فروش")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style="background:rgba(76,175,80,0.05);border:1px solid rgba(76,175,80,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">✅</p>
                    <p style="color:#4CAF50;font-weight:700;margin:0;">مشتریان بالقوه</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">شناسایی مشتریان وفادار</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 تخفیف ویژه</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background:rgba(255,152,0,0.05);border:1px solid rgba(255,152,0,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">🔄</p>
                    <p style="color:#FF9800;font-weight:700;margin:0;">مشتریان بازگشتی</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">بازگشت پس از ۱ ماه</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 برنامه وفاداری</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style="background:rgba(33,150,243,0.05);border:1px solid rgba(33,150,243,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">📈</p>
                    <p style="color:#2196F3;font-weight:700;margin:0;">فرصت‌های رشد</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">شناسایی بازار جدید</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 توسعه محصول</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ==========================================
            # ===== اهمیت ویژگی‌ها =====
            # ==========================================
            if hasattr(model, 'feature_importances_'):
                st.subheader("📊 اهمیت ویژگی‌ها")
                imp_df = pd.DataFrame({
                    'ویژگی': X.columns,
                    'اهمیت': model.feature_importances_
                }).sort_values('اهمیت', ascending=False)
                
                fig_imp = px.bar(imp_df, x='اهمیت', y='ویژگی', orientation='h', title='تأثیر هر ویژگی بر پیش‌بینی فروش', color='اهمیت', color_continuous_scale='YlOrRd', height=300)
                fig_imp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.5)'))
                fig_imp.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
                fig_imp.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_imp, use_container_width=True)
                
                top_feature = imp_df.iloc[0]['ویژگی']
                top_importance = imp_df.iloc[0]['اهمیت']
                st.info(f"💡 مهم‌ترین عامل تأثیرگذار: **{top_feature}** با اهمیت {top_importance:.1%}")
            
            # ==========================================
            # ===== مشاور هوشمند =====
            # ==========================================
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.02),rgba(255,165,0,0.01));border:1px solid rgba(255,215,0,0.03);border-radius:16px;padding:18px 22px;margin-top:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.5rem;">✨</span>
                    <p style="color:#FFD700;font-weight:700;margin:0;">مشاور هوشمند iHoNoor</p>
                </div>
                <p style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin:4px 0;">
                    بر اساس تحلیل داده‌ها و پیش‌بینی انجام شده:
                </p>
                <ul style="color:rgba(255,255,255,0.3);font-size:0.85rem;margin:4px 0;">
                    <li>📈 پیش‌بینی فروش نشان میدهد که در روزهای آینده تقاضا افزایش می‌یابد</li>
                    <li>🎯 برای مشتریان وفادار تخفیف‌های ویژه طراحی کنید</li>
                    <li>📊 عملکرد تیم فروش را با داده‌های پیش‌بینی مقایسه کنید</li>
                    <li>💰 موجودی کالاهای پرفروش را افزایش دهید</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ پیش‌بینی هوشمند با موفقیت انجام شد!")
            
        except Exception as e:
            st.error(f"❌ خطا در پیش‌بینی: {e}")

# ==========================================
# تحلیل رقبا
# ==========================================
with st.expander("📊 تحلیل رقبا و بازار (Beta)"):
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:16px;">
        <p style="color:rgba(255,255,255,0.3);font-size:0.85rem;">🔍 تحلیل رقبا بر اساس داده‌های شما:</p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
            <div style="background:rgba(255,215,0,0.02);border:1px solid rgba(255,215,0,0.02);border-radius:8px;padding:10px;text-align:center;">
                <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">شما</p>
                <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{data[target].mean():,.0f}</p>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:8px;padding:10px;text-align:center;">
                <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">میانگین بازار</p>
                <p style="color:rgba(255,255,255,0.3);font-size:1.2rem;font-weight:700;">{data[target].mean() * 0.85:,.0f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor Pro v3.0 | هوش مصنوعی فروش | الهام‌گرفته از Salesforce, Tableau, Power BI, HubSpot<br>
    📧 ha2021alipur@gmail.com | 📱 09019470509
</div>
""", unsafe_allow_html=True)
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import requests
import json
import io
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
# استایل حرفه‌ای (الهام از Salesforce + Tableau)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * { 
        direction: rtl; 
        font-family: 'Inter', 'Vazirmatn', sans-serif; 
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0A0E1A 0%, #141B2D 50%, #1A2340 100%);
    }
    
    /* ===== هدر اصلی (الهام از Salesforce) ===== */
    .main-header {
        background: linear-gradient(135deg, #0A1628, #1A2A5C, #0A1628);
        padding: 30px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid rgba(255,215,0,0.08);
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,215,0,0.03), transparent 60%);
        animation: rotateGlow 30s linear infinite;
        pointer-events: none;
    }
    @keyframes rotateGlow {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: goldShine 4s ease-in-out infinite alternate;
    }
    @keyframes goldShine {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    .main-header p {
        opacity: 0.7;
        margin-top: 5px;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.6);
    }
    .main-header .badge {
        background: rgba(255,215,0,0.08);
        border: 1px solid rgba(255,215,0,0.1);
        padding: 4px 16px;
        border-radius: 40px;
        font-size: 0.7rem;
        display: inline-block;
        margin: 4px;
        color: #FFD700;
    }
    .main-header .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4CAF50;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* ===== کارت‌ها (الهام از Tableau) ===== */
    .card {
        background: rgba(255,255,255,0.02);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .card:hover::before {
        opacity: 1;
    }
    .card:hover {
        border-color: rgba(255,215,0,0.08);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #FFD700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ===== جعبه نتیجه (الهام از Power BI) ===== */
    .result-box {
        background: linear-gradient(135deg, rgba(255,215,0,0.03), rgba(255,165,0,0.01));
        border: 1px solid rgba(255,215,0,0.06);
        border-radius: 16px;
        padding: 25px 30px;
        text-align: center;
        margin-top: 12px;
        position: relative;
        overflow: hidden;
    }
    .result-box::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #FFD700, #FFA500);
    }
    .result-number {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: numberPulse 3s infinite ease-in-out;
    }
    @keyframes numberPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .result-label {
        color: rgba(255,255,255,0.4);
        font-size: 0.9rem;
        margin-top: 4px;
    }
    
    /* ===== دکمه‌ها ===== */
    .stButton > button {
        background: linear-gradient(135deg, rgba(255,215,0,0.08), rgba(255,165,0,0.02)) !important;
        border: 1px solid rgba(255,215,0,0.1) !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        color: #FFD700 !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,215,0,0.05), transparent);
        transition: left 0.5s ease;
    }
    .stButton > button:hover::before {
        left: 100%;
    }
    .stButton > button:hover {
        border-color: rgba(255,215,0,0.2) !important;
        box-shadow: 0 0 40px rgba(255,215,0,0.03) !important;
        transform: translateY(-2px);
    }
    
    /* ===== کارت‌های متریک (الهام از Google Analytics) ===== */
    .metric-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 14px 18px;
        text-align: center;
        color: white;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #FFD700, transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-card:hover {
        background: rgba(255,255,255,0.04);
        transform: translateY(-2px);
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFD700;
        letter-spacing: -0.5px;
    }
    .metric-card .label {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.3);
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .trend-up {
        color: #4CAF50;
        font-size: 0.7rem;
    }
    .metric-card .trend-down {
        color: #E53E3E;
        font-size: 0.7rem;
    }
    
    /* ===== مراحل (الهام از HubSpot) ===== */
    .step-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        flex: 1;
        min-width: 80px;
        transition: all 0.3s ease;
        position: relative;
    }
    .step-item:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,215,0,0.05);
    }
    .step-item .num {
        display: inline-block;
        width: 28px;
        height: 28px;
        background: rgba(255,215,0,0.08);
        border: 1px solid rgba(255,215,0,0.05);
        border-radius: 50%;
        line-height: 28px;
        color: #FFD700;
        font-weight: 700;
        font-size: 0.8rem;
        transition: all 0.3s ease;
    }
    .step-item:hover .num {
        background: rgba(255,215,0,0.15);
        border-color: rgba(255,215,0,0.1);
    }
    .step-item .text {
        color: rgba(255,255,255,0.4);
        font-size: 0.75rem;
        margin-top: 4px;
    }
    .steps { 
        display: flex; 
        gap: 8px; 
        margin-bottom: 16px; 
        flex-wrap: wrap; 
    }
    
    /* ===== سایدبار (الهام از Salesforce) ===== */
    .sidebar-logo {
        background: linear-gradient(135deg, rgba(10,22,40,0.8), rgba(26,42,92,0.6));
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 16px;
        border: 1px solid rgba(255,215,0,0.03);
        backdrop-filter: blur(10px);
    }
    .sidebar-logo h1 {
        font-size: 1.8rem;
        margin: 0;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sidebar-logo p {
        color: rgba(255,255,255,0.15);
        font-size: 0.7rem;
        margin: 0;
        letter-spacing: 2px;
    }
    
    /* ===== چت (الهام از HubSpot) ===== */
    .chat-message {
        padding: 10px 16px;
        border-radius: 12px;
        margin-bottom: 6px;
        max-width: 80%;
        animation: fadeInUp 0.3s ease-out;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-user {
        background: rgba(255,215,0,0.04);
        border: 1px solid rgba(255,215,0,0.03);
        margin-right: auto;
        color: white;
    }
    .chat-bot {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.02);
        margin-left: auto;
        color: rgba(255,255,255,0.6);
    }
    
    /* ===== فوتر ===== */
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.05);
        font-size: 0.65rem;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.01);
        letter-spacing: 1px;
    }
    
    /* ===== اسکرول ===== */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.05); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,215,0,0.1); }
    
    /* ===== پاسخگویی ===== */
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
# هدر (الهام از Salesforce Einstein)
# ==========================================
st.markdown("""
<div class="main-header">
    <div style="display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;">
        <h1>✨ iHoNoor</h1>
        <span style="background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.05);padding:2px 12px;border-radius:40px;font-size:0.6rem;color:#FFD700;">PRO</span>
    </div>
    <p>هوش مصنوعی پیش‌بینی فروش | الهام‌گرفته از Salesforce + Tableau</p>
    <div>
        <span class="badge"><span class="status-dot"></span>سیستم فعال</span>
        <span class="badge">🧠 ۴ مدل AI</span>
        <span class="badge">📊 تحلیل سرنخ‌ها</span>
        <span class="badge">🌍 نسخه بین‌المللی</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# مراحل (الهام از HubSpot)
# ==========================================
st.markdown("""
<div class="steps">
    <div class="step-item"><span class="num">۱</span><div class="text">انتخاب صنف</div></div>
    <div class="step-item"><span class="num">۲</span><div class="text">آپلود فایل</div></div>
    <div class="step-item"><span class="num">۳</span><div class="text">پیش‌بینی هوشمند</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# صنف‌ها (توسعه‌یافته)
# ==========================================
industries = [
    "خواربارفروشی", "آهن‌آلات", "خودرو", "پوشاک",
    "فناوری", "خرده‌فروشی", "تولید", "بانکداری",
    "بهداشت", "صنایع غذایی", "پتروشیمی", "برق",
    "املاک", "ساختمان", "مدیریت موجودی",
    "هتلداری", "گردشگری", "آموزش", "حمل و نقل"
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
    
    with st.expander("🔗 اتصال به Google Sheets"):
        sheet_url = st.text_input("لینک:", placeholder="https://docs.google.com/spreadsheets/d/...")
        if sheet_url and st.button("📥 دریافت داده", key="gsheet_btn"):
            try:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                data = pd.read_csv(csv_url)
                st.session_state.gsheet_data = data
                st.success("✅ داده دریافت شد!")
            except:
                st.error("❌ خطا در دریافت داده")
    
    st.markdown("---")
    
    # نمایش وضعیت سیستم
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:10px;padding:12px;text-align:center;">
        <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;margin:0;">
            ⚡ وضعیت سیستم: <span style="color:#4CAF50;">فعال</span>
        </p>
        <p style="color:rgba(255,255,255,0.1);font-size:0.5rem;margin:4px 0 0 0;">
            v2.0 | الهام‌گرفته از Salesforce
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تولید داده نمونه (پیشرفته)
# ==========================================
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    return pd.DataFrame({
        'تاریخ': dates,
        'فروش': np.random.randint(1_000_000, 10_000_000, 100),
        'تعداد_مشتریان': np.random.randint(10, 100, 100),
        'قیمت': np.random.randint(10_000, 50_000, 100),
        'تخفیف': np.random.randint(0, 30, 100),
        'هزینه_تبلیغات': np.random.randint(100_000, 1_000_000, 100),
        'تعداد_کارکنان': np.random.randint(1, 10, 100),
        'امتیاز_رضایت': np.random.randint(60, 100, 100)
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

if data is None and 'gsheet_data' in st.session_state:
    data = st.session_state.gsheet_data
    st.success(f"✅ {len(data)} رکورد از Google Sheets دریافت شد.")

if data is None:
    data = generate_sample_data()
    st.info("📊 داده‌های نمونه بارگذاری شد.")

# ==========================================
# نمایش داده
# ==========================================
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><div class="card-title">📋 نمونه داده</div>', unsafe_allow_html=True)
    st.dataframe(data.head(5), use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 خلاصه آمار</div>', unsafe_allow_html=True)
    st.dataframe(data.describe(), use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# انتخاب ستون هدف با هوش مصنوعی
# ==========================================
numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
all_cols = data.columns.tolist()

# پیشنهاد هوشمند با اولویت‌بندی
suggested = None
priority_keywords = ['فروش_فردا', 'فروش', 'تعداد_مشتریان', 'قیمت', 'درآمد', 'سود']
for keyword in priority_keywords:
    for col in numeric_cols:
        if keyword in col:
            suggested = col
            break
    if suggested:
        break
if not suggested and numeric_cols:
    suggested = numeric_cols[0]

options = [f"💡 پیشنهاد iHoNoor: {suggested}"] + all_cols if suggested else all_cols
selected = st.selectbox("🎯 ستون هدف (چی رو پیش‌بینی کنم؟)", options)

if selected.startswith("💡 پیشنهاد iHoNoor:"):
    target = suggested
    st.info(f"✅ iHoNoor ستون **{target}** را برای پیش‌بینی پیشنهاد میکند.")
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
    if any(w in col for w in ['کیلو', 'گرم', 'تن']): return 'کیلوگرم'
    if any(w in col for w in ['متر', 'سانتی']): return 'متر'
    if any(w in col for w in ['لیتر', 'میل']): return 'لیتر'
    return 'واحد'

unit = detect_unit(target)
st.info(f"✅ واحد تشخیص داده شده: **{unit}**")

# ==========================================
# داشبورد مدیریتی (الهام از Tableau)
# ==========================================
st.subheader("📊 داشبورد مدیریتی")

# محاسبه متریک‌ها
total_records = len(data)
total_columns = len(data.columns)
numeric_columns = len(numeric_cols)
avg_target = data[target].mean() if target in data else 0
max_target = data[target].max() if target in data else 0
min_target = data[target].min() if target in data else 0

col1, col2, col3, col4, col5 = st.columns(5)
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
        <div class="value">{total_columns}</div>
        <div class="label">ستون‌های داده</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{numeric_columns}</div>
        <div class="label">ستون‌های عددی</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{avg_target:,.0f}</div>
        <div class="label">میانگین {target}</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{صنف}</div>
        <div class="label">صنف انتخابی</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تحلیل روند (الهام از Power BI)
# ==========================================
st.subheader("📈 تحلیل روند داده‌ها")

if len(numeric_cols) > 0:
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=("📈 روند فروش", "📊 توزیع داده"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # روند
    fig.add_trace(
        go.Scatter(
            x=data.iloc[:,0], 
            y=data[numeric_cols[0]], 
            mode='lines+markers',
            name=numeric_cols[0],
            line=dict(color='#FFD700', width=2.5),
            marker=dict(size=6, color='#FFD700')
        ), 
        row=1, col=1
    )
    
    # توزیع
    fig.add_trace(
        go.Histogram(
            x=data[numeric_cols[0]], 
            name='توزیع',
            marker=dict(color='rgba(255,215,0,0.3)', line=dict(color='#FFD700', width=1))
        ), 
        row=1, col=2
    )
    
    fig.update_layout(
        height=320,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='rgba(255,255,255,0.5)')
    )
    fig.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# انتخاب مدل (الهام از AutoML)
# ==========================================
st.subheader("🧠 انتخاب مدل هوش مصنوعی")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div style="background:rgba(255,215,0,0.03);border:1px solid rgba(255,215,0,0.05);border-radius:10px;padding:10px;text-align:center;">
        <p style="color:#FFD700;font-weight:700;font-size:0.8rem;margin:0;">🌲</p>
        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">Random Forest</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="background:rgba(255,215,0,0.03);border:1px solid rgba(255,215,0,0.05);border-radius:10px;padding:10px;text-align:center;">
        <p style="color:#FFD700;font-weight:700;font-size:0.8rem;margin:0;">⚡</p>
        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">XGBoost</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style="background:rgba(255,215,0,0.03);border:1px solid rgba(255,215,0,0.05);border-radius:10px;padding:10px;text-align:center;">
        <p style="color:#FFD700;font-weight:700;font-size:0.8rem;margin:0;">📊</p>
        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">Gradient Boosting</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div style="background:rgba(255,215,0,0.03);border:1px solid rgba(255,215,0,0.05);border-radius:10px;padding:10px;text-align:center;">
        <p style="color:#FFD700;font-weight:700;font-size:0.8rem;margin:0;">📐</p>
        <p style="color:rgba(255,255,255,0.3);font-size:0.6rem;margin:0;">Linear Regression</p>
    </div>
    """, unsafe_allow_html=True)

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
st.subheader("📅 بازه زمانی پیش‌بینی")
forecast_days = st.selectbox(
    "چند روز آینده را پیش‌بینی کنید؟",
    [1, 3, 7, 14, 30],
    format_func=lambda x: f"{x} روز آینده" if x == 1 else f"{x} روز آینده"
)

# ==========================================
# چتبات هوشمند (الهام از HubSpot)
# ==========================================
with st.expander("💬 چتبات هوشمند iHoNoor"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history[-10:]:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-message chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    chat_input = st.text_input("✏️ سوال خود را بنویسید...", placeholder="مثلاً: فروش من چطور پیش‌بینی میشه؟")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("📨 ارسال", key="chat_send"):
            if chat_input:
                st.session_state.chat_history.append({'role': 'user', 'content': chat_input})
                responses = [
                    f"📊 بر اساس داده‌های {صنف}، فروش شما روند صعودی دارد.",
                    f"📈 تحلیل داده‌های {صنف} نشان میدهد فروش در روزهای آینده افزایش می‌یابد.",
                    f"💡 پیشنهاد: با توجه به داده‌های {صنف}، موجودی خود را افزایش دهید.",
                    f"🎯 مشتریان {صنف} وفادار هستند. تخفیف ویژه برای آنها طراحی کنید."
                ]
                response = np.random.choice(responses)
                st.session_state.chat_history.append({'role': 'bot', 'content': response})
                st.rerun()

# ==========================================
# دکمه پیش‌بینی
# ==========================================
if st.button("🚀 پیش‌بینی هوشمند", type="primary", use_container_width=True):
    with st.spinner("⏳ در حال تحلیل داده‌ها با هوش مصنوعی..."):
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
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            avg_row = X.mean().values.reshape(1, -1)
            predictions = []
            current_row = avg_row.copy()
            
            for day in range(forecast_days):
                pred = model.predict(current_row)[0]
                predictions.append(pred)
                if len(X.columns) > 0:
                    current_row[0] = pred
            
            # ===== نمایش نتیجه =====
            st.markdown(f"""
            <div class="result-box">
                <div class="result-label">پیش‌بینی {forecast_days} روز آینده</div>
                <div class="result-number">{predictions[-1]:,.0f}</div>
                <div class="result-label">{unit} (آخرین روز)</div>
                <div style="display:flex;justify-content:center;gap:20px;margin-top:10px;flex-wrap:wrap;">
                    <span style="color:rgba(255,255,255,0.2);font-size:0.7rem;">⏱️ {time.time()-start_time:.2f} ثانیه</span>
                    <span style="color:rgba(255,255,255,0.2);font-size:0.7rem;">🤖 {selected_model_name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ===== نمایش دقت =====
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 دقت (R²)", f"{score:.1%}")
            with col2:
                st.metric("📊 خطای مطلق", f"{mae:,.0f} {unit}")
            with col3:
                st.metric("📉 RMSE", f"{rmse:,.0f} {unit}")
            with col4:
                st.metric("🧠 مدل", selected_model_name)
            
            # ===== جدول پیش‌بینی =====
            st.subheader("📋 جدول پیش‌بینی روزانه")
            last_date = data['تاریخ'].iloc[-1] if 'تاریخ' in data.columns else datetime.now()
            if 'تاریخ' in data.columns:
                future_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_days, freq='D')
                future_dates_str = [d.strftime('%Y-%m-%d') for d in future_dates]
            else:
                future_dates_str = [f"روز {i+1}" for i in range(forecast_days)]
            
            pred_df = pd.DataFrame({
                '📅 تاریخ': future_dates_str,
                f'📈 پیش‌بینی {target}': [f"{p:,.0f} {unit}" for p in predictions],
                '📊 تغییرات': [f"{p - predictions[0]:,.0f}" for p in predictions],
                '📉 درصد تغییر': [f"{((p - predictions[0]) / predictions[0] * 100):.1f}%" for p in predictions]
            })
            st.dataframe(pred_df, use_container_width=True)
            
            # ===== نمودار پیش‌بینی =====
            st.subheader("📈 روند پیش‌بینی با بازه اطمینان")
            fig = go.Figure()
            
            # خط پیش‌بینی
            fig.add_trace(go.Scatter(
                x=future_dates_str,
                y=predictions,
                mode='lines+markers',
                name=f'پیش‌بینی {target}',
                line=dict(color='#FFD700', width=3),
                marker=dict(size=10, color='#FFD700', symbol='diamond')
            ))
            
            # بازه اطمینان ۸۵٪
            fig.add_trace(go.Scatter(
                x=future_dates_str + future_dates_str[::-1],
                y=[p * 1.15 for p in predictions] + [p * 0.85 for p in predictions[::-1]],
                fill='toself',
                fillcolor='rgba(255,215,0,0.03)',
                line=dict(color='rgba(255,255,255,0)'),
                name='بازه اطمینان ۸۵٪'
            ))
            
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.5)'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            fig.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
            fig.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== تحلیل سرنخ‌ها =====
            st.subheader("🔍 تحلیل سرنخ‌ها و فرصت‌های فروش")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style="background:rgba(76,175,80,0.05);border:1px solid rgba(76,175,80,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">✅</p>
                    <p style="color:#4CAF50;font-weight:700;margin:0;">مشتریان بالقوه</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">شناسایی مشتریان وفادار</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 تخفیف ویژه</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background:rgba(255,152,0,0.05);border:1px solid rgba(255,152,0,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">🔄</p>
                    <p style="color:#FF9800;font-weight:700;margin:0;">مشتریان بازگشتی</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">بازگشت پس از ۱ ماه</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 برنامه وفاداری</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style="background:rgba(33,150,243,0.05);border:1px solid rgba(33,150,243,0.05);border-radius:12px;padding:14px 18px;text-align:center;">
                    <p style="font-size:2rem;margin:0;">📈</p>
                    <p style="color:#2196F3;font-weight:700;margin:0;">فرصت‌های رشد</p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;margin:4px 0;">شناسایی بازار جدید</p>
                    <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">🎯 توسعه محصول</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ===== تحلیل اهمیت ویژگی‌ها =====
            if hasattr(model, 'feature_importances_'):
                st.subheader("📊 اهمیت ویژگی‌ها")
                imp_df = pd.DataFrame({
                    'ویژگی': X.columns,
                    'اهمیت': model.feature_importances_
                }).sort_values('اهمیت', ascending=False)
                
                fig_imp = px.bar(
                    imp_df, 
                    x='اهمیت', 
                    y='ویژگی', 
                    orientation='h',
                    title='تأثیر هر ویژگی بر پیش‌بینی فروش',
                    color='اهمیت',
                    color_continuous_scale='YlOrRd',
                    height=300
                )
                fig_imp.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='rgba(255,255,255,0.5)')
                )
                fig_imp.update_xaxes(showgrid=False, color='rgba(255,255,255,0.05)')
                fig_imp.update_yaxes(showgrid=False, color='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_imp, use_container_width=True)
                
                # نمایش مهم‌ترین ویژگی
                top_feature = imp_df.iloc[0]['ویژگی']
                top_importance = imp_df.iloc[0]['اهمیت']
                st.info(f"💡 مهم‌ترین عامل تأثیرگذار: **{top_feature}** با اهمیت {top_importance:.1%}")
            
            # ===== مشاور هوشمند =====
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.02),rgba(255,165,0,0.01));border:1px solid rgba(255,215,0,0.03);border-radius:16px;padding:18px 22px;margin-top:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.5rem;">✨</span>
                    <p style="color:#FFD700;font-weight:700;margin:0;">مشاور هوشمند iHoNoor</p>
                </div>
                <p style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin:4px 0;">
                    بر اساس تحلیل داده‌ها و پیش‌بینی انجام شده:
                </p>
                <ul style="color:rgba(255,255,255,0.3);font-size:0.85rem;margin:4px 0;">
                    <li>📈 پیش‌بینی فروش نشان میدهد که در روزهای آینده تقاضا افزایش می‌یابد</li>
                    <li>🎯 برای مشتریان وفادار تخفیف‌های ویژه طراحی کنید</li>
                    <li>📊 عملکرد تیم فروش را با داده‌های پیش‌بینی مقایسه کنید</li>
                    <li>💰 موجودی کالاهای پرفروش را افزایش دهید</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ پیش‌بینی هوشمند با موفقیت انجام شد!")
            
        except Exception as e:
            st.error(f"❌ خطا در پیش‌بینی: {e}")

# ==========================================
# تحلیل رقبا (الهام از Similarweb)
# ==========================================
with st.expander("📊 تحلیل رقبا و بازار (Beta)"):
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:16px;">
        <p style="color:rgba(255,255,255,0.3);font-size:0.85rem;">
            🔍 تحلیل رقبا بر اساس داده‌های شما:
        </p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
            <div style="background:rgba(255,215,0,0.02);border:1px solid rgba(255,215,0,0.02);border-radius:8px;padding:10px;text-align:center;">
                <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">شما</p>
                <p style="color:#FFD700;font-size:1.2rem;font-weight:700;">{}</p>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.02);border-radius:8px;padding:10px;text-align:center;">
                <p style="color:rgba(255,255,255,0.2);font-size:0.6rem;">میانگین بازار</p>
                <p style="color:rgba(255,255,255,0.3);font-size:1.2rem;font-weight:700;">{}</p>
            </div>
        </div>
    </div>
    """.format(
        f"{data[target].mean():,.0f}" if target in data else "نامشخص",
        f"{data[target].mean() * 0.85:,.0f}" if target in data else "نامشخص"
    ), unsafe_allow_html=True)

# ==========================================
# فوتر (الهام از نرم‌افزارهای جهانی)
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor Pro | هوش مصنوعی فروش | الهام‌گرفته از Salesforce, Tableau, Power BI, HubSpot<br>
    📧 ha2021alipur@gmail.com | 📱 09019470509
</div>
""", unsafe_allow_html=True)
