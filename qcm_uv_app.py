import streamlit as st
import pandas as pd
import random
import os
import time
from streamlit_scroll_to_top import scroll_to_here

# Initialiser les états
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False
if 'scroll_to_bottom' not in st.session_state:
    st.session_state.scroll_to_bottom = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None

if st.session_state.scroll_to_top:
    scroll_to_here(0, key='top')  # Scroll to the top of the page
    st.session_state.scroll_to_top = False  # Reset the state after scrolling

# Démarre le chrono
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()

# Charger le fichier Excel
script_dir1 = os.path.dirname(__file__)
script_dir2 = os.getcwd()
try:
    test = os.listdir(script_dir1)
    script_dir= script_dir1
except:
    script_dir = script_dir2

st.set_page_config(layout="wide")

# Titre de l'application
st.title("📘 QCM TFP APS - Questions par UV", anchor="qcm_title")

# Choix du fichier au lancement
file_choice = st.radio("📂 Sélectionnez les questions à utiliser :", ["", "Questions réelles 2025", "Questions trouvées sur le Net"], index=1, label_visibility="visible",)

# Définir le nom du fichier en fonction du choix
if file_choice == "Questions trouvées sur le Net":
    excel_name = "TFP_APS_Questions_QCU_Internet.xlsx"
else:
    excel_name = "TFP_APS_Questions_QCU_Reel_2025.xlsx"

excel_path = os.path.join(script_dir, excel_name)

# Charger le fichier Excel
#df = pd.read_excel(excel_path, sheet_name="Liste_Questions", engine="openpyxl")
df_questions = pd.read_excel(excel_path, sheet_name="Liste_Questions", engine="openpyxl")
df_uv = pd.read_excel(excel_path, sheet_name="Liste_UV", engine="openpyxl")

# Liste des UV présentes dans les questions
uv_in_questions = df_questions["UV"].unique()

# Filtrer Liste_UV pour ne garder que celles présentes dans les questions
df_uv_filtered = df_uv[df_uv["UV"].isin(uv_in_questions)]

# Construire la liste affichée : "UV - Description"
uv_display_list = [f"{row['UV']} - {row['Description']}" for _, row in df_uv_filtered.iterrows()]

# Sélecteur Streamlit
selected_uv_display = st.selectbox("📚 Choisissez une UV :", uv_display_list)

# Extraire le nom réel de l'UV (avant le tiret)
selected_uv = selected_uv_display.split(" - ")[0]

# Filtrer les questions avec le vrai nom
uv_questions = df_questions[df_questions["UV"] == selected_uv].copy()
nb_questions = len(uv_questions)

# Initialiser les états
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# Initialisation des clés
if "last_file" not in st.session_state:
    st.session_state.last_file = file_choice
if "last_uv" not in st.session_state:
    st.session_state.last_uv = selected_uv

# Si fichier ou UV a changé, réinitialiser l'ordre
if (st.session_state.last_file != file_choice) or (st.session_state.last_uv != selected_uv) \
        or "question_order" not in st.session_state or st.session_state.get("reset_flag", False):
    st.session_state.last_file = file_choice
    st.session_state.last_uv = selected_uv
    st.session_state.submitted = False
    st.session_state.user_answers = {}
    st.session_state.question_order = random.sample(list(uv_questions.index), len(uv_questions))
    st.session_state.reset_flag = False
    st.session_state.start_time = time.time()   # Redémarre le chrono
    st.session_state.end_time = None


# Bouton de réinitialisation
if st.button("🔄 Réinitialiser le questionnaire"):
    st.session_state.submitted = False
    st.session_state.user_answers = {}
    st.session_state.reset_flag = True
    st.session_state.start_time = time.time() # Démarre le chrono
    st.rerun()


# =================================================================================
# LISTE DES QUESTIONS AVEC PROPOSITIONS ET REPONSES
# =================================================================================
# Affichage des questions
#uv_questions = df_questions.loc[st.session_state.question_order]
uv_questions = uv_questions.loc[st.session_state.question_order]
st.header(f"📝 Questions pour {selected_uv} ({nb_questions} questions)")

st.markdown("""
<style>
div[role='radiogroup'] label:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

score = 0
question_num = 0

for index, row in uv_questions.iterrows():
    question_num = question_num+1
    st.markdown("---")
    question_key = f"Q{row['Numéro Question']}"
    #st.markdown(f"**Question {int(row['Numéro Question'])} :** {row['Intitulé de la Question']}")
    st.markdown(
        f"**Question {question_num} :** {row['Intitulé de la Question']} "
        f"<span style='color:grey'>(Q{row['Numéro Question']})</span>",
        unsafe_allow_html=True
    )

    options = {k: row[f"Proposition {k}"] for k in ["A", "B", "C", "D", "E", "F"] if pd.notna(row[f"Proposition {k}"])}
    correct_answer = row["Bonne Réponse"]

    if not st.session_state.submitted:
        user_choice = st.radio(
            "Choisissez une réponse :",
            options=["Aucune sélection"] + list(options.keys()),
            format_func=lambda x: f"{x} - {options[x]}" if x in options else x,
            key=question_key,
            label_visibility = "hidden"
        )

        st.session_state.user_answers[question_key] = user_choice

    else:
        user_choice = st.session_state.user_answers.get(question_key, "")
        # ✅ Affichage des réponses
        if user_choice == "Aucune sélection":
            st.markdown(f"<span style='color:red'>❌ Aucune sélection</span>", unsafe_allow_html=True)
        for opt_key, opt_text in options.items():
            if user_choice == opt_key and opt_key == correct_answer:
                st.markdown(f"✅ {opt_key} - {opt_text}", unsafe_allow_html=True)
            elif user_choice == opt_key and opt_key != correct_answer:
                st.markdown(f"❌ {opt_key} - {opt_text}", unsafe_allow_html=True)
            elif opt_key == correct_answer and user_choice != correct_answer:
                st.markdown(f"✅ {opt_key} - {opt_text}", unsafe_allow_html=True)
            else:
                st.markdown(f"{opt_key} - {opt_text}")

        if user_choice == correct_answer:
            score += 1

# Bouton de soumission en bas de page
if not st.session_state.submitted:
    if st.button("✅ Soumettre mes réponses"):
        st.session_state.submitted = True
        st.session_state.end_time = time.time() # Fin du Chrono
        st.session_state.scroll_to_bottom = True
        st.rerun()
else:
    total_questions = len(uv_questions)
    score_out_of_20 = round((score / total_questions) * 20, 2)
    #st.subheader(f"🎯 Score : {score}/{total_questions} — Note : {score_out_of_20}/20")
    st.markdown("---")
    if score_out_of_20 >= 12:
        st.markdown(f"<span style='color:green; font-size:24px;'>🎯 Score : {score_out_of_20}/20</span>",
                    unsafe_allow_html=True)
    elif score_out_of_20 < 8:
        st.markdown(f"<span style='color:red; font-size:24px;'>🎯 Score : {score_out_of_20}/20</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:amber; font-size:24px;'>🎯 Score : {score_out_of_20}/20</span>",
                    unsafe_allow_html=True)
    st.markdown(
        f"<span style='margin-left:50px; color:grey; font-size:20px;'><b><i>Score total : {score}/{total_questions}</i></b></span>",
        unsafe_allow_html=True)

    # Calcul du temps passé
    elapsed = st.session_state.end_time - st.session_state.start_time
    #hours = int(elapsed // 3600)
    #minutes = int((elapsed % 3600) // 60)
    minutes = int(elapsed // 60)    # prévoit de dépasser 60 min)
    seconds = int(elapsed % 60)
    #time_total = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    time_total = f"{minutes:02d}:{seconds:02d}"

    avg_per_question = elapsed / total_questions
    avg_minutes = int(avg_per_question // 60)
    avg_seconds = int(avg_per_question % 60)
    time_avg = f"{avg_minutes:02d}:{avg_seconds:02d}"

    st.markdown(f"<span style='color:grey;'>⏱ Temps total : {time_total} / Temps moyen par question : {time_avg}</span>", unsafe_allow_html=True)

    # Bouton de réinitialisation
    if st.button("🔄 Réinitialiser le questionnaire "):
        st.session_state.submitted = False
        st.session_state.user_answers = {}
        st.session_state.reset_flag = True
        st.session_state.scroll_to_top = True
        st.session_state.start_time = time.time() # Démarre le chrono
        st.rerun()


# =================================================================================
# BAS DE PAGE
# =================================================================================
st.title("", anchor="bottom_page")
st.markdown("----")

if st.session_state.scroll_to_bottom:
    scroll_to_here(0, key='bottom')  # Scroll to the top of the page
    st.session_state.scroll_to_bottom = False  # Reset the state after scrolling

# As a text link
#st.markdown('[Back to Top](#qcm_title)')
#st.markdown("<a href='#qcm_title'>Go to top</a>", unsafe_allow_html=True);
# As an html button (needs styling added)
#st.markdown(''' <a target="_self" href="#qcm_title">
#                    <button>
#                        Back to Top
#                    </button>
#                </a>''', unsafe_allow_html=True)
