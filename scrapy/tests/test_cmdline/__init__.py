import sys
import os
from subprocess import Popen, PIPE
import unittest

import scrapy

class CmdlineTest(unittest.TestCase):

    def setUp(self):
        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = os.path.dirname(scrapy.__path__[0])
        self.env.pop('SCRAPY_SETTINGS_DISABLED', None)
        self.env['SCRAPY_SETTINGS_MODULE'] = 'scrapy.tests.test_cmdline.settings'

    def _execute(self, *new_args, **kwargs):
        args = (sys.executable, '-m', 'scrapy.command.cmdline') + new_args
        proc = Popen(args, stdout=PIPE, stderr=PIPE, env=self.env, **kwargs)
        comm = proc.communicate()
        return comm[0].strip()

    def test_default_settings(self):
        self.assertEqual(self._execute('settings', '--get', 'TEST1', '--init'), \
            'default')
        self.assertEqual(self._execute('settings', '--get', 'TEST1'), \
            'default + loaded + started')

    def test_override_settings_using_settings_arg(self):
        self.assertEqual(self._execute('settings', '--get', 'TEST1', '--init', \
            '--settings', 'scrapy.tests.test_cmdline.settings2'), \
            'override')
        self.assertEqual(self._execute('settings', '--get', 'TEST1', \
            '--settings', 'scrapy.tests.test_cmdline.settings2'), \
            'override + loaded + started')

    def test_override_settings_using_set_arg(self):
        self.assertEqual(self._execute('settings', '--get', 'TEST1', '--init', '--set', 'TEST1=override'), \
            'override')
        self.assertEqual(self._execute('settings', '--get', 'TEST1', '--set', 'TEST1=override'), \
            'override + loaded + started')

    def test_override_settings_using_envvar(self):
        self.env['SCRAPY_TEST1'] = 'override'
        self.assertEqual(self._execute('settings', '--get', 'TEST1', '--init'), \
            'override')
        self.assertEqual(self._execute('settings', '--get', 'TEST1'), \
            'override + loaded + started')

