import streamlit as st
import json
import swisseph as swe
from datetime import datetime
import math
import os

# Kerykeion (Harita Çizim Kütüphanesi) Importları
from kerykeion import AstrologicalSubjectFactory
from kerykeion.chart_data_factory import ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer

# Sayfa Ayarları
st.set_page_config(page_title="Astro-İstatistik Motoru", page_icon="🔮", layout="wide")

# Astrolojik Sabitler
BURCLAR = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", 
           "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

GEZEGENLER = {
    "Güneş": swe.SUN, "Ay": swe.MOON, "Mars": swe.MARS, 
    "Jüpiter": swe.JUPITER, "Satürn": swe.SATURN
}

# 🏆 TAKIM GÜÇ ENDEKSLERİ (İstatistiksel Yaklaşım)
TAKIM_GUCLERI = {
    "Galatasaray": 88, "Fenerbahçe": 87, "Beşiktaş": 82, "Trabzonspor": 80,
    "Başakşehir": 75, "Samsunspor": 72, "Kasımpaşa": 68, "Konyaspor": 67,
    "Göztepe": 65, "Rizespor": 64, "Alanyaspor": 63, "Gaziantep": 62,
    "Eyüpspor": 61, "Kocaelispor": 60, "Erzurumspor": 58, "Çorum": 57,
    "Amed Sportif": 56, "Gençlerbirliği": 55,
    "Bayern Münih": 92, "B. Dortmund": 84, "Liverpool": 90, "Arsenal": 88,
    "Manchester United": 81, "Chelsea": 80, "AC Milan": 83, "Inter": 86,
    "Juventus": 84, "Napoli": 85, "Athletic Bilbao": 78, "Real Sociedad": 76
}

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

# --- 1. HARİTA ÇİZİM FONKSİYONU ---
@st.cache_data # Her seferinde yeniden çizmesin diye önbelleğe alıyoruz
def harita_ciz():
    try:
        # Milano, 28 Ekim 2026, 18:30
        subject = AstrologicalSubjectFactory.from_birth_data(
            "Temel_Harita", 2026, 10, 28, 18, 30, 
            lng=9.19, lat=45.46, tz_str="Europe/Rome"
        )
        chart_data = ChartDataFactory.create_natal_chart_data(subject)
        chart_drawer = ChartDrawer(chart_data=chart_data)
        
        # SVG dosyasını oluştur
        if not os.path.exists("charts"): os.makedirs("charts")
        output_path = "charts/temel_harita.svg"
        chart_drawer.save_svg(output_path, "temel_harita")
        
        # SVG içeriğini oku ve HTML olarak döndür
        with open(output_path, "r", encoding="utf-8") as f:
            svg_icerik = f.read()
        return svg_icerik
    except Exception as e:
        return f"<p>Harita çizilemedi: {e}</p>"

# --- 2. GERÇEK ASTRONOMİK HESAPLAMA ---
def hesapla_harita(tarih_str):
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

# --- 3. MATEMATİKSEL SKOR MOTORU (POISSON) ---
def poisson_skor_hesapla(ev_guc, dep_guc, toplam_astro_puan):
    # Beklenen Gol (xG) hesaplama
    xG_ev = (ev_guc / 40) + 0.3
    xG_dep = (dep_guc / 50)
    
    # Astrolojik etkiyi xG'ye yansıt (Gol potansiyeli)
    astro_etki = toplam_astro_puan * 0.1
    xG_ev += astro_etki
    xG_dep += astro_etki
    
    xG_ev = max(0.1, xG_ev)
    xG_dep = max(0.1, xG_dep)

    def poisson(lam, k):
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)
    
    en_iyi_ihtimal = 0
    en_iyi_skor = (0,0)
    
    for i in range(5):
        for j in range(5):
            ihtimal = poisson(xG_ev, i) * poisson(xG_dep, j)
            if ihtimal > en_iyi_ihtimal:
                en_iyi_ihtimal = ihtimal
                en_iyi_skor = (i, j)
    return en_iyi_skor, en_iyi_ihtimal

def takim_gucu_bul(takim_adi):
    for key, guc in TAKIM_GUCLERI.items():
        if key.lower() in takim_adi.lower(): return guc
    return 50

# --- ARAYÜZ TASARIMI ---
st.title("🔮 Astro-İstatistik Tahmin Motoru")

# Sol Sütun: Harita, Sağ Sütun: Tahminler
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🌌 Temel Harita")
    st.write("28.10.2026 - Milano (AC Milan - Bologna)")
    st.markdown(harita_ciz(), unsafe_allow_html=True)

with col2:
    st.subheader("📊 Maç Analizleri")
    
    try:
        with open("bulletin.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if st.button("🚀 Bülteni Analiz Et", use_container_width=True):
            temel_harita = hesapla_harita("28.10.2026 18:30")
            
            for mac in data.get("matches", []):
                ev_takim = mac["home_team"]
                dep_takim = mac["away_team"]
                mac_adi = f"{ev_takim} - {dep_takim}"
                tarih = MAC_TAKVIMI.get(mac_adi, "30.10.2026 20:00")
                
                # Transit (Maç saati) haritası
                mac_haritasi = hesapla_harita(tarih)
                mars_aci, mars_puan = aci_bul(temel_harita["Mars"]["tam_derece"], mac_haritasi["Mars"]["tam_derece"])
                ay_aci, ay_puan = aci_bul(temel_harita["Ay"]["tam_derece"], mac_haritasi["Ay"]["tam_derece"])
                
                toplam_astro_puan = mars_puan + ay_puan
                
                # Takım güçleri
                ev_guc = takim_gucu_bul(ev_takim)
                dep_guc = takim_gucu_bul(dep_takim)
                
                # Skor Hesaplama
                skor, ihtimal = poisson_skor_hesapla(ev_guc, dep_guc, toplam_astro_puan)
                
                # Yorum
                if toplam_astro_puan < -3: yorum = "Sert savunma, kartlar ve kısır bir maç."
                elif toplam_astro_puan > 5: yorum = "Bol gollü, hücum futbolu."
                else: yorum = "Dengeli bir maç, istatistikler ön planda."
                
                with st.expander(f"⚽ {mac_adi} (Skor: {skor[0]} - {skor[1]})"):
                    st.write(f"**Tarih:** {tarih}")
                    st.write(f"**Güç Dengesi:** {ev_guc} vs {dep_guc}")
                    st.write(f"**Gökyüzü Etkisi:** Mars {mars_aci} / Ay {ay_aci}")
                    st.write(f"**Yorum:** {yorum}")
                    st.write(f"**İstatistiksel Olasılık:** %{round(ihtimal*100, 1)}")
                    
    except Exception as e:
        st.error(f"Bülten okunamadı: {e}")
