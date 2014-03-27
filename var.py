#! /usr/bin/python
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
## Package to deal with variables for data from *Grimoire
##
## Authors:
##   Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
##

from scm import SCM
from json import dumps


class VariableFactory:
    """Factory of Variable objects

    This factory helps to avoid repeating some patameters in all
    instantiations of variables, such as the database name"""

    def make (self, variable):
        """Create a variable.

        - variable (string): name of the variable
        """

        return Variable (variable = variable, database = self.database)


    def __init__(self, database):
        """Initialization

        - database (string): database url (SQLAlchemy conventions)
           example: 'mysql://jgb:XXX@localhost/vizgrimoire_cvsanaly'
        """

        self.database = database


class Variable:
    """Class for producing data for variables"""

    vars = {"scm/ncommits":
                {"type": "total",
                 "family": "scm",
                 "id": "ncommits",
                 "desc": "Number of commits"
                 }
            }


    def value (self):
        """Obtain the value for a variable"""

        if self.param["family"] == "scm":
            data = SCM (database = self.database, var = self.param["id"])
            if self.param["type"] == "total":
                return data.total()
            elif self.param["type"] == "timeseries":
                return data.timeseries()
        else:
            raise Exception ("Unknown family: " + self.param["family"] \
                                 + " (variable: " + variable + ")")

    def json (self, pretty=False):

        data = {"id": self.variable,
                "type": self.param["type"],
                "desc": self.param["desc"],
                "value": self.value()}
        separators=(',', ': ')
        encoding="utf-8"
        if pretty:
            sort_keys=True
            indent=4
        else:
            sort_keys=False
            indent=None
        return dumps(data, sort_keys=sort_keys,
                     indent=indent, separators=separators,
                     encoding=encoding)


    def __init__ (self, variable, database):
        """Initialize object

        - variable (string): name of the variable
        """        

        self.database = database
        if variable in Variable.vars:
            self.variable = variable
            self.param = self.vars[self.variable]
        else:
            assert False, "Unknown variable id: %s." % variable

    
if __name__ == "__main__":

    var_factory = VariableFactory (
        database = 'mysql://jgb:XXX@localhost/vizgrimoire_cvsanaly')
    ncommits = var_factory.make("scm/ncommits")
    print ncommits.value ()
    print ncommits.json(pretty=True)
