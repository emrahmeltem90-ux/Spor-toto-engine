import streamlit as st
import json
import swisseph as swe
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Astro-Toto Tahmin Motoru", page_icon="🔮", layout="centered")

# Astrolojik Sabitler
BURCLAR = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", 
           "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

GEZEGENLER = {
    "Güneş": swe.SUN, "Ay": swe.MOON, "Mars": swe.MARS, 
    "Jüpiter": swe.JUPITER, "Satürn": swe.SATURN
}

# Takımların Astrolojik Elementleri
TAKIM_ELEMENTLERI = {
    "Konyaspor": "Toprak", "Galatasaray": "Ateş", "Erzurumspor": "Hava", "Çorum": "Ateş",
    "Kocaelispor": "Toprak", "Rizespor": "Su", "Fenerbahçe": "Ateş", "Göztepe": "Su",
    "Amed Sportif": "Toprak", "Eyüpspor": "Hava", "Başakşehir": "Toprak", "Samsunspor": "Ateş",
    "Trabzonspor": "Su", "Gaziantep": "Ateş", "Kasımpaşa": "Su", "Beşiktaş": "Hava",
    "Gençlerbirliği": "Toprak", "Alanyaspor": "Ateş", "Bayern Münih": "Ateş", "Dortmund": "Ateş",
    "Chelsea": "Su", "Manchester United": "Ateş", "Liverpool": "Su", "Arsenal": "Ateş",
    "Athletic Bilbao": "Toprak", "Real Sociedad": "Su", "AC Milan": "Ateş", "Inter": "Toprak",
    "Juventus": "Toprak", "Napoli": "Su"
}

# Maç Tarihleri
MAC_TAKVIMI = {
    "Konyaspor - Galatasaray A.Ş.": "30.10.2026 20:00",
    "Erzurumspor FK - Çorum FK": "31.10.2026 13:30",
    "Kocaelispor - Çaykur Rizespor A.Ş.": "31.10.2026 16:00",
    "Fenerbahçe A.Ş. - Göztepe A.Ş.": "31.10.2026 19:00",
    "Amed Sportif Faaliyetler - Eyüpspor": "01.11.2026 13:30",
    "Başakşehir FK - Samsunspor A.Ş.": "01.11.2026 16:00",
    "Trabzonspor A.Ş. - Gaziantep FK A.Ş.": "01.11.2026 16:00",
    "Kasımpaşa A.Ş. - Beşiktaş A.Ş.": "01.11.2026 19:00",
    "Gençlerbirliği - Alanyaspor": "02.11.2026 20:00",
    "Bayern Münih - B. Dortmund": "31.10.2026 20:30",
    "Chelsea - Manchester United": "31.10.2026 15:30",
    "Liverpool - Arsenal": "01.11.2026 19:30",
    "Athletic Bilbao - Real Sociedad": "01.11.2026 23:00",
    "AC Milan - Inter": "31.10.2026 22:45",
    "Juventus - Napoli": "01.11.2026 22:45"
}

def hesapla_harita(tarih_str, enlem=45.46, boylam=9.19):
    dt = datetime.strptime(tarih_str, "%d.%m.%Y %H:%M")
    jd = swe.julday(dt.year, dt.month, dt.day, (dt.hour - 3) + dt.minute/60.0)
    harita = {}
    for isim, kod in GEZEGENLER.items():
        try:
            hesap = swe.calc_ut(jd, kod)[0]
            boylam_derece = hesap[0]
            burc_index = int(boylam_derece / 30)
            harita[isim] = {"burc": BURCLAR[burc_index], "tam_derece": boylam_derece}
        except: pass
    return harita

def aci_bul(derece1, derece2):
    fark = abs(derece1 - derece2)
    if fark > 180: fark = 360 - fark
    if abs(fark - 0) <= 5: return "Kavuşum", 5
    if abs(fark - 60) <= 5: return "Altmışlık", 3
    if abs(fark - 90) <= 5: return "Kare (Zorlu)", -5
    if abs(fark - 120) <= 5: return "Üçgen (Şanslı)", 4
    if abs(fark - 180) <= 5: return "Karşıt", -4
    return "Açı Yok", 0

def element_bul(takim_adi):
    for key, element in TAKIM_ELEMENTLERI.items():
        if key.lower() in takim_adi.lower(): return element
    return "Bilinmiyor"

# Arayüz Tasarımı
st.title("🔮 Astro-Toto Tahmin Motoru")
st.write("Bu uygulama, 1. görseldeki haritayı (28.10.2026 Milano) baz alarak maç saatlerindeki gökyüzü açılarını hesaplar ve eğlence amaçlı tahminler üretir.")

try:
    with open("bulletin.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    st.subheader(f"📅 Hafta {data.get('week', 1)} Bülteni")
    
    # Temel Haritayı Arka Planda Hesapla
    temel_harita = hesapla_harita("28.10.2026 18:30")
    
    if st.button("🚀 Maçları Astrolojik Olarak Analiz Et"):
        for mac in data.get("matches", []):
            ev_takim = mac["home_team"]
            dep_takim = mac["away_team"]
            mac_adi = f"{ev_takim} - {dep_takim}"
            tarih = MAC_TAKVIMI.get(mac_adi, "30.10.2026 20:00")
            
            mac_haritasi = hesapla_harita(tarih)
            
            mars_aci, mars_puan = aci_bul(temel_harita["Mars"]["tam_derece"], mac_haritasi["Mars"]["tam_derece"])
            ay_aci, ay_puan = aci_bul(temel_harita["Ay"]["tam_derece"], mac_haritasi["Ay"]["tam_derece"])
            
            ev_element = element_bul(ev_takim)
            dep_element = element_bul(dep_takim)
            
            ev_skor = 1 + (2 if ev_element == mac_haritasi["Mars"]["burc"] else 0) + mars_puan + ay_puan
            dep_skor = 1 + (1 if dep_element == mac_haritasi["Mars"]["burc"] else 0) + (mars_puan // 2)
            
            ev_skor, dep_skor = max(0, ev_skor), max(0, dep_skor)
            
            if mars_puan < 0: yorum = "⚠️ Sert mücadele, kartlar ve düşük skor."
            elif mars_puan > 0: yorum = "✨ Hücum futbolu ve bol gol."
            else: yorum = "⚖️ Dengeli maç."
            
            # Ekrana Yazdır
            with st.expander(f"⚽ {mac_adi} (Tahmini Skor: {ev_skor} - {dep_skor})"):
                st.write(f"**Tarih:** {tarih}")
                st.write(f"**Gökyüzü Açısı:** {mars_aci}")
                st.write(f"**Yorum:** {yorum}")
                
except FileNotFoundError:
    st.error("bulletin.json dosyası bulunamadı. Lütfen dosyanın doğru yerde olduğundan emin olun.")
