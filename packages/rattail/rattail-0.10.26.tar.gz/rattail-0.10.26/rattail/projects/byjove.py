# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Generator for 'byjove' projects
"""

import os

import colander

from rattail.projects import ProjectGenerator


class ByjoveProjectGenerator(ProjectGenerator):
    """
    Generator for Byjove app projects.
    """
    key = 'byjove'

    def make_schema(self, **kwargs):
        schema = colander.Schema()

        schema.add(colander.SchemaNode(name='name',
                                       typ=colander.String()))

        schema.add(colander.SchemaNode(name='slug',
                                       typ=colander.String()))

        return schema

    def generate_project(self, output, context, **kwargs):

        ##############################
        # root project dir
        ##############################

        self.generate('CHANGELOG.md.mako',
                      os.path.join(output, 'CHANGELOG.md'),
                      context)

        self.generate('gitignore',
                      os.path.join(output, '.gitignore'))

        self.generate('README.md.mako',
                      os.path.join(output, 'README.md'),
                      context)

        self.generate('vue.config.js.dist.mako',
                      os.path.join(output, 'vue.config.js.dist'),
                      context)
