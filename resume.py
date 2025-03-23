import os
import pdfplumber  # type: ignore
import fitz  # type: ignore
import re
import json
from collections import defaultdict

# 📌 Yapay Zeka sektörüne özel beceri listesi
# 📌 AI becerilerini tek bir listeye çevir
ALL_AI_SKILLS = {
    # 1. Programlama Dilleri ve Temel Beceriler
    "Programming_and_Fundamentals": [
        "Python", "R", "Julia", "Java", "C++", "JavaScript", "SQL", "Bash Scripting",
        "Data Structures", "Algorithms", "Version Control (Git)", "Debugging", "Code Optimization"
    ],

    # 2. Makine Öğrenmesi (Machine Learning)
    "Machine_Learning": [
        "Supervised Learning", "Unsupervised Learning", "Reinforcement Learning",
        "Semi-Supervised Learning", "Self-Supervised Learning", "Ensemble Methods",
        "Model Evaluation (Precision, Recall, F1, ROC-AUC)", "Hyperparameter Tuning (Grid Search, Random Search, Bayesian Optimization)",
        "Feature Engineering", "Feature Selection", "Dimensionality Reduction (PCA, t-SNE)",
        "Time Series Analysis", "Anomaly Detection", "Recommendation Systems", "Clustering (K-Means, DBSCAN)"
    ],

    # 3. Derin Öğrenme (Deep Learning)
    "Deep_Learning": [
        "Neural Networks (MLP, CNN, RNN, GAN)", "TensorFlow", "PyTorch", "Keras",
        "Transfer Learning", "Generative Models (GANs, VAEs)", "Optimization Techniques (Adam, SGD, RMSprop)",
        "Attention Mechanisms", "Transformers", "Explainable AI (XAI)", "Self-Supervised Learning",
        "Few-Shot Learning", "Meta-Learning", "Graph Neural Networks (GNNs)"
    ],

    # 4. Doğal Dil İşleme (Natural Language Processing - NLP)
    "Natural_Language_Processing": [
        "Text Preprocessing (Tokenization, Lemmatization, Stemming)", "Sentiment Analysis",
        "Named Entity Recognition (NER)", "Topic Modeling (LDA, NMF)", "Word Embeddings (Word2Vec, GloVe, FastText)",
        "Transformer Models (BERT, GPT, T5)", "Text Generation", "Machine Translation",
        "Speech Recognition (ASR)", "Chatbots", "Question Answering Systems", "Text Summarization",
        "Dialogue Systems", "Multilingual NLP", "Emotion Detection in Text"
    ],

    # 5. Bilgisayarlı Görü (Computer Vision)
    "Computer_Vision": [
        "Image Processing (OpenCV, PIL)", "Object Detection (YOLO, SSD, Faster R-CNN)",
        "Image Segmentation (U-Net, Mask R-CNN)", "Facial Recognition", "Optical Character Recognition (OCR)",
        "Pose Estimation", "Video Analysis", "Generative Models for Images (StyleGAN, CycleGAN)",
        "3D Vision", "Medical Image Analysis", "Scene Understanding", "Image Captioning"
    ],

    # 6. Veri Bilimi ve Analitiği (Data Science and Analytics)
    "Data_Science_and_Analytics": [
        "Data Wrangling (Pandas, NumPy)", "Data Visualization (Matplotlib, Seaborn, Plotly)",
        "Statistical Analysis (Hypothesis Testing, A/B Testing)", "Big Data Tools (Hadoop, Spark)",
        "Data Pipelines (ETL, Airflow)", "Database Management (SQL, NoSQL)", "Cloud Platforms (AWS, GCP, Azure)",
        "Experimentation and Tracking (MLflow, Weights & Biases)", "Data Governance", "Data Cleaning",
        "Data Annotation", "Data Augmentation", "Feature Stores"
    ],

    # 7. AI Araçları ve Çerçeveler (AI Tools and Frameworks)
    "AI_Tools_and_Frameworks": [
        "Scikit-Learn", "XGBoost", "LightGBM", "CatBoost", "TensorFlow", "PyTorch", "Keras",
        "Hugging Face Transformers", "OpenCV", "AutoML (H2O, AutoKeras)", "Model Deployment (Flask, FastAPI, Docker)",
        "ONNX", "MLOps Tools (Kubeflow, TFX)", "Ray", "Dask"
    ],

    # 8. Matematik ve İstatistik (Mathematics and Statistics)
    "Mathematics_and_Statistics": [
        "Linear Algebra", "Calculus", "Probability and Statistics", "Numerical Methods",
        "Optimization Theory", "Information Theory", "Bayesian Statistics", "Stochastic Processes",
        "Graph Theory", "Game Theory"
    ],

    # 9. Bulut ve Dağıtım (Cloud and Deployment)
    "Cloud_and_Deployment": [
        "AWS SageMaker", "Google AI Platform", "Azure ML", "Docker", "Kubernetes",
        "API Development (REST, GraphQL)", "Monitoring (Prometheus, Grafana)", "Serverless Computing",
        "Edge Computing", "Model Serving (TensorFlow Serving, Triton)", "CI/CD Pipelines"
    ],

    # 10. Yumuşak Beceriler (Soft Skills)
    "Soft_Skills": [
        "Problem-Solving", "Critical Thinking", "Communication", "Collaboration",
        "Project Management", "Time Management", "Leadership", "Adaptability",
        "Creativity", "Ethical Decision-Making"
    ],

    # 11. Yeni Nesil AI Becerileri (Emerging AI Skills)
    "Emerging_AI_Skills": [
        "Federated Learning", "Edge AI", "Quantum Machine Learning", "AI Ethics",
        "AI for Healthcare", "Multimodal AI", "AI in Robotics", "AI for Climate Science",
        "AI in Finance", "AI for Cybersecurity", "AI in Education", "AI for Autonomous Systems"
    ]
}

# 📌 Skorlama fonksiyonu
def calculate_scores(skills, category_weights):
    scores = {}
    total_score = 0

    for category, skills_list in skills.items():
        category_score = 0
        for skill in skills_list:
            # Her bir beceri için puan ekleyin (örneğin, her beceri 1 puan)
            category_score += 1

        # Kategori ağırlığı ile çarpın
        category_score *= category_weights.get(category, 10)
        scores[category] = category_score
        total_score += category_score

    scores["total_score"] = total_score
    return scores

# 📌 PDF'ten metin çıkarma - pdfplumber yöntemi
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
    except Exception as e:
        print(f"❌ Hata: {pdf_path} dosyası okunamadı. Hata: {e}")
    return text

# 📌 PDF'ten metin çıkarma - PyMuPDF (fitz) yöntemi
def extract_text_with_fitz(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"❌ Hata: {pdf_path} dosyası okunamadı. Hata: {e}")
    return text

# 📌 Metin ve Karakter temizleme fonksiyonu
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)  # Gereksiz boş satırları kaldır
    text = re.sub(r'\s+', ' ', text)  # Fazla boşlukları tek boşluk yap
    text = text.replace("ï¼​", "")  # Özel karakter düzeltme
    text = text.replace("Â", "")    # Diğer hatalı karakterler
    text = text.strip()
    return text

# 📌 AI becerilerini metinden çıkarma fonksiyonu
def extract_skills_from_text(text, skills_dict):
    skills = defaultdict(list)
    for skill_category, skills_list in skills_dict.items():
        for skill in skills_list:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                skills[skill_category].append(skill)
    return skills

# 📌 Kullanıcı bilgilerini çıkarma fonksiyonu
def extract_user_info_from_text(text):
    name = re.search(r"\b[A-Z][a-zA-Z'-]+\s+[A-Z][a-zA-Z'-]+\b", text)
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.search(r"\+\d{1,4}[\s-]?\(?\d{1,4}\)?[\s-]?\d{2,4}[\s-]?\d{2,4}[\s-]?\d{2,4}(?![\d-])", text)  # Telefon numarası
    linkedin = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/[a-zA-Z0-9-\._%]+", text)  # LinkedIn profili
    github = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9-\._%]+", text)  # GitHub profili

    return {
        "name": name.group(0) if name else "N/A",
        "email": email.group(0) if email else "N/A",
        "phone": phone.group(0) if phone else "N/A",
        "linkedin": linkedin.group(0) if linkedin else "N/A",
        "github": github.group(0) if github else "N/A",
    }

# 📌 Pozisyona göre ağırlıklandırma
def get_category_weights(target_category):
    # Varsayılan ağırlıklar
    category_weights = {
        "Machine_Learning": 10,
        "Deep_Learning": 10,
        "Data_Science_and_Analytics": 10,
        "Natural_Language_Processing": 10,
        "Computer_Vision": 10,
        "AI_Tools_and_Frameworks": 10,
        "Programming_and_Fundamentals": 5,
        "Mathematics_and_Statistics": 5,
        "Cloud_and_Deployment": 5,
        "Soft_Skills": 2.5,
        "Emerging_AI_Skills": 2.5
    }

    # Hedef kategori için ağırlığı artır
    if target_category in category_weights:
        category_weights[target_category] = 15  # Hedef kategoriye 15 ağırlık ver

    return category_weights

# 📌 PDF'den tüm bilgileri çıkarma
def extract_info_from_pdf(text, skills_dict, target_category):
    skills = extract_skills_from_text(text, skills_dict)
    user_info = extract_user_info_from_text(text)

    # Hedef kategoriye göre ağırlıklandırma
    category_weights = get_category_weights(target_category)

    # Skorları hesapla
    scores = calculate_scores(skills, category_weights)

    # Kullanıcı bilgilerini ve becerileri birleştir
    user_info["skills"] = skills
    user_info["scores"] = scores
    user_info["target_category"] = target_category  # Hedef kategoriyi de kaydet

    return user_info

# 📌 Özgeçmişleri işleme fonksiyonu
def process_resumes_with_ai_skills(folder_path, skills_dict, target_category, method="plumber"):
    processed_resumes = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            print(f"🔍 İşleniyor: {file_name}")
            file_path = os.path.join(folder_path, file_name)
            text = ""
            if method == "plumber":
                text = extract_text_from_pdf(file_path)
            elif method == "fitz":
                text = extract_text_with_fitz(file_path)

            user_info = extract_info_from_pdf(text, skills_dict, target_category)
            processed_resumes[file_name] = user_info

    return processed_resumes

# 📌 JSON olarak kaydetme fonksiyonu
def save_results_to_json(results, output_file="processed_ai_resumes.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

# 📌 Kullanıcıdan hedef kategoriyi al
def get_target_category_from_user():
    print("Lütfen aşağıdaki kategorilerden birini seçin:")
    for i, category in enumerate(ALL_AI_SKILLS.keys(), 1):
        print(f"{i}. {category}")
    choice = int(input("Seçiminiz (numara): "))
    target_category = list(ALL_AI_SKILLS.keys())[choice - 1]
    return target_category

# 📌 Ana işlem
if __name__ == "__main__":
    folder_path = "resumes/"  # Özgeçmişlerin bulunduğu klasör

    # Kullanıcıdan hedef kategoriyi al
    target_category = get_target_category_from_user()
    print(f"Seçilen kategori: {target_category}")

    # Kullanıcıdan kaç aday görmek istediğini al
    try:
        num_candidates = int(input("Kaç aday görmek istersiniz? (Örneğin: 5): "))
        if num_candidates <= 0:
            raise ValueError("Lütfen pozitif bir sayı girin.")
    except ValueError as e:
        print(f"❌ Hata: Geçersiz giriş. {e}")
        exit()

    # Özgeçmişleri işle
    processed_resumes = process_resumes_with_ai_skills(folder_path, ALL_AI_SKILLS, target_category, method="plumber")

    # JSON olarak kaydet
    save_results_to_json(processed_resumes, output_file="processed_ai_resumes.json")

    # Sonuçları sırala ve göster
    sorted_resumes = sorted(processed_resumes.items(), key=lambda x: x[1]["scores"]["total_score"], reverse=True)
    print(f"\n🔝 En uygun {num_candidates} aday:")
    for i, (file_name, user_info) in enumerate(sorted_resumes[:num_candidates], 1):
        print(f"{i}. {user_info['name']} - Toplam Puan: {user_info['scores']['total_score']}")

    print(f"\n✅ {len(processed_resumes)} adet özgeçmiş işlendi ve 'processed_ai_resumes.json' dosyasına kaydedildi.")