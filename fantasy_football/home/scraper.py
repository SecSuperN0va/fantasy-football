import datetime
import requests
import logging
import lxml.html
import re

from .models import SportsLeague, TeamStanding, Team

def solve(s):                                             
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)

class ScrapeError(BaseException):
    pass

class Scraper:

    def __init__(self):
        self.base_url = 'https://www.bbc.co.uk/sport/football/tables'
    
    def _get_page(self):
        with requests.get(self.base_url) as r:
            if r.status_code != 200:
                raise ScrapeError(f'got bad return code: {r}')
            if not r.content:
                raise ScrapeError(f'no response data')
            return r.content.decode()

    def _get_page_tree(self):
        page = self._get_page()
        try:
            page_tree = lxml.html.document_fromstring(page)
            return page_tree
        except Exception:
            logging.exception('failed to get page tree')
        raise ScrapeError('failed to get page tree')

    def _get_league_standings(self, tree):
        standings = []
        last_updated = None
        for lu in tree.xpath(".//div[contains(@class, 'StyledKeyFooter')]"):
            if 'Last Updated' in lu.text_content():
                print(lu.text_content())
                last_updated = lu.xpath("./p/span/text()")[0]
                last_updated = datetime.datetime.strptime(solve(last_updated), "%d %B %Y at %H:%M")

        for table_element in tree.xpath(".//table[@data-testid='football-table']"):
            headings = []
            # Get the headings
            for heading_row_element in table_element.xpath("./thead/tr/th/span/@data-always"):
                headings.append(str(heading_row_element))

            # Get the corresponding table row fields
            for body_row_element in table_element.xpath("./tbody/tr"):
                team = {}
                for i, row_field_element in enumerate(body_row_element.xpath("./td")):
                    if "Form" in row_field_element.get("aria-label"):
                        continue
                    
                    field_name = headings[i]
                    if row_field_element.get("aria-label") == "Team":
                        team_rank = str(row_field_element.xpath("./div/span[contains(@class, 'Rank')]/text()")[0])
                        team_name = str(row_field_element.xpath("./div//span[contains(@class, 'VisuallyHidden')]/text()")[0])
                        print('team rank', team_rank)
                        print('team name', team_name)
                        team['Rank'] = team_rank
                        field_content = team_name
                    else:
                        field_content = int(row_field_element.text_content())
                    team[field_name] = field_content
                standings.append(team)
        return standings, last_updated

    def get_standings(self):
        tree = self._get_page_tree()

        all_standings = {}
        last_updated_times = {}
        for element in tree.xpath("//section[@role='tabpanel']"):
            league_id = element.get("id")
            print(league_id)
            standings, last_updated = self._get_league_standings(element)
            all_standings[league_id] = standings
            last_updated_times[league_id] = last_updated
        return all_standings, last_updated_times


def update_league_database():
    scraper = Scraper()
    status = dict(errors=[], status='success')
    try:
        standings, last_updated_times = scraper.get_standings()
    except ScrapeError:
        logging.exception('failed to scrape!')
        status['status'] = 'failed'
        return status
    for league_slug, league_standings in standings.items():
        try:
            matching_league = SportsLeague.objects.get(bbc_name_slug=league_slug)
        except Exception:
            status['errors'].append(f'no SportsLeague with bbc slug: {league_slug}')
            continue

        if not matching_league.active:
            logging.info(f'skipping inactive league during scrape: {league_slug}')
            continue

        for team_standings in league_standings:
            team_name = team_standings.get('Team')
            team_points = team_standings.get('Points')
            team_rank = team_standings.get('Rank')
            team, _ = Team.objects.get_or_create(name=team_name)
            logging.info('got team and league: ', team, matching_league)
            team_standing, _ = TeamStanding.objects.get_or_create(team=team, league=matching_league)
            logging.info('got standing: ', team_standing)
            team_standing.points = team_points
            team_standing.rank = team_rank
            team_standing.save()
        matching_league.last_updated = last_updated_times.get(league_slug, matching_league.last_updated)
        matching_league.save()
    return status

def get_database_update_times():
    last_updated = {}
    for league in SportsLeague.objects.all():
        last_updated[league.name] = league.last_updated
    return last_updated

if __name__ == '__main__':
    update_league_database()