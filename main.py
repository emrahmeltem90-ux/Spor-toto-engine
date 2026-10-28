import math

class SporTotoEngine:
    def __init__(self):
        self.matches = []

    def add_match(self, home_team, away_team, home_odds, draw_odds, away_odds):
        """Bültendeki bir maçı oranları ve takımlarıyla sisteme ekler."""
        self.matches.append({
            "home": home_team,
            "away": away_team,
            "odds": {"1": home_odds, "0": draw_odds, "2": away_odds}
        })

    def calculate_implied_probabilities(self, match_idx):
        """Bahis oranlarından bahis piyasası olasılıklarını (marj arındırılmış) hesaplar."""
        match = self.matches[match_idx]
        odds = match["odds"]
        
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
        """Poisson dağılımı ile belirli bir gol olma olasılığını hesaplar."""
        return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

    def analyze_match_score(self, home_lambda, away_lambda, max_goals=5):
        """Poisson modeli ile en olası skor matrisini çıkarır."""
        matrix = []
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                p = self.poisson_probability(home_lambda, h) * self.poisson_probability(away_lambda, a)
                matrix.append({"score": f"{h}-{a}", "prob": p * 100})
        
        matrix.sort(key=lambda x: x["prob"], reverse=True)
        return matrix[:3]

    def analyze_all_matches(self):
        """Eklenen tüm maçların piyasa beklentilerini ekrana döker."""
        print(f"\n{'Ev Sahibi':<20} | {'Deplasman':<20} | {'MS 1 (%)':<10} | {'MS 0 (%)':<10} | {'MS 2 (%)':<10}")
        print("-" * 80)
        for i, match in enumerate(self.matches):
            probs = self.calculate_implied_probabilities(i)
            print(f"{match['home']:<20} | {match['away']:<20} | {probs['1']:<10} | {probs['0']:<10} | {probs['2']:<10}")

if __name__ == "__main__":
    print("=== SPOR TOTO & ANALİZ MOTORU BAŞLATILDI ===")
    toto = SporTotoEngine()
    
    toto.add_match("Konyaspor", "Galatasaray", 4.20, 3.60, 1.65)
    toto.add_match("Fenerbahçe", "Göztepe", 1.35, 4.50, 6.50)
    toto.add_match("Kasımpaşa", "Beşiktaş", 2.80, 3.40, 2.10)
    toto.add_match("AC Milan", "Inter", 2.50, 3.20, 2.70)
    
    toto.analyze_all_matches()
    
    print("\n--- Poisson Skor Analizi Örneği (Konyaspor vs Galatasaray) ---")
    top_scores = toto.analyze_match_score(home_lambda=1.1, away_lambda=1.8)
    for item in top_scores:
        print(f"Skor: {item['score']} | Olasılık: %{item['prob']:.2f}")
