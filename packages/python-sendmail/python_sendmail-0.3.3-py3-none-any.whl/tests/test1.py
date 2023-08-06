#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import os
import yaml
import unittest
import sendmail

try:
    from localsettings import accounts
except:
    with open(os.environ["LOCALSETTINGS"], "rb") as fobj:
        accounts = yaml.safe_load(fobj)


class TestSendmail(unittest.TestCase):
    def setUp(self):
        self.account = accounts["default"]

    def test1(self):
        from_address = self.account.get("user")
        to_address = self.account.get("user")
        kwargs = {
            "from_address": from_address,
            "to_addresses": [to_address],
            "subject": "test1 {}".format(os.sys.version_info),
            "content": "test content",
        }
        kwargs.update(self.account)
        sendmail.sendmail(**kwargs)
        assert True

    def test2(self):
        from_address = self.account.get("user")
        to_address = self.account.get("user")
        kwargs = {
            "from_address": from_address,
            "to_addresses": [to_address],
            "subject": "test2 {}".format(os.sys.version_info),
            "content": "test content",
            "attachs": [
                "tests/data/hello world.txt",
            ],
        }
        kwargs.update(self.account)
        sendmail.sendmail(**kwargs)
        assert True

    def test3(self):
        from_address = self.account.get("user")
        to_address = self.account.get("user")
        kwargs = {
            "from_address": from_address,
            "to_addresses": [to_address],
            "subject": "test3 {}".format(os.sys.version_info),
            "content": "test content",
            "attachs": [
                {
                    "filepath": "tests/data/hello world.txt",
                    "filename": "测试附件.txt",
                }
            ],
        }
        kwargs.update(self.account)
        sendmail.sendmail(**kwargs)
        assert True
