import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# 创建 Firefox 浏览器
# ============================================================

def create_driver():

    # 指定 geckodriver
    service = Service(
        r"C:\Users\Administrator\restful-booker-test\geckodriver.exe"
    )

    # 指定 Firefox
    options = Options()
    options.binary_location = r"E:\APP\firefox.exe"

    # 创建浏览器
    driver = webdriver.Firefox(
        service=service,
        options=options
    )

    return driver


# ============================================================
# 测试1：打开酒店网站
# ============================================================

def test_open_website():

    driver = create_driver()

    try:

        # 打开酒店网站
        driver.get(
            "https://automationintesting.online"
        )

        # 等待页面加载
        time.sleep(3)

        print("网页标题：", driver.title)

        # 验证网页标题
        assert "Restful-booker-platform" in driver.title

        print("网页打开成功")

    finally:

        driver.quit()


# ============================================================
# 测试2：验证房间类型
# ============================================================

def test_rooms():

    driver = create_driver()

    try:

        # 打开酒店网站
        driver.get(
            "https://automationintesting.online"
        )

        # 找到 Rooms
        rooms = WebDriverWait(
            driver,
            10
        ).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, "Rooms")
            )
        )

        # 点击 Rooms
        rooms.click()

        print("已点击 Rooms")

        # 等待房间加载
        WebDriverWait(
            driver,
            10
        ).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(text(), 'Single')]"
                )
            )
        )

        # 获取页面文字
        page_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        # 验证三种房型
        assert "Single" in page_text
        assert "Double" in page_text
        assert "Suite" in page_text

        print("Single / Double / Suite 验证成功")

    finally:

        driver.quit()


# ============================================================
# 测试3：自动完成房间预订并验证结果
# ============================================================

def test_create_booking():

    driver = create_driver()

    try:

        # ====================================================
        # 第一步：打开网站
        # ====================================================

        driver.get(
            "https://automationintesting.online"
        )

        print("已打开酒店网站")

        # ====================================================
        # 第二步：等待房间列表加载
        # ====================================================

        WebDriverWait(
            driver,
            10
        ).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(text(), 'Single')]"
                )
            )
        )

        print("房间列表加载完成")

        # ====================================================
        # 第三步：找到 Book now
        # ====================================================

        book_buttons = WebDriverWait(
            driver,
            10
        ).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//a[contains(@class, 'btn-primary') "
                    "and normalize-space()='Book now']"
                )
            )
        )

        print(
            "找到 Book now 数量：",
            len(book_buttons)
        )

        # 确认找到房间
        assert len(book_buttons) > 0

        # ====================================================
        # 第四步：点击第一个房间
        # ====================================================

        book_buttons[0].click()

        print("已点击 Single Room 的 Book now")

        # ====================================================
        # 第五步：等待进入预订页面
        # ====================================================

        WebDriverWait(
            driver,
            10
        ).until(
            EC.url_contains("/reservation/")
        )

        print(
            "已经进入预订页面：",
            driver.current_url
        )

        # ====================================================
        # 第六步：点击第一个 Reserve Now
        # ====================================================

        reserve_button = WebDriverWait(
            driver,
            20
        ).until(
            EC.element_to_be_clickable(
                (By.ID, "doReservation")
            )
        )

        print("已找到第一个 Reserve Now")

        reserve_button.click()

        print("已点击第一个 Reserve Now")

        # ====================================================
        # 第七步：等待填写信息页面
        # ====================================================

        firstname = WebDriverWait(
            driver,
            20
        ).until(
            EC.visibility_of_element_located(
                (By.NAME, "firstname")
            )
        )

        print("填写信息页面加载成功")

        # ====================================================
        # 第八步：填写 Firstname
        # ====================================================

        firstname.clear()
        firstname.send_keys("AutoTest")

        print("Firstname 填写成功")

        # ====================================================
        # 第九步：填写 Lastname
        # ====================================================

        lastname = WebDriverWait(
            driver,
            10
        ).until(
            EC.visibility_of_element_located(
                (By.NAME, "lastname")
            )
        )

        lastname.clear()
        lastname.send_keys("User")

        print("Lastname 填写成功")

        # ====================================================
        # 第十步：填写 Email
        # ====================================================

        email = WebDriverWait(
            driver,
            10
        ).until(
            EC.visibility_of_element_located(
                (By.NAME, "email")
            )
        )

        email.clear()
        email.send_keys("autotest@example.com")

        print("Email 填写成功")

        # ====================================================
        # 第十一步：填写 Phone
        # ====================================================

        phone = WebDriverWait(
            driver,
            10
        ).until(
            EC.visibility_of_element_located(
                (By.NAME, "phone")
            )
        )

        phone.clear()
        phone.send_keys("12345678901")

        print("Phone 填写成功")
        print("所有预订信息填写完成")

        # ====================================================
        # 第十二步：找到最终 Reserve Now
        # ====================================================

        final_reserve_button = WebDriverWait(
            driver,
            20
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[normalize-space()='Reserve Now']"
                )
            )
        )

        print("已找到最终 Reserve Now 按钮")

        # ====================================================
        # 第十三步：提交预订
        # ====================================================

        final_reserve_button.click()

        print("已点击最终 Reserve Now")

        # ====================================================
        # 第十四步：等待 Booking Confirmed
        # ====================================================

        WebDriverWait(
            driver,
            20
        ).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(text(), 'Booking Confirmed')]"
                )
            )
        )

        print("Booking Confirmed 已出现")

        # ====================================================
        # 第十五步：获取确认页面文字
        # ====================================================

        page_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        print("确认页面内容：")
        print(page_text)

        # ====================================================
        # 第十六步：验证预订成功
        # ====================================================

        assert "Booking Confirmed" in page_text

        print("Booking Confirmed 验证通过")

        # ====================================================
        # 第十七步：验证入住日期
        # ====================================================

        assert "2026-09-08" in page_text

        print("入住日期验证通过")

        # ====================================================
        # 第十八步：验证退房日期
        # ====================================================

        assert "2026-09-09" in page_text

        print("退房日期验证通过")

        # ====================================================
        # 最终结果
        # ====================================================

        print("")
        print("========================================")
        print("Selenium 自动预订测试：PASS")
        print("预订结果验证：PASS")
        print("========================================")

    finally:

        # 关闭浏览器
        driver.quit()