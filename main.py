from one_page import handle_one_page
import random
from random import choice, choices


def start_loop(count, url, get_character, get_preference):
    """
    循环填写问卷
    @param count: 填写多少份问卷
    """
    loop = 0
    while True:
        handle_one_page(url)
        loop += 1
        print(loop)
        if loop > count:
            break


def get_random_preference():
    li = [
        choices(["品牌知名度", '产品效果', '价格', '用户评价', '包装设计', '促销活动'],
                k=random.randint(1, 5)),
        choices(["非常了解", '较为了解', '一般', '信任与自豪', '好奇想尝试'],
                k=random.randint(1, 4)),
        choices(["获得正面用户评价", '价格优惠', '获得专业认证', '有明星代言'],
                k=random.randint(1, 3)),
        choices(['每季度至少一次', '偶尔购买'], k=1),
    ]
    li2 = []
    [li2.extend(ele) for ele in li]
    return choices(li2, k=random.randint(0, len(li2)))


def get_random_character():

    return choice([
        ['18-24岁', '学生', '3000元以下'],
        [choice(['18-24岁', '25-34岁', '35-44岁']), choice(['上班族', '自由职业者']),
         choice(['3000-5000元', '5001-8000元', '8001-12000元', '12001元以上'])],
    ])


def main():
    url = "https://www.wjx.cn/vm/Oxelygh.aspx"  # 问卷地址
    count = 80  # 要多少份问卷

    def get_random_choices():
        choices = []
        choices.extend(get_random_character())
        choices.extend(get_random_preference())
        return choices
    loop = 0
    while True:
        handle_one_page(url, get_random_choices())
        loop += 1
        print(loop)
        if loop > count:
            break


if __name__ == '__main__':
    main()
