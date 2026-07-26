import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
import jdatetime
import time
warnings.filterwarnings('ignore')

# ==========================================
# تنظیمات اولیه
# ==========================================
st.set_page_config(
    page_title="iHoNoor | پیش‌بینی هوشمند",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# استایل ساده و زیبا
# ==========================================
st.markdown("""
<style>
    * { direction: rtl; font-family: 'Vazirmatn', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #0A1628, #1A2A4A);
        padding: 25px 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        color: rgba(255,255,255,0.6);
        margin-top: 5px;
    }
    .card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        color: white;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FFD700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .result-box {
        background: rgba(255,215,0,0.05);
        border: 1px solid rgba(255,215,0,0.1);
        border-radius: 16px;
        padding: 25px 30px;
        text-align: center;
        margin-top: 12px;
    }
    .result-number {
        font-size: 2.8rem;
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
        background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,165,0,0.02));
        border: 1px solid rgba(255,215,0,0.1);
        border-radius: 12px;
        padding: 12px 32px;
        color: #FFD700;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        border-color: rgba(255,215,0,0.3);
        box-shadow: 0 0 30px rgba(255,215,0,0.02);
    }
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.1);
        font-size: 0.7rem;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.02);
    }
    .step-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 12px 18px;
        text-align: center;
        flex: 1;
        min-width: 100px;
    }
    .step-item .num {
        display: inline-block;
        width: 28px;
        height: 28px;
        background: rgba(255,215,0,0.1);
        border-radius: 50%;
        line-height: 28px;
        color: #FFD700;
        font-weight: 800;
        font-size: 0.8rem;
    }
    .step-item .text {
        color: rgba(255,255,255,0.6);
        font-size: 0.8rem;
        margin-top: 4px;
    }
    .steps {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# هدر
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>✨ iHoNoor</h1>
    <p>پیش‌بینی هوشمند فروش | ساده، سریع، دقیق</p>
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
    "🏪 خواربارفروشی", "🔩 آهن‌آلات", "🚗 خودرو", "👗 پوشاک",
    "📱 فناوری", "🛒 خرده‌فروشی", "🏭 تولید", "💰 بانکداری",
    "🏥 بهداشت", "🍔 صنایع غذایی", "⛽ پتروشیمی", "⚡ برق",
    "🏢 املاک", "🏗️ ساختمان", "📦 مدیریت موجودی"
]

with st.sidebar:
    st.markdown("""
    <div style="background:rgba(255,215,0,0.03);border:1px solid rgba(255,215,0,0.05);border-radius:12px;padding:16px;text-align:center;margin-bottom:16px;">
        <h1 style="font-size:1.8rem;margin:0;background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">iHo<span style="background:linear-gradient(135deg,#FFD700,#FFA500);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Noor</span></h1>
        <p style="color:rgba(255,255,255,0.2);font-size:0.65rem;">پیش‌بینی هوشمند</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ انتخاب صنف", industries)
    
    st.markdown("---")
    
    فایل = st.file_uploader("📁 آپلود فایل", type=["csv", "xlsx", "xls"])
    
    st.markdown("---")
    
    st.caption("💡 فایل نمونه: شامل ستون‌های تاریخ و فروش")

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
        'قیمت': np.random.randint(10_000, 50_000, 100)
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
    st.dataframe(data.head(5))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 خلاصه</div>', unsafe_allow_html=True)
    st.dataframe(data.describe())
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

# تشخیص واحد
def detect_unit(col):
    col = col.lower()
    if any(w in col for w in ['نفر', 'مشتری', 'تعداد']): return 'نفر'
    if any(w in col for w in ['تومان', 'ریال', 'فروش', 'قیمت', 'درآمد']): return 'تومان'
    if 'درصد' in col: return 'درصد'
    return 'واحد'

unit = detect_unit(target)
st.info(f"✅ واحد: **{unit}**")

# ==========================================
# بازه زمانی
# ==========================================
st.subheader("📅 بازه زمانی")
forecast_days = st.selectbox(
    "چند روز آینده؟",
    [1, 3, 7, 14, 30],
    format_func=lambda x: f"{x} روز"
)

# ==========================================
# دکمه پیش‌بینی
# ==========================================
if st.button("🚀 پیش‌بینی کن", type="primary", use_container_width=True):
    with st.spinner("⏳ در حال پیش‌بینی..."):
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
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = r2_score(y_test, y_pred)
            
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
            
            # دقت
            st.metric("🎯 دقت مدل", f"{score:.1%}")
            
            # جدول
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
                title=f'روند پیش‌بینی',
                xaxis_title='تاریخ',
                yaxis_title=unit,
                height=300,
                plot_bgcolor='rgba(255,255,255,0.02)',
                paper_bgcolor='rgba(255,255,255,0.02)',
                font=dict(color='rgba(255,255,255,0.8)')
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
    ✨ iHoNoor | ha2021alipur@gmail.com
</div>
""", unsafe_allow_html=True)
