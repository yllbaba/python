import pandas as pd

class Analyzer:
    def __init__(self, filepath):
        try:
            self.data = pd.read_csv(filepath)
        except Exception as e:
            print("Error loading file:", e)

    def top_scorer(self):
        return self.data.sort_values("points", ascending=False).iloc[0]

    def average_points(self):
        return self.data["points"].mean()

    def mvp(self):
        self.data["efficiency"] = (
            self.data["points"] +
            self.data["assists"] +
            self.data["rebounds"]
        ) / self.data["games"]

        return self.data.sort_values("efficiency", ascending=False).iloc[0]