# 🧠 Resume Analyzer

A smart, AI-powered tool that analyzes how well a resume matches a job description using NLP techniques like Named Entity Recognition (NER), BERT embeddings, and Cosine Similarity.

## 🚀 Features

- Upload a resume and job description (JD)
- Extracts keywords, skills, and job roles using NER
- Uses BERT for semantic similarity scoring
- Displays a match score between resume and JD
- Clean and interactive UI built with Streamlit

## 🛠️ Technologies Used

- Python
- Streamlit
- spaCy
- Hugging Face Transformers (BERT)
- scikit-learn (TF-IDF, Cosine Similarity)

## 📂 Folder Structure

├── streamlit_app    # Streamlit app file
├── model.py
├── utils.py # Similarity calculation
├── requirements.txt
├── .gitignore
├── README.md

📈 Future Improvements

-Support for PDF parsing and multilingual resumes

-Suggest keyword improvements for job seekers

-Save and export match reports
