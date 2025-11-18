import streamlit as st
import cvxpy as cp
import numpy as np

st.set_page_config(page_title="CWA Predictor", layout="wide")

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("🎓 CWA Predictor")
st.sidebar.subheader("Academic Planning Tool")

menu = st.sidebar.radio(
    "Navigation",
    ["Grade Calculator", "Analytics", "History"],
    index=0
)

st.sidebar.info(
    "Developed for university students to plan their academic goals effectively."
)

# -------------------------------
# MAIN PAGE CONTENT
# -------------------------------
if menu == "Grade Calculator":

    # Top Title + Subtitle
    st.title("🎓 CWA Predictor")
    st.write("Calculate the grades you need to achieve your target CWA")

    # Reset + Export buttons (right aligned)
    top_col1, top_col2 = st.columns([8, 1.2])
    with top_col1:
        st.write("")
    with top_col2:
        st.button("🔁 Reset Form")
        st.button("📤 Export")

    # ================================
    # Academic History Section
    # ================================
    st.markdown("### 📘 Academic History")

    ah_col1, ah_col2, ah_col3, ah_col4, ah_col5, ah_col6 = st.columns(6)

    with ah_col1:
        target_cwa = st.number_input("Target CWA (0–100)", placeholder="e.g. 85", step = 1)

    with ah_col2:
       courses_taken =  st.number_input("Courses Taken", placeholder="e.g. 12", step = 1)

    with ah_col3:
        total_credits = st.number_input("Total Credit Hours for the new semester", placeholder="e.g. 36", step = 1)

    with ah_col4:
        current_cwa = st.number_input("Current CWA", placeholder="e.g. 78.5", step = 0.1)
    
    with ah_col5:
        current_total_score = st.number_input("Current total cumulative score", placeholder = "e.g 12434")

    with ah_col6:
        current_total_credits = st.number_input("Current total credit hours", placeholder="e.g. 78")

    # ================================
    # Goal Feasibility Card
    # ================================

    # feasibility_card = st.container(border=True)
    # with feasibility_card:
    #     st.write("Feasibility result will appear here…")

    # ================================
    # Current Semester Courses
    # ================================
    st.markdown("### 📚 Current Semester Courses")

    if "courses_list" not in st.session_state:
        st.session_state.courses_list = []

    if "final_courses" not in st.session_state:
        st.session_state.final_courses = []

    one_col, _ = st.columns([5, 5])

    with one_col:
        if st.button("➕ Add Course", use_container_width=True):
            if len(st.session_state.courses_list) < int(courses_taken):
                st.session_state.courses_list.append({"name": "", "credit": 0.0})
            else:
                st.warning("Max courses reached.")

    def add_courses():
        # remove the invalid loop
        # remove the missing courses_list

        course_col1, course_col2 = st.columns(2)

        with course_col1:
            for i, c in enumerate(st.session_state.courses_list):
                c["name"] = st.text_input(
                    f"Course {i+1}",
                    value=c["name"],
                    placeholder="Course Name",
                    key=f"name_{i}"
                )

        with course_col2:
            for i, c in enumerate(st.session_state.courses_list):
                c["credit"] = st.number_input(
                    f"Credit {i+1}",
                    value=c["credit"],
                    step=1.0,
                    key=f"credit_{i}"
                )
    add_courses()
    if st.button("Submit", use_container_width=True):
        st.session_state.final_courses = [
            {"name": c["name"], "credit": c["credit"]}
            for c in st.session_state.courses_list
            if c["name"] != ""  # optional filter
        ]
        st.success("Courses submitted!")

    total_entered_credits = sum(c["credit"] for c in st.session_state.final_courses)

        # Compare with expected total
    if total_entered_credits == total_credits:
        st.success("Courses submitted successfully!")
    else:
        st.error(
            f"Credit hour mismatch! Expected {total_credits}, "
            f"but got {total_entered_credits}."
        )
    # st.write("Final submitted list:")
    # st.write(st.session_state.final_courses)



    def predict_scores_cvxpy(courses, current_total_credits, current_cwa, target_cwa):
        credits = np.array([float(c["credit"]) for c in courses])
        n = len(credits)
        
        # Calculate required points
        prev_points = current_cwa * current_total_credits
        total_credits_after = current_total_credits + credits.sum()
        target_points = target_cwa * total_credits_after
        required_points = target_points - prev_points
        
        # CVXPY problem
        scores = cp.Variable(n)
        
        # Credit-weighted minimization
        objective = cp.Minimize(credits @ scores)
        
        # Constraints
        constraints = [
            credits @ scores >= required_points,  # Meet or exceed target
            scores >= 0,
            scores <= 100
        ]
        
        prob = cp.Problem(objective, constraints)
        prob.solve()



        results = []
        if prob.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE] and scores.value is not None:
            for i, c in enumerate(courses):
                results.append({
                "name": c.get("name", f"Course {i+1}"),
                "credit": float(c["credit"]),
                "score": float(np.round(scores.value[i], 2))
            })  
            status = prob.status

        else:
            for i, c in enumerate(courses):
                results.append({
                    "name": c.get("name", f"Course {i+1}"),
                    "credit": float(c["credit"]),
                    "score": "N/A"
                })
            status = prob.status
        return results, status
        
        # return [float(np.round(s, 2)) for s in scores.value]
    
    courses = st.session_state.final_courses
    scores, status = predict_scores_cvxpy(
    courses,
    current_total_credits=current_total_credits,   # from your input widget
    current_cwa=current_cwa,                       # from your input widget
    target_cwa=target_cwa                          # from your input widget
    )
    st.write("Suggested scores per course:")
# CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                table {
                    font-size: 30px;  /* Change this value to adjust font size */
                }
                </style>
                """


    st.markdown("### 🎯 Goal Feasibility")
    feasibility_card = st.container(border=True)
    with feasibility_card:
        if status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
            st.success("✅ Optimal solution found!")
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(scores)
        elif status == cp.INFEASIBLE:
            st.error("❌ Target CWA is not achievable with these courses")
            st.info("Try lowering your target CWA or taking different courses")

        else:
            st.warning(f"⚠️ Solver issue: {status}")
            st.info("The problem might be infeasible or there might be numerical issues")
        




# -------------------------------
# ANALYTICS PAGE
# -------------------------------
elif menu == "Analytics":
    st.title("📈 Analytics")
    st.write("Charts and academic insights will appear here…")

# -------------------------------
# HISTORY PAGE
# -------------------------------
elif menu == "History":
    st.title("🕓 History")
    st.write("Past academic planning entries will appear here…")

