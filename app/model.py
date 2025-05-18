###skills & keywords extraction\
###keyword matching
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer,util
from utils import compute_overlap
from utils import parse_experience

###load Bert-based senetence transformer model
model=SentenceTransformer('all-MiniLm-l6-v2')

def get_similarity(text1:str,text2:str)->float:


    if not text1 or not text2:
        return 0.0
    ###generate sentence embeddings
    embeddings1=model.encode(text1,convert_to_tensor=True)
    embeddings2=model.encode(text2,convert_to_tensor=True)

    ##compute cosine similarity
    similarity=util.cos_sim(embeddings1,embeddings2)
    return float(similarity[0][0])


def keyword_score(jd_text,resume_text,top_n=10):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([jd_text, resume_text])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

# Extract top N keywords from JD
    vectorizer.fit([jd_text])
    tfidf_vector = vectorizer.transform([jd_text])
    keywords = sorted(
        zip(vectorizer.get_feature_names_out(), tfidf_vector.toarray()[0]),
        key=lambda x: x[1], reverse=True
    )[:top_n]
    top_keywords = [k for k, _ in keywords]
    matched = [k for k in top_keywords if re.search(r'\b' + re.escape(k) + r'\b', resume_text.lower())]
    return {
    "keyword_score": float(similarity),
    "top_keywords": top_keywords,
    "matched_keywords": matched,
    "missing_keywords": list(set(top_keywords) - set(matched))
}

###ner parsing

nlp=spacy.load('en_core_web_sm')

def extract_entities(text):
    doc=nlp(text)

    entities={
         "ORG": [], "PERSON": [], "DATE": [], "GPE": [],
        "SKILLS": [], "EDUCATION": [], "EXPERIENCE_YEARS": []
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    ##Education Extraction
    edu_keywords=["bachelor","master","phd","degree","graduate","undergraduate"]
    entities["Education"]=[sent.text for sent in doc.events]

    ##Experience extraction
    experience_matches=re.find_all(r'(\d+)\+?\s+years?',text.lower())
    entities["EXPERIENCE_YEARS"]=[int(e) for e in experience_matches]

    return entities

def  score_resume(jd_text,resume_text,required_experience=0):
    semantic=get_similarity(jd_text,resume_text)
    keyword_overlap = compute_overlap(jd_text, resume_text)

    keyword_result=keyword_score(jd_text,resume_text)
     # Experience score
    resume_experience = parse_experience(resume_text)
    experience_bonus = 0.1 if resume_experience >= required_experience else 0.0

    
    
    # Final score calculation
    final_score = (
        0.6 * semantic +
        0.3 * keyword_result['keyword_score'] +
        0.1 * keyword_overlap +
        experience_bonus
    )
    if final_score >= 0.75:
        match_level = "Excellent Match"
        rating = "⭐⭐⭐⭐⭐"
        recommendation = "This resume strongly aligns with the job requirements."
    elif final_score >= 0.5:
        match_level = "Good Match"
        rating = "⭐⭐⭐⭐"
        recommendation = "Resume aligns well, but could benefit from minor updates."
    elif final_score >= 0.3:
        match_level = "Partial Match"
        rating = "⭐⭐⭐"
        recommendation = "Some important areas are missing or underrepresented."
    else:
        match_level = "Low Match"
        rating = "⭐⭐"
        recommendation = "Resume needs significant improvements to match the job."

    suggestions = []
    if not resume_experience:
        suggestions.append("Add a clear Experience section with years and job titles.")
    if keyword_result["missing_keywords"]:
        suggestions.append("Include missing keywords like: " + ", ".join(keyword_result["missing_keywords"][:5]) + ".")

    return {
        "semantic_score": round(semantic, 2),
        "keyword_score": round(keyword_result['keyword_score'], 2),
        "keyword_overlap": round(keyword_overlap, 2),
        "final_score": round(final_score, 2),
        "experience": resume_experience,
        "matched_keywords": keyword_result['matched_keywords'],
        "missing_keywords": keyword_result['missing_keywords'],
        "top_keywords": keyword_result['top_keywords'],
        "match_level": match_level,
        "rating": rating,
        "recommendation": recommendation,
        "suggestions": suggestions
    }
    