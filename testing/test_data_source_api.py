#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Bitergia
#
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
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#
# import MySQLdb, os, random, string, sys
# import data_source

import json, os, unittest
from report import Report
from filter import Filter
import logging

from GrimoireUtils import getPeriod, read_main_conf
from GrimoireUtils import compare_json_data, completePeriodIds
from GrimoireUtils import createJSON, compareJSON
from utils import read_options

class DataSourceTest(unittest.TestCase):
    @staticmethod
    def init():
        opts = read_options()
        Report.init(opts.config_file)
        logging.info("Init Data Source")

    @staticmethod
    def close():
        logging.info("End Data Source")

    def test_get_bots(self):
        for ds in Report.get_data_sources():
            bots = ds.get_bots()
            self.assertTrue(isinstance(bots, list))

    def test_set_bots(self):
        bots = ['test']
        for ds in Report.get_data_sources():
            ds.set_bots(bots)
            ds_bots = ds.get_bots()
            self.assertEqual(ds_bots[0], bots[0])

    def test_get_name(self):
        for ds in Report.get_data_sources():
            ds_name = ds.get_name()
            self.assertNotEqual(ds_name, "")

    def test_get_db_name(self):
        for ds in Report.get_data_sources():
            ds_db_name = ds.get_db_name()
            self.assertNotEqual(ds_db_name, "")

    def test_get_evolutionary_filename(self):
        for ds in Report.get_data_sources():
            f_evol = ds().get_evolutionary_filename()
            self.assertNotEqual(f_evol, "")

    def test_get_evolutionary_data(self):
        opts = read_options()
        period = getPeriod(opts.granularity)
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        # Test without filters
        for ds in Report.get_data_sources():
            # Create the evolutionary data from dbs and check with test JSON
            logging.info(ds.get_name() + " test_get_evolutionary_data")
            Report.connect_ds(ds)
            ds_data = ds.get_evolutionary_data (period, startdate,
                                                enddate, identities_db)

            test_json = ds().get_evolutionary_filename()
            f_test_json = os.path.join("json", test_json)

            self.assertTrue(DataSourceTest._compare_data(ds_data, f_test_json))

    def test_create_evolutionary_report(self):
        opts = read_options()
        period = getPeriod(opts.granularity)
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        # Test without filters
        for ds in Report.get_data_sources():
            # Create the evolutionary data from dbs and check with test JSON
            logging.info(ds.get_name() + " create_evolutionary_report")
            Report.connect_ds(ds)
            ds.create_evolutionary_report (period, startdate,
                                           enddate, opts.destdir, identities_db)

            ds_json = ds().get_evolutionary_filename()
            f_test_json = os.path.join("json", ds_json)
            f_report_json = os.path.join(opts.destdir, ds_json)

            self.assertTrue(compareJSON(f_test_json, f_report_json))

    @staticmethod
    def _compare_data(data, json_file):
        # Create a temporary JSON file with data
        from tempfile import NamedTemporaryFile
        data_file = NamedTemporaryFile()
        data_file_name = data_file.name
        data_file.close()
        createJSON(data, data_file_name, check=False, skip_fields = [])

        return compareJSON(data_file_name, json_file)

    def test_get_agg_filename(self):
        for ds in Report.get_data_sources():
            f_agg = ds().get_agg_filename()
            self.assertNotEqual(f_agg, "")

    def test_get_agg_data(self):
        opts = read_options()
        period = getPeriod(opts.granularity)
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        # Test without filters
        for ds in Report.get_data_sources():
            logging.info(ds.get_name() + " test_get_agg_data")
            # Create the evolutionary data from dbs and check with test JSON
            Report.connect_ds(ds)
            ds_data = ds.get_agg_data (period, startdate,
                                        enddate, identities_db)

            test_json = os.path.join("json",ds().get_agg_filename())

            self.assertTrue(DataSourceTest._compare_data(ds_data, test_json))

    def test_create_agg_report(self):
        opts = read_options()
        period = getPeriod(opts.granularity)
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        # Test without filters
        for ds in Report.get_data_sources():
            logging.info(ds.get_name() + " create_agg_report")
            # Create the evolutionary data from dbs and check with test JSON
            Report.connect_ds(ds)
            ds.create_agg_report (period, startdate,
                                  enddate, opts.destdir, identities_db)

            ds_json = ds().get_agg_filename()
            f_test_json = os.path.join("json", ds_json)
            f_report_json = os.path.join(opts.destdir, ds_json)

            self.assertTrue(compareJSON(f_test_json, f_report_json))


    def test_get_agg_evol_filters_data(self):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"
        period = getPeriod(opts.granularity)


        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']
        bots = []

        # Test for all filters
        for ds in Report.get_data_sources():
            Report.connect_ds(ds)
            for filter_ in Report.get_filters():
                filter_name = filter_.get_name()
                filter_name_short = filter_.get_name_short()
                items = ds.get_filter_items(filter_, startdate, enddate, identities_db, bots)
                if items is None: continue
                if (isinstance(items, dict)): items = items['name']

                if not isinstance(items, (list)): items = [items]

                for item in items:
                    filter_item = Filter(filter_.get_name(), item)
#                    item_name = item
#                    if ds.get_name() not in ["irc","scr"]:
#                        item_name = "'"+item+"'"
                    item_file = item
                    if ds.get_name() in ["its","scr"] :
                        item_file = item.replace("/","_")

                    elif ds.get_name() == "mls":
                        item_file = item.replace("/","_").replace("<","__").replace(">","___")

                    logging.info(ds.get_name() +","+ filter_name+","+ item+","+ "agg")
                    agg = ds.get_agg_data(period, startdate, enddate, identities_db, filter_item)
                    fn = item_file+"-"+ds.get_name()+"-"+filter_name_short+"-static.json"
                    test_json = os.path.join("json",fn)
                    self.assertTrue(DataSourceTest._compare_data(agg, test_json))

                    logging.info(ds.get_name() +","+ filter_name+","+ item+","+ "evol")
                    evol = ds.get_evolutionary_data(period, startdate, enddate, identities_db, filter_item)
                    fn = item_file+"-"+ds.get_name()+"-"+filter_name_short+"-evolutionary.json"
                    test_json = os.path.join("json",fn)
                    self.assertTrue(DataSourceTest._compare_data(evol, test_json))

    def test_get_filter_items(self):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']
        bots = []

        for ds in Report.get_data_sources():
            Report.connect_ds(ds)
            for filter_ in Report.get_filters():
                items = ds.get_filter_items(filter_, startdate, enddate, identities_db, bots)
                if items is None: continue
                if (isinstance(items, dict)): items = items['name']
                if not isinstance(items, (list)): items = [items]

                if ds.get_name() in ["scr"] :
                    items = [item.replace("/","_") for item in items]

                elif ds.get_name() == "mls":
                    items = [item.replace("/","_").replace("<","__").replace(">","___") 
                             for item in items] 

                fn = ds.get_name()+"-"+filter_.get_name_plural()+".json"
                createJSON(items, opts.destdir+"/"+ fn)
                test_json = os.path.join("json",fn)
                new_json = opts.destdir+"/"+ fn

                if ds.get_name() not in ["scr"] :
                    # scr repos format is more complex and 
                    # is checked already in test_get_agg_evol_filters_data 
                    self.assertTrue(compareJSON(test_json, new_json))

    def test_get_top_data (self):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"
        npeople = opts.npeople

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        for ds in Report.get_data_sources():
            Report.connect_ds(ds)
            top = ds.get_top_data(startdate, enddate, identities_db, None, npeople)
            test_json = os.path.join("json",ds.get_name()+"-top.json")
            self.assertTrue(DataSourceTest._compare_data(top, test_json))

    def test_create_top_report (self):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        for ds in Report.get_data_sources():
            Report.connect_ds(ds)
            ds.create_top_report(startdate, enddate, opts.destdir, opts.npeople, identities_db)

            fn = ds.get_name()+"-top.json"
            test_json = os.path.join("json",fn)
            top_json = os.path.join(opts.destdir,fn)

            self.assertTrue(compareJSON(test_json, top_json))

    def test_get_filter_summary (self):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"
        period = getPeriod(opts.granularity)


        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        for ds in Report.get_data_sources():
            if ds.get_name() not in ['scm','its','mls']:
                continue
            Report.connect_ds(ds)
            for filter_ in Report.get_filters():
                if (filter_.get_name() == "company"):
                    summary = ds.get_filter_summary(filter_, period, startdate,
                                          enddate, identities_db, 10)
                    test_json = os.path.join("json",filter_.get_summary_filename(ds))
                    self.assertTrue(DataSourceTest._compare_data(summary, test_json))

    def test_get_filter_item_top (self):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"
        npeople = opts.npeople

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        for ds in Report.get_data_sources():
            if ds.get_name() not in ['scm','its','mls']:
                continue
            Report.connect_ds(ds)
            bots = ds.get_bots()
            for filter_ in Report.get_filters():
                items = ds.get_filter_items(filter_, startdate, enddate,
                                            identities_db, bots)
                if items is None: continue
                if (isinstance(items, dict)): items = items['name']
                if not isinstance(items, (list)): items = [items]

                for item in items:
                    filter_item = Filter(filter_.get_name(), item)
                    top = ds.get_top_data(startdate, enddate, identities_db,
                                          filter_item, npeople)
                    if top is None: continue
                    test_json = os.path.join("json",filter_item.get_top_filename(ds()))
                    self.assertTrue(DataSourceTest._compare_data(top, test_json))

    # get_top_people, get_person_evol, get_person_agg tests included
    def test_create_people_report(self):
        #period, startdate, enddate, identities_db):
        opts = read_options()
        startdate = "'"+opts.startdate+"'"
        enddate = "'"+opts.enddate+"'"
        period = getPeriod(opts.granularity)

        automator = read_main_conf(opts.config_file)
        identities_db = automator['generic']['db_identities']

        for ds in Report.get_data_sources():
            Report.connect_ds(ds)

            if ds.get_name() == "downloads": continue

            fpeople = ds.get_top_people_file(ds.get_name())
            people = ds.get_top_people(startdate, enddate, identities_db, opts.npeople)
            test_json = os.path.join("json",fpeople)
            self.assertTrue(DataSourceTest._compare_data(people, test_json))

            for upeople_id in people :
                evol_data = ds.get_person_evol(upeople_id, period, startdate, enddate,
                                                identities_db, type_analysis = None)
                fperson = ds().get_person_evol_file(upeople_id)
                test_json = os.path.join("json",fperson)
                self.assertTrue(DataSourceTest._compare_data(evol_data, test_json))


                agg = ds.get_person_agg(upeople_id, startdate, enddate,
                                         identities_db, type_analysis = None)
                fperson = ds().get_person_agg_file(upeople_id)
                test_json = os.path.join("json",fperson)
                self.assertTrue(DataSourceTest._compare_data(agg, test_json))

    def test_create_r_reports(self):
        # R black box generated reports. Can not test
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN,format='%(asctime)s %(message)s')

    DataSourceTest.init()
    suite = unittest.TestLoader().loadTestsFromTestCase(DataSourceTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

    DataSourceTest.close()