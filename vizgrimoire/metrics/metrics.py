## Copyright (C) 2014 Bitergia
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details. 
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## This file is a part of GrimoireLib
##  (an Python library for the MetricsGrimoire and vizGrimoire systems)
##
##
## Authors:
##   Daniel Izquierdo-Cortazar <dizquierdo@bitergia.com>


from GrimoireUtils import completePeriodIds, GetDates, GetPercentageDiff
from metrics_filter import MetricFilters

class Metrics(object):

    default_period = "month"
    default_start = "'2010-01-01'"
    default_end = "'2014-01-01'"
    id = None
    name = None
    desc = None
    data_source = None
    domains_limit = 100

    def __init__(self, dbcon = None, filters = None):
        """db connection and filter to be used"""
        self.db = dbcon
        self.filters = filters
        if filters == None:
            self.filters = MetricFilters(Metrics.default_period,
                                         Metrics.default_start, Metrics.default_end, 
                                         None)


    def get_definition(self):
        def_ = {
               "id":self.id,
               "name":self.name,
               "desc":self.desc
        }
        return def_

    def get_data_source(self):
        """ Returns the family of the instance """
        return Metrics.data_source

    def _get_sql(self, evolutionary):
        """ Returns specific sql for the provided filters """
        raise NotImplementedError

    def get_data_source(self):
        return self.data_source

    def get_ts (self):
        """ Returns a time serie of values """
        query = self._get_sql(True)
        ts = self.db.ExecuteQuery(query)
        return completePeriodIds(ts, self.filters.period, 
                                 self.filters.startdate, self.filters.enddate)

    def get_agg(self):
        """ Returns an aggregated value """
        query = self._get_sql(False)
        return self.db.ExecuteQuery(query)

    def get_agg_diff_days(self, date, days):
        """ Returns the trend metrics between now and now-days values """
        # Keeping state of origin filters
        filters = self.filters

        chardates = GetDates(date, days)
        self.filters = MetricFilters(filters.period,
                                     chardates[1], chardates[0], filters.type_analysis)
        last = self.get_agg()
        last = int(last[self.id])
        self.filters = MetricFilters(filters.period,
                                     chardates[2], chardates[1], filters.type_analysis)
        prev = self.get_agg()
        prev = int(prev[self.id])

        data = {}
        data['diff_net'+self.id+'_'+str(days)] = last - prev
        data['percentage_'+self.id+'_'+str(days)] = GetPercentageDiff(prev, last)
        data[self.id+'_'+str(days)] = last

        # Returning filters to their original value
        self.filters = filters
        return (data)

    def _get_top_supported_filters(self):
        return []

    def _get_top_global(self, days = 0, metric_filters = None):
        return {}

    def _get_top(self, metric_filters = None, days = 0):
        if metric_filters.type_analysis and metric_filters.type_analysis is not None:
            if metric_filters.type_analysis[0] not in self._get_top_supported_filters():
                 return
            if metric_filters.type_analysis[0] == "repository":
                alist = self._get_top_repository(metric_filters)
            if metric_filters.type_analysis[0] == "company":
                alist = self._get_top_company(metric_filters)
            if metric_filters.type_analysis[0] == "country":
                alist = self._get_top_country(metric_filters)
            if metric_filters.type_analysis[0] == "domain":
                alist = self._get_top_domain(metric_filters)
            if metric_filters.type_analysis[0] == "project":
                alist = self._get_top_project(metric_filters)
        else:
            alist = self._get_top_global(days, metric_filters)
        return alist

    def get_list(self, metric_filters = None, days = 0):
        """ Returns a list of items. Mainly used for tops. """
        mlist = {}

        if metric_filters is not None:
            metric_filters_orig = self.filters
            self.filters = metric_filters

        mlist = self._get_top(self.filters, days)

        if metric_filters is not None: self.filters = metric_filters_orig

        return mlist

    def get_bots_filter_sql (self, metric_filters = None):
        bots = self.data_source.get_bots()
        if metric_filters is not None:
            if metric_filters.people_out is not None:
                bots = metric_filters.people_out
        filter_bots = ''
        for bot in bots:
            filter_bots = filter_bots + " u.identifier<>'"+bot+"' AND "
        if filter_bots != '': filter_bots = filter_bots[:-4]
        return filter_bots
