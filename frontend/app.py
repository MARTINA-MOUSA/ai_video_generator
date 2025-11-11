"""
Streamlit Frontend for AI Video Generator
"""
import streamlit as st
import requests
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Video Generator | مولد الفيديو بالذكاء الاصطناعي",
    page_icon="🎬",
    layout="wide"
)

# API Base URL
API_BASE_URL = st.sidebar.text_input(
    "API URL",
    value="http://localhost:8000",
    help="Backend API URL"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .video-container {
        margin: 2rem 0;
    }
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        display: inline-block;
    }
    .status-pending { background-color: #ffc107; color: #000; }
    .status-processing { background-color: #17a2b8; color: #fff; }
    .status-completed { background-color: #28a745; color: #fff; }
    .status-failed { background-color: #dc3545; color: #fff; }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def generate_video(prompt: str, duration: int = None, model: str = None):
    """Generate video via API"""
    try:
        payload = {"prompt": prompt}
        if duration:
            payload["duration"] = duration
        if model:
            payload["model"] = model
        
        response = requests.post(
            f"{API_BASE_URL}/api/video/generate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"خطأ في إنشاء الفيديو: {str(e)}")
        return None


def get_job_status(job_id: str):
    """Get job status"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/jobs/{job_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"خطأ في الحصول على حالة المهمة: {str(e)}")
        return None


def main():
    """Main application"""
    st.markdown('<div class="main-header"><h1>🎬 AI Video Generator</h1><h2>مولد الفيديو بالذكاء الاصطناعي</h2></div>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ لا يمكن الاتصال بالـ API. تأكد من تشغيل الـ Backend.")
        st.info("لتشغيل الـ Backend: `cd backend && uvicorn main:app --reload`")
        return
    
    st.success("✅ متصل بالـ API بنجاح")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎥 إنشاء فيديو جديد", "📊 حالة المهام", "📁 الفيديوهات المولدة"])
    
    with tab1:
        st.header("إنشاء فيديو جديد")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prompt = st.text_area(
                "أدخل البرومبت",
                height=150,
                placeholder="مثال: فيديو عن غروب الشمس على شاطئ البحر مع أمواج هادئة...",
                help="اكتب وصفاً تفصيلياً للفيديو الذي تريد إنشاءه"
            )
        
        with col2:
            duration = st.slider(
                "مدة الفيديو (ثانية)",
                min_value=5,
                max_value=120,
                value=10,
                step=5,
                help="الحد الأقصى: 120 ثانية (دقيقتان)"
            )
            
            model_choice = st.selectbox(
                "النموذج (اختياري)",
                ["تلقائي", "Gemini", "HuggingFace", "Replicate", "Fallback"],
                help="اختر النموذج المستخدم (أو اتركه تلقائي)"
            )
            
            # Map Arabic choice to API value
            model_map = {
                "تلقائي": None,
                "Gemini": "gemini",
                "HuggingFace": "huggingface",
                "Replicate": "replicate",
                "Fallback": "fallback"
            }
            model = model_map.get(model_choice)
        
        if st.button("🚀 إنشاء الفيديو", type="primary", use_container_width=True):
            if not prompt:
                st.warning("⚠️ يرجى إدخال برومبت")
            else:
                with st.spinner("جارٍ إنشاء الفيديو..."):
                    result = generate_video(
                        prompt,
                        duration if duration > 5 else None,
                        model
                    )
                    
                    if result:
                        st.success(f"✅ {result.get('message', 'تم بدء عملية الإنشاء')}")
                        st.info(f"🆔 Job ID: `{result.get('job_id')}`")
                        
                        # Store job ID in session state
                        if 'job_ids' not in st.session_state:
                            st.session_state.job_ids = []
                        st.session_state.job_ids.insert(0, result.get('job_id'))
    
    with tab2:
        st.header("حالة المهام")
        
        # Job ID input
        job_id = st.text_input("أدخل Job ID لمتابعة حالة المهمة")
        
        if job_id:
            if st.button("🔍 البحث", use_container_width=True):
                status = get_job_status(job_id)
                
                if status:
                    display_job_status(status)
        
        # Recent jobs from session
        if 'job_ids' in st.session_state and st.session_state.job_ids:
            st.subheader("المهام الأخيرة")
            for jid in st.session_state.job_ids[:5]:
                if st.button(f"📊 {jid[:8]}...", key=f"job_{jid}", use_container_width=True):
                    status = get_job_status(jid)
                    if status:
                        display_job_status(status)
    
    with tab3:
        st.header("الفيديوهات المولدة")
        st.info("قريباً: عرض جميع الفيديوهات المولدة")


def display_job_status(status: dict):
    """Display job status"""
    status_value = status.get('status', 'unknown')
    
    # Status badge
    status_colors = {
        'pending': 'status-pending',
        'processing': 'status-processing',
        'completed': 'status-completed',
        'failed': 'status-failed'
    }
    
    status_class = status_colors.get(status_value, '')
    st.markdown(f'<div class="status-badge {status_class}"><strong>الحالة: {status_value}</strong></div>', unsafe_allow_html=True)
    
    # Progress bar
    if status_value in ['pending', 'processing']:
        progress = status.get('progress', 0)
        st.progress(progress / 100)
        st.caption(f"التقدم: {progress}%")
    
    # Job details
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**البرومبت:**")
        st.write(status.get('prompt', 'N/A'))
        
        if status.get('enhanced_prompt'):
            with st.expander("البرومبت المحسن"):
                st.write(status.get('enhanced_prompt'))
    
    with col2:
        st.write("**التفاصيل:**")
        st.write(f"النموذج: {status.get('model_used', 'N/A')}")
        st.write(f"المدة: {status.get('duration_seconds', 'N/A')} ثانية")
        st.write(f"تاريخ الإنشاء: {status.get('created_at', 'N/A')}")
    
    # Video display
    if status_value == 'completed' and status.get('video_url'):
        st.subheader("🎥 الفيديو المولد")
        video_url = f"{API_BASE_URL}{status.get('video_url')}"
        st.video(video_url)
        
        if st.button("⬇️ تحميل الفيديو", use_container_width=True):
            st.info(f"رابط التحميل: {video_url}")
    
    # Error message
    if status_value == 'failed':
        st.error(f"❌ خطأ: {status.get('error_message', 'Unknown error')}")


if __name__ == "__main__":
    main()

