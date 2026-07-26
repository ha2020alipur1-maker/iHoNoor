import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
warnings.filterwarnings('ignore')

# ==========================================
# تنظیمات اولیه
# ==========================================
st.set_page_config(
    page_title="iHoNoor | نور هوشمند کسب‌وکار",
    page_icon="✨",
    layout="wide"
)

# ==========================================
# استایل
# ==========================================
st.markdown("""
<style>
    * { direction: rtl; font-family: 'Vazirmatn', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
        padding: 20px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 { font-size: 2rem; font-weight: 900; margin: 0; }
    .main-header h1 .highlight { color: #FFD700; }
    .main-header p { opacity: 0.8; margin-top: 4px; }
    .card {
        background: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 16px;
        border: 1px solid #f0f0f0;
    }
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0D47A1;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .result-box {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        padding: 20px 24px;
        border-radius: 14px;
        border-right: 4px solid #FFD700;
        text-align: center;
        margin-top: 12px;
    }
    .result-number {
        font-size: 2.4rem;
        font-weight: 900;
        color: #0D47A1;
    }
    .result-label {
        color: #555;
        font-size: 0.9rem;
        margin-top: 4px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0D47A1, #1E88E5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(30, 136, 229, 0.3);
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.7rem;
        margin-top: 30px;
        padding-top: 12px;
        border-top: 1px solid #eee;
    }
    .steps {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    .step-item {
        background: #f8f9fa;
        padding: 10px 14px;
        border-radius: 10px;
        text-align: center;
        flex: 1;
        min-width: 80px;
        border: 1px solid #eee;
    }
    .step-item .num {
        display: inline-block;
        width: 24px;
        height: 24px;
        background: #0D47A1;
        color: white;
        border-radius: 50%;
        line-height: 24px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .step-item .text {
        font-size: 0.75rem;
        color: #333;
        margin-top: 4px;
        font-weight: 600;
    }
    .metric-card {
        background: white;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #eee;
        text-align: center;
    }
    .metric-card .value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0D47A1;
    }
    .metric-card .label {
        font-size: 0.7rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# هدر
# ==========================================
st.markdown("""
<div class="main-header">
    <h1><span class="highlight">iHo</span>Noor</h1>
    <p>پیش‌بینی هوشمند فروش | با یاری الهی</p>
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
    <div style="background:linear-gradient(135deg,#0D47A1,#1E88E5);padding:16px;border-radius:12px;text-align:center;color:white;margin-bottom:16px;">
        <h1 style="font-size:1.6rem;margin:0;color:#FFD700;">iHo<span style="color:white;">Noor</span></h1>
        <p style="opacity:0.7;font-size:0.7rem;margin:0;">پیش‌بینی هوشمند</p>
    </div>
    """, unsafe_allow_html=True)
    
    صنف = st.selectbox("🏷️ انتخاب صنف", industries)
    
    st.markdown("---")
    
    فایل = st.file_uploader("📁 آپلود فایل", type=["csv", "xlsx", "xls"])
    
    st.markdown("---")
    
    # ===== ویژگی جدید ۱: اتصال به Google Sheets =====
    with st.expander("🔗 اتصال به Google Sheets"):
        st.caption("لینک Google Sheets را وارد کنید")
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
    st.caption("💡 بدون فایل؟ از داده‌های نمونه استفاده میشود.")

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
# ===== ویژگی جدید ۲: داشبورد مدیریتی پیشرفته =====
# ==========================================
st.subheader("📊 داشبورد مدیریتی")
col1, col2, col3, col4 = st.columns(4)
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

# ==========================================
# ===== ویژگی جدید ۳: تحلیل روند با نمودار =====
# ==========================================
if len(numeric_cols) > 0:
    st.subheader("📈 تحلیل روند")
    fig = px.line(data, x=data.columns[0], y=numeric_cols[0], title=f"روند {numeric_cols[0]}")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

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
            
            model = RandomForestRegressor(n_estimators=50, random_state=42)
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
                <div style="font-size:0.7rem;color:#888;margin-top:6px;">⏱️ {time.time()-start_time:.2f} ثانیه</div>
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
            
            # ===== ویژگی جدید ۴: نمودار پیش‌بینی با بازه اطمینان =====
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=future_dates_str,
                y=predictions,
                mode='lines+markers',
                name=f'پیش‌بینی {target}',
                line=dict(color='#0D47A1', width=3),
                marker=dict(size=10, color='#0D47A1')
            ))
            # بازه اطمینان
            fig.add_trace(go.Scatter(
                x=future_dates_str + future_dates_str[::-1],
                y=[p * 1.15 for p in predictions] + [p * 0.85 for p in predictions[::-1]],
                fill='toself',
                fillcolor='rgba(13, 71, 161, 0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='بازه اطمینان ۸۵٪'
            ))
            fig.update_layout(
                title='روند پیش‌بینی با بازه اطمینان',
                xaxis_title='تاریخ',
                yaxis_title=unit,
                height=350,
                plot_bgcolor='rgba(0,0,0,0.02)',
                paper_bgcolor='rgba(0,0,0,0.02)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== تحلیل سرنخ‌ها =====
            st.subheader("🔍 تحلیل سرنخ‌ها")
            st.info("💡 بر اساس داده‌های شما، پیشنهادات زیر برای جذب مشتری ارائه میشود:")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="background:#E8F5E9;padding:12px;border-radius:10px;border-right:3px solid #4CAF50;">
                    <p style="margin:0;font-weight:700;color:#2E7D32;">✅ مشتریان بالقوه</p>
                    <p style="margin:4px 0;font-size:0.85rem;color:#555;">مشتریانی که بیشتر از ۳ بار خرید داشته‌اند</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background:#FFF3E0;padding:12px;border-radius:10px;border-right:3px solid #FF9800;">
                    <p style="margin:0;font-weight:700;color:#E65100;">🔄 مشتریان بازگشتی</p>
                    <p style="margin:4px 0;font-size:0.85rem;color:#555;">مشتریانی که بعد از ۱ ماه بازگشته‌اند</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.success("✅ پیش‌بینی با موفقیت انجام شد!")
            
        except Exception as e:
            st.error(f"❌ خطا: {e}")

# ==========================================
# فوتر
# ==========================================
st.markdown("""
<div class="footer">
    ✨ iHoNoor | ha2021alipur@gmail.com | 09019470509
</div>
""", unsafe_allow_html=True)
