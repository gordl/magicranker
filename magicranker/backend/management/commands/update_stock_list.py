from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from magicranker.backend.scrapers import asx, nasdaq_lister
from magicranker.stock.models import Detail

class Command(BaseCommand):
    help = 'Scrape ASX.com.au and get updated list of stocks'

    def _get_exchange_stock_list(self):
        #Get list of symbols, default to asx.
        if settings.STOCK_EXCHANGE == "asx":
            return asx.get_full_stock_list()
        else:
            return nasdaq_lister.get_stock_list(settings.STOCK_EXCHANGE)

    def _get_full_stock_list(self):
        """
        Get the full stock list using the asx module
        and add it to the database
        """
        # Get list of symbols
        stocks = self._get_exchange_stock_list()

        # Get today's date
        today = datetime.today()

        new_count = 0
        update_count = 0

        # Add stock_list to the db if they aren't there already
        if stocks:
            for stock in stocks:
                stock, created = Detail.objects.get_or_create(
                    code=stock, defaults={'is_listed': True})
                if created:
                    new_count += 1
                    stock.first_listed = today
                else:
                    update_count += 1

                stock.is_listed = True
                stock.last_listed = today
                stock.save()
        else:
            return False
            logging.error('Failed to download stock list')

        return new_count, update_count

    def _set_unlisted_companies(self):
        """
        Set companies that haven't been updated in 2 weeks to unlisted
        """
        two_weeks_ago = (datetime.today() - timedelta(weeks=2)).date()
        stocks = Detail.objects.filter(is_listed=True)
        unlisted_count = 0
        for stock in stocks:
            if stock.last_listed <= two_weeks_ago:
                stock.is_listed = False
                unlisted_count += 1
                stock.save()

        return unlisted_count

    def handle(self, *args, **kwargs):
        results = self._get_full_stock_list()

        if results:
            new_count, update_count = results
            unlisted_count = self._set_unlisted_companies()

            message = '{0} new companies\n'.format(new_count)
            message += '{0} updated companies\n'.format(update_count)
            message += '{0} unlisted companies'.format(unlisted_count)
        else:
            message = 'Failed to run\n'
