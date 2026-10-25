import streamlit as st
import pandas as pd
import database
from datetime import date

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None

database.create_users_table()    

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="JobTrack | Career Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PROFESSIONAL UI
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #172554;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    div.stButton > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 600;
    }

    div[data-testid="stForm"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.title("💼 JobTrack")
    st.caption("YOUR CAREER COMPANION")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "➕ Add Application",
            "📋 My Applications",
            "🔄 Update Status",
            "✏️ Edit Application",
            "🗑️ Delete Application"
        ],
        key="main_navigation"
    )

    st.divider()
    st.caption("Powered by Python & MySQL")


# ==========================================
# DATABASE
# ==========================================

try:
    applications = database.get_applications() or []
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def applications_dataframe(rows):
    return pd.DataFrame(
        rows,
        columns=[
            "ID",
            "Company",
            "Role",
            "Application Date",
            "Source",
            "Status",
            "Interview Date",
            "Notes"
        ]
    )


def show_applications(rows):
    if rows:
        st.dataframe(
            applications_dataframe(rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No applications found.")


# ==========================================
# DASHBOARD STATISTICS
# ==========================================

total = len(applications)
applied = sum(1 for app in applications if app[5] == "Applied")
interview = sum(1 for app in applications if app[5] == "Interview")
rejected = sum(1 for app in applications if app[5] == "Rejected")
selected = sum(1 for app in applications if app[5] == "Selected")


# ==========================================
# PAGE 1: DASHBOARD
# ==========================================

if page == "🏠 Dashboard":

    st.title("Welcome to JobTrack 👋")
    st.write("Manage your job applications and track your career progress.")
    st.divider()

    st.subheader("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Applications", total)
    col2.metric("Interview Calls", interview)
    col3.metric("Selected", selected)

    col4, col5 = st.columns(2)

    col4.metric("Applied", applied)
    col5.metric("Rejected", rejected)

    st.divider()
    st.subheader("📈 Application Analytics")

    if applications:
        chart_data = pd.DataFrame({
            "Status": ["Applied", "Interview", "Rejected", "Selected"],
            "Count": [applied, interview, rejected, selected]
        })

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Applications by Status**")
            st.bar_chart(chart_data.set_index("Status"))

        with col2:
            st.write("**Application Summary**")
            st.dataframe(
                chart_data,
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        st.subheader("🕒 Recent Applications")

        recent = sorted(
            applications,
            key=lambda app: app[0],
            reverse=True
        )[:5]

        show_applications(recent)

    else:
        st.info("No applications yet. Add your first application to get started.")


# ==========================================
# PAGE 2: ADD APPLICATION
# ==========================================

elif page == "➕ Add Application":

    st.title("➕ Add Job Application")
    st.write("Record the details of a new job application.")
    st.divider()

    with st.form("add_application_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            company = st.text_input("Company Name *")
            role = st.text_input("Job Role *")
            application_date = st.date_input(
                "Application Date",
                value=date.today()
            )

        with col2:
            source = st.selectbox(
                "Application Source",
                [
                    "LinkedIn",
                    "Naukri",
                    "Indeed",
                    "Company Website",
                    "Referral",
                    "Other"
                ]
            )

            status = st.selectbox(
                "Application Status",
                ["Applied", "Interview", "Rejected", "Selected"]
            )

            has_interview = st.checkbox("Add Interview Date?")
            interview_date = None

            if has_interview:
                interview_date = st.date_input(
                    "Interview Date",
                    value=date.today(),
                    key="add_interview_date"
                )

        notes = st.text_area(
            "Notes",
            placeholder="Recruiter details, interview notes, etc."
        )

        submitted = st.form_submit_button(
            "💾 Save Application",
            use_container_width=True
        )

        if submitted:
            if not company.strip() or not role.strip():
                st.error("Please enter Company Name and Job Role.")
            else:
                try:
                    database.add_application(
                        company.strip(),
                        role.strip(),
                        application_date,
                        source,
                        status,
                        interview_date,
                        notes.strip(),
                        st.session_state.user_id
                    )

                    st.success("Application saved successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Unable to save application: {e}")


# ==========================================
# PAGE 3: MY APPLICATIONS
# ==========================================

elif page == "📋 My Applications":

    st.title("📋 My Applications")
    st.write("Search, filter and review all your job applications.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        search_company = st.text_input(
            "🔍 Search Company",
            placeholder="Enter company name..."
        )

    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Applied", "Interview", "Rejected", "Selected"]
        )

    filtered = applications

    if search_company.strip():
        filtered = [
            app for app in filtered
            if search_company.lower() in str(app[1]).lower()
        ]

    if status_filter != "All":
        filtered = [
            app for app in filtered
            if app[5] == status_filter
        ]

    st.write(
        f"Showing {len(filtered)} of {len(applications)} applications"
    )

    if filtered:
        df = applications_dataframe(filtered)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download CSV",
            data=csv_data,
            file_name="job_applications.csv",
            mime="text/csv"
        )
    else:
        st.info("No matching applications found.")


# ==========================================
# PAGE 4: UPDATE STATUS
# ==========================================

elif page == "🔄 Update Status":

    st.title("🔄 Update Application Status")
    st.write("Select an application and update its current status.")
    st.divider()

    if applications:
        options = {
            f"ID {app[0]} | {app[1]} | {app[2]}": app
            for app in applications
        }

        selected_label = st.selectbox(
            "Select Application",
            list(options.keys())
        )

        selected_app = options[selected_label]

        status_options = ["Applied", "Interview", "Rejected", "Selected"]
        current_status = (
            selected_app[5]
            if selected_app[5] in status_options
            else "Applied"
        )

        new_status = st.selectbox(
            "New Status",
            status_options,
            index=status_options.index(current_status),
            key="update_status_select"
        )

        if st.button("🔄 Update Status", use_container_width=True):
            try:
                database.update_status(selected_app[0], new_status)
                st.success("Application status updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Unable to update status: {e}")

    else:
        st.info("No applications found. Add an application first.")


# ==========================================
# PAGE 5: EDIT APPLICATION
# ==========================================

elif page == "✏️ Edit Application":

    st.title("✏️ Edit Job Application")
    st.write("Update the details of an existing application.")
    st.divider()

    if applications:

        options = {
            f"ID {app[0]} | {app[1]} | {app[2]}": app
            for app in applications
        }

        selected_label = st.selectbox(
            "Choose application to edit",
            list(options.keys()),
            key="edit_application_select"
        )

        selected_app = options[selected_label]

        app_id = selected_app[0]

        with st.form("edit_application_form"):

            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input(
                    "Company Name *",
                    value=str(selected_app[1] or "")
                )

                role = st.text_input(
                    "Job Role *",
                    value=str(selected_app[2] or "")
                )

                current_app_date = selected_app[3] or date.today()

                if isinstance(current_app_date, str):
                    current_app_date = date.fromisoformat(current_app_date)

                application_date = st.date_input(
                    "Application Date",
                    value=current_app_date
                )

            with col2:
                source_options = [
                    "LinkedIn",
                    "Naukri",
                    "Indeed",
                    "Company Website",
                    "Referral",
                    "Other"
                ]

                current_source = selected_app[4]
                if current_source not in source_options:
                    source_options.append(current_source)

                source = st.selectbox(
                    "Application Source",
                    source_options,
                    index=source_options.index(current_source)
                )

                status_options = [
                    "Applied",
                    "Interview",
                    "Rejected",
                    "Selected"
                ]

                current_status = selected_app[5]
                if current_status not in status_options:
                    current_status = "Applied"

                status = st.selectbox(
                    "Application Status",
                    status_options,
                    index=status_options.index(current_status)
                )

                current_interview_date = selected_app[6]
                has_interview = st.checkbox(
                    "Add Interview Date?",
                    value=current_interview_date is not None
                )

                interview_date = None

                if has_interview:
                    if current_interview_date is None:
                        current_interview_date = date.today()
                    elif isinstance(current_interview_date, str):
                        current_interview_date = date.fromisoformat(
                            current_interview_date
                        )

                    interview_date = st.date_input(
                        "Interview Date",
                        value=current_interview_date,
                        key="edit_interview_date"
                    )

            notes = st.text_area(
                "Notes",
                value=str(selected_app[7] or "")
            )

            save_changes = st.form_submit_button(
                "💾 Save Changes",
                use_container_width=True
            )

            if save_changes:
                if not company.strip() or not role.strip():
                    st.error("Company Name and Job Role are required.")
                else:
                    try:
                        success = database.update_application(
                            app_id,
                            company.strip(),
                            role.strip(),
                            application_date,
                            source,
                            status,
                            interview_date,
                            notes.strip()
                        )

                        if success:
                            st.success("Application updated successfully!")
                        else:
                            st.info(
                                "No database row was changed. "
                                "The details may be identical to the saved values."
                            )

                        st.rerun()

                    except Exception as e:
                        st.error(f"Unable to edit application: {e}")

    else:
        st.info("No applications available to edit.")


# ==========================================
# PAGE 6: DELETE APPLICATION
# ==========================================

elif page == "🗑️ Delete Application":

    st.title("🗑️ Delete Job Application")
    st.write("Remove an application you no longer need.")
    st.warning("Deleting an application is permanent.")
    st.divider()

    if applications:

        options = {
            f"ID {app[0]} | {app[1]} | {app[2]}": app
            for app in applications
        }

        selected_label = st.selectbox(
            "Choose application to delete",
            list(options.keys()),
            key="delete_application_select"
        )

        selected_app = options[selected_label]

        st.subheader("Application Details")

        st.write(f"**Company:** {selected_app[1]}")
        st.write(f"**Job Role:** {selected_app[2]}")
        st.write(f"**Status:** {selected_app[5]}")
        st.write(f"**Application ID:** {selected_app[0]}")

        confirm_delete = st.checkbox(
            "I understand this application will be permanently deleted."
        )

        if st.button(
            "🗑️ Delete Application",
            type="primary",
            use_container_width=True
        ):

            if not confirm_delete:
                st.error("Please confirm before deleting.")
            else:
                try:
                    success = database.delete_application(selected_app[0])

                    if success:
                        st.success("Application deleted successfully!")
                        st.rerun()
                    else:
                        st.warning(
                            "Application was not deleted. "
                            "It may already have been removed."
                        )

                except Exception as e:
                    st.error(f"Unable to delete application: {e}")

    else:
        st.info("No applications available to delete.")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "JobTrack | Built with Python, Streamlit, Pandas and MySQL"
)