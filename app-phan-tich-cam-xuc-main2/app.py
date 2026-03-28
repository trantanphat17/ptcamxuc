import streamlit as st
import pandas as pd
import time
import plotly.express as px  
import re 
from groq import Groq # SỬ DỤNG THƯ VIỆN MỚI
from st_aggrid import AgGrid, GridOptionsBuilder

# =============================
# CẤU HÌNH API GROQ (LLAMA 3)
# =============================
# Lấy API key từ file secrets.toml
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

def clean_text(text):
    text = str(text) 
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    return text.strip()

def analyze(text):
    try:
        cleaned_text = clean_text(text)
        if not cleaned_text:
            return None
            
        # Gọi API Groq với mô hình Llama 3 8B (Nhanh và mượt)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia phân tích cảm xúc. Chỉ được phép trả về duy nhất 1 từ: 'POS' (nếu tích cực), 'NEG' (nếu tiêu cực), hoặc 'NEU' (nếu bình thường). Tuyệt đối không giải thích thêm."
                },
                {
                    "role": "user",
                    "content": f"Bình luận: '{cleaned_text}'"
                }
            ],
            model="llama-3.3-70b-versatile", 
            temperature=0.1,
        )
        
        result = chat_completion.choices[0].message.content.strip().upper()
        
        # Làm sạch kết quả trả về
        if "POS" in result: return "POS"
        elif "NEG" in result: return "NEG"
        elif "NEU" in result: return "NEU"
        else: return "NEU" 
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# =============================
# HÀM VẼ BẢNG: ÉP CSS TRỰC TIẾP VÀO LÕI AG-GRID
# =============================
def display_full_text_grid(dataframe, height=250):
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(wrapText=True, autoHeight=True, enableMenu=False, enableFilter=False, resizable=True)
    if "noi_dung_binh_luan" in dataframe.columns:
        gb.configure_column("noi_dung_binh_luan", wrapText=True, autoHeight=True, flex=1)
    elif "Bình luận gốc" in dataframe.columns:
        gb.configure_column("Bình luận gốc", wrapText=True, autoHeight=True, flex=1)
        
    grid_options = gb.build()
    
    giao_dien_dark_mode = {
        ".ag-root-wrapper": {"border": "1px solid #333f50 !important", "border-radius": "10px !important", "overflow": "hidden"},
        ".ag-header": {"background-color": "#0e1117 !important", "border-bottom": "1px solid #333f50 !important"},
        ".ag-header-cell-text": {"color": "#9ca3af !important", "font-weight": "bold !important", "font-size": "14px"},
        ".ag-row": {"background-color": "#0e1117 !important", "border-bottom": "1px solid #333f50 !important"},
        ".ag-cell": {"color": "#fafafa !important", "line-height": "1.5 !important", "padding": "10px !important"},
        ".ag-row-hover": {"background-color": "#262730 !important"}
    }
    
    AgGrid(dataframe, gridOptions=grid_options, height=height, width="100%", theme="streamlit", custom_css=giao_dien_dark_mode, fit_columns_on_grid_load=True)

# =============================
# CẤU HÌNH TRANG & GIAO DIỆN (CSS)
# =============================
st.set_page_config(page_title="Phân Tích Cảm Xúc bằng AI", page_icon="✨", layout="centered")

st.markdown("""
<style>
.stApp{ background: radial-gradient(circle at top,#0f172a,#020617); color:white; }
.hero{ text-align:center; padding:40px; }
.hero h1{ font-size:55px; font-weight:800; background: linear-gradient(90deg,#22c1c3,#fdbb2d); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p{ color:#9ca3af; font-size:20px; }
.result-box{ padding:20px; border-radius:15px; text-align:center; font-size:22px; font-weight:700; margin-top: 20px; }
.positive{ background:#052e16; color:#4ade80; border: 1px solid #4ade80; }
.negative{ background:#450a0a; color:#f87171; border: 1px solid #f87171; }
.neutral{ background:#422006; color:#facc15; border: 1px solid #facc15; }
div.streamlit-aggrid { border: 1px solid #475569; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(34, 193, 195, 0.3); color: white !important; }
div.streamlit-aggrid .ag-theme-alpine-dark { color: white !important; }
div[data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
button[data-baseweb="tab"] { border: 2px solid #475569 !important; border-radius: 10px !important; padding: 10px 30px !important; background-color: transparent !important; color: #9ca3af !important; transition: all 0.3s ease-in-out !important; }
button[data-baseweb="tab"]:hover { border-color: #22c1c3 !important; color: white !important; }
button[data-baseweb="tab"][aria-selected="true"] { background: linear-gradient(90deg, #1e293b, #0f172a) !important; border: 2px solid #22c1c3 !important; color: #22c1c3 !important; box-shadow: 0 4px 15px rgba(34, 193, 195, 0.3) !important; }
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>HỆ THỐNG PHÂN TÍCH CẢM XÚC</h1>
    <p>Tích hợp Siêu mô hình AI Llama 3 (Meta) siêu tốc độ</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Phân tích Nhanh", "Phân tích File Dữ liệu"])

with tab1:
    st.write("Phân tích Một Bình luận")
    text = st.text_area("Nhập bình luận của bạn:", placeholder="Ví dụ: App load nhanh, giao diện đẹp 10 điểm...", height=120)
    
    if st.button("Phân tích bằng AI", key="btn_instant"):
        if text.strip() == "":
            st.warning("Vui lòng nhập bình luận trước khi phân tích!")
        else:
            with st.spinner("Llama 3 đang xử lý..."):
                label = analyze(text)
                
                if label in ["POS", "NEG", "NEU"]:
                    if label == "POS":
                        st.markdown(f"<div class='result-box positive'>Tích Cực</div>", unsafe_allow_html=True)
                    elif label == "NEG":
                        st.markdown(f"<div class='result-box negative'>Tiêu Cực</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-box neutral'>Bình Thường</div>", unsafe_allow_html=True)
                else:
                    st.error(f"Lỗi hệ thống: {label}")

with tab2:
    st.write("Phân tích Tập dữ liệu (CSV)")
    file = st.file_uploader("Tải lên file định dạng CSV", type="csv")
    
    if file:
        df = pd.read_csv(file)
        st.write("**Xem trước toàn bộ dữ liệu:**")
        display_full_text_grid(df.copy(), height=250)
           
        valid_columns = [col for col in df.columns if not str(col).startswith("::")]
        column = st.selectbox("Chọn cột chứa bình luận cần phân tích:", valid_columns)
        max_rows = len(df)
        num_rows = st.slider("Chọn số lượng bình luận muốn phân tích:", min_value=1, max_value=max_rows, value=min(20, max_rows))
        
        if st.button("Bắt đầu Phân tích Dữ liệu", key="btn_dataset"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            data_to_analyze = df.head(num_rows)
            total_rows = len(data_to_analyze)
            
            for i, row in data_to_analyze.iterrows():
                status_text.text(f"Đang phân tích dòng {i+1} / {total_rows}...")
                text_val = str(row[column])
                
                label = analyze(text_val)
                star = "Lỗi / Không xác định"
                
                if label == "POS": star = "Tích cực"
                elif label == "NEG": star = "Tiêu cực"
                elif label == "NEU": star = "Bình thường"
                elif label and "ERROR" in label: star = f"Lỗi API: Rate Limit"
                
                results.append({
                    "Bình luận gốc": text_val,
                    "Phân loại cảm xúc": star
                })
                
                progress_bar.progress((i + 1) / total_rows)
                # Groq cho phép 30 câu/phút, nghỉ 2.5s là cực kỳ an toàn
                time.sleep(2.5) 
            
            status_text.empty()
            st.success("Phân tích hoàn tất!")
            
            result_df = pd.DataFrame(results)
            display_full_text_grid(result_df, height=250)
            
            st.markdown("Tổng quan Cảm xúc")
            sentiment_counts = result_df["Phân loại cảm xúc"].value_counts().reset_index()
            sentiment_counts.columns = ["Cảm xúc", "Số lượng"]
            
            color_discrete_map = {
                "Tích cực": "#4ade80",   
                "Tiêu cực": "#f87171",
                "Bình thường": "#facc15"
            }
            
            for lbl in sentiment_counts["Cảm xúc"]:
                if lbl not in color_discrete_map:
                    color_discrete_map[lbl] = "#9ca3af"
            
            fig = px.pie(
                sentiment_counts, 
                values="Số lượng", 
                names="Cảm xúc",
                color="Cảm xúc",
                color_discrete_map=color_discrete_map,
                hole=0.4 
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            
            st.plotly_chart(fig, use_container_width=True)