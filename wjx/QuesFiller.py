from .Questionnaire import Questionnaire
from .RolePreferenceManager import RolePreferenceManager
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage import ChromiumPage
from DrissionPage.errors import NoRectError
from .Config import Config
import random
from .logger import logger
import os
import json
import time


class QuestionareFiller:
    """
    支持角色偏好和历史记录的问卷填写器。
    """

    def __init__(self):
        if not RolePreferenceManager.rolePrefConfExists():
            raise (
                "角色偏好配置不存在，请先创建角色偏好配置，手动调整过配置后再填写问卷。"
            )
        rolePrefManager = RolePreferenceManager()
        for role in rolePrefManager.roles:
            oneRolePref = rolePrefManager.getPrefByRole(role)
            totalCount = Config()["roleCount"]
            loop = 0
            record = self.getRecord()
            if record.get(role, None) is None:
                record[role] = 0

            while record[role] < totalCount[role]:
                ques = Questionnaire()
                ques.optimizedWalkQuestions({
                    ques.questionType["单选题"]: lambda field: self.fillSingleChoiceQues(field, oneRolePref),
                    ques.questionType["多选题"]: lambda field: self.fillMultiChoiceQues(field, oneRolePref),
                    ques.questionType["填空题"]: lambda field: self.fillTextQues(
                        field, oneRolePref)
                })
                # # TODO 这里可以改成只walk一次
                # ques.walkQuestions(
                #     _type=Questionnaire.questionType["单选题"],
                #     callback=lambda field: self.fillSingleChoiceQues(
                #         field, oneRolePref
                #     ),
                # )
                # ques.walkQuestions(
                #     _type=Questionnaire.questionType["多选题"],
                #     callback=lambda field: self.fillMultiChoiceQues(
                #         field, oneRolePref),
                # )
                # ques.walkQuestions(
                #     _type=Questionnaire.questionType["填空题"],
                #     callback=lambda field: self.fillTextQues(
                #         field, oneRolePref),
                # )

                def submitSuccess():
                    nonlocal loop
                    loop += 1
                    record[role] += 1
                    self.setRecord(record)
                    logger.info(
                        f"role: {role}, loop: {loop}, record:{record} totalCount: {totalCount}"
                    )
                ques.submit(successCallback=submitSuccess)

    def fillTextQues(self, field: ChromiumElement, oneRolePref: dict):
        quesText = field.s_ele("css:.field-label").text
        rolePrefQuesList = oneRolePref["填空题"]

        # 从角色偏好配置中找到匹配的题目和答案
        matchingRolePrefQues = next(
            (
                rolePrefQues
                for rolePrefQues in rolePrefQuesList
                if quesText == rolePrefQues["题目"]
            ),
            None,
        )
        if not matchingRolePrefQues:
            raise ValueError("当前题目在角色偏好配置中不存在。")

        # 填写答案
        field.ele("tag:input").input(matchingRolePrefQues["答案"])

    # TODO fillSingleChoiceQues 和 fillMultiChoiceQues 相似度很高
    def fillSingleChoiceQues(self, field: ChromiumElement, oneRolePref: dict):

        # TODO 这里获取quesText和下面获取choice 和rolePreference里的重复出现了，
        # 对DrissionPage的控制可以合并到Questionnaire里
        quesText = field.s_ele("css:.field-label").text
        rolePrefQuesList = oneRolePref["单选题"]

        # 从角色偏好配置中找到匹配的题目和权重
        matchingRolePrefQues = next(
            (
                rolePrefQues
                for rolePrefQues in rolePrefQuesList
                if quesText == rolePrefQues["题目"]
            ),
            None,
        )
        if not matchingRolePrefQues:
            raise ValueError("当前题目在角色偏好配置中不存在。")

        # 根据权重做出选择
        choiceWeights: dict = matchingRolePrefQues["选项权重"]
        choices = list(choiceWeights.keys())
        weights = [choiceWeights[choice] for choice in choices]
        selectedChoice = random.choices(choices, weights=weights, k=1)[0]
        for choice in field.eles("css:.label"):
            if choice.text == selectedChoice:
                choice.click()
                break

    def fillMultiChoiceQues(self, field: ChromiumElement, oneRolePref: dict):
        quesText = field.s_ele("css:.field-label").text
        rolePrefQuesList = oneRolePref["多选题"]

        # 从角色偏好配置中找到匹配的题目和权重
        matchingRolePrefQues = next(
            (
                rolePrefQues
                for rolePrefQues in rolePrefQuesList
                if quesText == rolePrefQues["题目"]
            ),
            None,
        )
        if not matchingRolePrefQues:
            raise ValueError("当前题目在角色偏好配置中不存在。")

        # 根据权重做出选择
        choiceWeights: dict = matchingRolePrefQues["选项权重"]
        choices = list(choiceWeights.keys())
        weights = [choiceWeights[choice] for choice in choices]
        choiceNumber = random.randint(2, len(choices))
        selectedChoices = random.choices(
            choices, weights=weights, k=choiceNumber)
        for choice in field.eles("css:.label"):
            if choice.text in selectedChoices:
                choice.click()

    def getRecord(self) -> dict:
        parent = os.path.dirname(os.path.abspath(__file__))
        recordPath = os.path.join(parent, "record.json")
        if not os.path.exists(recordPath):
            return {}
        with open(recordPath, "r", encoding="utf-8") as f:
            return json.load(f)

    def setRecord(self, record: dict) -> dict:
        parent = os.path.dirname(os.path.abspath(__file__))
        recordPath = os.path.join(parent, "record.json")
        with open(recordPath, "w", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    QuestionareFiller()