# AI Resume Analyzer 🤖📄

## 📌 Proje Özeti
Bu proje, özgeçmişleri analiz ederek ve adayları becerilerine, deneyimlerine ve eğitimlerine göre sıralayarak işe alım sürecinde İK departmanlarına yardımcı olmak için tasarlanmıştır. Araç, özellikle Yapay Zeka, Veri Bilimi, Makine Öğrenimi ve ilgili alanlardaki teknik roller için faydalıdır.

## 🚀 Özellikler
- **PDF Ayrıştırma:** `pdfplumber` ve `PyMuPDF` kullanılarak PDF özgeçmiş ayrıştırmayı destekler.
- **Yetenek Çıkarımı:** Özgeçmişlerden yapay zeka ile ilgili becerileri çıkarır.
- **Kullanıcı Dostu Çıktı:** Aday ayrıntıları ve puanları içeren bir JSON dosyası oluşturur.
- **Puanlama Sistemi**: Adayları becerilerine, deneyimlerine ve eğitimlerine göre puanlar.
- **Kategori Tabanlı Sıralama**: Adayları belirli iş kategorilerine göre sıralar (örneğin Veri Bilimi, Makine Öğrenimi, Doğal Dil İşleme).

## 📂 Kurulum
1. Repoyu klonlayın:
``
git clone https://github.com/hawanbeats/resume_scorer.git
cd resume_scorer
``
2. Gerekli bağımlılıkları yükleyin:
``
pip install -r requirements.txt
``

## 🛠️ Kullanım
1. Özgeçmişlerinizi ``resumes/`` klasörüne koyun.
2. Komut dosyasını çalıştırın:
``
python main.py
``
3. Senaryo:
- Hedef kategori ve kaç aday sıralamak istediğiniz sorulacak (örneğin, Veri Bilimi, Makine Öğrenimi).
- Özgeçmişleriniz analiz edilecek ve bir JSON dosyası oluşturulacak (``processed_ai_resumes.json``).
- En iyi adaylar puanlarına göre sıralanacak.

## 📊 Örnek Çıktı
Kod aşağıdaki yapıya sahip bir JSON dosyası oluşturur:
```json
{
  "resume1.pdf": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "skills": {
      "Machine_Learning": ["Python", "TensorFlow"],
      "Data_Science": ["Pandas", "NumPy"]
    },
    "scores": {
      "Machine_Learning": 20,
      "Data_Science": 15,
      "total_score": 35
    },
    "target_category": "Machine_Learning"
  }
}
```
## 📝 Yeni Özellikler Ekleme
- **Deneyim ve Eğitim Bilgisi Çıkarımı**: Özgeçmişlerden deneyim ve eğitim bilgilerini çıkaracak şekilde genişletebilirsiniz.
- **Çoklu Dil Desteği**: Farklı dillerdeki özgeçmişleri destekleyebilirsiniz.
- **Gelişmiş Puanlama**: Deneyim ve eğitim bilgilerine göre puanlama sistemi ekleyebilirsiniz.

## 🤝 Katkıda Bulunma
Katkılarınızı bekliyorum! Katkıda bulunmak için aşağıdaki adımları izleyin:
1. Repoyu forklayın.
2. Yeni bir branch oluşturun (git checkout -b ozellik/OzellikAdiniz).
3. Değişikliklerinizi commit edin (git commit -m 'Yeni özellik eklendi').
4. Branch'inizi pushlayın (git push origin ozellik/OzellikAdiniz).
5. Pull request oluşturun.

## 📧 İletişim
Sorularınız veya önerileriniz için bana ulaşabilirsiniz:
- E-posta: damirlihasan2002@gmail.com
- LinkedIn: [LinkedIn Profilim](https://www.linkedin.com/in/hasan-damirli/)
- GitHub: [GitHub Profilim](https://github.com/hawanbeats)
