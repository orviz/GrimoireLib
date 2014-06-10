#!/usr/bin/env python

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
# This file is a part of GrimoireLib
#
# Authors:
#     Alvaro del Castillo <acs@bitergia.com>
#
#

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
import logging
import sys
from Wikimedia import GetCompaniesQuartersSCR, GetPeopleQuartersSCR
from Wikimedia import GetNewSubmitters, GetNewMergers, GetNewAbandoners
from Wikimedia import GetGoneSubmitters, GetGoneMergers, GetGoneAbandoners
from Wikimedia import GetNewSubmittersActivity, GetGoneSubmittersActivity
from Wikimedia import GetPeopleIntakeSQL

import GrimoireUtils, GrimoireSQL
from GrimoireUtils import dataFrame2Dict, createJSON, completePeriodIds
from GrimoireUtils import valRtoPython, getPeriod, checkFloatArray
from report import Report
import SCR
from utils import read_options

def aggData(period, startdate, enddate, idb, destdir):
    agg = SCR.SCR.get_agg_data (period, startdate, enddate, idb)
    createJSON(agg, destdir+"/scr-static.json")

def tsData(period, startdate, enddate, idb, destdir, granularity, conf):
    evol = SCR.SCR.get_evolutionary_data (period, startdate, enddate, idb)
    createJSON(evol, destdir+"/scr-evolutionary.json")

# Unify top format
def safeTopIds(top_data_period):
    if not isinstance(top_data_period['id'], (list)):
        for name in top_data_period:
            top_data_period[name] = [top_data_period[name]]
    return top_data_period['id']

def peopleData(period, startdate, enddate, idb, destdir, top_data):
    top = safeTopIds(top_data['reviewers'])
    top += safeTopIds(top_data['reviewers.last year'])
    top += safeTopIds(top_data['reviewers.last month'])
    top += safeTopIds(top_data['openers.'])
    top += safeTopIds(top_data['openers.last year'])
    top += safeTopIds(top_data['openers.last_month'])
    top += safeTopIds(top_data['mergers.'])
    top += safeTopIds(top_data['mergers.last year'])
    top += safeTopIds(top_data['mergers.last_month'])
    # remove duplicates
    people = list(set(top)) 
    createJSON(people, destdir+"/scr-people.json")

    for upeople_id in people:
        evol = SCR.GetPeopleEvolSCR(upeople_id, period, startdate, enddate)
        evol = completePeriodIds(evol, period, startdate, enddate)
        createJSON(evol, destdir+"/people-"+str(upeople_id)+"-scr-evolutionary.json")

        agg = SCR.GetPeopleStaticSCR(upeople_id, startdate, enddate)
        createJSON(agg, destdir+"/people-"+str(upeople_id)+"-scr-static.json")

def reposData(period, startdate, enddate, idb, destdir, conf):
    filter_ = Report.get_filter("repository")
    SCR.SCR.create_filter_report(filter_, period, startdate, enddate, destdir, None, idb, [])

def companiesData(period, startdate, enddate, idb, destdir):
    filter_ = Report.get_filter("company")
    SCR.SCR.create_filter_report(filter_, period, startdate, enddate, destdir, None, idb, [])

def countriesData(period, startdate, enddate, idb, destdir):
    filter_ = Report.get_filter("country")
    SCR.SCR.create_filter_report(filter_, period, startdate, enddate, destdir, None, idb, [])

def topData(period, startdate, enddate, idb, destdir, bots, npeople):
    top_reviewers = {}
    top_reviewers['reviewers'] = SCR.GetTopReviewersSCR(0, startdate, enddate, idb, bots, npeople)
    top_reviewers['reviewers.last year']= SCR.GetTopReviewersSCR(365, startdate, enddate, idb, bots, npeople)
    top_reviewers['reviewers.last month']= SCR.GetTopReviewersSCR(31, startdate, enddate, idb, bots, npeople)

    # Top openers
    top_openers = {}
    top_openers['openers.']=SCR.GetTopOpenersSCR(0, startdate, enddate,idb, bots, npeople)
    top_openers['openers.last year']=SCR.GetTopOpenersSCR(365, startdate, enddate,idb, bots, npeople)
    top_openers['openers.last_month']=SCR.GetTopOpenersSCR(31, startdate, enddate,idb, bots, npeople)

    # Top mergers
    top_mergers = {}
    top_mergers['mergers.last year']=SCR.GetTopMergersSCR(365, startdate, enddate,idb, bots, npeople)
    top_mergers['mergers.']=SCR.GetTopMergersSCR(0, startdate, enddate,idb, bots, npeople)
    top_mergers['mergers.last_month']=SCR.GetTopMergersSCR(31, startdate, enddate,idb, bots, npeople)

    # The order of the list item change so we can not check it
    top_all = dict(top_reviewers.items() +  top_openers.items() + top_mergers.items())
    createJSON (top_all, destdir+"/scr-top.json")

    return (top_all)

def quartersData(period, startdate, enddate, idb, destdir, bots):
    # Needed files. Ugly hack for date format
    people = SCR.GetPeopleListSCR("'"+startdate+"'", "'"+enddate+"'", bots)
    createJSON(people, destdir+"/scr-people-all.json", False)
    companies = SCR.GetCompaniesSCRName("'"+startdate+"'", "'"+enddate+"'", idb)
    createJSON(companies, destdir+"/scr-companies-all.json", False)

    start = datetime.strptime(startdate, "%Y-%m-%d")
    start_quarter = (start.month-1)%3 + 1
    end = datetime.strptime(enddate, "%Y-%m-%d")
    end_quarter = (end.month-1)%3 + 1

    companies_quarters = {}
    people_quarters = {}

    quarters = (end.year - start.year) * 4 + (end_quarter - start_quarter)

    for i in range(0, quarters):
        year = start.year
        quarter = (i%4)+1
        # logging.info("Analyzing companies and people quarter " + str(year) + " " +  str(quarter))
        data = GetCompaniesQuartersSCR(year, quarter, idb)
        companies_quarters[str(year)+" "+str(quarter)] = data
        data_people = GetPeopleQuartersSCR(year, quarter, idb, 25, bots)
        people_quarters[str(year)+" "+str(quarter)] = data_people
        start = start + relativedelta(months=3)
    createJSON(companies_quarters, destdir+"/scr-companies-quarters.json")
    createJSON(people_quarters, destdir+"/scr-people-quarters.json")

def CodeContribKPI(destdir):
    code_contrib = {}
    code_contrib["submitters"] = GetNewSubmitters()
    code_contrib["mergers"] = GetNewMergers()
    code_contrib["abandoners"] = GetNewAbandoners()
    createJSON(code_contrib, destdir+"/scr-code-contrib-new.json")

    code_contrib = {}
    code_contrib["submitters"] = GetGoneSubmitters()
    code_contrib["mergers"] = GetGoneMergers()
    code_contrib["abandoners"] = GetGoneAbandoners()
    createJSON(code_contrib, destdir+"/scr-code-contrib-gone.json")


    data = GetNewSubmittersActivity()
    evol = {}
    evol['people'] = {}
    for upeople_id in data['upeople_id']:
        pdata = SCR.GetPeopleEvolSubmissionsSCR(upeople_id, period, startdate, enddate)
        pdata = completePeriodIds(pdata, period, startdate, enddate)
        evol['people'][upeople_id] = {"submissions":pdata['submissions']}
        # Just to have the time series data
        evol = dict(evol.items() + pdata.items())
    if 'changes' in evol:
        del evol['changes'] # closed (metrics) is included in people
    createJSON(evol, destdir+"/new-people-activity-scr-evolutionary.json")

    data = GetGoneSubmittersActivity()
    evol = {}
    evol['people'] = {}
    for upeople_id in data['upeople_id']:
        pdata = SCR.GetPeopleEvolSubmissionsSCR(upeople_id, period, startdate, enddate)
        pdata = completePeriodIds(pdata, period, startdate, enddate)
        evol['people'][upeople_id] = {"submissions":pdata['submissions']}
        # Just to have the time series data
        evol = dict(evol.items() + pdata.items())
    if 'changes' in evol:
        del evol['changes'] # closed (metrics) is included in people
    createJSON(evol, destdir+"/gone-people-activity-scr-evolutionary.json")

    # data = GetPeopleLeaving()
    # createJSON(data, destdir+"/leaving-people-scr.json")

    evol = {}
    data = completePeriodIds(GetPeopleIntakeSQL(0,1), period, startdate, enddate)
    evol['month'] = data['month']
    evol['id'] = data['id']
    evol['date'] = data['date']
    evol['num_people_1'] = data['people']
    evol['num_people_1_5'] = completePeriodIds(GetPeopleIntakeSQL(1,5),period, startdate, enddate)['people']
    evol['num_people_5_10'] = completePeriodIds(GetPeopleIntakeSQL(5,10), period, startdate, enddate)['people']
    createJSON(evol, destdir+"/scr-people-intake-evolutionary.json")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    logging.info("Starting SCR data source analysis")
    opts = read_options()
    period = getPeriod(opts.granularity)
    reports = opts.reports.split(",")
    # filtered bots


    # bots = ['wikibugs','gerrit-wm','wikibugs_','wm-bot','','Translation updater bot','jenkins-bot','L10n-bot']

    Report.init(opts.config_file, opts.metrics_path)
    # TODO: hack because VizR library needs. Fix in lib in future
    startdate = "'"+opts.startdate+"'"
    enddate = "'"+opts.enddate+"'"

    GrimoireSQL.SetDBChannel (database=opts.dbname, user=opts.dbuser, password=opts.dbpassword)

    tsData (period, startdate, enddate, opts.identities_db, opts.destdir, opts.granularity, opts)
    aggData(period, startdate, enddate, opts.identities_db, opts.destdir, bots)
    quartersData(period, opts.startdate, opts.enddate, opts.identities_db, opts.destdir, bots)
    top = topData(period, startdate, enddate, opts.identities_db, opts.destdir, bots, opts.npeople)

    if ('people' in reports):
        peopleData (period, startdate, enddate, opts.identities_db, opts.destdir, top)
    if ('repositories' in reports):
        reposData (period, startdate, enddate, opts.identities_db, opts.destdir, opts)
    if ('countries' in reports):
        countriesData (period, startdate, enddate, opts.identities_db, opts.destdir)
    if ('companies' in reports):
        companiesData (period, startdate, enddate, opts.identities_db, opts.destdir)

    # Specific Wikiemdia KPI analysis
    CodeContribKPI(opts.destdir)

    logging.info("SCR data source analysis OK")
