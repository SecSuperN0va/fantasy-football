from django.shortcuts import render, get_object_or_404
from django.template.defaulttags import register
from home.views import FFTemplateView
from home.models import FFLeague, SportsLeague
# Create your views here.

class LeaguesView(FFTemplateView):
    template_name = "league/index.html"


class LeagueView(FFTemplateView):
    template_name = "league/single_league.html"

    def get_context_data(self, **kwargs):
        ff_league = get_object_or_404(FFLeague, pk=self.kwargs.get('league_id'))
        players = ff_league.players.prefetch_related('selections')
        players_with_scores = [(p, p.league_score(ff_league)) for p in players]
        players_with_scores = list(reversed(sorted(players_with_scores, key=lambda x: x[1])))
        sports_leagues = SportsLeague.objects.prefetch_related().filter(active=True)
        player_league_selections = list()
        for player in players:
            player_selections = [(x, player.get_league_selection(ff_league, x)) for x in sports_leagues]
            player_league_selections.append((player, player_selections))
        context = super().get_context_data(**kwargs)
        context.update(
            ff_league=ff_league,
            players_with_scores=players_with_scores,
            sports_leagues=sports_leagues,
            player_league_selections=player_league_selections,
        )
        return context


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)