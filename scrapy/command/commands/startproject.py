import sys
import string
import re
import shutil
from os.path import join, exists

import scrapy
from scrapy.command import ScrapyCommand
from scrapy.utils.template import render_templatefile, string_camelcase
from scrapy.utils.python import ignore_patterns, copytree

TEMPLATES_PATH = join(scrapy.__path__[0], 'templates', 'project')

TEMPLATES_TO_RENDER = (
    ('scrapy-ctl.py',),
    ('${project_name}', 'settings.py.tmpl'),
    ('${project_name}', 'items.py.tmpl'),
    ('${project_name}', 'pipelines.py.tmpl'),
)

IGNORE = ignore_patterns('*.pyc', '.svn')

class Command(ScrapyCommand):

    requires_project = False

    def syntax(self):
        return "<project_name>"

    def short_desc(self):
        return "Create new project with an initial project template"

    def run(self, args, opts):
        if len(args) != 1:
            return False
        project_name = args[0]
        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            print 'Error: Project names must begin with a letter and contain only\n' \
                'letters, numbers and underscores'
            sys.exit(1)
        elif exists(project_name):
            print "Error: directory %r already exists" % project_name
            sys.exit(1)

        moduletpl = join(TEMPLATES_PATH, 'module')
        copytree(moduletpl, join(project_name, project_name), ignore=IGNORE)
        shutil.copy(join(TEMPLATES_PATH, 'scrapy-ctl.py'), project_name)
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_name,
                string.Template(path).substitute(project_name=project_name))
            render_templatefile(tplfile, project_name=project_name,
                ProjectName=string_camelcase(project_name))
