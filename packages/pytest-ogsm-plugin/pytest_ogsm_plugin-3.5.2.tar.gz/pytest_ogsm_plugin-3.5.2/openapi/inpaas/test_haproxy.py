#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 10:24 AM
# @Author  : cw
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/10/13 3:17 PM
# @Author  : cw
import logging
import sys

import pytest

# from initdata.init_objects import InitDataClass

# init_objects = InitDataClass()
logger = logging.getLogger('AutoTest_Api')


@pytest.mark.base
def test_haproxy():
    """haproxy测试1"""
    logger.info("---haproxy测试---")
    action = "CreateVdc"
    method = "POST"
    print(123123123132313)
    assert 1 == 1


@pytest.mark.base
def test_haproxy2():
    """haproxy测试2"""
    logger.info("---haproxy---")
    action = "CreateVdc"
    method = "POST"

    # json1 = init_objects.create_vdc_body(product)
    # print(json1)
    assert 1 == 2


@pytest.mark.base
@pytest.mark.all
def test_haproxy3():
    """haproxy测试3"""
    logger.info("---haproxy测试---")
    action = "CreateVdc"
    method = "POST"
    logging.info("---haproxy测试---")
    print('12312313231312')
    # json1 = init_objects.create_vdc_body(product)
    # print(json1)
    assert 1 == 2


@pytest.mark.base
@pytest.mark.all
def test_myoutput(capsys):  # or use "capfd" for fd-level
    print("hello")
    sys.stderr.write("world\n")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == "world\n"
    print("next")
    captured = capsys.readouterr()
    assert captured.out == "next\n"
