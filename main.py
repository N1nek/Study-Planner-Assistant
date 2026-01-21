import streamlit as st
import google.generativeai as genai
from datetime import date
import pandas as pd
import plotly.express as px
from database import get_db_managers

# Page config
st.set_page_config(
    page_title="Study Planner Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #f5f5f5;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.main-header {
    text-align: center;
    color: #1a1a1a;
    font-size: 2.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.sub-header {
    text-align: center;
    color: #333333;
    font-size: 1rem;
    margin-bottom: 2rem;
}
.stButton>button {
    background-color: #5a6c7d;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #3d4f5e;
    border: none;
}
.delete-button {
    background-color: #e74c3c !important;
}
.delete-button:hover {
    background-color: #c0392b !important;
}
.stat-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
}
.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #1a1a1a;
}
.stat-label {
    color: #333333;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}
.subject-card {
    background-color: white;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border-left: 4px solid #5a6c7d;
}
.stMarkdown p, .stMarkdown {
    color: #1a1a1a !important;
}
[data-testid="stMetricLabel"] {
    color: #333333 !important;
}
[data-testid="stMetricValue"] {
    color: #1a1a1a !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize database managers
if 'db_managers' not in st.session_state:
    st.session_state.db_managers = get_db_managers()

db_mgr = st.session_state.db_managers

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize API key
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.gemini_api_key,
        help="Enter your Google Gemini API key from https://aistudio.google.com/app/apikey"
    )

    if api_key:
        st.session_state.gemini_api_key = api_key
        try:
            genai.configure(api_key=api_key)
            st.success("✓ API Key configured")
        except Exception as e:
            st.error(f"API Key error: {str(e)}")
    else:
        st.warning("⚠ Please enter your Gemini API key")

    st.markdown("---")
    st.markdown("### 📍 Navigation")
    page = st.radio(
        "Go to:",
        ["🏠 Home", "💬 Chat Assistant", "📚 Subjects", "📝 Tasks", "📊 Analytics"],
        label_visibility="collapsed"
    )

# AI Chat function
def chat_with_ai(message):
    if not st.session_state.gemini_api_key:
        return "Please configure your Gemini API key in the sidebar."

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # Build context
        subjects_df = db_mgr['subjects'].read()
        tasks_df = db_mgr['tasks'].read()
        pending_count = len(db_mgr['tasks'].get_by_status(completed=False))

        context = f"""You are a helpful study planning assistant.
Current subjects: {subjects_df["name"].tolist() if not subjects_df.empty else "None"}
Pending tasks: {pending_count}

User question: {message}

Provide helpful, concise advice about studying, time management, or task prioritization."""

        response = model.generate_content(context)
        return response.text

    except Exception as e:
        return f"Error: {str(e)}. Make sure you're using a valid API key from https://aistudio.google.com/app/apikey"

# PAGES
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">📚 Study Planner Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered study scheduling and task management</p>', unsafe_allow_html=True)

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📅 Generate Weekly Schedule", use_container_width=True):
            st.info("Navigate to Chat Assistant to generate your schedule!")

    with col2:
        if st.button("💡 Study Tips", use_container_width=True):
            st.info("Navigate to Chat Assistant for personalized study tips!")

    with col3:
        if st.button("🎯 Prioritize Tasks", use_container_width=True):
            st.info("Navigate to Tasks to manage your priorities!")

    st.markdown("---")

    # Get metrics
    total_hours = db_mgr['analytics'].get_total_study_hours()
    task_stats = db_mgr['analytics'].get_task_stats()
    avg_difficulty = db_mgr['analytics'].get_average_difficulty()

    # Quick Stats
    st.markdown("### 📈 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_hours:.1f}h</div><div class="stat-label">Total Study Hours</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{task_stats["completed"]}</div><div class="stat-label">Completed Tasks</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{task_stats["pending"]}</div><div class="stat-label">Pending Tasks</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_difficulty:.1f}/10</div><div class="stat-label">Avg Difficulty</div></div>', unsafe_allow_html=True)

elif page == "💬 Chat Assistant":
    st.markdown('<h1 class="main-header">💬 Chat with AI Study Assistant</h1>', unsafe_allow_html=True)

    if not st.session_state.gemini_api_key:
        st.warning("⚠ Please enter your Gemini API key in the sidebar to use the chat assistant.")
        st.info("Get your free API key at https://aistudio.google.com/app/apikey")

    # Chat container
    chat_container = st.container()

    with chat_container:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["message"])
            with st.chat_message("assistant"):
                st.write(chat["response"])

    # Chat input
    user_message = st.chat_input("Ask me anything about your studies...")

    if user_message:
        with chat_container:
            with st.chat_message("user"):
                st.write(user_message)

            with st.spinner("Thinking..."):
                response = chat_with_ai(user_message)

            with chat_container:
                with st.chat_message("assistant"):
                    st.write(response)

        # Save to history
        st.session_state.chat_history.append({"message": user_message, "response": response})
        db_mgr['chat'].create(user_message, response)

elif page == "📚 Subjects":
    st.markdown('<h1 class="main-header">📚 Manage Subjects</h1>', unsafe_allow_html=True)

    # Add new subject form
    with st.expander("➕ Add New Subject", expanded=False):
        with st.form("add_subject_form"):
            col1, col2 = st.columns(2)

            with col1:
                subject_name = st.text_input("Subject Name")
                difficulty = st.slider("Difficulty Level", 1, 10, 5)

            with col2:
                hours = st.number_input("Weekly Hours", min_value=0.5, max_value=40.0, value=3.0, step=0.5)
                priority = st.slider("Priority", 1, 5, 3)

            submitted = st.form_submit_button("Add Subject")

            if submitted and subject_name:
                db_mgr['subjects'].create(subject_name, difficulty, hours, priority)
                st.success(f"✓ Added subject: {subject_name}")
                st.rerun()

    # Display subjects
    subjects = db_mgr['subjects'].read()

    if not subjects.empty:
        st.markdown("### Your Subjects")

        for _, subject in subjects.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                with col1:
                    st.markdown(f"**{subject['name']}**")

                with col2:
                    st.markdown(f"🎯 Difficulty: {subject['difficulty']}/10")

                with col3:
                    st.markdown(f"⏰ {subject['hours']}h/week")

                with col4:
                    st.markdown(f"🔥 Priority: {subject['priority']}/5")

                with col5:
                    # Delete button for each subject
                    if st.button("🗑️ Delete", key=f"delete_{subject['id']}", type="secondary"):
                        db_mgr['subjects'].delete(subject['id'])
                        st.success(f"✓ Deleted: {subject['name']}")
                        st.rerun()

                st.markdown("---")
    else:
        st.info("No subjects added yet. Add your first subject above!")

elif page == "📝 Tasks":
    st.markdown('<h1 class="main-header">📝 Manage Tasks</h1>', unsafe_allow_html=True)

    subjects = db_mgr['subjects'].read()

    if subjects.empty:
        st.warning("⚠ Please add subjects first before creating tasks!")
    else:
        # Add new task form
        with st.expander("➕ Add New Task", expanded=False):
            with st.form("add_task_form"):
                col1, col2 = st.columns(2)

                with col1:
                    task_subject = st.selectbox("Subject", subjects['name'].tolist())
                    task_title = st.text_input("Task Title")
                    task_description = st.text_area("Description")

                with col2:
                    task_due_date = st.date_input("Due Date")
                    task_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=20.0, value=2.0, step=0.5)

                submitted = st.form_submit_button("Add Task")

                if submitted and task_title:
                    subject_id = subjects[subjects['name'] == task_subject]['id'].iloc[0]
                    db_mgr['tasks'].create(subject_id, task_title, task_description, task_due_date, task_hours)
                    st.success(f"✓ Added task: {task_title}")
                    st.rerun()

        # Display tasks in tabs
        st.markdown("### Your Tasks")
        tab1, tab2 = st.tabs(["⏳ Pending", "✅ Completed"])

        with tab1:
            pending_tasks = db_mgr['tasks'].get_by_status(completed=False)

            if not pending_tasks.empty:
                for _, task in pending_tasks.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([4, 2, 1])

                        with col1:
                            st.markdown(f"**{task['title']}**")
                            st.caption(f"Subject: {task['subject_name']}")
                            if task['description']:
                                st.caption(f"📄 {task['description']}")

                        with col2:
                            st.caption(f"📅 Due: {task['due_date']}")
                            st.caption(f"⏱️ Est: {task['estimated_hours']}h")

                        with col3:
                            if st.button("✓", key=f"complete_{task['id']}"):
                                db_mgr['tasks'].mark_complete(task['id'])
                                st.rerun()

                        st.markdown("---")
            else:
                st.info("No pending tasks!")

        with tab2:
            completed_tasks = db_mgr['tasks'].get_by_status(completed=True)

            if not completed_tasks.empty:
                for _, task in completed_tasks.iterrows():
                    with st.container():
                        col1, col2 = st.columns([4, 2])

                        with col1:
                            st.markdown(f"~~**{task['title']}**~~")
                            st.caption(f"Subject: {task['subject_name']}")

                        with col2:
                            st.caption(f"📅 Due: {task['due_date']}")
                            st.caption(f"⏱️ Est: {task['estimated_hours']}h")

                        st.markdown("---")
            else:
                st.info("No completed tasks yet!")

elif page == "📊 Analytics":
    st.markdown('<h1 class="main-header">📊 Study Analytics & Insights</h1>', unsafe_allow_html=True)

    # Get analytics
    total_hours = db_mgr['analytics'].get_total_study_hours()
    task_stats = db_mgr['analytics'].get_task_stats()
    avg_difficulty = db_mgr['analytics'].get_average_difficulty()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Study Hours", f"{total_hours:.1f}h")

    with col2:
        st.metric("Completed Tasks", task_stats["completed"])

    with col3:
        st.metric("Pending Tasks", task_stats["pending"])

    with col4:
        st.metric("Avg Difficulty", f"{avg_difficulty:.1f}/10")

    st.markdown("---")

    # Charts
    hours_by_subject = db_mgr['analytics'].get_hours_by_subject()

    if not hours_by_subject.empty and hours_by_subject['hours'].sum() > 0:
        st.markdown("### 📊 Study Hours by Subject")
        fig = px.bar(
            hours_by_subject, 
            x="name", 
            y="hours", 
            title="Total Study Hours per Subject",
            labels={"name": "Subject", "hours": "Hours"}, 
            color="hours", 
            color_continuous_scale="Greys"
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font=dict(color="#2c3e50"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📈 Task Completion Status")
    completion_data = pd.DataFrame({
        "Status": ["Completed", "Pending"], 
        "Count": [task_stats["completed"], task_stats["pending"]]
    })

    fig2 = px.pie(
        completion_data, 
        values="Count", 
        names="Status", 
        title="Task Distribution",
        color_discrete_sequence=["#7f8c8d", "#bdc3c7"]
    )
    fig2.update_layout(paper_bgcolor="white", font=dict(color="#2c3e50"))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Log study session (without reload button)
    st.markdown("### 📝 Log Study Session")

    subjects = db_mgr['subjects'].read()

    if not subjects.empty:
        with st.form("log_study_session"):
            col1, col2, col3 = st.columns(3)

            with col1:
                # Add empty option at the beginning
                subject_options = [""] + subjects['name'].tolist()
                log_subject = st.selectbox("Subject", subject_options, index=0)

            with col2:
                # Date with None as default (empty)
                log_date = st.date_input("Date", value=None)

            with col3:
                # Hours starting at 0
                log_hours = st.number_input("Hours Studied", min_value=0.0, max_value=12.0, value=0.0, step=0.5)

            log_notes = st.text_area("Notes (optional)", value="")

            submitted = st.form_submit_button("Log Session")

            if submitted:
                # Validation: ensure all required fields are filled
                if not log_subject or log_subject == "":
                    st.error("❌ Please select a subject!")
                elif log_date is None:
                    st.error("❌ Please select a date!")
                elif log_hours == 0.0:
                    st.warning("⚠️ Are you sure you want to log 0 hours?")
                else:
                    subject_id = subjects[subjects['name'] == log_subject]['id'].iloc[0]
                    db_mgr['logs'].create(subject_id, log_date, log_hours, log_notes)
                    st.success("✓ Study session logged!")
                    st.rerun()
    else:
        st.warning("⚠ Please add subjects first!")

    st.markdown("---")

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">📚 Study Planner Assistant | Built with Streamlit</p>', unsafe_allow_html=True)
