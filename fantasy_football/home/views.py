import logging
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.contrib import messages

from .models import FFLeague
from .scraper import update_league_database, get_database_update_times

class FFTemplateView(TemplateView):

    def get_context_data(self, **kwargs):
        last_updated_times = {}
        try:
            last_updated_times.update(get_database_update_times())
        except Exception:
            logging.exception('failed to get database update times')
        
        context = super().get_context_data(
            **kwargs,
            ff_leagues=FFLeague.objects.all(),
            database_update_times=last_updated_times,
        )
        return context


class HomeView(FFTemplateView):
    template_name = "home/index.html"


class ScrapeView(RedirectView):

    def get(self, *args, **kwargs):
        logging.info('scraping requested...')
        try:
            res = update_league_database()
            messages.info(self.request, f"database update status: {res}", extra_tags='refresh')
        except Exception as e:
            logging.exception('failed to update database with exception')
            messages.error(self.request, f'failed to update database with exception: {e}')
        return super().get(*args, **kwargs)