#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/16 4:42 PM
# @Author  : cw
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 10:24 AM
# @Author  : cw
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/10/13 3:17 PM
# @Author  : cw
import logging

import pytest

# from initdata.init_objects import InitDataClass

# init_objects = InitDataClass()
logger = logging.getLogger('AutoTest_Api')


@pytest.mark.base
def test_lvs():
    """lvs测试"""
    logger.info("---lvs测试---")
    action = "CreateVdc"
    method = "POST"

    # json1 = init_objects.create_vdc_body(product)
    # print(json1)
    assert 1 == 1


@pytest.mark.base
def test_lvs2():
    """lvs测试2"""
    logger.info("---lvs2---")
    action = "CreateVdc"
    method = "POST"

    # json1 = init_objects.create_vdc_body(product)
    # print(json1)
    assert 1 == 2


@pytest.mark.base
@pytest.mark.all
def test_lvs3():
    """lvs测试3"""
    logger.info("---lvs测试---")
    action = "CreateVdc"
    method = "POST"

    # json1 = init_objects.create_vdc_body(product)
    # print(json1)
    assert 1 == 3
