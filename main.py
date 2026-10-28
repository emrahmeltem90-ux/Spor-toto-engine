import json
import swisseph as swe
from datetime import datetime

# Astrolojik Sabitler
BURCLAR = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", 
           "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

GEZEGENLER = {
    "Güneş": swe.SUN, "Ay": swe.MOON, "Mars": swe.MARS, 
    "Jüpiter": swe.JUPITER, "Satürn": swe.SATURN
}

# Takımların Astrolojik Elementleri
TAKIM_ELEMENTLERI = {
    "Konyaspor": "Toprak", "Galatasaray": "Ateş",
    "Erzurumspor": "Hava", "Çorum": "Ateş",
    "Kocaelispor": "Toprak", "Rizespor": "Su",
    "Fenerbahçe": "Ateş", "Göztepe": "Su",
    "Amed Sportif": "Toprak", "Eyüpspor": "Hava",
    "Başakşehir": "Toprak", "Samsunspor": "Ateş",
    "Trabzonspor": "Su", "Gaziantep": "Ateş",
    "Kasımpaşa": "Su", "Beşiktaş": "Hava",
    "Gençlerbirliği": "Toprak", "Alanyaspor": "Ateş",
    "Bayern Münih": "Ateş", "Dortmund": "Ateş",
    "Chelsea": "Su", "Manchester United": "Ateş",
    "Liverpool": "Su", "Arsenal": "Ateş",
    "Athletic Bilbao": "Toprak", "Real Sociedad": "Su",
    "AC Milan": "Ateş", "Inter": "Toprak",
    "Juventus": "Toprak", "Napoli": "Su"
}

# 2. Görseldeki Maç Tarihleri ve Saatleri
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

class SporTotoEngine:
    def __init__(self, bulletin_path="bulletin.json"):
        self.bulletin_path = bulletin_path
        self.hafta = 0
        self.matches = []
        self.temel_harita = {}
        self.load_bulletin()
        self.hesapla_temel_harita()

    def load_bulletin(self):
        """GitHub'daki JSON yapısını okur."""
        try:
            with open(self.bulletin_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.hafta = data.get("week", 1)
                self.matches = data.get("matches", [])
            print(f"✅ Hafta {self.hafta} bülteni başarıyla yüklendi. Toplam {len(self.matches)} maç var.")
        except Exception as e:
            print(f"❌ Bülten yüklenirken hata oluştu: {e}")
            self.matches = []

    def hesapla_harita(self, tarih_str, enlem=45.46, boylam=9.19):
        """Girilen tarih için astronomik harita çıkarır."""
        dt = datetime.strptime(tarih_str, "%d.%m.%Y %H:%M")
        # Türkiye Saati (TSİ) için UT (Evrensel Zaman) farkı: -3 saat
        jd = swe.julday(dt.year, dt.month, dt.day, (dt.hour - 3) + dt.minute/60.0)
        
        harita = {}
        for isim, kod in GEZEGENLER.items():
            try:
                hesap = swe.calc_ut(jd, kod)[0]
                boylam_derece = hesap[0]
                burc_index = int(boylam_derece / 30)
                harita[isim] = {"burc": BURCLAR[burc_index], "tam_derece": boylam_derece}
            except:
                pass
        return harita

    def hesapla_temel_harita(self):
        """1. Görseldeki Doğum Haritasını (28.10.2026 18:30 Milano) hesaplar."""
        print("⏳ Temel Harita (28.10.2026 18:30 Milano) Hesaplanıyor...")
        self.temel_harita = self.hesapla_harita("28.10.2026 18:30")
        print("✅ Temel Harita Hazır.\n")

    def aci_bul(self, derece1, derece2):
        """Gezegenler arası açıları hesaplar."""
        fark = abs(derece1 - derece2)
        if fark > 180: fark = 360 - fark
        
        if abs(fark - 0) <= 5: return "Kavuşum", 5
        if abs(fark - 60) <= 5: return "Altmışlık", 3
        if abs(fark - 90) <= 5: return "Kare (Zorlu)", -5
        if abs(fark - 120) <= 5: return "Üçgen (Şanslı)", 4
        if abs(fark - 180) <= 5: return "Karşıt", -4
        return "Açı Yok", 0

    def element_bul(self, takim_adi):
        """A.Ş., FK gibi ekleri yok sayarak takımın elementini bulur."""
        for key, element in TAKIM_ELEMENTLERI.items():
            if key.lower() in takim_adi.lower():
                return element
        return "Bilinmiyor"

    def mac_tahmin_et(self, mac):
        ev_takim = mac["home_team"]
        dep_takim = mac["away_team"]
        mac_adi = f"{ev_takim} - {dep_takim}"
        
        # Tarihi sözlükten çek, yoksa varsayılan bir tarih ver
        tarih = MAC_TAKVIMI.get(mac_adi, "30.10.2026 20:00")
        
        mac_haritasi = self.hesapla_harita(tarih)
        
        # Mars ve Ay açılarını hesapla
        mars_aci, mars_puan = self.aci_bul(
            self.temel_harita["Mars"]["tam_derece"], mac_haritasi["Mars"]["tam_derece"]
        )
        ay_aci, ay_puan = self.aci_bul(
            self.temel_harita["Ay"]["tam_derece"], mac_haritasi["Ay"]["tam_derece"]
        )

        ev_element = self.element_bul(ev_takim)
        dep_element = self.element_bul(dep_takim)

        # Skor Başlangıç Değerleri
        ev_skor = 1
        dep_skor = 1

        # Astrolojik Etki Puanlaması
        if ev_element == mac_haritasi["Mars"]["burc"]: ev_skor += 2
        if dep_element == mac_haritasi["Mars"]["burc"]: dep_skor += 1

        ev_skor += mars_puan + ay_puan
        dep_skor += (mars_puan // 2) # Deplasman etkisi daha az

        # Skorlar eksiye düşmesin
        ev_skor, dep_skor = max(0, ev_skor), max(0, dep_skor)

        # Yorum Motoru
        if mars_puan < 0:
            yorum = "⚠️ Sert mücadele, kartlar ve düşük skor bekleniyor."
        elif mars_puan > 0:
            yorum = "✨ Hücum futbolu ve bol gol ihtimali yüksek."
        else:
            yorum = "⚖️ Dengeli maç, orta saha savaşı."

        return {
            "mac_id": mac.get("match_id"),
            "mac": mac_adi,
            "tarih": tarih,
            "mars_aci": mars_aci,
            "skor": f"{ev_skor} - {dep_skor}",
            "yorum": yorum
        }

    def tum_bulteni_analiz_et(self):
        print(f"\n🔮 --- HAFTA {self.hafta} ASTROLOJİK TAHMİN SONUÇLARI --- 🔮\n")
        for mac in self.matches:
            sonuc = self.mac_tahmin_et(mac)
            print(f"⚽ Maç ID: {sonuc['mac_id']} | {sonuc['mac']}")
            print(f"   📅 {sonuc['tarih']} | 🔥 Mars Açısı: {sonuc['mars_aci']}")
            print(f"   📜 {sonuc['yorum']}")
            print(f"   🎯 Tahmini Skor: {sonuc['skor']}\n")

if __name__ == "__main__":
    engine = SporTotoEngine()
    engine.tum_bulteni_analiz_et()
