import pandas as pd


class Analyzer:
    """Legacy analyzer retained for compatibility.

    Prefer the FastAPI service layer in app/services for new work.
    """

    def __init__(self, filepath: str) -> None:
        self.data = pd.read_csv(filepath)

    def top_scorer(self) -> pd.Series:
        return self.data.sort_values("points", ascending=False).iloc[0]

    def average_points(self) -> float:
        return float(self.data["points"].mean())

    def mvp(self) -> pd.Series:
        self.data["efficiency"] = (
            self.data["points"] + self.data["assists"] + self.data["rebounds"]
        ) / self.data["games"]
        return self.data.sort_values("efficiency", ascending=False).iloc[0]
