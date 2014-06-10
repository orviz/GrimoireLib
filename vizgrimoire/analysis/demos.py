#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2014 Bitergia
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#       Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
#
# Demography analysis. Age of developers in the project, age of
# developers still with activity, and so on.

from analyses import Analyses
from scm import PeriodCondition, NomergesCondition
from demography import ActivityPersons, DurationPersons
from datetime import datetime

class Demography(Analyses):

    id = "demography"
    name = "Demography"
    desc = "Age of developers in project"

    def __get_sql__(self):
   
        raise NotImplementedError


    def result(self):

        database = 'mysql://' + self.db.user + ':' + \
            self.db.password + '@' + self.db.host + '/' + \
            self.db.database
        print self.filters.period
        print self.filters.startdate
        print self.filters.enddate
        print self.filters.type_analysis
        print self.filters.npeople
        startdate = datetime.strptime(self.filters.startdate, "'%Y-%m-%d'")
        enddate = datetime.strptime(self.filters.enddate, "'%Y-%m-%d'")
        print startdate
        print enddate
        period = PeriodCondition (start = datetime(2014,1,1), end = None)
        nomerges = NomergesCondition()

        data = ActivityPersons (
            database = database,
            var = "list_authors",
            conditions = (period,nomerges))
        age = DurationPersons (var = "age",
                               activity = data.activity())
        return age.durations().json()


if __name__ == '__main__':

    from query_builder import DSQuery
    from metrics_filter import MetricFilters

    filters = MetricFilters("week", "'2013-06-01'", "'2014-01-01'",
                            ["repository", "'nova.git'"])
    dbcon = DSQuery(user = "jgb", password = "XXX", 
                    database = "openstack_cvsanaly_2014-06-06",
                    identities_db = "openstack_cvsanaly_2014-06-06")
    dem = Demography(dbcon, filters)
    print dem.result()

