## Copyright (C) 2012, 2013 Bitergia
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
## This file is a part of the vizGrimoire R package
##  (an R library for the MetricsGrimoire and vizGrimoire systems)
##
## ITS.R
##
## Queries for ITS data analysis
##
## Authors:
##   Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
##   Daniel Izquierdo <dizquierdo@bitergia.com>
##   Alvaro del Castillo <acs@bitergia.com>
##   Luis Cañas-Díaz <lcanas@bitergia.com>

from GrimoireSQL import GetSQLGlobal, GetSQLPeriod, GetSQLReportFrom
from GrimoireSQL import GetSQLReportWhere, ExecuteQuery, BuildQuery
from GrimoireUtils import GetPercentageDiff, GetDates, completePeriodIds
import GrimoireUtils

##############
# Specific FROM and WHERE clauses per type of report
##############

def GetITSSQLRepositoriesFrom ():
    # tables necessary for repositories 
    return (", trackers t")

def GetITSSQLRepositoriesWhere (repository):
    # fields necessary to match info among tables
    return (" i.tracker_id = t.id and t.url = "+repository+" ")

def GetITSSQLCompaniesFrom (i_db):
    # fields necessary for the companies analysis

    return(" , people_upeople pup,
                   ",i_db,".companies c,
                   ",i_db,".upeople_companies upc", sep=""))
def GetITSSQLCompaniesWhere (name):
    # filters for the companies analysis
    return(" i.submitted_by = pup.people_id and
                   pup.upeople_id = upc.upeople_id and
                   upc.company_id = c.id and
                   i.submitted_on >= upc.init and
                   i.submitted_on < upc.end and
                   c.name = ",name, sep=""))

def GetITSSQLCountriesFrom (i_db):
    # fields necessary for the countries analysis

    return(" , people_upeople pup,
                   ",i_db,".countries c,
                   ",i_db,".upeople_countries upc", sep=""))

def GetITSSQLCountriesWhere (name):
    # filters for the countries analysis
    return(" i.submitted_by = pup.people_id and
                   pup.upeople_id = upc.upeople_id and
                   upc.country_id = c.id and
                   c.name = ",name, sep=""))


def GetITSSQLDomainsFrom (i_db):
    # fields necessary for the domains analysis

    return(" , people_upeople pup,
                   ",i_db,".domains d,
                   ",i_db,".upeople_domains upd", sep=""))


def GetITSSQLDomainsWhere (name):
    # filters for the domains analysis
    return(" i.submitted_by = pup.people_id and
                   pup.upeople_id = upd.upeople_id and
                   upd.domain_id = d.id and
                   d.name = ",name, sep=""))

##########
#Generic functions to obtain FROM and WHERE clauses per type of report
##########

def GetITSSQLReportFrom (identities_db, type_analysis):
    #generic function to generate 'from' clauses
    #"type" is a list of two values: type of analysis and value of 
    #such analysis

    analysis = type_analysis[1]
    value = type_analysis[2]

    from = ""

    if (! is.na(analysis)):
        from = ifelse (analysis == 'repository', from, GetITSSQLRepositoriesFrom()),
                ifelse (analysis == 'company', from, GetITSSQLCompaniesFrom(identities_db)),
                ifelse (analysis == 'country', from, GetITSSQLCountriesFrom(identities_db)),
                ifelse (analysis == 'domain', from, GetITSSQLDomainsFrom(identities_db)),
                NA))))
    return (from)



def GetITSSQLReportWhere (type_analysis):
    #generic function to generate 'where' clauses

    #"type" is a list of two values: type of analysis and value of 
    #such analysis
    analysis = type_analysis[1]
    value = type_analysis[2]
    where = ""

    if (! is.na(analysis)):
        where = ifelse (analysis == 'repository', where, GetITSSQLRepositoriesWhere(value)),
                ifelse (analysis == 'company', where, GetITSSQLCompaniesWhere(value)),
                ifelse (analysis == 'country', where, GetITSSQLCountriesWhere(value)),
                ifelse (analysis == 'domain', where, GetITSSQLDomainsWhere(value)),
                NA))))
    return (where)


##########
# Meta functions to retrieve data
##########

def GetITSInfo (period, startdate, enddate, identities_db, type_analysis, closed_condition, evolutionary):
    # Meta function to aggregate all of the evolutionary or
    # aggregated functions

    data = data.frame()

    if (evolutionary):
        closed = EvolIssuesClosed(period, startdate, enddate, identities_db, type_analysis, closed_condition)
        closers = EvolIssuesClosers(period, startdate, enddate, identities_db, type_analysis, closed_condition)
        changed = EvolIssuesChanged(period, startdate, enddate, identities_db, type_analysis)
        changers = EvolIssuesChangers(period, startdate, enddate, identities_db, type_analysis)
        open = EvolIssuesOpened(period, startdate, enddate, identities_db, type_analysis)
        openers = EvolIssuesOpeners(period, startdate, enddate, identities_db, type_analysis)
        repos = EvolIssuesRepositories(period, startdate, enddate, identities_db, type_analysis)

        data = merge(closed, changed, all = TRUE)
        data = merge(data, open, all = TRUE)
        data = merge(data, repos, all = TRUE)
        data = merge(data, openers, all = TRUE)
        data = merge(data, closers, all = TRUE)
        data = merge(data, changers, all = TRUE)
     else :
        closed = AggIssuesClosed(period, startdate, enddate, identities_db, type_analysis, closed_condition)
        closers = AggIssuesClosers(period, startdate, enddate, identities_db, type_analysis, closed_condition)
        changed = AggIssuesChanged(period, startdate, enddate, identities_db, type_analysis)
        changers = AggIssuesChangers(period, startdate, enddate, identities_db, type_analysis)
        open = AggIssuesOpened(period, startdate, enddate, identities_db, type_analysis)
        openers = AggIssuesOpeners(period, startdate, enddate, identities_db, type_analysis)
        repos = AggIssuesRepositories(period, startdate, enddate, identities_db, type_analysis)
        init_date = GetInitDate(startdate, enddate, identities_db, type_analysis)
        end_date = GetEndDate(startdate, enddate, identities_db, type_analysis)
        data = merge(closed, changed)
        data = merge(data, open)
        data = merge(data, repos)
        data = merge(data, openers)
        data = merge(data, closers)
        data = merge(data, changers)
        data = merge(data, init_date)
        data = merge(data, end_date)

    return(data)


def EvolITSInfo (period, startdate, enddate, identities_db, type_analysis = list(NA, NA), closed_condition):
    #Evolutionary info all merged in a dataframe
    return(GetITSInfo(period, startdate, enddate, identities_db, type_analysis, closed_condition, TRUE))



def AggITSInfo (period, startdate, enddate, identities_db, type_analysis = list(NA, NA), closed_condition):
    #Agg info all merged in a dataframe
    return(GetITSInfo(period, startdate, enddate, identities_db, type_analysis, closed_condition, FALSE))

#########
#Functions to obtain info per type of basic piece of data
#########

# All of the EvolXXX or StaticXXX contains the same parameters:
#    period:
#    startdate:
#    enddate:
#    identities_db: MySQL database name
#    type_analysis: tuple with two values: typeof and value
#                   typeof = 'companies', 'countries', 'repositories' or ''
#                   value = any value that corresponds with the type of analysis


# Generic functions to calculate the evolution of the backlog for a given
# status or set of statuses. This is based on the analysis of the 
# issues_log_xxxx table

def BuildWeekDate (date):
   return(getISOWEEKYear(date), getISOWEEKWeek(date), sep=""))


def GetEvolBacklogTickets (period, startdate, enddate, statuses, name.logtable, filter="") :
    # Return backlog of tickets in the statuses passed as parameter
    q = "SELECT DISTINCT issue_id, status, date FROM ",name.logtable," ", filter ," ORDER BY date ASC")
    query = new("Query", sql = q)
    res = run(query)

    pending.tickets = data.frame()
    start = as.POSIXlt(gsub("'", "", startdate))
    end = as.POSIXlt(gsub("'", "", enddate))

    if (period == "month") :
        samples = GetMonthsBetween(start, end, extra=TRUE)
        pending.tickets = CountBacklogTickets(samples, res, statuses)
        colnames(pending.tickets) = c('month', 'pending_tickets')
        posixdates = as.POSIXlt(as.numeric(pending.tickets$month), origin="1970-01-01")
        dates = as.Date(posixdates)
        dates = as.numeric(format(dates, "%Y"))*12 + as.numeric(format(dates, "%m"))
        pending.tickets$month = dates

    else if (period == "week"):
        samples = GetWeeksBetween(start, end, extra=TRUE)
        pending.tickets = CountBacklogTickets(samples, res, statuses)
        colnames(pending.tickets) = c('week', 'pending_tickets')
        posixdates = as.POSIXlt(as.numeric(pending.tickets$week), origin="1970-01-01")
        dates = as.Date(posixdates)
        #It's needed in this case to call a function to build the correct
        #yearweek value according to how this is done in MySQL
        dates = lapply(dates, BuildWeekDate)
        dates = as.numeric(dates)
        pending.tickets$week = dates

    return(pending.tickets)



def CountBacklogTickets (samples, res, statuses):
    # return number of tickets in status = statuses per period of time
    #
    # Warning: heavy algorithm, it could be improved if the backlog is
    # calculated backwards and the data is reduced in every iteration
    #
    # Fixme: it is needed to check if there are more that a status for
    # an issue at the same time
    #
    backlog_tickets = data.frame()
    periods = length(samples$unixtime)
    for (p in (1:periods)):

        if ( p == periods):
            break

        date_unixtime = samples$unixtime[p]
        next_unixtime_str = samples$unixtime[p+1]

        next_date = as.POSIXlt(as.numeric(next_unixtime_str), origin="1970-01-01")
        #print("[" , date() , "] date_unixtime = ",date_unixtime, " next_date = ", next_date)) # debug mode?

        resfilter = subset(res,res$date < next_date)

        if (nrow(resfilter) > 0):
            maxs = aggregate(date ~ issue_id, data = resfilter, FUN = max)
            resultado = merge(maxs, resfilter)
            # filtering by status
            total = 0
            for (s in statuses):
                aux = nrow(subset(resultado, resultado$status==s))
                total = aux + total

            ## print("[" , date() , "] backlog tickets:", total)) # debug mode?
        else:
            total = 0

        aux_df = data.frame(month=date_unixtime, backlog_tickets = total)
        if (nrow(backlog_tickets)):
            backlog_tickets = merge(backlog_tickets,aux_df, all=TRUE)
        else:
            backlog_tickets = aux_df

    return(backlog_tickets)




# Generic function to obtain the current photo of a given issue
# This is based on the field "status" from the issues table

def GetCurrentStatus (period, startdate, enddate, identities_db, status):
    # This functions provides  of the status specified by 'status'
    # group by submitted date. Thus, as an example, for those issues 
    # in status = open, it is possible to know when they were submitted

    fields = " count(distinct(id)) as current_", status, sep="")
    tables = " issues ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")
    filters = " status = '", status, "' and ", GetITSSQLReportWhere(type_analysis) , sep="")
    q = GetSQLPeriod(period,'submitted_on', fields, tables, filters,
            startdate, enddate)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


#TODO: check the differences between function GetCurrentOpened and GetEvolClosed,
# GetEvolOpened, etc... in some cases such as opened, openers, closed, closers, 
# changed and changers is more than enough to just count changes in table changes
# opened when the issue was submitted (and submitted by) and closers providing the
# closed condition. Do we get whe same results if using the Backlog table?

def GetOpened (period, startdate, enddate, identities_db, type_analysis, evolutionary):
    #This function returns the evolution or agg number of opened issues
    #This function can be also reproduced using the Backlog function.
    #However this function is less time expensive.
    fields = " count(distinct(i.id)) as opened "
    tables = " issues i ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")
    filters = GetITSSQLReportWhere(type_analysis) 
    q = BuildQuery(period, startdate, enddate, " submitted_on ", fields, tables, filters, evolutionary)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


def AggIssuesOpened (period, startdate, enddate, identities_db, type_analysis):
    # Returns aggregated number of opened issues
    return(GetOpened(period, startdate, enddate, identities_db, type_analysis, FALSE))



def EvolIssuesOpened (period, startdate, enddate, identities_db, type_analysis):
    #return(GetEvolBacklogTickets(period, startdate, enddate, status, name.logtable, filter))
    return(GetOpened(period, startdate, enddate, identities_db, type_analysis, TRUE))



def GetOpeners (period, startdate, enddate, identities_db, type_analysis, evolutionary, closed_condition):
    #This function returns the evolution or agg number of people opening issues
    fields = " count(distinct(pup.upeople_id)) as openers "
    tables = " issues i ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")
    filters = GetITSSQLReportWhere(type_analysis)

    if (is.na(type_analysis[1])) :
        #Specific case for the basic option where people_upeople table is needed
        #and not taken into account in the initial part of the query
        tables = tables, ", people_upeople pup", sep="")
        filters = filters, " and i.submitted_by = pup.people_id", sep="")
    

    if (type_analysis[1] == "repository"):
        #Adding people_upeople table
        tables = tables, ", people_upeople pup", sep="")
        filters = filters, " and i.submitted_by = pup.people_id ", sep="")
    

    q = BuildQuery(period, startdate, enddate, " submitted_on ", fields, tables, filters, evolutionary)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)



def AggIssuesOpeners (period, startdate, enddate, identities_db, type_analysis):
    # Returns aggregated number of opened issues
    return(GetOpeners(period, startdate, enddate, identities_db, type_analysis, FALSE))

def EvolIssuesOpeners (period, startdate, enddate, identities_db, type_analysis):
    #return(GetEvolBacklogTickets(period, startdate, enddate, status, name.logtable, filter))
    return(GetOpeners(period, startdate, enddate, identities_db, type_analysis, TRUE))

def GetClosed (period, startdate, enddate, identities_db, type_analysis, evolutionary, closed_condition):
    #This function returns the evolution or agg number of closed issues
    #This function can be also reproduced using the Backlog function.
    #However this function is less time expensive.
    fields = " count(distinct(i.id)) as closed "
    tables = " issues i, changes ch ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")

    filters = " i.id = ch.issue_id and ", closed_condition, sep="") 
    filters_ext = GetITSSQLReportWhere(type_analysis)
    if (filters_ext != ""):
        filters = filters, " and ", filters_ext, sep="")
    
 
    #Action needed to replace issues filters by changes one
    filters = gsub("i.submitted", "ch.changed", filters)
    
    q = BuildQuery(period, startdate, enddate, " ch.changed_on ", fields, tables, filters, evolutionary)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)

def AggIssuesClosed (period, startdate, enddate, identities_db, type_analysis, closed_condition):
    # Returns aggregated number of closed issues
    return(GetClosed(period, startdate, enddate, identities_db, type_analysis, FALSE, closed_condition))

def EvolIssuesClosed (period, startdate, enddate, identities_db, type_analysis, closed_condition):
    #return(GetEvolBacklogTickets(period, startdate, enddate, status, name.logtable, filter))
    return(GetClosed(period, startdate, enddate, identities_db, type_analysis, TRUE, closed_condition))

def GetClosers (period, startdate, enddate, identities_db, type_analysis, evolutionary, closed_condition):
    #This function returns the evolution or agg number of closed issues
    #This function can be also reproduced using the Backlog function.
    #However this function is less time expensive.
    fields = " count(distinct(pup.upeople_id)) as closers "
    tables = " issues i, changes ch ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")

    #closed condition filters
    filters = " i.id = ch.issue_id and ", closed_condition, sep="")
    filters_ext = GetITSSQLReportWhere(type_analysis)
    if (filters_ext != ""):
        filters = filters, " and ", filters_ext, sep="")
    
 
    #unique identities filters
    if (is.na(type_analysis[1])) :
        #Specific case for the basic option where people_upeople table is needed
        #and not taken into account in the initial part of the query
        tables = tables, ", people_upeople pup", sep="")
        filters = filters, " and i.submitted_by = pup.people_id", sep="")
    

    if (type_analysis[1] == "repository"):
        #Adding people_upeople table
        tables = tables, ", people_upeople pup", sep="")
        filters = filters, " and i.submitted_by = pup.people_id ", sep="")
    

    #Action needed to replace issues filters by changes one
    filters = gsub("i.submitted", "ch.changed", filters)


    q = BuildQuery(period, startdate, enddate, " ch.changed_on ", fields, tables, filters, evolutionary)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


def AggIssuesClosers (period, startdate, enddate, identities_db, type_analysis, closed_condition):
    # Returns aggregated number of closed issues
    return(GetClosers(period, startdate, enddate, identities_db, type_analysis, FALSE, closed_condition))



def EvolIssuesClosers (period, startdate, enddate, identities_db, type_analysis, closed_condition):
    #return(GetEvolBacklogTickets(period, startdate, enddate, status, name.logtable, filter))
    return(GetClosers(period, startdate, enddate, identities_db, type_analysis, TRUE, closed_condition))

def GetChanged (period, startdate, enddate, identities_db, type_analysis, evolutionary):
    #This function returns the evolution or agg number of changed issues
    #This function can be also reproduced using the Backlog function.
    #However this function is less time expensive.
    fields = " count(distinct(ch.issue_id)) as changed "
    tables = " issues i, changes ch ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")

    filters = " i.id = ch.issue_id "
    filters_ext = GetITSSQLReportWhere(type_analysis)
    if (filters_ext != ""):
        filters = filters, " and ", filters_ext, sep="")
    

    #Action needed to replace issues filters by changes one
    filters = gsub("i.submitted", "ch.changed", filters)

    q = BuildQuery(period, startdate, enddate, " ch.changed_on ", fields, tables, filters, evolutionary)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


def AggIssuesChanged (period, startdate, enddate, identities_db, type_analysis):
    # Returns aggregated number of closed issues
    return(GetChanged(period, startdate, enddate, identities_db, type_analysis, FALSE))

def EvolIssuesChanged (period, startdate, enddate, identities_db, type_analysis):
    return(GetChanged(period, startdate, enddate, identities_db, type_analysis, TRUE))


def GetChangers (period, startdate, enddate, identities_db, type_analysis, evolutionary):
    #This function returns the evolution or agg number of changed issues
    #This function can be also reproduced using the Backlog function.
    #However this function is less time expensive.
    fields = " count(distinct(pup.upeople_id)) as changers "
    tables = " issues i, changes ch ", GetITSSQLReportFrom(identities_db, type_analysis), sep="")

    filters = " i.id = ch.issue_id "
    filters_ext = GetITSSQLReportWhere(type_analysis)
    if (filters_ext != ""):
        filters = filters, " and ", filters_ext, sep="")

    #unique identities filters
    if (is.na(type_analysis[1])) :
        #Specific case for the basic option where people_upeople table is needed
        #and not taken into account in the initial part of the query
        tables = tables, ", people_upeople pup", sep="")
        filters = filters, " and i.submitted_by = pup.people_id", sep="")

    if (type_analysis[1] == "repository"):
        #Adding people_upeople table
        tables = tables, ", people_upeople pup", sep="")
        filters = filters, " and i.submitted_by = pup.people_id ", sep="")

    #Action needed to replace issues filters by changes one
    filters = gsub("i.submitted", "ch.changed", filters)

    q = BuildQuery(period, startdate, enddate, " ch.changed_on ", fields, tables, filters, evolutionary)
    query = new ("Query", sql = q)
    data = run(query)
    return (data)

def AggIssuesChangers (period, startdate, enddate, identities_db, type_analysis):
    # Returns aggregated number of closed issues
    return(GetChangers(period, startdate, enddate, identities_db, type_analysis, FALSE))

def EvolIssuesChangers (period, startdate, enddate, identities_db, type_analysis):
    return(GetChangers(period, startdate, enddate, identities_db, type_analysis, TRUE))

# Repositories
def GetIssuesRepositories (period, startdate, enddate, identities_db, type_analysis, evolutionary):
    # Generic function that counts repositories

    fields = " COUNT(DISTINCT(tracker_id)) AS trackers  ", sep="")
    tables = " issues i ", GetITSSQLReportFrom(identities_db, type_analysis))
    filters = GetITSSQLReportWhere(type_analysis)

    q = BuildQuery(period, startdate, enddate, " i.submitted_on ", fields, tables, filters, evolutionary)
    return(ExecuteQuery(q))

def EvolIssuesRepositories (period, startdate, enddate, identities_db, type_analysis = list(NA, NA)):
    # Evolution of trackers
    return(GetIssuesRepositories(period, startdate, enddate, identities_db, type_analysis, TRUE))

def AggIssuesRepositories (period, startdate, enddate, identities_db, type_analysis = list(NA, NA)):
    # Evolution of trackers
    return(GetIssuesRepositories(period, startdate, enddate, identities_db, type_analysis, FALSE))

def GetIssuesStudies (period, startdate, enddate, identities_db, type_analysis, evolutionary, study):
    # Generic function that counts evolution/agg number of specific studies with similar
    # database schema such as domains, companies and countries
    fields = ' count(distinct(name)) as ', study, sep="")
    tables = " issues i ", GetITSSQLReportFrom(identities_db, type_analysis))
    filters = GetITSSQLReportWhere(type_analysis)

    #Filtering last part of the query, not used in this case
    #filters = gsub("and\n( )+(d|c|cou|com).name =.*$", "", filters)
    
    q = BuildQuery(period, startdate, enddate, " i.submitted_on ", fields, tables, filters, evolutionary)
    q = gsub("and[[:space:]]*(d|c|cou|com).name[[:space:]]*=[[:space:]]*('.*'|NA)", "", q)
    data = ExecuteQuery(q)
    return(data)

def EvolIssuesDomains (period, startdate, enddate, identities_db):
    # Evol number of domains used
    return(GetIssuesStudies(period, startdate, enddate, identities_db, list('domain', NA), TRUE, 'domains'))

def EvolIssuesCountries (period, startdate, enddate, identities_db):
    # Evol number of countries
    return(GetIssuesStudies(period, startdate, enddate, identities_db, list('country', NA), TRUE, 'countries'))

def EvolIssuesCompanies (period, startdate, enddate, identities_db):
    # Evol number of companies
    data = GetIssuesStudies(period, startdate, enddate, identities_db, list('company', NA), TRUE, 'companies')
    return(data)

def AggIssuesDomains (period, startdate, enddate, identities_db):
    # Agg number of domains
    return(GetIssuesStudies(period, startdate, enddate, identities_db, list('domain', NA), FALSE, 'domains'))

def AggIssuesCountries (period, startdate, enddate, identities_db):
    # Agg number of countries
    return(GetIssuesStudies(period, startdate, enddate, identities_db, list('country', NA), FALSE, 'countries'))

def AggIssuesCompanies (period, startdate, enddate, identities_db):
    # Agg number of companies
    return(GetIssuesStudies(period, startdate, enddate, identities_db, list('company', NA), FALSE, 'companies'))

def GetDate (startdate, enddate, identities_db, type_analysis=list(NA, NA), type):
    # date of submmitted issues (type= max or min)
    if (type=="max"):
        fields = " DATE_FORMAT (max(submitted_on), '%Y-%m-%d') as last_date", sep="")
     else :
        fields = " DATE_FORMAT (min(submitted_on), '%Y-%m-%d') as first_date", sep="")

    tables = " issues i ", GetITSSQLReportFrom(identities_db, type_analysis))
    filters = GetITSSQLReportWhere(type_analysis)

    q = BuildQuery(NA, startdate, enddate, " i.submitted_on ", fields, tables, filters, "FALSE") 
    data = ExecuteQuery(q)
    return(data)    

def GetInitDate (startdate, enddate, identities_db, type_analysis):
    #Initial date of submitted issues
    return(GetDate(startdate, enddate, identities_db, type_analysis, "min"))

def GetEndDate (startdate, enddate, identities_db, type_analysis):
    #End date of submitted issues
    return(GetDate(startdate, enddate, identities_db, type_analysis, "max"))

###############
# Others
###############

def AggAllParticipants (startdate, enddate):
    # All participants from the whole history
    q = "SELECT count(distinct(pup.upeople_id)) as allhistory_participants from people_upeople pup"
    query = new("Query", sql = q)
    return(run(query))


def TrackerURL ():
    # URL of the analyzed tracker
    q = paste ("SELECT url, name as type FROM trackers t JOIN 
                 supported_trackers s ON t.type = s.id limit 1")
    query = new ("Query", sql = q)
    return(run(query))

###############
# Lists of repositories, companies, countries and other analysis
###############

def GetReposNameITS (startdate, enddate) :
    # List the url of each of the repositories analyzed
    # Those are order by the number of opened issues (dec order)
    q = paste (" SELECT t.url as name
                  FROM issues i, 
                       trackers t
                  WHERE i.tracker_id=t.id and
                        i.submitted_on >= ", startdate, " and
                        i.submitted_on < ", enddate, "
                  GROUP BY t.url 
                  ORDER BY count(distinct(i.id)) DESC ", sep="")
    query = new ("Query", sql = q)
    data = run(query)
    return (data)

def GetTablesDomainsITS (i_db, table='') :
    tables = GetTablesOwnUniqueIdsITS(table)
    tables = tables,',',i_db,'.upeople_domains upd',sep='')

def GetFiltersDomainsITS (table='') :
    filters = GetFiltersOwnUniqueIdsITS(table)
    filters = filters,"AND pup.upeople_id = upd.upeople_id")

def GetDomainsNameITS (startdate, enddate, identities_db, closed_condition, filter=c()) :
    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " dom.name<>'",aff,"' and ",sep="")

    tables = GetTablesDomainsITS(identities_db)
    tables = tables,",",identities_db,".domains dom")

    q = paste ("SELECT dom.name
                 FROM ", tables, "
                 WHERE ", GetFiltersDomainsITS()," AND
                       dom.id = upd.domain_id and
                       ",affiliations,"
                       c.changed_on >= ", startdate, " AND
                       c.changed_on < ", enddate, " AND
                       ", closed_condition,"
                 GROUP BY dom.name
                 ORDER BY COUNT(DISTINCT(c.issue_id)) DESC", sep="")
    query = new("Query", sql = q)
    data = run(query)
    return (data)

def GetCountriesNamesITS (startdate, enddate, identities_db, closed_condition) :
    # List each of the countries analyzed
    # Those are order by number of closed issues
    q = "select cou.name
                    from issues i, 
                         changes ch,
                         people_upeople pup,
                         ", identities_db, ".upeople_countries upc,
                         ", identities_db, ".countries cou
                    where i.id = ch.issue_id and
                          ch.changed_by = pup.people_id and
                          pup.upeople_id = upc.upeople_id and
                          upc.country_id = cou.id and
                          ch.changed_on >= ", startdate, " and
                          ch.changed_on < ", enddate," and
                          ", closed_condition, "
                          group by cou.name 
                          order by count(distinct(i.id)) desc", sep="") 
    query = new("Query", sql = q)
    data = run(query)
    return (data)

def GetCompaniesNameITS (startdate, enddate, identities_db, closed_condition, filter) :
    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " c.name<>'",aff,"' and ",sep="")

    # list each of the companies analyzed
    # those are order by number of closed issues
        q = "select c.name
                    from issues i, 
                         changes ch,
                         people_upeople pup,
                         ", identities_db, ".upeople_companies upc,
                         ", identities_db, ".companies c
                    where i.id = ch.issue_id and
                          ch.changed_by = pup.people_id and
                          pup.upeople_id = upc.upeople_id and
                          upc.company_id = c.id and
                          ch.changed_on >= ", startdate, " and
                          ch.changed_on < ", enddate," and
                          ", affiliations, 
                          closed_condition, "
                          group by c.name 
                          order by count(distinct(i.id)) desc", sep="")
    query = new("Query", sql = q)
    data = run(query)
    return (data)





################
# Last activity functions
################


##
## GetDiffClosedDays
##
## Get differences in number of closed tickets between two periods.
##  - date: final date of the two periods.
##  - days: number of days for each period.
##  - closed_condition: SQL string to define the condition of "closed"
##     for a ticket
## Example of parameters, for analizing the difference during the last
##  two weeks for the day 2013-11-25:
##  (date="2013-11-25", days=7, closed_condition=...)
##
def GetDiffClosedDays (period, identities_db, date, days, type_analysis=list(NA, NA), closed_condition):
    # This function provides the percentage in activity between two periods
    chardates = GetDates(date, days)
    lastclosed = AggIssuesClosed(period, chardates[2], chardates[1], identities_db, type_analysis, closed_condition)
    lastclosed = as.numeric(lastclosed[1])
    prevclosed = AggIssuesClosed(period, chardates[3], chardates[2], identities_db, type_analysis, closed_condition)
    prevclosed = as.numeric(prevclosed[1])
    diffcloseddays = data.frame(diff_netclosed = numeric(1), percentage_closed = numeric(1))
    diffcloseddays$diff_netclosed = lastclosed - prevclosed
    diffcloseddays$percentage_closed = GetPercentageDiff(prevclosed, lastclosed)

    colnames(diffcloseddays) = c("diff_netclosed","_",days, sep=""), "percentage_closed","_",days, sep=""))
    return (diffcloseddays)


##
## GetDiffClosersDays
##
## Get differences in number of ticket closers between two periods.
##  - date: final date of the two periods.
##  - days: number of days for each period.
##  - closed_condition: SQL string to define the condition of "closed"
##     for a ticket
## Example of parameters, for analizing the difference during the last
##  two weeks for the day 2013-11-25:
##  (date="2013-11-25", days=7, closed_condition=...)
##
def GetDiffClosersDays (period, identities_db, date, days, type_analysis=list(NA, NA), closed_condition):
    # This function provides the percentage in activity between two periods

    chardates = GetDates(date, days)
    lastclosers = AggIssuesClosers(period, chardates[2], chardates[1], identities_db, type_analysis, closed_condition)
    lastclosers = as.numeric(lastclosers[1])
    prevclosers = AggIssuesClosers(period, chardates[3], chardates[2], identities_db, type_analysis, closed_condition)
    prevclosers = as.numeric(prevclosers[1])
    diffclosersdays = data.frame(diff_netclosers = numeric(1), percentage_closers = numeric(1))

    diffclosersdays$diff_netclosers = lastclosers - prevclosers
    diffclosersdays$percentage_closers = GetPercentageDiff(prevclosers, lastclosers)

    colnames(diffclosersdays) = c("diff_netclosers","_",days, sep=""), "percentage_closers","_",days, sep=""))

    return (diffclosersdays)


def GetDiffOpenedDays (period, identities_db, date, days, type_analysis=list(NA, NA)):
    # This function provides the percentage in activity between two periods
    chardates = GetDates(date, days)
    last_opened = AggIssuesOpened(period, chardates[2], chardates[1], identities_db, type_analysis)
    prev_opened = AggIssuesOpened(period, chardates[3], chardates[2], identities_db, type_analysis)

    diff_opened_days = data.frame(diff_netopened = numeric(1), percentage_opened = numeric(1))
    diff_opened_days$diff_netopened = as.numeric(last_opened - prev_opened)
    diff_opened_days$percentage_opened = GetPercentageDiff(prev_opened, last_opened)
    colnames(diff_opened_days) = c("diff_netopened","_",days, sep=""), "percentage_opened","_",days, sep=""))
    return (diff_opened_days)


def GetDiffChangersDays (period, identities_db, date, days, type_analysis=list(NA, NA)):
    # This function provides the percentage in activity between two periods
    chardates = GetDates(date, days)
    last_changers = AggIssuesChangers(period, chardates[2], chardates[1], identities_db, type_analysis)
    prev_changers = AggIssuesChangers(period, chardates[3], chardates[2], identities_db, type_analysis)

    diff_changers_days = data.frame(diff_netchangers = numeric(1), percentage_changers = numeric(1))
    diff_changers_days$diff_netchangers = as.numeric(last_changers - prev_changers)
    diff_changers_days$percentage_changers = GetPercentageDiff(prev_changers, last_changers)

    colnames(diff_changers_days) = c("diff_netchangers","_",days, sep=""), "percentage_changers","_",days, sep=""))

    return (diff_changers_days)

def GetLastActivityITS (days, closed_condition) :
    # opened issues
    q = "select count(*) as opened_",days,"
                from issues
                where submitted_on >= (
                      select (max(submitted_on) - INTERVAL ",days," day)
                      from issues)", sep="");
    query = new("Query", sql = q)
    data1 = run(query)

    # closed issues
    q = "select count(distinct(issue_id)) as closed_",days,"
                from changes
                where  ", closed_condition,"
                and changed_on >= (
                      select (max(changed_on) - INTERVAL ",days," day)
                      from changes)", sep="");
    query = new("Query", sql = q)
    data2 = run(query)

    # closers
    q = paste ("SELECT count(distinct(pup.upeople_id)) as closers_",days,"
                 FROM changes, people_upeople pup
                 WHERE pup.people_id = changes.changed_by and
                 changed_on >= (
                     select (max(changed_on) - INTERVAL ",days," day)
                      from changes) AND ", closed_condition, sep="");

    query = new ("Query", sql = q)
    data3 = run(query)

    # people_involved    
    q = paste ("SELECT count(distinct(pup.upeople_id)) as changers_",days,"
                 FROM changes, people_upeople pup
                 WHERE pup.people_id = changes.changed_by and
                 changed_on >= (
                     select (max(changed_on) - INTERVAL ",days," day)
                      from changes)", sep="");
    query = new ("Query", sql = q)
    data4 = run(query)

    agg_data = merge(data1, data2)
    agg_data = merge(agg_data, data3)

    return (agg_data)




################
# Top functions
################

def GetTopClosersByAssignee (days = 0, startdate, enddate, identities_db, filter = c("")) :

    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " com.name<>'", aff ,"' and ", sep="")
    

    date_limit = ""
    if (days != 0 ) :
        query = new("Query",
                sql = "SELECT @maxdate:=max(changed_on) from changes limit 1")
        data = run(query)
        date_limit = " AND DATEDIFF(@maxdate, changed_on)<",days)
    
    q = "SELECT up.id as id, 
                       up.identifier as closers, 
                       count(distinct(ill.issue_id)) as closed 
                FROM people_upeople pup, 
                     ", identities_db, ".upeople_companies upc, 
                     ", identities_db, ".upeople up, 
                     ", identities_db, ".companies com,
                     issues_log_launchpad ill 
                WHERE ill.assigned_to = pup.people_id and 
                      pup.upeople_id = up.id and 
                      up.id = upc.upeople_id and 
                      upc.company_id = com.id and
                      ", affiliations, "
                      ill.date >= upc.init and 
                      ill.date < upc.end and 
                      ill.change_id  in ( 
                                     select id 
                                     from changes 
                                     where new_value='Fix Committed' and 
                                           changed_on>=", startdate, " and 
                                           changed_on<", enddate, " ", date_limit,") 
                GROUP BY up.identifier 
                ORDER BY closed desc limit 10;", sep="")

    query = new ("Query", sql = q)
    data = run(query)
    return (data)


def GetTablesOwnUniqueIdsITS (table='') :
    tables = 'changes c, people_upeople pup'
    if (table == "issues") tables = 'issues i, people_upeople pup'
    return (tables)


def GetTablesCompaniesITS (i_db, table='') :
    tables = GetTablesOwnUniqueIdsITS(table)
    tables = tables,',',i_db,'.upeople_companies upc',sep='')


def GetFiltersOwnUniqueIdsITS (table='') :
    filters = 'pup.people_id = c.changed_by'
    if (table == "issues") filters = 'pup.people_id = i.submitted_by'
    return (filters)


def GetFiltersCompaniesITS (table='') :
    filters = GetFiltersOwnUniqueIdsITS(table)
    filters = filters,"AND pup.upeople_id = upc.upeople_id")
    if (table == 'issues') :
        filters = filters,"AND submitted_on >= upc.init AND submitted_on < upc.end")
     else :
         filters = filters,"AND changed_on >= upc.init AND changed_on < upc.end")

def GetCompanyTopClosers (company_name, startdate, enddate,
        identities_db, filter = c(''), closed_condition) :
    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " AND up.identifier<>'",aff,"' ",sep='')

    q = "SELECT up.id as id, up.identifier as closers,
                       COUNT(DISTINCT(c.id)) as closed
                FROM ", GetTablesCompaniesITS(identities_db),",
                     ",identities_db,".companies com,
                     ",identities_db,".upeople up
                WHERE ", GetFiltersCompaniesITS()," AND ", closed_condition, "
                      AND pup.people_id = up.id
                      AND upc.company_id = com.id
                      AND com.name = ",company_name,"
                      AND changed_on >= ",startdate," AND changed_on < ",enddate,
                      affiliations, "
                GROUP BY changed_by ORDER BY closed DESC LIMIT 10;",sep='')
    query = new ("Query", sql = q)
    data = run(query)
    return (data)

def GetTopClosers (days = 0, startdate, enddate,
        identities_db, filter = c(""), closed_condition) :

    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " com.name<>'", aff ,"' and ", sep="")

    date_limit = ""
    if (days != 0 ) :
        query = new("Query",
                sql = "SELECT @maxdate:=max(changed_on) from changes limit 1")
        data = run(query)
        date_limit = " AND DATEDIFF(@maxdate, changed_on)<",days)
    
    q = "SELECT up.id as id, up.identifier as closers,
                       count(distinct(c.id)) as closed
                FROM ",GetTablesCompaniesITS(identities_db), ", ",
                     identities_db,".companies com,
                     ",identities_db,".upeople up
                WHERE ",GetFiltersCompaniesITS() ," and
                      ", affiliations, "
                      upc.company_id = com.id and
                      c.changed_by = pup.people_id and
                      pup.upeople_id = up.id and
                      c.changed_on >= ", startdate, " and
                      c.changed_on < ", enddate, " and ",
                      closed_condition, " ", date_limit, "
                GROUP BY up.identifier
                ORDER BY closed desc
                LIMIT 10;", sep="")
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


def GetDomainTopClosers (domain_name, startdate, enddate,
        identities_db, filter = c(''), closed_condition) :
    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " AND up.identifier<>'",aff,"' ",sep='')

    q = "SELECT up.id as id, up.identifier as closers,
                COUNT(DISTINCT(c.id)) as closed
                FROM ", GetTablesDomainsITS(identities_db),",
                     ",identities_db,".domains dom,
                     ",identities_db,".upeople up
                WHERE ", GetFiltersDomainsITS()," AND ", closed_condition, "
                      AND pup.people_id = up.id
                      AND upd.domain_id = dom.id
                      AND dom.name = ",domain_name,"
                      AND changed_on >= ",startdate," AND changed_on < ",enddate,
                      affiliations, "
                GROUP BY changed_by ORDER BY closed DESC LIMIT 10;",sep='')
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


def GetTopOpeners (days = 0, startdate, enddate,
        identities_db, filter = c(""), closed_condition = closed_condition) :
    affiliations = ""
    for (aff in filter):
        affiliations = affiliations, " com.name<>'", aff ,"' and ", sep="")

    date_limit = ""
    if (days != 0 ) :
        query = new("Query",
                sql = "SELECT @maxdate:=max(submitted_on) from issues limit 1")
        data = run(query)
        date_limit = " AND DATEDIFF(@maxdate, submitted_on)<",days)
    

    q = "SELECT up.id as id, up.identifier as openers,
                    count(distinct(i.id)) as opened
                FROM ",GetTablesCompaniesITS(identities_db,'issues'), ", ",
                    identities_db,".companies com,
                    ",identities_db,".upeople up
                WHERE ",GetFiltersCompaniesITS('issues') ," and
                    ", affiliations, "
                    upc.company_id = com.id and
                    pup.upeople_id = up.id and
                    i.submitted_on >= ", startdate, " and
                    i.submitted_on < ", enddate,
                    date_limit, "
                    GROUP BY up.identifier
                    ORDER BY opened desc
                    LIMIT 10;", sep="")
    query = new ("Query", sql = q)
    data = run(query)
    return (data)


#################
# People information, to be refactored
#################

def GetPeopleListITS (startdate, enddate) :
    fields = "DISTINCT(pup.upeople_id) as pid, count(c.id) as total"
    tables = GetTablesOwnUniqueIdsITS()
    filters = GetFiltersOwnUniqueIdsITS()
    filters = filters,"GROUP BY pid ORDER BY total desc")
    q = GetSQLGlobal('changed_on',fields,tables, filters, startdate, enddate)
        query = new("Query", sql = q)
        data = run(query)
        return (data)


def GetPeopleQueryITS (developer_id, period, startdate, enddate, evol) :
    fields = "COUNT(c.id) AS closed"
    tables = GetTablesOwnUniqueIdsITS()
    filters = GetFiltersOwnUniqueIdsITS(), "AND pup.upeople_id = ", developer_id)

    if (evol) :
        q = GetSQLPeriod(period,'changed_on', fields, tables, filters,
                            startdate, enddate)
     else :
        fields = fields,
                ",DATE_FORMAT (min(changed_on),'%Y-%m-%d') as first_date,
                  DATE_FORMAT (max(changed_on),'%Y-%m-%d') as last_date")
        q = GetSQLGlobal('changed_on', fields, tables, filters,
                            startdate, enddate)

    return (q)

def GetPeopleEvolITS (developer_id, period, startdate, enddate) :
    q = GetPeopleQueryITS(developer_id, period, startdate, enddate, TRUE)
    query = new("Query", sql = q)
    data = run(query)
    return (data)

def GetPeopleStaticITS (developer_id, startdate, enddate) :
    q = GetPeopleQueryITS(developer_id, period, startdate, enddate, FALSE)
    query = new("Query", sql = q)
    data = run(query)
    return (data)

#################
# Micro studies
#################

def EvolBMIIndex (period, startdate, enddate, identities_db, type_analysis, closed_condition):
    #Metric based on chapter 4.3.1
    #Metrics and Models in Software Quality Engineering by Stephen H. Kan

    #This will fail if dataframes have different lenght (to be fixe)
    closed = EvolIssuesClosed(period, startdate, enddate, identities_db, type_analysis, closed_condition)
    opened = EvolIssuesOpened(period, startdate, enddate, identities_db, type_analysis)
    evol_bmi = (closed$closed / opened$opened) * 100

    closed$closers = NULL
    opened$openers = NULL

    data = merge(closed, opened, ALL=TRUE)
    data = data.frame(data, evol_bmi)
    return (data)

def GetClosedSummaryCompanies (period, startdate, enddate, identities_db, closed_condition, num_companies):

    # All companies info
    q = "SELECT com.name as name,
                 YEARWEEK( changed_on , 3 ) AS week,
                 COUNT(DISTINCT(issue_id)) AS closed
         FROM changes c,
              people_upeople pup,
              ",identities_db,".upeople_companies upc ,
              ",identities_db,".companies com
         WHERE changed_on >=",startdate," AND
               changed_on < ",enddate,"  AND
               pup.people_id = c.changed_by AND
               pup.upeople_id = upc.upeople_id AND
               changed_on >= upc.init AND
               changed_on < upc.end  AND
               ",closed_condition,"  AND
               upc.company_id = com.id
         GROUP BY com.name,
                  YEARWEEK( changed_on , 3 )
         ORDER BY com.name,
                  YEARWEEK( changed_on , 3 );", sep="")
         #",closed_condition,"  AND
    query = new ("Query", sql = q)
    data = run(query)
    companies  = GetCompaniesNameITS(startdate, enddate, identities_db, closed_condition, c("-Bot", "-Individual", "-Unknown"))
    companies = companies$name

    count = 1
    first_companies = data.frame()
    first = TRUE
    for (company in companies):
        # Cleaning data
        company_data = subset(data, data$name %in% company)
        company_data = completePeriodIds(company_data, conf$granularity, conf)
        company_data = company_data[order(company_data$id), ]
        company_data[is.na(company_data)] = 0
        company_data$name = NULL

        # Up to here, everything's correct, dataset is as expected
        # In the following I should move to merge companies and others
        # as similarly done in mls and scm
        if (count <= num_companies -1):
            # Case of companies with entity in the dataset
            if (first):
                first = FALSE
                first_companies = company_data

            first_companies = merge(first_companies, company_data, all=TRUE)
            colnames(first_companies)[colnames(first_companies)=="closed"] = company

         else :
            #Case of companies that are aggregated in the field Others
            if (first==FALSE):
                first = TRUE
                first_companies$Others = company_data$closed
            else:
                first_companies$Others = first_companies$Others + company_data$closed
        count = count + 1
    return(first_companies)