from DrissionPage import ChromiumPage
from DrissionPage._elements.chromium_element import ChromiumElement
import random
import time
import json
import pathlib
import os
from .Config import Config
from .logger import logger


class Questionnaire:
    """
    问卷类，负责打开浏览器，进行问卷相关操作，比如遍历题目、提交问卷、处理弹窗。
    """

    questionType = {"单选题": "3", "多选题": "4"}

    def __init__(self):
        url = Config()["url"]
        self.page = ChromiumPage()
        self.page.get(url)
        self.fields = self.page.eles("css:.field")
        self.handleTips()

    def walkQuestions(self, _type=None, callback: callable = None) -> None:
        """
        遍历所有题目，对每一题调用callback。
        你可以设置_type参数来过滤题型。
        期望的调用方式：
        Questionnaire().walkQuestions(
            _type=Questionnaire.questionType["单选题"],
            callback=lambda field: self.fillSingleChoiceQues(field, rolePref),
        )

        @param: _type: 题型，可选值为Questionnaire.questionType内的值
        @param: callback: 回调函数，接受一个参数field，field是一个ChromiumElement对象，代表每一题的元素。
        return: None
        """
        if callback == None:
            raise ValueError("请设置回调函数")
        for field in self.fields:
            if type(field) is ChromiumElement:
                fieldType = field.attr("type")
                if _type == None or fieldType == _type:
                    callback(field)

    def submit(self, successCallback: callable = None):
        """
        点击提交按钮并关闭浏览器
        """
        self.page.ele("css:#SubmitBtnGroup").click()
        time.sleep(random.randint(1, 2))
        if self.page.s_ele("css:#rectMask"):
            self.page.ele("css:#rectMask").click()
        time.sleep(random.randint(5, 6))

        # TODO 检测页面有没有跳转，如果没跳转说明提交遇到了问题，这里需要写的更规范一些
        # 这里可能会遇到
        if self.page.s_ele("多选"):
            logger.info("检测到页面没有跳转，20s后重新处理")
            loop = 0
            while loop < 20:
                time.sleep(1)
                logger.info(f"剩余时间：{20-loop}s")
                loop += 1
        if successCallback:
            successCallback()
        self.page.quit()

    def handleTips(self):
        """
        处理提示弹窗
        """
        sign = self.page.s_ele("之前已经回答了部分题目")
        if sign:
            ele = self.page.ele("css:.layui-layer-btn1")
            if ele:
                ele.click()
