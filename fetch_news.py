import requests
import json
import time
import os

# Lấy API Key từ Github Secrets
API_KEY = os.environ.get("NEWSDATA_API_KEY")

# TỪ ĐIỂN 50 QUỐC GIA & NGÔN NGỮ CHUẨN CỦA NEWSDATA.IO
COUNTRY_LANG_MAP = {
    # --- CHÂU Á & THÁI BÌNH DƯƠNG ---
    "vn": "vi",  # Việt Nam - Tiếng Việt
    "jp": "ja",  # Nhật Bản - Tiếng Nhật (Newsdata dùng 'ja')
    "kr": "ko",  # Hàn Quốc - Tiếng Hàn
    "cn": "zh",  # Trung Quốc - Tiếng Trung
    "tw": "zh",  # Đài Loan - Tiếng Trung
    "hk": "zh",  # Hồng Kông - Tiếng Trung
    "in": "hi",  # Ấn Độ - Tiếng Hindi (Hoặc dùng 'en' nếu muốn lấy báo tiếng Anh)
    "id": "id",  # Indonesia - Tiếng Indo
    "my": "ms",  # Malaysia - Tiếng Mã Lai
    "th": "th",  # Thái Lan - Tiếng Thái
    "sg": "en",  # Singapore - Tiếng Anh
    "ph": "en",  # Philippines - Tiếng Anh
    "au": "en",  # Úc - Tiếng Anh
    "nz": "en",  # New Zealand - Tiếng Anh

    # --- CHÂU ÂU ---
    "gb": "en",  # Anh Quốc - Tiếng Anh
    "fr": "fr",  # Pháp - Tiếng Pháp
    "de": "de",  # Đức - Tiếng Đức
    "it": "it",  # Ý - Tiếng Ý
    "es": "es",  # Tây Ban Nha - Tiếng Tây Ban Nha
    "pt": "pt",  # Bồ Đào Nha - Tiếng Bồ Đào Nha
    "ru": "ru",  # Nga - Tiếng Nga
    "ua": "uk",  # Ukraine - Tiếng Ukraine
    "nl": "nl",  # Hà Lan - Tiếng Hà Lan
    "be": "fr",  # Bỉ - Tiếng Pháp (Hoặc 'nl')
    "ch": "de",  # Thụy Sĩ - Tiếng Đức (Hoặc 'fr', 'it')
    "at": "de",  # Áo - Tiếng Đức
    "se": "sv",  # Thụy Điển - Tiếng Thụy Điển
    "no": "no",  # Na Uy - Tiếng Na Uy
    "dk": "da",  # Đan Mạch - Tiếng Đan Mạch
    "fi": "fi",  # Phần Lan - Tiếng Phần Lan
    "pl": "pl",  # Ba Lan - Tiếng Ba Lan
    "cz": "cs",  # Cộng hòa Séc - Tiếng Séc
    "ro": "ro",  # Romania - Tiếng Romania
    "hu": "hu",  # Hungary - Tiếng Hungary
    "gr": "el",  # Hy Lạp - Tiếng Hy Lạp
    "tr": "tr",  # Thổ Nhĩ Kỳ - Tiếng Thổ Nhĩ Kỳ

    # --- CHÂU MỸ ---
    "us": "en",  # Mỹ - Tiếng Anh
    "ca": "en",  # Canada - Tiếng Anh (Hoặc 'fr')
    "mx": "es",  # Mexico - Tiếng Tây Ban Nha
    "br": "pt",  # Brazil - Tiếng Bồ Đào Nha
    "ar": "es",  # Argentina - Tiếng Tây Ban Nha
    "co": "es",  # Colombia - Tiếng Tây Ban Nha
    "cl": "es",  # Chile - Tiếng Tây Ban Nha
    "pe": "es",  # Peru - Tiếng Tây Ban Nha
    "ve": "es",  # Venezuela - Tiếng Tây Ban Nha

    # --- TRUNG ĐÔNG & CHÂU PHI ---
    "ae": "ar",  # UAE (Các Tiểu vương quốc Ả Rập) - Tiếng Ả Rập
    "sa": "ar",  # Ả Rập Xê Út - Tiếng Ả Rập
    "eg": "ar",  # Ai Cập - Tiếng Ả Rập
    "il": "he",  # Israel - Tiếng Do Thái (Hebrew)
    "za": "en"   # Nam Phi - Tiếng Anh
}

# 3 Chủ đề hot nhất
CATEGORIES = "top,business,technology,breaking"
all_news_data = {}

print(f"🚀 Bắt đầu lấy tin tức cho {len(COUNTRY_LANG_MAP)} quốc gia...\n")

for country, language in COUNTRY_LANG_MAP.items():
    url = f"https://newsdata.io/api/1/latest?apikey={API_KEY}&country={country}&category={CATEGORIES}&language={language}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") == "success":
            results = data.get("results", [])
            grouped_news = {"top": [], "business": [], "technology": [], "breaking": []}
            
            for article in results:
                categories_of_article = article.get("category", [])
                for cat in categories_of_article:
                    if cat in grouped_news and len(grouped_news[cat]) < 2:
                        grouped_news[cat].append({
                            "title": article.get("title", ""),
                            "url": article.get("link", ""), 
                            "source": article.get("source_name", "")
                        })
                        break
            
            final_6_news = []
            for cat, items in grouped_news.items():
                final_6_news.extend(items)
                
            all_news_data[country] = final_6_news
            print(f"✅ Thành công: {country.upper()} (Ngôn ngữ: {language}) - Lấy được {len(final_6_news)} bài")
            
        else:
            # Nếu API báo lỗi (Ví dụ: hết lượt, sai key...)
            print(f"❌ Lỗi API ở {country.upper()}: {data.get('results', data)}")
            
    except Exception as e:
        print(f"❌ Lỗi mạng/Hệ thống ở {country.upper()}: {str(e)}")
        
    # Nghỉ 1.5 giây để tránh bị Newsdata khóa mõm vì Spam Request
    time.sleep(1.5)

# Lưu thành 1 file JSON duy nhất chứa data của cả 50 nước
with open("news_data.json", "w", encoding="utf-8") as f:
    json.dump(all_news_data, f, ensure_ascii=False, indent=4)
    
print("\n🎉 Đã hoàn tất! Dữ liệu được lưu vào news_data.json")