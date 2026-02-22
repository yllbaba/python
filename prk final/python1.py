class Player:
    def __init__(self, name, team, points, assists, rebounds, games):
        self.name = name
        self.team = team
        self.points = int(points)
        self.assists = int(assists)
        self.rebounds = int(rebounds)
        self.games = int(games)

    def ppg(self):
        return self.points / self.games

    def apg(self):
        return self.assists / self.games

    def rpg(self):
        return self.rebounds / self.games

    def efficiency(self):
        return (self.points + self.assists + self.rebounds) / self.games