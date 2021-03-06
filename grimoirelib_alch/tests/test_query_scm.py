# -*- coding: utf-8 -*-

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
## Unit tests for scm_query.py
## 
## Authors:
##   Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
##

from grimoirelib_alch.query.scm import DB, Query
from grimoirelib_alch.type.timeseries import TimeSeries
from datetime import datetime
import unittest

url = 'mysql://jgb:XXX@localhost/'
schema = 'vizgrimoire_cvsanaly'
schema_id = 'vizgrimoire_cvsanaly'
start = datetime(2013,11,13)
end = datetime(2014,2,1)

class TestSCMQuery (unittest.TestCase):

    def setUp (self):
        database = DB (url = url,
                       schema = schema,
                       schema_id = schema_id)
        self.session = database.build_session(Query, echo = False)

    def _test_select_nscmlog (self, variables, results):
        """Test select_nscmlog with different variables

        - variables (list): variables to test
        - results (list): expected results
            Each item in results corresponds to an item in variable
        """

        # Number (count)
        res = self.session.query().select_nscmlog(variables).all()
        self.assertEqual (res, results[0])
        # Number (count), except those that correspond to commits that
        #   doesn't touch files (merges)
        res = self.session.query() \
            .select_nscmlog(variables) \
            .filter_nomerges() \
            .all()
        self.assertEqual (res, results[1])

    def test_select_ncsmlog (self):
        """Test select_ncsmlog"""

        self._test_select_nscmlog (["commits",],
                                   [[(3646L,)], [(3405L,)]])
        self._test_select_nscmlog (["authors",],
                                   [[(14L,)], [(14L,)]])
        self._test_select_nscmlog (["committers",],
                                   [[(14L,)], [(14L,)]])

    def _test_select_nscmlog_period (self, variables, results):
        """Test select_nscmlog with different variables and periods

        - variables (list): variables to test
        - results (list): expected results
            Each item in results corresponds to an item in variables
        """

        # Test for variable (count)
        res = self.session.query().select_nscmlog(variables) \
            .filter_period(start=start,end=end).all()
        self.assertEqual (res, results[0])
        # Test for variable (count) considering only commits "touch files"
        #  (that is, merges are excluded)
        res = self.session.query().select_nscmlog(variables) \
            .filter_nomerges() \
            .filter_period(start=start, end=end) \
            .all()
        self.assertEqual (res, results[1])
        # Test for variable (count), using authoring date for commits
        res = self.session.query().select_nscmlog(variables) \
            .filter_period(start=start, end=end, date="author") \
            .all()
        self.assertEqual (res, results[2])

    def test_select_ncsmlog_period (self):
        """Test select_ncsmlog"""

        self._test_select_nscmlog_period (["commits",],
                                          [[(730,)], [(666,)], [(728,)]])
        self._test_select_nscmlog_period (["authors",],
                                          [[(9,)], [(9,)], [(9,)]])
        self._test_select_nscmlog_period (["committers",],
                                          [[(9,)], [(9,)], [(9,)]])

    def _test_select_listpersons (self, kind, uid, correct):
        """Test select_listpersons, for a specific kind of persons

        - kind (string): kind of person: authors, committers, all
        - uid (boolean): to use or not to use unique ids
        - correct (list): correct results
        """

        if uid:
            res = self.session.query() \
                .select_listpersons_uid(kind)
        else:
            res = self.session.query() \
                .select_listpersons(kind)
        res = res.filter_period(start=start, end=end) \
            .limit(5).all()
        self.assertEqual (res, correct)

    def test_select_listpersons (self):
        """Test select_listpersons"""

        correct_nouid = {
            "authors":
                [(1L, u'Alvaro del Castillo', 'acs@bitergia.com'),
                 (3L, u'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                 (4L, u'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                 (5L, u'Daniel Izquierdo Cortazar','dizquierdo@bitergia.com'),
                 (6L, u'Luis Cañas-Díaz', 'lcanas@bitergia.com')],
            "committers":
                [(1L, u'Alvaro del Castillo', 'acs@bitergia.com'),
                 (3L, u'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                 (4L, u'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                 (5L, u'Daniel Izquierdo Cortazar', 'dizquierdo@bitergia.com'),
                 (6L, u'Luis Cañas-Díaz', 'lcanas@bitergia.com')],
            "all":
                [(1L, u'Alvaro del Castillo', 'acs@bitergia.com'),
                 (3L, u'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                 (4L, u'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                 (5L, u'Daniel Izquierdo Cortazar', 'dizquierdo@bitergia.com'),
                 (6L, u'Luis Cañas-Díaz', 'lcanas@bitergia.com')]}
        correct_uid = {
            "authors":
                [(1L, u'Alvaro del Castillo'), 
                 (3L, u'Jesus M. Gonzalez-Barahona'),
                 (4L, u'Daniel Izquierdo'),
                 (6L, u'Luis Cañas-Díaz'),
                 (7L, u'Santiago Dueñas')],
            "committers": 
                [(1L, u'Alvaro del Castillo'), 
                 (3L, u'Jesus M. Gonzalez-Barahona'),
                 (4L, u'Daniel Izquierdo'),
                 (6L, u'Luis Cañas-Díaz'),
                 (7L, u'Santiago Dueñas')],
            "all":
                [(1L, u'Alvaro del Castillo'), 
                 (3L, u'Jesus M. Gonzalez-Barahona'),
                 (4L, u'Daniel Izquierdo'),
                 (6L, u'Luis Cañas-Díaz'),
                 (7L, u'Santiago Dueñas')]}

        for uid in (False, True):
            if uid:
                correct = correct_uid
            else:
                correct = correct_nouid
            self._test_select_listpersons (kind = "authors", uid = uid,
                                           correct = correct["authors"])
            self._test_select_listpersons (kind = "committers", uid = uid,
                                           correct = correct["committers"])
            self._test_select_listpersons (kind = "all", uid = uid,
                                           correct = correct["all"])

    def test_select_nbranches (self):
        """Test select_nbranches"""

        correct = [[(17L,)],
                   [(5L,)],
                   TimeSeries ("months",
                               start=datetime(2013,11,13),
                               end=datetime(2014,01,01),
                               data=[(datetime(2013,11,13), (3L,)),
                                     (datetime(2013,12,13), (2L,)),
                                     (datetime(2014,01,13), (2L,))]
                               )]
        res = self.session.query().select_nbranches()
        self.assertEqual (res.all(), correct[0])
        res = res.join(DB.SCMLog) \
            .filter_period(start=start, end=end)
        self.assertEqual (res.all(), correct[1])
        res = res.group_by_period().timeseries()
        self.assertEqual (res, correct[2])

    def test_select_nfiles (self):
        """Test select_nfiles"""

        correct = [[(37519L,)],
                   [(3541L,)],
                   TimeSeries ("months",
                               start=datetime(2013,11,13),
                               end=datetime(2014,01,01),
                               data=[(datetime(2013,11,13), (96L,)),
                                     (datetime(2013,12,13), (2197L,)),
                                     (datetime(2014,01,13), (1350L,))]
                               )]
        res = self.session.query().select_nfiles()
        self.assertEqual (res.all(), correct[0])
        res = res.join(DB.SCMLog) \
            .filter_period(start=start, end=end)
        self.assertEqual (res.all(), correct[1])
        res = res.group_by_period().timeseries()
        self.assertEqual (res, correct[2])

    def test_select_repos (self):
        """Test select_nfiles"""

        correct = [[(1L, u'vizgrimoire.github.com.git'),
                    (2L, u'VizGrimoireJS.git'),
                    (3L, u'VizGrimoireJS-lib.git'),
                    (4L, u'VizGrimoireR.git'),
                    (5L, u'VizGrimoireUtils.git')],
                   [(2L, u'VizGrimoireJS.git'),
                    (3L, u'VizGrimoireJS-lib.git'),
                    (4L, u'VizGrimoireR.git'),
                    (5L, u'VizGrimoireUtils.git')],
                   [(5L, )]
                   ]
        res = self.session.query().select_repos(names = True, distinct = True)
        self.assertEqual (res.all(), correct[0])
        res = res.join(DB.SCMLog) \
            .filter_period(start=start, end=end)
        self.assertEqual (res.all(), correct[1])
        res = self.session.query().select_repos(distinct = True,
                                                count = True)
        self.assertEqual (res.all(), correct[2])

    def test_select_listbranches (self):
        """Test select_listbranches"""

        correct = [
            [(1L, 'master'), (2L, 'tinycolor'), (3L, 'webkit-companies'),
             (4L, 'openstack-bootstrap'), (5L, 'openstack'),
             (6L, 'apiClean'), (7L, 'puppet'), (8L, 'redhat'),
             (9L, 'mediawiki'), (10L, '1.x'), (11L, 'issue-4'),
             (12L, 'minJSONfiles'), (13L, 'restapi'),
             (14L, 'unique-ids'), (15L, 'newperiodR'),
             (16L, 'newperiod'), (17L, 'gerrit')],
            [(1L, 'master'), (8L, 'redhat'), (9L, 'mediawiki'),
             (12L, 'minJSONfiles'), (13L, 'restapi')]
            ]
        res = self.session.query().select_listbranches()
        self.assertEqual (res.all(), correct[0])
        res = res.join(DB.SCMLog) \
            .filter_period(start=start, end=end)
        self.assertEqual (res.all(), correct[1])


    def test_filter_persons (self):
        """Test filter_persons"""
        
        res = self.session.query().select_nscmlog(["commits"]) \
            .filter_persons ([2,3]) \
            .all()
        self.assertEqual (res, [(1303L,)])
        res = self.session.query().select_nscmlog(["commits"]) \
            .filter_persons ([1,2], "committers") \
            .all()
        self.assertEqual (res, [(2515L,)])

    def test_filter_paths (self):
        """Test filter_paths"""
        
        res = self.session.query().select_nscmlog(["commits"]) \
            .filter_paths (("examples",)) \
            .all()
        self.assertEqual (res, [(708L,)])
        res = self.session.query().select_nscmlog(["commits"]) \
            .filter_paths (("src", "examples",)) \
            .all()
        self.assertEqual (res, [(1787L,)])


    def test_group_by_repo (self):
        """Test group_by_repo"""

        correct = [
            [(11L, 1L), (1375L, 2L), (1615L, 3L), (1428L, 4L), (36L, 5L)],
            [(11L, 1L), (1343L, 2L), (1570L, 3L), (1109L, 4L), (13L, 5L)],
            [(11L, 1L, 'vizgrimoire.github.com.git'),
             (1375L, 2L, 'VizGrimoireJS.git'),
             (1615L, 3L, 'VizGrimoireJS-lib.git'),
             (1428L, 4L, 'VizGrimoireR.git'),
             (36L, 5L, 'VizGrimoireUtils.git')]]

        # Number of commits for each repo
        res = self.session.query().select_nscmlog(["commits",]) \
            .group_by_repo().all()
        self.assertEqual (res, correct[0])
        # Number of commits for each repo until some date
        res = self.session.query().select_nscmlog(["commits",]) \
            .group_by_repo() \
            .filter_period(end=datetime(2014,1,1)).all()
        self.assertEqual (res, correct[1])
        # Number of commits for each repo, including repo name
        res = self.session.query().select_nscmlog(["commits",]) \
            .group_by_repo(names=True).all()
        self.assertEqual (res, correct[2])

    def test_group_by (self):
        """Test combinations of group_by_* functions"""

        correct = [
            [(29L, 2L, 'VizGrimoireJS.git', 11L, 2013L),
             (79L, 2L, 'VizGrimoireJS.git', 12L, 2013L),
             (31L, 2L, 'VizGrimoireJS.git', 1L, 2014L),
             (8L, 3L, 'VizGrimoireJS-lib.git', 11L, 2013L),
             (105L, 3L, 'VizGrimoireJS-lib.git', 12L, 2013L),
             (39L, 3L, 'VizGrimoireJS-lib.git', 1L, 2014L),
             (55L, 4L, 'VizGrimoireR.git', 11L, 2013L),
             (131L, 4L, 'VizGrimoireR.git', 12L, 2013L),
             (219L, 4L, 'VizGrimoireR.git', 1L, 2014L),
             (8L, 5L, 'VizGrimoireUtils.git', 11L, 2013L),
             (5L, 5L, 'VizGrimoireUtils.git', 12L, 2013L),
             (21L, 5L, 'VizGrimoireUtils.git', 1L, 2014L)]
            ]

        res = self.session.query().select_nscmlog(["commits",]) \
            .group_by_repo(names=True).group_by_period() \
            .filter_period(start=start, end=end)
        self.assertEqual (res.all(), correct[0])

    def test_chains (self):
        """Test different query chains

        It only tests that the execution of the corresponding
        SQL query doesn't rise some exception."""

        res = self.session.query() \
            .select_personsdata_uid("authors") \
            .select_commitsperiod() \
            .filter_nomerges() \
            .filter_period(start=datetime(2013,12,1),
                           end=datetime(2014,2,1)) \
                           .group_by_person()
        res = self.session.query().select_nscmlog(["commits",]) \
            .select_personsdata_uid("authors") \
            .select_commitsperiod() \
            .group_by_person() \
            .order_by("nocommits desc") \
            .limit(10)
        res = self.session.query().select_nscmlog(["commits",]) \
            .select_personsdata_uid("authors") \
            .select_commitsperiod() \
            .group_by_person() \
            .order_by("nocommits desc") \
            .limit(10).all()

if __name__ == "__main__":
    unittest.main()
