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

# Stocker les réponses de l'utilisateur
user_answers = {}

# Affichage des questions
st.header(f"📝 Questions pour {selected_uv}")
for index, row in uv_questions.iterrows():
    question_key = f"Q{row['Numéro Question']}"
    st.subheader(f"Question {int(row['Numéro Question'])} : {row['Intitulé de la Question']}")
    
    options = {
        "A": row["Proposition A"],
        "B": row["Proposition B"],
        "C": row["Proposition C"],
        "D": row["Proposition D"],
        "E": row["Proposition E"]
    }
    
    # Afficher les options avec boutons radio
    user_answers[question_key] = st.radio(
        "Choisissez une réponse :",
        options=list(options.keys()),
        format_func=lambda x: f"{x} - {options[x]}",
        key=question_key
    )

# Bouton de soumission
if st.button("✅ Soumettre mes réponses"):
    score = 0
    st.header("📊 Résultats")
    
    for index, row in uv_questions.iterrows():
        question_key = f"Q{row['Numéro Question']}"
        correct_answer = row["Bonne Réponse"]
        user_answer = user_answers[question_key]
        is_correct = user_answer == correct_answer
        result_symbol = "✅" if is_correct else "❌"
        result_color = "green" if is_correct else "red"
        
        st.markdown(
            f"<span style='color:{result_color}; font-size:16px;'>{result_symbol} "
            f"Question {int(row['Numéro Question'])} : Votre réponse : {user_answer} | "
            f"Bonne réponse : {correct_answer}</span>",
            unsafe_allow_html=True
        )
        
        if is_correct:
            score += 1

    # Calcul de la note sur 10
    total_questions = len(uv_questions)
    score_out_of_10 = round((score / total_questions) * 10, 2)
    st.subheader(f"🎯 Note finale : **{score_out_of_10} / 10**")
    
