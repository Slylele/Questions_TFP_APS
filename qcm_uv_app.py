import streamlit as st
import pandas as pd

# Charger le fichier Excel
df = pd.read_excel("TFP_APS_Questions_QCU.xlsx", sheet_name="Liste_Questions", engine="openpyxl")

# Liste des UV disponibles
uv_list = df["UV"].unique()

# Titre de l'application
st.title("📘 QCM TFP APS - Questions par UV")

# Sélection de l'UV
selected_uv = st.selectbox("📚 Choisissez une UV :", uv_list)

# Filtrer les questions pour l'UV sélectionnée
uv_questions = df[df["UV"] == selected_uv]

# Initialiser les réponses de l'utilisateur
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# Affichage des questions
st.header(f"📝 Questions pour {selected_uv}")
score = 0

for index, row in uv_questions.iterrows():
    question_key = f"Q{row['Numéro Question']}"
    st.markdown(f"**Question {int(row['Numéro Question'])} :** {row['Intitulé de la Question']}")

    options = {
        "A": row["Proposition A"],
        "B": row["Proposition B"],
        "C": row["Proposition C"],
        "D": row["Proposition D"],
        "E": row["Proposition E"]
    }

    if not st.session_state.submitted:
        # Afficher les options avec boutons radio sans sélection par défaut
        user_choice = st.radio(
            "Choisissez une réponse :",
            options=[""] + list(options.keys()),
            format_func=lambda x: f"{x} - {options[x]}" if x in options else "Aucune sélection",
            key=question_key
        )
        st.session_state.user_answers[question_key] = user_choice
    else:
        user_choice = st.session_state.user_answers.get(question_key, "")
        correct_answer = row["Bonne Réponse"]

        # Affichage des options avec couleurs et icônes
        for opt_key, opt_text in options.items():
            if user_choice == opt_key and opt_key == correct_answer:
                st.markdown(f"<span style='color:green;'>✅ {opt_key} - {opt_text}</span>", unsafe_allow_html=True)
            elif user_choice == opt_key and opt_key != correct_answer:
                st.markdown(f"<span style='color:red;'>❌ {opt_key} - {opt_text}</span>", unsafe_allow_html=True)
            elif opt_key == correct_answer and user_choice != correct_answer:
                st.markdown(f"<span style='color:green;'>✅ {opt_key} - {opt_text}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"{opt_key} - {opt_text}")

        if user_choice == correct_answer:
            score += 1

# Bouton de soumission en bas de page
if not st.session_state.submitted:
    if st.button("✅ Soumettre mes réponses"):
        st.session_state.submitted = True
        st.experimental_rerun()
else:
    total_questions = len(uv_questions)
    score_out_of_10 = round((score / total_questions) * 10, 2)
    st.subheader(f"🎯 Note finale : **{score_out_of_10} / 10**")
    
