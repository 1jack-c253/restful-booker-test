# Restful Booker Platform 测试项目

对公开练习平台 [automationintesting.online](https://automationintesting.online)（Restful Booker Platform）
的**接口测试**与 **UI 自动化测试**。

项目包含两套测试：接口层用 `requests`，界面层用 `Selenium`（Firefox）。

---

## 一、测试执行结果

```
8 passed, 2 xfailed in 21.01s
```

| 结果 | 数量 | 说明 |
|---|---|---|
| ✅ 通过 | 8 | |
| ⚠️ xfail（预期失败） | 2 | **已知接口缺陷**，见 §三 |
| ❌ 失败 | 0 | |

> 使用 `pytest.mark.xfail` 标记已知缺陷：测试本身的断言是正确的，
> 但被测接口当前存在缺陷，因此标记为「预期失败」并在 `reason` 中记录缺陷详情。
> **待服务端修复后，这两条会自动变成 XPASS（意外通过），提示可以移除标记。**

---

## 二、测试覆盖范围

### 接口测试（`test_api.py`，10 条用例）

| 分类 | 用例 | 验证点 |
|---|---|---|
| **查询** | `test_get_rooms` | 房间列表返回 200，房间数正确 |
| | `test_get_room_by_id` | 按 id 查询，房间号 / 类型字段正确 |
| | `test_get_invalid_room` | **查询不存在的房间号**（反向用例）→ 见缺陷 ① |
| **认证** | `test_login` | 登录返回 token |
| | `test_get_booking_without_auth` | **未登录访问订单接口**，应返回 401 |
| | `test_get_booking_with_auth` | 登录后携带 token 访问，应返回 200 |
| **创建** | `test_create_booking` | 创建成功返回 201 与 bookingid |
| **完整流程** | `test_create_and_get_booking` | 创建 → 查询 → **比对创建与查询的数据一致性** |
| | `test_create_and_update_booking` | 创建 → 修改 → 验证 → 见缺陷 ② |
| | `test_create_and_delete_booking` | 创建 → 删除 → **再次查询断言返回 404**，确认数据真的被删除 |

**几个设计要点：**

- **认证用 `requests.Session()`**：Session 会保留 Cookie，登录一次后后续请求自动携带凭证
- **反向测试**：不只测「正常能通过」，还测「异常输入应该被拒绝」——未授权访问、不存在的资源
- **链式验证**：创建接口返回的 `bookingid` 自动取出，供后续查询 / 修改 / 删除使用，而非写死
- **删除后二次确认**：删除接口返回成功不代表数据真的没了，因此删完再查一次，断言 404

### UI 自动化测试（`test_selenium.py`，3 条用例）

| 用例 | 验证点 |
|---|---|
| `test_open_website` | 打开首页，校验页面标题 |
| `test_rooms` | 进入房间列表，校验 Single / Double / Suite 三种房型 |
| `test_create_booking` | **端到端预订流程**：选房 → 进入预订页 → 填写姓名 / 邮箱 / 电话 → 提交 → 断言「Booking Confirmed」与入住 / 退房日期 |

**几个设计要点：**

- **显式等待（`WebDriverWait`）**：所有元素操作前均等待元素可点击 / 可见，而非使用 `time.sleep` 死等
- **多种定位方式**：`By.ID`、`By.NAME`、`By.XPATH`、`By.LINK_TEXT`、`By.TAG_NAME`
- **`try / finally` 保证浏览器关闭**：即使断言失败也不会残留浏览器进程
- **等待导航完成**：点击「Book now」后用 `url_contains("/reservation/")` 等待跳转，而非固定等待

---

## 三、发现的接口缺陷

### 缺陷 ①：查询不存在的房间号返回 500 而非 404

```http
GET /api/room/999   →  500 Internal Server Error   （期望 404 Not Found）
```

**对比实验**（确认问题边界）：

| 请求 | 返回 | 说明 |
|---|---|---|
| `GET /api/room/abc` | 404 | 非数字，正常返回未找到 |
| `GET /api/room/-1` | 404 | 负数，正常返回未找到 |
| `GET /api/room/999` | **500** | 数字格式合法但记录不存在 → **崩溃** |
| `GET /api/room/0` | **500** | 同上 |

**结论**：服务端对「查询无结果」这一分支未做处理，直接抛出了异常。
合理行为应是统一返回 404。

### 缺陷 ②：更新预订时 roomid 不变则返回 409

```http
PUT /api/booking/{id}   →  409 Conflict   （期望 200 OK）
```

**对比实验**（5 组，与日期无关，只看 roomid 是否变化）：

| 创建于 | 修改为 | 结果 |
|---|---|---|
| 房间 3 | 房间 3（数据原样不动） | **409** |
| 房间 3 | 房间 3（改短日期） | **409** |
| 房间 3 | **房间 2** | 200 ✅ |
| 房间 1 | 房间 1（数据原样不动） | **409** |
| 房间 1 | **房间 2** | 200 ✅ |

**结论**：只要 PUT 请求中的 `roomid` 与创建时相同，服务端就返回冲突；
换成其他房间则成功。推测服务端在做房间可用性校验时，
**把该预订自身也判定为「占用」**，导致自冲突。合理行为应是更新时跳过对自身的可用性冲突判定。

---

## 四、关于测试数据清理

这个站点是**公开沙箱**，任何人都可以写入数据。实测房间 1 中已累积 12 条来自
不同测试者的预订数据。

因此本项目遵循一个原则：**测试自己创建的数据，测试自己清理。**

`test_api.py` 中的 `cleanup_booking()` 用于在用例执行后删除本次创建的预订，
避免反复执行污染环境、影响后续用例（清理动作放在断言之前，保证断言失败时也能执行到）。

> 早期版本缺少这步清理，导致每次执行都会在房间中留下一条预订。

---

## 五、运行方式

```bash
pip install -r requirements.txt
```

### 接口测试

```bash
pytest test_api.py -v
```

### UI 自动化测试

需要先准备 Firefox 与 geckodriver，并在 `test_selenium.py` 的 `create_driver()`
中配置本机路径；然后：

```bash
pytest test_selenium.py -v
```

> 提示：Windows 上若 `python` 命令被 Microsoft Store 存根占用，请使用 Python 完整路径。

---

## 六、技术栈

| | |
|---|---|
| 语言 | Python 3.13 |
| 接口测试 | requests + pytest |
| UI 自动化 | Selenium（Firefox + geckodriver） |
| 测试框架 | pytest 9.1.1（含 `xfail` 标记已知缺陷） |
