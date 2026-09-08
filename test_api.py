import requests


def test_get_rooms():
    response = requests.get("https://automationintesting.online/api/room")

    assert response.status_code == 200
    assert "rooms" in response.json()
    assert len(response.json()["rooms"]) == 3


def test_get_room_by_id():
    response = requests.get("https://automationintesting.online/api/room/1")

    assert response.status_code == 200
    assert response.json()["roomid"] == 1
    assert response.json()["roomName"] == "101"
    assert response.json()["type"] == "Single"
def test_get_invalid_room():
    response = requests.get("https://automationintesting.online/api/room/999")

    assert response.status_code == 404


def test_get_booking_without_auth():
    response = requests.get(
        "https://automationintesting.online/api/booking/?roomid=1"
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Authentication required"

def test_create_booking():
    url = "https://automationintesting.online/api/booking/"

    data = {
        "roomid": 1,
        "firstname": "AutoTest",
        "lastname": "User",
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-10-20",
            "checkout": "2026-10-25"
        }
    }

    response = requests.post(url, json=data)

    assert response.status_code == 201
    assert "bookingid" in response.json()

def test_login():
    url = "https://automationintesting.online/api/auth/login"

    data = {
        "username": "admin",
        "password": "password"
    }

    response = requests.post(url, json=data)

    assert response.status_code == 200
    assert "token" in response.json()


def test_get_booking_with_auth():
    # ========================================
    # 第一步：创建一个 Session
    # ========================================

    # Session 可以理解成一个“会记住 Cookie 的浏览器”
    # 后面的请求会自动使用前面服务器返回的 Cookie
    session = requests.Session()

    # ========================================
    # 第二步：登录系统
    # ========================================

    # 登录接口地址
    login_url = "https://automationintesting.online/api/auth/login"

    # 登录账号和密码
    login_data = {
        "username": "admin",
        "password": "password"
    }

    # 使用 Session 发送登录请求
    login_response = session.post(
        login_url,
        json=login_data
    )

    # 确认登录成功
    assert login_response.status_code == 200

    # 获取登录返回的 Token
    token = login_response.json()["token"]

    # 确认 Token 不为空
    print("Token 是否获取成功：", bool(token))
    print("Token 长度：", len(token))

    # ========================================
    # 第三步：手动把 Token 保存到 Session Cookie
    # ========================================

    # 把 Token 保存到 Session 的 Cookie 中
    session.cookies.set(
        "token",
        token,
        domain="automationintesting.online"
    )

    # ========================================
    # 第四步：查询 Booking
    # ========================================

    # Booking 查询接口
    booking_url = (
        "https://automationintesting.online/api/booking/?roomid=1"
    )

    # 使用同一个 Session 发送请求
    # Cookie 会自动带上
    response = session.get(booking_url)

    # 打印实际结果
    print("Booking 查询状态码：", response.status_code)
    print("Booking 查询结果：", response.text)

    # 查询成功应该返回 200
    assert response.status_code == 200

def test_create_and_get_booking():
    # ========================================
    # 第一步：创建一个 Session
    # ========================================

    # Session 可以保存 Cookie，方便后续请求继续使用
    session = requests.Session()

    # ========================================
    # 第二步：登录获取 Token
    # ========================================

    # 登录接口地址
    login_url = "https://automationintesting.online/api/auth/login"

    # 登录账号和密码
    login_data = {
        "username": "admin",
        "password": "password"
    }

    # 发送登录请求
    login_response = session.post(
        login_url,
        json=login_data
    )

    # 确认登录成功
    assert login_response.status_code == 200

    # 获取 Token
    token = login_response.json()["token"]

    # 把 Token 保存到 Session 的 Cookie 中
    session.cookies.set(
        "token",
        token,
        domain="automationintesting.online"
    )

    # ========================================
    # 第三步：创建预订
    # ========================================

    # 创建 Booking 的接口地址
    create_url = "https://automationintesting.online/api/booking/"

    # 预订数据
    booking_data = {
        "roomid": 1,
        "firstname": "AutoFlow",
        "lastname": "Test",
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-10",
            "checkout": "2026-11-15"
        }
    }

    # 发送创建预订请求
    create_response = session.post(
        create_url,
        json=booking_data
    )

    # 打印创建结果
    print("创建预订状态码：", create_response.status_code)
    print("创建预订结果：", create_response.text)

    # 创建成功应该返回 201
    assert create_response.status_code == 201

    # ========================================
    # 第四步：自动获取 bookingid
    # ========================================

    # 从创建预订的响应中获取 bookingid
    booking_id = create_response.json()["bookingid"]

    # 确认 bookingid 成功获取
    print("自动获取的 bookingid：", booking_id)

    # ========================================
    # 第五步：查询刚刚创建的预订
    # ========================================

    # 把刚才自动获取的 bookingid 放进 URL
    get_url = (
        f"https://automationintesting.online/api/booking/{booking_id}"
    )

    # 查询 Booking
    get_response = session.get(get_url)

    # 打印查询结果
    print("查询预订状态码：", get_response.status_code)
    print("查询预订结果：", get_response.text)

    # 查询成功应该返回 200
    assert get_response.status_code == 200

    # ========================================
    # 第六步：验证创建的数据和查询的数据一致
    # ========================================

    # 获取查询结果
    result = get_response.json()

    # 验证 bookingid 一致
    assert result["bookingid"] == booking_id

    # 验证房间一致
    assert result["roomid"] == 1

    # 验证姓名一致
    assert result["firstname"] == "AutoFlow"
    assert result["lastname"] == "Test"

    # 验证入住日期一致
    assert result["bookingdates"]["checkin"] == "2026-11-10"

    # 验证退房日期一致
    assert result["bookingdates"]["checkout"] == "2026-11-15"

    # 如果运行到这里，说明整个流程验证成功
    print("创建预订 → 查询预订 → 数据一致，测试通过")

def test_create_and_update_booking():
    # ========================================
    # 第一步：创建 Session，并登录
    # ========================================

    # Session 可以保存认证信息，方便后续请求使用
    session = requests.Session()

    login_url = "https://automationintesting.online/api/auth/login"

    login_data = {
        "username": "admin",
        "password": "password"
    }

    # 登录获取 Token
    login_response = session.post(
        login_url,
        json=login_data
    )

    # 登录必须成功
    assert login_response.status_code == 200

    # 获取 Token
    token = login_response.json()["token"]

    # 将 Token 保存到 Cookie
    session.cookies.set(
        "token",
        token,
        domain="automationintesting.online"
    )

    # ========================================
    # 第二步：创建预订
    # ========================================

    create_url = "https://automationintesting.online/api/booking/"

    create_data = {
        "roomid": 1,
        "firstname": "BeforeUpdate",
        "lastname": "User",
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-12-05"
        }
    }

    # 创建预订
    create_response = session.post(
        create_url,
        json=create_data
    )

    print("创建预订状态码：", create_response.status_code)

    # 创建成功应该返回 201
    assert create_response.status_code == 201

    # 自动获取 bookingid
    booking_id = create_response.json()["bookingid"]

    print("创建的 bookingid：", booking_id)

    # ========================================
    # 第三步：修改预订
    # ========================================

    # 使用刚才自动获取的 bookingid
    update_url = (
        f"https://automationintesting.online/api/booking/{booking_id}"
    )

    # 修改后的数据
    update_data = {
        "roomid": 1,
        "firstname": "AfterUpdate",
        "lastname": "UpdatedUser",
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-12-02",
            "checkout": "2026-12-06"
        }
    }

    # 发送 PUT 请求修改预订
    update_response = session.put(
        update_url,
        json=update_data,
        headers={
            "Referer": "https://automationintesting.online/"
        }
    )

    print("修改预订状态码：", update_response.status_code)
    print("修改结果：", update_response.text)

    # 修改成功应该返回 200
    assert update_response.status_code == 200

    # ========================================
    # 第四步：验证修改结果
    # ========================================

    result = update_response.json()["booking"]

    # 验证姓名已经修改
    assert result["firstname"] == "AfterUpdate"
    assert result["lastname"] == "UpdatedUser"

    # 验证押金状态已经修改
    assert result["depositpaid"] is False

    # 验证日期已经修改
    assert result["bookingdates"]["checkin"] == "2026-12-02"
    assert result["bookingdates"]["checkout"] == "2026-12-06"

    print("创建 → 修改 → 验证，测试通过")


def test_create_and_delete_booking():
    # ========================================
    # 第一步：创建 Session，并登录
    # ========================================

    session = requests.Session()

    login_url = "https://automationintesting.online/api/auth/login"

    login_data = {
        "username": "admin",
        "password": "password"
    }

    # 登录
    login_response = session.post(
        login_url,
        json=login_data
    )

    # 登录必须成功
    assert login_response.status_code == 200

    # 获取 Token
    token = login_response.json()["token"]

    # 将 Token 保存到 Cookie
    session.cookies.set(
        "token",
        token,
        domain="automationintesting.online"
    )

    # ========================================
    # 第二步：创建一个测试预订
    # ========================================

    create_url = "https://automationintesting.online/api/booking/"

    create_data = {
        "roomid": 1,
        "firstname": "DeleteTest",
        "lastname": "User",
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-01-10",
            "checkout": "2027-01-15"
        }
    }

    create_response = session.post(
        create_url,
        json=create_data
    )

    print("创建预订状态码：", create_response.status_code)

    # 创建成功应该返回 201
    assert create_response.status_code == 201

    # 自动获取 bookingid
    booking_id = create_response.json()["bookingid"]

    print("创建的 bookingid：", booking_id)

    # ========================================
    # 第三步：删除刚刚创建的预订
    # ========================================

    delete_url = (
        f"https://automationintesting.online/api/booking/{booking_id}"
    )

    # 发送 DELETE 请求
    delete_response = session.delete(
        delete_url,
        headers={
            "Referer": "https://automationintesting.online/"
        }
    )

    print("删除预订状态码：", delete_response.status_code)
    print("删除结果：", delete_response.text)

    # 删除成功应该返回 202
    assert delete_response.status_code == 202

    # ========================================
    # 第四步：再次查询，确认已经删除
    # ========================================

    get_url = (
        f"https://automationintesting.online/api/booking/{booking_id}"
    )

    get_response = session.get(get_url)

    print("删除后查询状态码：", get_response.status_code)

    # 已删除的 Booking 应该不存在
    assert get_response.status_code == 404

    print("创建 → 删除 → 验证不存在，测试通过")