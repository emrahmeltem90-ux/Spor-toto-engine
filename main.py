import math
import json
import swisseph as swe
from datetime import datetime

# Astrolojik sabitler
BURCLAR = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", 
           "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

GEZEGENLER = {
    "Güneş": swe.SUN, "Ay": swe.MOON, "Mars": swe.MARS, 
    "Jüpiter": swe.JUPITER, "Satürn": swe.SATURN
}

class SporTotoEngine:
    def __init__(self, bulletin_path="bulletin.json"):
        self.bulletin_path = bulletin_path
        self.matches = []
        self.temel_harita = {}
        self.load_bulletin()
        self.hesapla_temel_harita()

    def load_bulletin(self):
        """Dışarıdaki bulletin.json dosyasını okur."""
        try:
            with open(self.bulletin_path, 'r', encoding='utf-8') as file:
                self.matches = json.load(file)
            print(f"✅ {len(self.matches)} maç başarıyla yüklendi.")
        except Exception as e:
            print(f"❌ Bülten yüklenirken hata oluştu: {e}")
            self.matches = []

    def hesapla_harita(self, tarih_str, enlem=45.46, boylam=9.19):
        """Belirtilen tarih için gezegen konumlarını hesaplar."""
        dt = datetime.strptime(tarih_str, "%d.%m.%Y %H:%M")
        # Evrensel saat (UT) hesaplaması (Türkiye saati için -3 saat)
        jd = swe.julday(dt.year, dt.month, dt.day, (dt.hour - 3) + dt.minute/60.0)
        
        harita = {}
        for isim, kod in GEZEGENLER.items():
            try:
                hesap = swe.calc_ut(jd, kod)[0]
                boylam_derece = hesap[0]
                burc_index = int(boylam_derece / 30)
                harita[isim] = {
                    "burc": BURCLAR[burc_index], 
                    "tam_derece": boylam_derece
                }
            except:
                pass
        return harita

    def hesapla_temel_harita(self):
        """1. Görseldeki Doğum Haritasını (28.10.2026 Milano) hesaplar."""
        print("⏳ Temel Harita (28.10.2026) Hesaplanıyor...")
        self.temel_harita = self.hesapla_harita("28.10.2026 18:30")
        print("✅ Temel Harita Hazır.\n")

    def aci_bul(self, derece1, derece2):
        """İki gezegen arasındaki açıyı hesaplar ve puan döndürür."""
        fark = abs(derece1 - derece2)
        if fark > 180: fark = 360 - fark
        
        if abs(fark - 0) <= 5: return "Kavuşum", 5
        if abs(fark - 60) <= 5: return "Altmışlık", 3
        if abs(fark - 90) <= 5: return "Kare (Zorlu)", -5
        if abs(fark - 120) <= 5: return "Üçgen (Şanslı)", 4
        if abs(fark - 180) <= 5: return "Karşıt", -4
        return "Açı Yok", 0

    def mac_tahmin_et(self, mac):
        """Tek bir maç için astrolojik analiz yapar ve skor üretir."""
        # Maç saatinin transit haritasını çıkar (Maçın şehri bilinmediği için varsayılan kullanıldı)
        mac_haritasi = self.hesapla_harita(mac["tarih"])
        
        if not mac_haritasi or not self.temel_harita:
            return "Hesaplama Hatası"

        # Mars (Savaş/Rekabet) ve Jüpiter (Şans/Genişleme) açılarını bul
        mars_aci, mars_puan = self.aci_bul(
            self.temel_harita["Mars"]["tam_derece"], 
            mac_haritasi["Mars"]["tam_derece"]
        )
        
        ay_aci, ay_puan = self.aci_bul(
            self.temel_harita["Ay"]["tam_derece"], 
            mac_haritasi["Ay"]["tam_derece"]
        )

        # Skor Algoritması
        ev_skor = 1
        dep_skor = 1

        # Element uyumu (Ev sahibi avantajı)
        if mac["ev_element"] == mac_haritasi["Mars"]["burc"]:
            ev_skor += 2
        if mac["dep_element"] == mac_haritasi["Mars"]["burc"]:
            dep_skor += 1

        # Astrolojik açı puanları
        ev_skor += mars_puan
        dep_skor += (mars_puan // 2)
        ev_skor += ay_puan

        # Skorları 0'dan küçük olamaz yap
        ev_skor = max(0, ev_skor)
        dep_skor = max(0, dep_skor)

        # Yorum belirleme
        if mars_puan < 0:
            yorum = "⚠️ Mars Kare/Karşıt: Sert mücadele, kartlar ve düşük skor."
        elif mars_puan > 0:
            yorum = "✨ Mars Üçgen/Altmışlık: Hücum futbolu ve bol gol."
        else:
            yorum = "⚖️ Gökyüzü sakin: Dengeli maç."

        return {
            "mac": f"{mac['ev']} - {mac['dep']}",
            "tarih": mac["tarih"],
            "mars_aci": mars_aci,
            "ay_aci": ay_aci,
            "skor": f"{ev_skor} - {dep_skor}",
            "yorum": yorum
        }

    def tum_bulteni_analiz_et(self):
        """Bültendeki tüm maçları sırayla analiz eder."""
        print("\n🔮 --- ASTROLOJİK MAÇ TAHMİN SONUÇLARI --- 🔮\n")
        for mac in self.matches:
            sonuc = self.mac_tahmin_et(mac)
            if isinstance(sonuc, dict):
                print(f"⚽ {sonuc['mac']} ({sonuc['tarih']})")
                print(f"   🔥 Mars Açısı: {sonuc['mars_aci']} | 🌙 Ay Açısı: {sonuc['ay_aci']}")
                print(f"   📜 {sonuc['yorum']}")
                print(f"   🎯 Tahmini Skor: {sonuc['skor']}\n")

# Programı Çalıştır
if __name__ == "__main__":
    engine = SporTotoEngine()
    engine.tum_bulteni_analiz_et()
