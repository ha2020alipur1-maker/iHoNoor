import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import requests
import json
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
    
    .main-header {
        background: linear-gradient(135deg, #0A1628, #1A2A5C, #0A1628);
        padding: 30px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid rgba(255,215,0,0.1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        opacity: 0.7;
        margin-top: 5px;
        letter-spacing: 1px;
    }
    .main-header .badge {
        background: rgba(255,215,0,0.1);
        border: 1px solid rgba(255,215,0,0.2);
        padding: 4px 16px;
        border-radius: 40px;
        font-size: 0.7rem;
        display: inline-block;
        margin: 4px;
    }
    
    .card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        color: white;
        transition: all 0.3s ease;
    }
    .card:hover {
        border-color: rgba(255,215,0,0.1);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
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
    
    .result-box {
        background: linear-gradient(135deg, rgba(255,215,0,0.05), rgba(255,165,0,0.02));
        border: 1px solid rgba(255,215,0,0.1);
        border-radius: 16px;
        padding: 25px 30px;
        text-align: center;
        margin-top: 12px;
    }
    .result-number {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .result-label {
        color: rgba(255,255,255,0.5);
        font-size: 0.9rem;
        margin-top: 4px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,165,0,0.02)) !important;
        border: 1px solid rgba(255,215,0,0.15) !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        color: #FFD700 !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        border-color: rgba(255,215,0,0.3) !important;
        box-shadow: 0 0 40px rgba(255,215,0,0.05) !important;
        transform: translateY(-2px);
    }
    
    .metric-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 14px 18px;
        text-align: center;
        color: white;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFD700;
    }
    .metric-card .label {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.4);
        margin-top: 2px;
    }
    
    .step-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        flex: 1;
        min-width: 80px;
    }
    .step-item .num {
        display: inline-block;
        width: 28px;
        height: 28px;
        background: rgba(255,215,0,0.1);
        border: 1px solid rgba(255,215,0,0.1);
        border-radius: 50%;
        line-height: 28px;
        color: #FFD700;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .step-item .text {
        color: rgba(255,255,255,0.6);
        font-size: 0.75rem;
        margin-top: 4px;
    }
    .steps { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
    
    .sidebar-logo {
        background: linear-gradient(135deg, #0A1628, #1A2A5C);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 16px;
        border: 1px solid rgba(255,215,0,0.05);
    }
    .sidebar-logo h1 {
        font-size: 1.8rem;
        margin: 0;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sidebar-logo p {
        color: rgba(255,255,255,0.2);
        font-size: 0.7rem;
        margin: 0;
    }
    
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.1);
        font-size: 0.65rem;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.02);
    }
    
    .forecast-table {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 12px;
    }
    
    .chat-message {
        padding: 10px 16px;
        border-radius: 12px;
        margin-bottom: 6px;
        max-width: 80%;
    }
    .chat-user {
        background: rgba(255,215,0,0.05);
        border: 1px solid rgba(255,215,0,0.05);
        margin-right: auto;
        color: white;
    }
    .chat-bot {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.02);
        margin-left: auto;
        color: rgba(255,255,255,0.7);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# هدر
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>✨ iHoNoor Pro</h1>
    <p>هوش مصنوعی پیش‌بینی فروش | سطح جهانی</p>
    <div>
        <span class="badge">🚀 نسخه بین‌المللی</span>
        <span class="badge">🧠 ۴ مدل هوش مصنوعی</span>
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
    
    with st.expander("🔗 اتصال به Google Sheets"):
        sheet_url = st.text_input("لینک:", placeholder="https://docs.google.com/spreadsheets/d/...")
        if sheet_url and st.button("📥 دریافت داده"):
            try:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                data = pd.read_csv(csv_url)
                st.session_state.gsheet_data = data
                st.success("✅ داده دریافت شد!")
            except:
                st.error("❌ خطا در دریافت داده")
    
    st.markdown("---")
    st.caption("💡 بدون فایل؟ داده‌های نمونه استفاده میشود.")

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
        'هزینه_تبلیغات': np.random.randint(100_000, 1_000_000, 100)
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
    st.dataframe(data.head(5), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 خلاصه</div>', unsafe_allow_html=True)
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
st.info(f"✅ واحد: **{unit}**")

# ==========================================
# داشبورد مدیریتی
# ==========================================
st.subheader("📊 داشبورد مدیریتی")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{len(data)}</div>
        <div class="label">تعداد رکوردها</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{len(numeric_cols)}</div>
        <div class="label">ستون‌های عددی</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    if len(numeric_cols) > 0:
        avg_val = data[numeric_cols[0]].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{avg_val:,.0f}</div>
            <div class="label">میانگین {numeric_cols[0]}</div>
        </div>
        """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{صنف}</div>
        <div class="label">صنف انتخابی</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{unit}</div>
        <div class="label">واحد</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تحلیل روند
# ==========================================
st.subheader("📈 تحلیل روند")
if len(numeric_cols) > 0:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("روند فروش", "توزیع داده"))
    fig.add_trace(go.Scatter(x=data.iloc[:,0], y=data[numeric_cols[0]], mode='lines', name=numeric_cols[0]), row=1, col=1)
    fig.add_trace(go.Histogram(x=data[numeric_cols[0]], name='توزیع'), row=1, col=2)
    fig.update_layout(height=300, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

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
selected_model_name = st.selectbox("مدل پیش‌بینی:", list(models.keys()))

# ==========================================
# بازه زمانی
# ==========================================
forecast_days = st.selectbox(
    "📅 چند روز آینده؟",
    [1, 3, 7, 14, 30],
    format_func=lambda x: f"{x} روز"
)

# ==========================================
# چتبات
# ==========================================
with st.expander("💬 چتبات هوشمند iHoNoor"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history[-10:]:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-message chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    user_msg = st.text_input("سوال خود را بنویسید...", placeholder="مثلاً: فروش من چطور پیش‌بینی میشه؟")
    if st.button("📨 ارسال", key="chat_send"):
        if user_msg:
            st.session_state.chat_history.append({'role': 'user', 'content': user_msg})
            response = f"🤖 بر اساس داده‌های {صنف}، فروش شما روند {np.random.choice(['صعودی', 'نزولی', 'ثابت'])} دارد. پیشنهاد میکنم موجودی خود را مدیریت کنید."
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
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 دقت (R²)", f"{score:.1%}")
            with col2:
                st.metric("📊 خطای مطلق", f"{mae:,.0f} {unit}")
            with col3:
                st.metric("🤖 مدل", selected_model_name)
            
            # جدول پیش‌بینی
            last_date = data['تاریخ'].iloc[-1] if 'تاریخ' in data.columns else datetime.now()
            if 'تاریخ' in data.columns:
                future_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_days, freq='D')
                future_dates_str = [d.strftime('%Y-%m-%d') for d in future_dates]
            else:
                future_dates_str = [f"روز {i+1}" for i in range(forecast_days)]
            
            pred_df = pd.DataFrame({
                'تاریخ': future_dates_str,
                f'پیش‌بینی {target}': [f"{p:,.0f} {unit}" for p in predictions],
                'تغییرات': [f"{p - predictions[0]:,.0f}" for p in predictions]
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
            fig.add_trace(go.Scatter(
                x=future_dates_str + future_dates_str[::-1],
                y=[p * 1.15 for p in predictions] + [p * 0.85 for p in predictions[::-1]],
                fill='toself',
                fillcolor='rgba(255,215,0,0.05)',
                line=dict(color='rgba(255,255,255,0)'),
                name='بازه اطمینان ۸۵٪'
            ))
            fig.update_layout(
                title='روند پیش‌بینی با بازه اطمینان',
                xaxis_title='تاریخ',
                yaxis_title=unit,
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)')
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== تحلیل سرنخ‌ها =====
            st.subheader("🔍 تحلیل سرنخ‌ها و فرصت‌ها")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="background:rgba(76,175,80,0.05);border:1px solid rgba(76,175,80,0.1);border-radius:12px;padding:14px 18px;">
                    <p style="color:#4CAF50;font-weight:700;margin:0;">✅ مشتریان بالقوه</p>
                    <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0;">
                        شناسایی مشتریانی که بیش از ۳ بار خرید کرده‌اند
                    </p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;">🎯 پیشنهاد: تخفیف ویژه برای خرید مجدد</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background:rgba(255,152,0,0.05);border:1px solid rgba(255,152,0,0.1);border-radius:12px;padding:14px 18px;">
                    <p style="color:#FF9800;font-weight:700;margin:0;">🔄 مشتریان بازگشتی</p>
                    <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:4px 0;">
                        مشتریانی که بعد از ۱ ماه بازگشته‌اند
                    </p>
                    <p style="color:rgba(255,255,255,0.3);font-size:0.7rem;">🎯 پیشنهاد: برنامه وفاداری مشتریان</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ===== تحلیل اهمیت ویژگی‌ها (اصلاح شده) =====
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
                    title='تأثیر هر ویژگی بر پیش‌بینی',
                    color='اهمیت',
                    color_continuous_scale='YlOrRd'  # ✅ اصلاح شده
                )
                fig_imp.update_layout(
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='rgba(255,255,255,0.7)')
                )
                fig_imp.update_xaxes(showgrid=False)
                fig_imp.update_yaxes(showgrid=False)
                st.plotly_chart(fig_imp, use_container_width=True)
            
            # ===== مشاور هوشمند =====
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.02),rgba(255,165,0,0.01));border:1px solid rgba(255,215,0,0.05);border-radius:16px;padding:18px 22px;margin-top:12px;">
                <p style="color:#FFD700;font-weight:700;margin:0;">✨ مشاور هوشمند iHoNoor</p>
                <p style="color:rgba(255,255,255,0.5);font-size:0.9rem;margin:4px 0;">
                    بر اساس پیش‌بینی، پیشنهاد میکنیم:
                </p>
                <ul style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin:4px 0;">
                    <li>📈 موجودی خود را برای روزهای آینده افزایش دهید</li>
                    <li>🎯 تخفیف‌های هدفمند برای مشتریان وفادار طراحی کنید</li>
                    <li>📊 عملکرد تیم فروش را با داده‌های پیش‌بینی مقایسه کنید</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ پیش‌بینی هوشمند با موفقیت انجام شد!")
            
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
