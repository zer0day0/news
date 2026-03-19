import requests
import json
import time
import os

# Lấy API Key từ Github Secrets
API_KEY = os.environ.get("NEWSDATA_API_KEY")
FILE_NAME = "news_data.json" # Tên file lưu trữ

# TỪ ĐIỂN 50 QUỐC GIA CHẠY ADS (ĐÃ TỐI ƯU eCPM VÀ CHẤT LƯỢNG TIN TỨC)
COUNTRY_LANG_MAP = {
    # --- TIER 1 & CHÂU ÂU (eCPM CAO - Khách V.I.P) ---
    "us": "en",  # Mỹ
    # "gb": "en",  # Anh
    # "ca": "en",  # Canada
    # "de": "de",  # Đức
    # "fr": "fr",  # Pháp
    # "es": "es",  # Tây Ban Nha
    # "it": "it",  # Ý (MỚI THÊM)
    # "nl": "nl",  # Hà Lan
    # "be": "fr",  # Bỉ 
    # "pt": "pt",  # Bồ Đào Nha
    # "pl": "pl",  # Ba Lan
    # "gr": "el",  # Hy Lạp
    # "ro": "ro",  # Romania

    # # --- CHÂU MỸ LATIN ---
    # "mx": "es",  # Mexico
    # "co": "es",  # Colombia
    # "ve": "es",  # Venezuela

    # # --- CHÂU Á & ĐẠI DƯƠNG (Volume khủng + eCPM tốt) ---
    # "vn": "vi",  # Việt Nam (Để Dev tự test)
    # "in": "en",  # Ấn Độ (MỚI THÊM - Dùng tiếng Anh để lấy tin Tech/Biz)
    # "sg": "en",  # Singapore (MỚI THÊM)
    # "id": "id",  # Indonesia
    # "th": "th",  # Thái Lan
    # "ph": "en",  # Philippines
    # "kh": "en",  # Campuchia 
    # "bd": "en",  # Bangladesh 
    # "pk": "en",  # Pakistan
    # "np": "en",  # Nepal
    # "pg": "en",  # Papua New Guinea

    # # --- TRUNG ĐÔNG (eCPM Rất Tốt) ---
    # "ae": "en",  # UAE 
    # "sa": "ar",  # Saudi Arabia (MỚI THÊM)
    # "il": "he",  # Israel (MỚI THÊM)
    # "iq": "ar",  # Iraq
    # "tr": "tr",  # Thổ Nhĩ Kỳ

    # # --- CHÂU PHI (Giữ lại các nước có Volume app của bạn tốt nhất) ---
    # "za": "en",  # Nam Phi (MỚI THÊM - eCPM đỉnh nhất Châu Phi)
    # "eg": "ar",  # Ai Cập
    # "dz": "ar",  # Algeria
    # "tn": "ar",  # Tunisia
    # "cm": "fr",  # Cameroon
    # "ug": "en",  # Uganda
    # "na": "en",  # Namibia
    # "rw": "en",  # Rwanda
    # "mz": "pt",  # Mozambique
    # "ml": "fr",  # Mali
    # "tg": "fr",  # Togo
    # "sd": "ar",  # Sudan
    # "zm": "en",  # Zambia
    # "bj": "fr",  # Benin
    # "zw": "en",  # Zimbabwe
    # "bw": "en",  # Botswana
    # "mg": "fr",  # Madagascar
    # "ao": "pt"   # Angola
}

# Chủ đề hot nhất cho App Đồng hồ thông minh
CATEGORIES = "health,business,technology,science"

# --- BƯỚC 1: ĐỌC LẠI DATA CŨ ĐỂ LÀM "PHAO CỨU SINH" ---
all_news_data = {}
if os.path.exists(FILE_NAME):
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            all_news_data = json.load(f)
        print("📦 Đã load thành công data cũ làm Backup!")
    except Exception as e:
        print("⚠️ File cũ trống hoặc lỗi, sẽ tạo mới hoàn toàn.")

print(f"🚀 Bắt đầu lấy tin tức cho {len(COUNTRY_LANG_MAP)} quốc gia...\n")

# --- BƯỚC 2: TIẾN HÀNH CẬP NHẬT TỪNG QUỐC GIA ---
for country, language in COUNTRY_LANG_MAP.items():
    url = f"https://newsdata.io/api/1/latest?apikey={API_KEY}&country={country}&category={CATEGORIES}&language={language}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") == "success":
            results = data.get("results", [])
            final_news = []
            
            # LƯỚI LỌC KÉP: Chặn trùng URL và chặn trùng Tiêu đề
            used_urls = set()
            used_titles = set() 
            
            # --- VÒNG LẶP 1: Nhặt theo chủ đề ---
            grouped_news = {"business": [], "technology": [], "health": [],"science": []}
            
            for article in results:
                article_url = article.get("link", "")
                raw_title = article.get("title", "")
                
                # Làm sạch tiêu đề (Viết thường, bỏ khoảng trắng hai đầu) để so sánh chuẩn nhất
                clean_title = raw_title.lower().strip() if raw_title else ""
                
                categories_of_article = article.get("category", [])
                
                for cat in categories_of_article:
                    # Kiểm tra xem URL hoặc Tiêu đề này đã có trong set chưa
                    if cat in grouped_news and len(grouped_news[cat]) < 2 and article_url not in used_urls and clean_title not in used_titles:
                        grouped_news[cat].append({
                            "title": raw_title,
                            "url": article_url,
                            "source": article.get("source_name", article.get("source_id", "News")),
                            "description": article.get("description", "") or "", 
                            "category": categories_of_article,
                            "pubDate": article.get("pubDate", ""),
                            "fetched_at": article.get("fetched_at", ""), 
                            "image_url": article.get("image_url", "") or ""
                        })
                        # Đánh dấu là đã lấy
                        used_urls.add(article_url)
                        if clean_title:
                            used_titles.add(clean_title)
                        break
            
            for cat, items in grouped_news.items():
                final_news.extend(items)
                
            # --- VÒNG LẶP 2: Vét máng cho đủ 8 bài ---
            if len(final_news) < 8:
                for article in results:
                    if len(final_news) >= 8: 
                        break
                        
                    article_url = article.get("link", "")
                    raw_title = article.get("title", "")
                    clean_title = raw_title.lower().strip() if raw_title else ""
                    
                    # Áp dụng lưới lọc kép cho cả vòng vét máng
                    if article_url not in used_urls and clean_title not in used_titles:
                        final_news.append({
                            "title": raw_title,
                            "url": article_url,
                            "source": article.get("source_name", article.get("source_id", "News")),
                            "description": article.get("description", "") or "",
                            "category": article.get("category", []),
                            "pubDate": article.get("pubDate", ""),
                            "fetched_at": article.get("fetched_at", ""),
                            "image_url": article.get("image_url", "") or ""
                        })
                        used_urls.add(article_url)
                        if clean_title:
                            used_titles.add(clean_title)
            
            # --- VÒNG LẶP 3: Sort theo pubDate (Mới nhất lên đầu) ---
            final_news.sort(key=lambda x: str(x.get("pubDate", "")), reverse=True)

            # CHỈ GHI ĐÈ DICTIONARY NẾU CÓ DATA MỚI TRẢ VỀ
            if len(final_news) > 0:
                all_news_data[country] = final_news
                print(f"✅ Thành công: {country.upper()} - Lấy được {len(final_news)} bài (Đã lọc trùng lặp)")
            else:
                print(f"⚠️ {country.upper()} không có tin mới, giữ nguyên data cũ.")
            
        else:
            print(f"❌ Lỗi API ở {country.upper()}: {data.get('results', data)} -> Dùng lại data cũ.")
            
    except Exception as e:
        print(f"❌ Lỗi mạng/Hệ thống ở {country.upper()}: {str(e)} -> Dùng lại data cũ.")
        
    time.sleep(1.5)

# --- BƯỚC 3: XUẤT RA FILE AN TOÀN ---
with open(FILE_NAME, "w", encoding="utf-8") as f:
    json.dump(all_news_data, f, ensure_ascii=False, indent=4)

print("\n🎉 Đã hoàn tất! Dữ liệu được lưu an toàn vào news_data.json")
