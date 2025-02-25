from DrissionPage._elements.chromium_element import ChromiumElement
from .Questionnaire import Questionnaire
import random
import time
import os
import json
from .Config import Config
from .logger import logger


class RolePreferenceManager:
    """
    管理角色偏好配置。
    包含一个default和每个role的偏好
    """

    parentPath = os.path.dirname(os.path.abspath(__file__))
    rolePrefConfDir = os.path.join(
        parentPath, "configs", "RolePreferenceConfigs")

    @classmethod
    def rolePrefConfExists(cls):
        return os.path.exists(cls.rolePrefConfDir)

    def __init__(self):

        if not self.rolePrefConfExists():
            logger.info("检测到RolePreferenceConfigs不存在,创建配置")
            self.createRandomRolePrefConfig()
        else:
            logger.info("RolePreferenceConfigs已存在")

        # 获取目录下所有roles
        # 二编，这里的roles会在QuesFiller里使用。
        self.roles = []
        for filename in os.listdir(self.rolePrefConfDir):
            filepath = os.path.join(self.rolePrefConfDir, filename)
            if not os.path.isfile(filepath):
                continue
            roleName = os.path.splitext(filename)[0]  # 去除文件后缀
            if roleName == "default":
                continue
            self.roles.append(roleName)

    def getPrefByRole(self, role: str):
        if role not in self.roles:
            raise ValueError(f"角色 '{role}' 不存在")
        rolePrefConfPath = os.path.join(self.rolePrefConfDir, f"{role}.json")
        if not os.path.exists(rolePrefConfPath):
            raise FileNotFoundError(
                f"角色 '{role}' 的配置文件 '{rolePrefConfPath}' 不存在"
            )

        defaultRolePrefConfPath = os.path.join(
            self.rolePrefConfDir, "default.json")
        with open(defaultRolePrefConfPath, "r", encoding="utf-8") as f:
            defaultPrefConf: dict = json.loads(f.read())

        with open(rolePrefConfPath, "r", encoding="utf-8") as f:
            rolePrefConf: dict = json.loads(f.read())

        # 合并两个dict
        for quesType in ["单选", "多选"]:
            exists = rolePrefConf.get(quesType, None)
            if not exists:
                continue
            for quesDict in rolePrefConf[quesType]:
                quesText = quesDict["题目"]
                for index, defaultQuesDict in enumerate(defaultPrefConf[quesType]):
                    defaultQuesText = defaultQuesDict["题目"]
                    if quesText == defaultQuesText:
                        defaultPrefConf[quesType][index] = quesDict
                        break

        updatedPrefConf = defaultPrefConf
        return updatedPrefConf

    def createRandomRolePrefConfig(self):
        """
        根据configs/config.json的roleCount字段，创建随机的角色偏好配置文件
        """
        if os.path.exists(self.rolePrefConfDir):
            raise FileExistsError(
                "试图创建RolePreferenceConfig，但wjx.configs.RolePreferenceConfigs 目录已存在，为避免误操作，请删除wjx.configs.RolePreferenceConfigs 后重试"
            )
        else:
            os.mkdir(self.rolePrefConfDir)

        self.singleChoiceQuestions = []
        self.multiChoicesQuestions = []
        self.textQuestions = []
        ques = Questionnaire()
        ques.walkQuestions(
            _type=Questionnaire.questionType["单选题"],
            callback=self.extractSingleChoice,
        )
        ques.walkQuestions(
            _type=Questionnaire.questionType["多选题"],
            callback=self.extractMultipleChoices,
        )
        ques.walkQuestions(
            _type=Questionnaire.questionType["填空题"],
            callback=self.extractTextQues,
        )
        rolePrefConfTemplate = {
            "单选题": self.singleChoiceQuestions,
            "多选题": self.multiChoicesQuestions,
            "填空题": self.textQuestions,
        }

        templateString = json.dumps(
            rolePrefConfTemplate, ensure_ascii=False, indent=4)
        defaultRolePrefConfPath = os.path.join(
            self.rolePrefConfDir, "default.json")
        with open(defaultRolePrefConfPath, "w", encoding="utf-8") as f:
            f.write(templateString)

        for role in Config()["roleCount"]:
            specRolePrefConfPath = os.path.join(
                self.rolePrefConfDir, f"{role}.json")
            with open(specRolePrefConfPath, "w", encoding="utf-8") as f:
                f.write(templateString)
        logger.info("RolePreferenceConfigs生成完毕。")

    def extractTextQues(self, field: ChromiumElement):
        """
        提取填空题的题目和选项
        """
        question = field.s_ele("css:.field-label").text
        result = {"题目": question, "答案": "无"}
        self.textQuestions.append(result)

    # TODO extractSingleChoice 和 extractMultipleChoices 相似度很高

    def extractSingleChoice(self, field: ChromiumElement):
        """
        提取单选题的题目和选项
        """
        # TODO field.s_ele("css:.field-label").text被用了四次，
        # 应该单独写一个Question类，里面写一个getQuestionText方法，walkQuestions应该返回Question对象
        question = field.s_ele("css:.field-label").text
        choices = [choice.text for choice in field.s_eles("css:.label")]
        result = {"题目": question, "选项权重": {}}
        for choice in choices:
            result["选项权重"][choice] = random.randint(1, 5)
        self.singleChoiceQuestions.append(result)

    def extractMultipleChoices(self, field: ChromiumElement):
        """
        提取多选题的题目和选项
        """
        question = field.s_ele("css:.field-label").text
        choices = [choice.text for choice in field.s_eles("css:.label")]
        result = {"题目": question, "选项权重": {}}
        for choice in choices:
            result["选项权重"][choice] = random.randint(1, 5)
        self.multiChoicesQuestions.append(result)


if __name__ == "__main__":
    RolePreferenceManager()
