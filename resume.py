import os
import pdfplumber  # type: ignore
import fitz  # type: ignore
import re
import json
from collections import defaultdict
from transformers import pipeline

# JSON dosyalarını oku

with open("degree.json", "r", encoding="utf-8") as f:
    DEGREES = json.load(f)

with open("universities.json", "r", encoding="utf-8") as f:
    UNIVERSITIES = json.load(f)

with open("faculties.json", "r", encoding="utf-8") as f:
    FACULTIES = json.load(f)

with open("filter_titles.json", "r", encoding="utf-8") as f:
    FILTER_TITLES = json.load(f)

with open("all_ai_skills.json", "r", encoding="utf-8") as f:
    ALL_AI_SKILLS = json.load(f)

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

# 📌 İsim ve soyisim çıkarma fonksiyonu
def is_valid_name(name):
    """İsmin geçerli olup olmadığını kontrol eder."""
    if not name or len(name.split()) != 2:  # İsim ve soyisim tam olmalı (2 kelime)
        return False
    if any(char.isdigit() for char in name):  # Sayı içermemeli
        return False
    if "@" in name or "http" in name:  # E-posta veya URL olmamalı
        return False
    if name.lower() in FILTER_TITLES:  # Filtre listesinde olmamalı
        return False
    return True

def extract_full_name_from_text(text):
    """PDF'ten çıkarılan metinden isim ve soyismi belirler."""
    lines = text.split("\n")[:10]  # İlk 10 satırı al
    candidate_names = []

    for line in lines:
        words = clean_text(line).split()
        if len(words) == 2 and is_valid_name(" ".join(words)):  # İsim soyisim tek satırda
            return words[0].capitalize() + " " + words[1].capitalize()
        candidate_names.extend(words)

    # Alternatif olarak alt alta yazılmış isimleri kontrol et
    for i in range(len(candidate_names) - 1):
        full_name = candidate_names[i] + " " + candidate_names[i + 1]
        if is_valid_name(full_name):
            return full_name.capitalize()

    return "N/A"  # İsim bulunamazsa "N/A" döndür

# 📌 Kullanıcı bilgilerini çıkarma fonksiyonu
def extract_user_info_from_text(text):
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.search(r"\+\d{1,4}[\s-]?\(?\d{1,4}\)?[\s-]?\d{2,4}[\s-]?\d{2,4}[\s-]?\d{2,4}(?![\d-])", text)  # Telefon numarası
    linkedin = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/[a-zA-Z0-9-\._%]+", text)  # LinkedIn profili
    github = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9-\._%]+", text)  # GitHub profili
    name = extract_full_name_from_text(text)  # İsim ve soyisim bilgisi

    return {
        "full name": name,
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
    print("Lütfen aşağıdaki kategorilerden birini seçin: ")
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
        num_candidates = int(input("Kaç aday görmek istersiniz? "))
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
        print(f"{i}. {user_info['full name']} - Toplam Puan: {user_info['scores']['total_score']}")

    print(f"\n✅ {len(processed_resumes)} adet özgeçmiş işlendi ve 'processed_ai_resumes.json' dosyasına kaydedildi.")
