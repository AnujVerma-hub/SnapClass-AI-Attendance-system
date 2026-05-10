import streamlit as st
from src.database.config import supabase
from src.database.db import enroll_student_to_subject
import time
from PIL import Image
from src.database.db import create_attendance

def show_attendance_resutls(df, logs):
    st.write("Please Review attenance before confirming")
    st.dataframe(df,hide_index=True, width='stretch')

    c1, c2 = st.columns(2)

    with c1:
       if st.button("Discard",width='stretch'):
           st.session_state.attendance_images = []
           st.session_state.voice_attendance_results = None
           st.rerun()

    with c2:
        if st.button("Confirm & Save", type='primary',width='stretch'):
            try:
                create_attendance(logs)
                st.toast("Attendance taken")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception as e:
                st.error("sync failed")


@st.dialog("Attendance Results")
def attendance_results_dialog(df, logs):
    show_attendance_resutls(df,logs)

    

                
        
