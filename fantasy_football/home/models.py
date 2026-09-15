from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}' 


class SportsLeague(models.Model):
    name = models.CharField(max_length=100)
    bbc_name_slug = models.CharField(max_length=100, default="", unique=True)
    last_updated = models.DateTimeField(null=True, default=None)
    active = models.BooleanField(default=False)
    order_idx = models.IntegerField(default=0)

    class Meta:
        ordering = ['order_idx']

    def __str__(self):
        return f'{self.order_idx}. {self.name} ({self.bbc_name_slug}, last updated: {self.last_updated})'


class Player(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def league_score(self, league):
        score = 0
        for s in self.selections.prefetch_related('ff_league'):
            if s.ff_league == league:
                score += s.total_points
        return score
    
    def get_league_selection(self, ff_league, league):
        for s in self.selections.prefetch_related('ff_league', 'league'):
            if s.ff_league == ff_league and s.league == league:
                return s


class TeamStanding(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="standings")
    league = models.ForeignKey(SportsLeague, on_delete=models.CASCADE, related_name="standings")
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return f'TeamStanding(team={self.team}, league={self.league}, points={self.points}, rank={self.rank})'


class FFLeague(models.Model):
    """Fantasy Football League"""
    name = models.CharField(max_length=100)
    players = models.ManyToManyField(Player, related_name='players', blank=True)

    def __str__(self):
        return self.name
    
    @property
    def player_scores(self):
        return {p: p.league_score(self) for p in self.players.prefetch_related('selections')}


class Selection(models.Model):
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="winning_selections")
    loser = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="losing_selections")
    league = models.ForeignKey(SportsLeague, on_delete=models.CASCADE, related_name="selections")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="selections")
    ff_league = models.ForeignKey(FFLeague, on_delete=models.CASCADE, related_name="selections", null=True, default=None)

    def _get_standing_in_league(self, team, league):
        for s in league.standings.prefetch_related('team'):
            if s.team == team:
                return s

    @property
    def winner_standing(self):
        return self._get_standing_in_league(self.winner, self.league)
    
    @property
    def loser_standing(self):
        return self._get_standing_in_league(self.loser, self.league)
    
    @property
    def total_points(self):
        winner_points = self.winner_standing.points
        loser_points = self.loser_standing.points
        return winner_points - loser_points
    
    def __str__(self):
        return f'Selection(player={self.player.name}, league={self.league.name}, winner={self.winner.name}, loser={self.loser.name})'
