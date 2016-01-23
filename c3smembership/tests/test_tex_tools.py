# -*- coding: utf-8 -*-
"""
Test module for c3smembership.tex_tools.
"""

import unittest
from c3smembership.tex_tools import TexTools


class TestTexTools(unittest.TestCase):
    """
    Test module for c3smembership.tex_tools.
    """

    def test_escape(self):
        """
        Test method TexTools.escape
        """
        unescaped = u'&%$#_{}~^\\<>℅'
        escaped = TexTools.escape(unescaped)
        expected = u'\\&\\%\\$\\#\\_\\{\}\\textasciitilde{}\\^{}' + \
                   u'\\textbackslash{}\\textless\\textgreaterc/o'
        self.assertEqual(escaped, expected)
