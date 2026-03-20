import requests
import json
import time
import os
from datetime import datetime, timezone 

# Lấy API Key từ Github Secrets
API_KEY = os.environ.get("NEWSDATA_API_KEY")
FILE_NAME = "news_data.json" # Tên file lưu trữ

# TỪ ĐIỂN 50 QUỐC GIA CHẠY ADS (ĐÃ TỐI ƯU eCPM VÀ CHẤT LƯỢNG TIN TỨC)
COUNTRY_LANG_MAP = {
    # --- TIER 1 & CHÂU ÂU (eCPM CAO - Khách V.I.P) ---
    "us": "en",  # Mỹ
    "gb": "en",  # Anh
    "ca": "en",  # Canada
    "de": "de",  # Đức
    "fr": "fr",  # Pháp
    "es": "es",  # Tây Ban Nha
    "it": "it",  # Ý (MỚI THÊM)
    "nl": "nl",  # Hà Lan
    "be": "fr",  # Bỉ 
    "pt": "pt",  # Bồ Đào Nha
    "pl": "pl",  # Ba Lan
    "gr": "el",  # Hy Lạp
    "ro": "ro",  # Romania

    # --- CHÂU MỸ LATIN ---
    "mx": "es",  # Mexico
    "co": "es",  # Colombia
    "ve": "es",  # Venezuela

    # --- CHÂU Á & ĐẠI DƯƠNG (Volume khủng + eCPM tốt) ---
    "vn": "vi",  # Việt Nam (Để Dev tự test)
    "in": "en",  # Ấn Độ (MỚI THÊM - Dùng tiếng Anh để lấy tin Tech/Biz)
    "sg": "en",  # Singapore (MỚI THÊM)
    "id": "id",  # Indonesia
    "th": "th",  # Thái Lan
    "ph": "en",  # Philippines
    "kh": "en",  # Campuchia 
    "bd": "en",  # Bangladesh 
    "pk": "en",  # Pakistan
    "np": "en",  # Nepal
    "pg": "en",  # Papua New Guinea

    # --- TRUNG ĐÔNG (eCPM Rất Tốt) ---
    "ae": "en",  # UAE 
    "sa": "ar",  # Saudi Arabia (MỚI THÊM)
    "il": "he",  # Israel (MỚI THÊM)
    "iq": "ar",  # Iraq
    "tr": "tr",  # Thổ Nhĩ Kỳ

    # --- CHÂU PHI (Giữ lại các nước có Volume app của bạn tốt nhất) ---
    "za": "en",  # Nam Phi (MỚI THÊM - eCPM đỉnh nhất Châu Phi)
    "eg": "ar",  # Ai Cập
    "dz": "ar",  # Algeria
    "tn": "ar",  # Tunisia
    "cm": "fr",  # Cameroon
    "ug": "en",  # Uganda
    "na": "en",  # Namibia
    "rw": "en",  # Rwanda
    "mz": "pt",  # Mozambique
    "ml": "fr",  # Mali
    "tg": "fr",  # Togo
    "sd": "ar",  # Sudan
    "zm": "en",  # Zambia
    "bj": "fr",  # Benin
    "zw": "en",  # Zimbabwe
    "bw": "en",  # Botswana
    "mg": "fr",  # Madagascar
    "ao": "pt"   # Angola
}

# Chủ đề hot nhất cho App Đồng hồ thông minh
CATEGORIES = "business,technology,sports,environment"

# --- LOGIC TỰ ĐỘNG ĐỔI CATEGORY THEO KHUNG GIỜ (TỐI ƯU TRẢI NGHIỆM) ---
# Lấy giờ hiện tại của Server Github (Tính theo UTC)
current_utc_hour = datetime.now(timezone.utc).hour

if 0 <= current_utc_hour < 6:
    # 01:00 UTC (Tương ứng 08:00 Sáng VN)
    CATEGORIES = "business,technology,sports,environment"
    session_name = "🌅 BUỔI SÁNG (Kinh doanh, Tech, Thể thao, Môi trường)"

elif 6 <= current_utc_hour < 12:
    # 07:00 UTC (Tương ứng 14:00 Chiều VN)
    CATEGORIES = "entertainment,food,lifestyle,tourism"
    session_name = "☀️ BUỔI TRƯA/CHIỀU (Giải trí, Ẩm thực, Phong cách sống, Du lịch)"

elif 12 <= current_utc_hour < 18:
    # 13:00 UTC (Tương ứng 20:00 Tối VN)
    CATEGORIES = "health,education,science,business"
    session_name = "🌙 BUỔI TỐI (Sức khỏe, Giáo dục, Khoa học, Thị trường)"

else:
    # 19:00 UTC (Tương ứng 02:00 Đêm VN)
    CATEGORIES = "technology,sports,environment,lifestyle"
    session_name = "🌌 ĐÊM MUỘN (Tech, Thể thao, Môi trường, Đời sống)"

print(f"🕒 Khung giờ hiện tại (UTC): {current_utc_hour}h")
print(f"🎯 Đang kích hoạt chế độ: {session_name}")
print(f"📡 Categories sẽ fetch: {CATEGORIES}\n")

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
            
            # CHỈ LẤY CÁC TRƯỜNG DỮ LIỆU NHƯ CŨ, KHÔNG LỌC TRÙNG LẶP
            for article in results:
                final_news.append({
                    "title": article.get("title", ""),
                    "url": article.get("link", ""),
                    "source": article.get("source_name", article.get("source_id", "News")),
                    "description": article.get("description", "") or "",
                    "category": article.get("category", []),
                    "pubDate": article.get("pubDate", ""),
                    "fetched_at": article.get("fetched_at", ""),
                    "image_url": article.get("image_url", "") or ""
                })

            # CHỈ GHI ĐÈ DICTIONARY NẾU CÓ DATA MỚI TRẢ VỀ
            if len(final_news) > 0:
                all_news_data[country] = final_news
                print(f"✅ Thành công: {country.upper()} - Lấy được {len(final_news)} bài")
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
