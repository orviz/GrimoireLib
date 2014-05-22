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

""" Authors metric for the source code management system """

import logging
import MySQLdb

import re, sys

from metrics import Metrics

from GrimoireUtils import completePeriodIds

from metrics_filter import MetricFilters

from query_builder import SCMQuery

class Commits(Metrics):
    """ Commits metric class for source code management systems """

    def __init__(self, dbcon, filters):
        self.db = dbcon
        self.filters = filters
        self.id = "commits"
        self.name = "Commits"
        self.desc = "Changes to the source code"
        self.data_source = "SCM"
        self.sql = ""

    def __get_commits__ (self, evolutionary):
        # This function contains basic parts of the query to count commits.
        # That query is built and results returned.
        query = self.__get_sql__(evolutionary)
        return self.db.ExecuteQuery(query)


    def __get_sql__(self, evolutionary):
        fields = " count(distinct(s.id)) as commits "
        tables = " scmlog s, actions a " + self.db.GetSQLReportFrom(self.filters.type_analysis)
        filters = self.db.GetSQLReportWhere(self.filters.type_analysis, "author") + " and s.id=a.commit_id "

        query = self.db.BuildQuery(self.filters.period, self.filters.startdate, 
                                   self.filters.enddate, " s.date ", fields, 
                                   tables, filters, evolutionary)
        return query
        

    def get_data_source(self):
        return self.data_source

    def get_ts (self):
        # Returns the evolution of commits through the time
        data = self.__get_commits__(True)
        return completePeriodIds(data, self.filters.period, self.filters.startdate, self.filters.enddate)
    
    def get_agg(self):
        return self.__get_commits__(False)        

    def get_list(self):
        #to be implemented
        pass

# Examples of use

filters = MetricFilters("week", "'2010-01-01'", "'2014-01-01'", ["company", "'Red Hat'"])
dbcon = SCMQuery("dic_cvsanaly_openstack_2259", "root", "", "dic_cvsanaly_openstack_2259")
redhat = Commits(dbcon, filters)
print redhat.get_ts()
print redhat.get_agg()
print redhat.get_data_source()
