import math
import json

class SporTotoEngine:
    def __init__(self, bulletin_path="bulletin.json"):
        self.bulletin_path = bulletin_path
        self.matches = []
        self.load_bulletin()

    def load_bulletin(self):
        """Dışarıdaki bulletin.json dosyasını okuyarak 15 maçı sisteme yükler."""
        try:
            with open(self.bulletin_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.matches = data.get("matches", [])
            print(f"Bülten yüklendi! Hafta: {data.get('week', 1)} | Toplam Maç: {len(self.matches)}")
        except FileNotFoundError:
            print("Hata: bulletin.json dosyası bulunamadı!")

    def calculate_implied_probabilities(self, match):
        """Bahis oranlarından marj arındırılmış piyasa olasılıklarını hesaplar."""
        odds = match["odds"]
        if odds["1"] <= 0 or odds["0"] <= 0 or odds["2"] <= 0:
            return {"1": 0.0, "0": 0.0, "2": 0.0}
        
        p1 = 1 / odds["1"]
        p0 = 1 / odds["0"]
        p2 = 1 / odds["2"]
        total_margin = p1 + p0 + p2
        
        return {
            "1": round((p1 / total_margin) * 100, 2),
            "0": round((p0 / total_margin) * 100, 2),
            "2": round((p2 / total_margin) * 100, 2)
        }

    def poisson_probability(self, lmbda, k):
        return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

    def analyze_match_score(self, home_lambda, away_lambda, max_goals=5):
        matrix = []
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                p = self.poisson_probability(home_lambda, h) * self.poisson_probability(away_lambda, a)
                matrix.append({"score": f"{h}-{a}", "prob": p * 100})
        matrix.sort(key=lambda x: x["prob"], reverse=True)
        return matrix[:3]

    def analyze_all_matches(self):
        print(f"\n{'Ev Sahibi':<25} | {'Deplasman':<25} | {'MS 1 (%)':<10} | {'MS 0 (%)':<10} | {'MS 2 (%)':<10}")
        print("-" * 95)
        for match in self.matches:
            probs = self.calculate_implied_probabilities(match)
            print(f"{match['home_team']:<25} | {match['away_team']:<25} | {probs['1']:<10} | {probs['0']:<10} | {probs['2']:<10}")

if __name__ == "__main__":
    print("=== SPOR TOTO ANALİZ MOTORU BAŞLATILDI ===")
    engine = SporTotoEngine("bulletin.json")
    engine.analyze_all_matches()
