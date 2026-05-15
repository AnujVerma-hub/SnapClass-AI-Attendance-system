import streamlit as st
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.database.db import check_teacher_exists,create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher
from src.components.dailog_create_subjects import create_subject_dialog
from src.components.dialog_share_subjects import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_results_dialog
from src.components.subject_card import subject_card
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.database.config import supabase
import numpy as np
from datetime import datetime
import pandas as pd
from datetime import datetime

def teacher_screen():

    style_base_layout_dashboard()
    style_base_layout()

    
    
    # st.text_input("Enter Username", placeholder="@askname")
    # st.text_input("Enter Name", placeholder="Anuj Verma")
    # st.text_input("Enter Password", placeholder="Enter Your Password")
    # st.text_input("Confirm Password", placeholder="Confirm Your Password")

    # st.markdown("""----""")

    # cl1,cl2 = st.columns(2,gap='small', vertical_alignment='center')

    # with cl1:
    #     st.button("Resigter Now", shortcut="control+Enter", type='primary',width='stretch')
    # with cl2:
    #     st.button("Login instead", type='secondary',width='stretch')

    def teacher_dashboard():
        teacher_data = st.session_state.teacher_data
        c1, c2 = st.columns(2,vertical_alignment='center', gap='xxlarge')

        with c1:
            header_dashboard()

        with c2:
            st.subheader(f""" Welcome, {teacher_data['name']}""")
            if st.button("Logout",type='secondary',key='loginbackbtn', shortcut='control+backspace'):
                st.session_state["is_logged_in"] = False
                del st.session_state.teacher_data
                st.rerun()

        st.space()

        if "current_teacher_tab" not in st.session_state:
            st.session_state.current_teacher_tab = "take_attendance"

        tab1, tab2, tab3 = st.columns(3)

        with tab1:
            type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
            if st.button("Take Attendance",type=type1, width = 'stretch', icon=":material/ar_on_you:"):
                st.session_state.current_teacher_tab = "take_attendance"
                st.rerun()
        with tab2:
            type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
            if st.button("Manage subjects",type=type2, width = 'stretch', icon=":material/book_ribbon:"):
                st.session_state.current_teacher_tab = "manage_subjects"
                st.rerun()

        with tab3:
            type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
            if st.button("Attendance records",type=type3, width = 'stretch', icon=":material/cards_stack:"):
                st.session_state.current_teacher_tab = "attendance_records"
                st.rerun()

        st.divider()

        if st.session_state.current_teacher_tab == "take_attendance":
            teacher_tab_take_attendance()
        if st.session_state.current_teacher_tab == "manage_subjects":
            teacher_tab_manage_subjects()
        if st.session_state.current_teacher_tab == "attendance_records":
            teacher_tab_attendance_records()
        

    def teacher_tab_take_attendance():
        teacher_id = st.session_state.teacher_data['teacher_id']
        st.header("Take AI attendance")

        if "attendance_images" not in st.session_state:
            st.session_state.attendance_images = []

        subjects = get_teacher_subjects(teacher_id)
        if not subjects:
            st.warning("You haven't created any subjects yet! Please create onr to begin")
            return

        subject_options = {f"{s['name']}- {s['subject_code']}": s['subject_id'] for s in subjects}

        col1 , col2 = st.columns([3,1], vertical_alignment='bottom')

        with col1:
            selected_subject_labels = st.selectbox("Select Subject", options=list(subject_options.keys()))
        with col2:
            if st.button("Add Photos", type='primary', icon=":material/photo_prints:", width='stretch'):
                add_photos_dialog()

        selected_subject_id = subject_options[selected_subject_labels]

        st.divider()

        if st.session_state.attendance_images:
            st.header("Added Photos")
            galary_cols = st.columns(4)

            for idx, img in enumerate(st.session_state.attendance_images):
                with galary_cols[idx % 4]:
                    st.image(img, width='stretch', caption=f"Photo {idx+1}")

        has_images = bool(st.session_state.attendance_images)
        c1,c2,c3 = st.columns(3)

        with c1:
            if st.button("Clear All photos", width='stretch', type='tertiary', icon=":material/delete:", disabled=not has_images):
                st.session_state.attendance_images = []
                st.rerun()

        with c2:
            

            if st.button("Run Face Analysis", width='stretch', type='secondary', icon=":material/analytics:", disabled=not has_images):
                with st.spinner("Deep Scanning Classroom Images.."):
                    all_detected_id = {}

                    for idx, img in enumerate(st.session_state.attendance_images):
                        np_img = np.array(img.convert('RGB'))
                        detected,_,_ = predict_attendance(np_img)

                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)

                                all_detected_id.setdefault(student_id,[]).append(f"Photo {idx+1}")

                    enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id",selected_subject_id).execute()

                    enrolled_students = enrolled_res.data

                    if not enrolled_students:
                        st.warning("No students enrolled in this course")

                    else:
                        results, attendance_logs = [],[]

                        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                        for node in enrolled_students:
                            student = node['students']
                            sources = all_detected_id.get(int(student['student_id']), [])
                            is_present = len(sources) > 0

                            results.append({
                                "Name": student['name'],
                                "ID": student['student_id'],
                                "Source": ", ".join(sources) if is_present else "-",
                                "Status": "✅ Present" if is_present else "❌ Absent"
                            })

                            attendance_logs.append({
                                "student_id": student['student_id'],
                                "subject_id": selected_subject_id,
                                "timestamp": current_timestamp,
                                "is_present": bool(is_present)
                            })


                    attendance_results_dialog(pd.DataFrame(results), attendance_logs)


        with c3:
            if st.button("use voice attendance", type='primary', width='stretch', icon=":material/mic:"):
                voice_attendance_dialog(selected_subject_id)





                

    def teacher_tab_manage_subjects():
        teacher_id = st.session_state.teacher_data['teacher_id']
        col1, col2 = st.columns(2)
        with col1:
            st.header('Manage Subjects', width='stretch')

        with col2:
            if st.button('Create New Subject', width='stretch'):
                create_subject_dialog(teacher_id)


        # LIST all SUBJECTS
        subjects = get_teacher_subjects(teacher_id)
        if subjects:
            for sub in subjects:
                stats = [
                    ("🫂", "Students", sub['total_students']),
                    ("🕰️", "Classes", sub['total_classes']),
                ]
            def share_btn():
                if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.space()

            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats=stats,
                footer_callback=share_btn
            )
        else:
            st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")



    def teacher_tab_attendance_records():
        st.header("Attendance records")

        teacher_id = st.session_state.teacher_data['teacher_id']

        records = get_attendance_for_teacher(teacher_id)

        if not records:
            return
        
        data = []

        for r in records:
            ts = r.get('timestamp')

            data.append({
                "ts_group": ts.split(".")[0] if ts else None,
                "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else None,
                "Subject": r['subjects']['name'],
                "Subject Code": r['subjects']['subject_code'],
                "is_present": bool(r.get("is_present",False))
            })

        df = pd.DataFrame(data)

        summary = (
            df.groupby(["ts_group","Time", "Subject", "Subject Code"])
            .agg(
                present_count = ('is_present','sum'),
                total_count = ('is_present', 'count')
            ).reset_index()
        )

        summary["Attendance Stats"] = (
            "✅ " + summary['present_count'].astype(str) + " /"
            + summary['total_count'].astype(str) + " Students"
        )

        display_df = (summary.sort_values(by="ts_group", ascending=True)
                      [["Time", "Subject", "Subject Code", "Attendance Stats"]]
                      
                      )

        st.dataframe(display_df, width='stretch', hide_index=True)


        

    def login_teacher(username, password):
        if not username or not password:
            return False
        
        teacher = teacher_login(username, password)

        if teacher:
            st.session_state.user_role = "teacher"
            st.session_state.teacher_data = teacher
            st.session_state.is_logged_in = True
            return True
        return False

    def teacher_screen_login():
        c1, c2 = st.columns(2,vertical_alignment='center', gap='xxlarge')

        with c1:
            header_dashboard()

        with c2:
            if st.button("Go back to Home",type='secondary',key='loginbackbtn', shortcut='control+backspace'):
                st.session_state["login_type"] = None
                st.rerun()
            

        st.header("Login using Password", text_alignment='center')
        st.space()
        st.space()

        teacher_username = st.text_input("Enter Username", placeholder="@askname")
        teacher_passoword = st.text_input('Enter password', type='password', placeholder='Enter your Password')

        st.divider()

        cl1,cl2 = st.columns(2,gap='small', vertical_alignment='center')

        with cl1:
            if st.button("Login Now", shortcut="control+Enter", type='secondary',width='stretch', icon=':material/passkey:'):
                if login_teacher(teacher_username,teacher_passoword):
                    st.toast("welcome back!", icon="👋")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username and password")
                
        with cl2:
            if st.button("Register Instead", type='primary',width='stretch', icon=':material/passkey:'):
                st.session_state.teacher_login_type = "register"

    def register_teacher(teacher_username,teacher_name,teacher_password,confirm_password):
        if not teacher_username or not teacher_name or not teacher_password:
            return False, "All Fields are Required!"
        if check_teacher_exists(teacher_username):
            return False, "Username already taken"
        if teacher_password != confirm_password:
            return False, "Password doesn't match"
        
        try:
            create_teacher(teacher_username,teacher_password,teacher_name)
            return True, "Successfully Created! Login now"
        except Exception as e:
            return False, "Unexpected Error"
        
        

    def teacher_screen_register():
        c1, c2 = st.columns(2,vertical_alignment='center', gap='xxlarge')

        with c1:
            header_dashboard()

        with c2:
            if st.button("Go back to Home",type='secondary',key='loginbackbtn', shortcut='control+backspace'):
                st.session_state["login_type"] = None
                st.rerun()
            

        st.header("Register Your Teacher Profile")

        st.space()
        st.space()

        
        teacher_username = st.text_input("Enter Username", placeholder="@askname")
        teacher_name = st.text_input("Enter Name", placeholder="Anuj Verma")
        teacher_password = st.text_input("Enter Password", placeholder="Enter Your Password",type='password')
        confirm_password = st.text_input("Confirm Password", placeholder="Confirm Your Password", type='password')

        st.divider()

        cl1,cl2 = st.columns(2,gap='small', vertical_alignment='center')

        with cl1:
            if st.button("Register Now", shortcut="control+Enter", type='primary',width='stretch', icon=':material/passkey:'):
                success, message = register_teacher(teacher_username,teacher_name,teacher_password,confirm_password)

                if success:
                    st.success(message)
                    import time
                    time.sleep(2)
                    st.session_state.teacher_login_type = "login"
                    st.rerun()
                else:
                    st.error(message)
                
        with cl2:
            if st.button("Login Instead", type='secondary',width='stretch', icon=':material/passkey:'):
                st.session_state.teacher_login_type = "login"

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == 'login':
        teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()



        

