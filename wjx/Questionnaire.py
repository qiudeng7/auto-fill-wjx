from DrissionPage import ChromiumPage
from DrissionPage._elements.chromium_element import ChromiumElement
import random
import time
import json
import pathlib
import os
from .Config import Config
from .logger import logger
from typing import Callable
from DrissionPage.errors import NoRectError


class Questionnaire:
    """
    问卷类，负责打开浏览器，进行问卷相关操作，比如遍历题目、提交问卷、处理弹窗。
    """

    questionType = {"单选题": "3", "多选题": "4", "填空题": "1"}

    def __init__(self):
        url = Config()["url"]
        self.page = ChromiumPage()
        self.page.get(url)
        self.fields = self.page.eles("css:.field")
        self.handleTips()

    def walkQuestions(self, _type=None, callback: Callable = None) -> None:
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

    # 优化版的题目遍历
    def optimizedWalkQuestions(self, quesHandler: dict[str, Callable[[ChromiumElement], None]]):
        for field in self.fields:
            fieldType = field.attr("type")
            handler = quesHandler[fieldType]
            try:
                handler(field)
            except NoRectError as e:
                print("未找到元素，跳过")
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
        while True:
            if self.page.url == Config()["url"]:
                time.sleep(.3)
                continue
            else:
                break
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


if __name__ == "__main__":
    Questionnaire().optimizedWalkQuestions({
        "1": lambda e: print("类型1"),
        "2": lambda e: print("类型2"),
        "3": lambda e: print("类型3"),
        "4": lambda e: print("类型4"),
        "5": lambda e: print("类型5"),
    })
