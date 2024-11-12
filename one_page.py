from DrissionPage import Chromium
from DrissionPage._elements.chromium_element import ChromiumElement
import random


def handle_one_page(url, must_choices):

    chromium = Chromium()
    page = chromium.get_tab()
    page.get(url)
    fields = page.eles("css:.field")

    def handle_tip():
        sign = page.s_ele("之前已经回答了部分题目")
        if sign:
            ele = page.ele("css:.layui-layer-btn1")
            if ele:
                ele.click()
    import time
    time.sleep(2)
    handle_tip()

    for f in fields:
        # handle_tip()
        if type(f) is ChromiumElement:
            _type = f.attr('type')
            if _type == '3':
                radios: list[ChromiumElement] = f.eles("css:.ui-radio")
                must_choice = [
                    radio for radio in radios if radio.text in must_choices]
                if len(must_choice) != 0:
                    [c.click() for c in must_choice]
                else:
                    radio = random.choice(radios)
                    if type(radio) is ChromiumElement:
                        radio.click()
            if _type == '4':
                checkboxs = f.eles("css:.ui-checkbox")
                must_choice = [
                    checkbox for checkbox in checkboxs if checkbox.text in must_choices]
                if len(must_choice) != 0:
                    [c.click() for c in must_choice]
                else:
                    num = int(0.5 * len(checkboxs))
                    boxs = random.choices(checkboxs, k=num)
                    [box.click() for box in boxs]

    page.ele("css:#SubmitBtnGroup").click()
    time.sleep(3)
    chromium.quit()
