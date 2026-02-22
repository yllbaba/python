from models.analyzer import Analyzer

analyzer = Analyzer("data/players.csv")

print("Top Scorer:")
print(analyzer.top_scorer())

print("\nMVP:")
print(analyzer.mvp())