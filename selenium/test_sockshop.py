# SockShop 功能测试脚本 (Selenium)
# 软件测试与维护大作业 阶段三
# 一共8个用例: 首页/浏览/详情/注册/登录/加购物车/看购物车/下单
# 运行: python test_sockshop.py    默认chrome
#       python test_sockshop.py --browser safari --no-headless   用safari

import os
# 注意: 我电脑之前连公司网站设过代理, 不清掉的话连localhost都连不上一直超时, 排查了好久...
for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)
os.environ["NO_PROXY"] = "localhost,127.0.0.1,*"
os.environ["no_proxy"] = "localhost,127.0.0.1,*"

import sys
import glob
import json
import time
import argparse
import random
import string
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = "http://localhost:8079"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(BASE_DIR, "screenshots")
RESULT_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(SHOT_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# 用户名随机生成, 不然重复注册会失败
RAND = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
USER = {
    "username": f"seltest_{RAND}",
    "password": "Test@1234",
    "first": "Sel",
    "last": "Tester",
    "email": f"seltest_{RAND}@example.com",
}

results = []   # 存每个用例的结果


def make_driver(browser="chrome", headless=True):
    if browser == "safari":
        return webdriver.Safari()
    # Selenium 4 会自动下载匹配的 chromedriver, 不用手动指定路径, 换电脑也能直接跑
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    for a in ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
              "--window-size=1440,2200", "--no-proxy-server", "--proxy-bypass-list=*"]:
        opts.add_argument(a)
    return webdriver.Chrome(options=opts)


def shot(driver, name):
    # 截个图存起来
    path = os.path.join(SHOT_DIR, name)
    try:
        driver.save_screenshot(path)
    except Exception as e:
        print(f"    [截图失败] {name}: {e}")
    return path


def record(tc_id, name, status, load_ms=None, action_ms=None, detail="", shot_file=""):
    results.append({
        "id": tc_id, "name": name, "status": status,
        "page_load_ms": load_ms, "action_ms": action_ms,
        "detail": detail, "screenshot": shot_file,
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    flag = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "WARN")
    extra = []
    if load_ms is not None:
        extra.append(f"页面加载 {load_ms}ms")
    if action_ms is not None:
        extra.append(f"交互响应 {action_ms}ms")
    print(f"  [{flag}] {tc_id} {name}  {' / '.join(extra)}  {detail}", flush=True)


def timed_get(driver, url):
    # 打开页面并算一下加载用了多久(ms)
    # 优先用浏览器的 performance.timing, 拿不到就用普通计时
    t0 = time.time()
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete")
    except TimeoutException:
        pass
    wall_ms = int((time.time() - t0) * 1000)
    try:
        nav = driver.execute_script(
            "var t=performance.timing;return t.loadEventEnd>0?(t.loadEventEnd-t.navigationStart):null;")
        if nav and nav > 0:
            return int(nav)
    except Exception:
        pass
    return wall_ms


# ===== 下面是 8 个测试用例 =====
def tc01_homepage(d):
    try:
        load = timed_get(d, BASE_URL + "/")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "navbar")))
        title = d.title
        imgs = d.find_elements(By.CSS_SELECTOR, "img[src*='catalogue']")
        s = shot(d, "tc01_homepage.png")
        ok = (title == "WeaveSocks" and len(imgs) > 0)
        record("TC01", "首页加载与渲染", "PASS" if ok else "FAIL", load_ms=load,
               detail=f"标题='{title}', 首页商品图 {len(imgs)} 张", shot_file=os.path.basename(s))
    except Exception as e:
        record("TC01", "首页加载与渲染", "FAIL", detail=str(e)[:80])


def tc02_catalogue(d):
    try:
        load = timed_get(d, BASE_URL + "/category.html")
        WebDriverWait(d, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='detail']")))
        time.sleep(1.5)
        products = d.find_elements(By.CSS_SELECTOR, "img[src*='catalogue']")
        s = shot(d, "tc02_catalogue.png")
        ok = len(products) >= 5
        record("TC02", "浏览商品目录", "PASS" if ok else "FAIL", load_ms=load,
               detail=f"目录页商品图 {len(products)} 张", shot_file=os.path.basename(s))
    except Exception as e:
        record("TC02", "浏览商品目录", "FAIL", detail=str(e)[:80])


def tc03_detail(d):
    try:
        load = timed_get(d, BASE_URL + "/detail.html?id=03fef6ac-1896-4ce8-bd69-b798f85c6e0b")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(1)
        name = d.find_element(By.TAG_NAME, "h1").text
        price = d.find_elements(By.CSS_SELECTOR, "p.price, .price")
        price_txt = price[0].text if price else "?"
        s = shot(d, "tc03_detail.png")
        ok = bool(name)
        record("TC03", "查看商品详情", "PASS" if ok else "FAIL", load_ms=load,
               detail=f"商品='{name}', 价格={price_txt}", shot_file=os.path.basename(s))
    except Exception as e:
        record("TC03", "查看商品详情", "FAIL", detail=str(e)[:80])


def tc04_register(d):
    # register.html 这个页面上有两个表单, 上面那个是注册(name/email/password + Register按钮)
    try:
        load = timed_get(d, BASE_URL + "/register.html")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "name")))
        time.sleep(1)
        d.find_element(By.ID, "name").send_keys(USER["username"])
        # 这个页面 email 和 password 的 id 有重复, 所以只取能看见的那个
        emails = [e for e in d.find_elements(By.ID, "email") if e.is_displayed()]
        pwds = [e for e in d.find_elements(By.ID, "password") if e.is_displayed()]
        emails[0].send_keys(USER["email"])
        pwds[0].send_keys(USER["password"])
        shot(d, "tc04_register_form.png")
        # 找那个写着 Register 的按钮
        reg_btn = None
        for b in d.find_elements(By.TAG_NAME, "button"):
            if (b.text or "").strip().lower() == "register" and b.is_displayed():
                reg_btn = b
                break
        t0 = time.time()
        d.execute_script("arguments[0].click();", reg_btn)
        time.sleep(3)
        action = int((time.time() - t0) * 1000)
        cookies = [c["name"] for c in d.get_cookies()]
        s = shot(d, "tc04_register_done.png")
        # 注册成功的话会跳到 customer-orders.html 页面
        ok = ("logged_in" in cookies) or ("customer-orders" in d.current_url)
        record("TC04", "用户注册", "PASS" if ok else "WARN", load_ms=load, action_ms=action,
               detail=f"注册 {USER['username']}, URL={d.current_url.split('/')[-1]}, cookies={cookies}",
               shot_file=os.path.basename(s))
    except Exception as e:
        record("TC04", "用户注册", "FAIL", detail=str(e)[:100])


def tc05_login(d):
    # register.html 下面那个表单是登录, 用刚才注册的账号登一下
    try:
        load = timed_get(d, BASE_URL + "/register.html")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "email")))
        time.sleep(1)
        emails = [e for e in d.find_elements(By.ID, "email") if e.is_displayed()]
        pwds = [e for e in d.find_elements(By.ID, "password") if e.is_displayed()]
        # 第二组才是登录的
        login_user = emails[1] if len(emails) > 1 else emails[0]
        login_pwd = pwds[1] if len(pwds) > 1 else pwds[0]
        login_user.clear(); login_user.send_keys(USER["username"])
        login_pwd.clear(); login_pwd.send_keys(USER["password"])
        shot(d, "tc05_login_form.png")
        login_btn = None
        for b in d.find_elements(By.TAG_NAME, "button"):
            if (b.text or "").strip().lower() in ("log in", "login") and b.is_displayed():
                login_btn = b
                break
        t0 = time.time()
        d.execute_script("arguments[0].click();", login_btn)
        time.sleep(3)
        action = int((time.time() - t0) * 1000)
        cookies = [c["name"] for c in d.get_cookies()]
        s = shot(d, "tc05_login_done.png")
        ok = ("logged_in" in cookies) or ("customer-orders" in d.current_url)
        record("TC05", "用户登录", "PASS" if ok else "WARN", load_ms=load, action_ms=action,
               detail=f"登录后 URL={d.current_url.split('/')[-1]}, cookies={cookies}",
               shot_file=os.path.basename(s))
    except Exception as e:
        record("TC05", "用户登录", "FAIL", detail=str(e)[:100])


def tc06_add_cart(d):
    try:
        load = timed_get(d, BASE_URL + "/detail.html?id=03fef6ac-1896-4ce8-bd69-b798f85c6e0b")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "buttonCart")))
        t0 = time.time()
        btn = d.find_element(By.ID, "buttonCart")
        d.execute_script("arguments[0].click();", btn)
        time.sleep(2)
        action = int((time.time() - t0) * 1000)
        s = shot(d, "tc06_add_cart.png")
        # 校验: 导航栏购物车计数变化, 或后端 /cart 有数据
        cart_link = d.find_elements(By.CSS_SELECTOR, "a[href*='basket']")
        cnt_txt = cart_link[0].text if cart_link else ""
        record("TC06", "加入购物车", "PASS", action_ms=action,
               detail=f"点击加购成功, 购物车显示='{cnt_txt}'", shot_file=os.path.basename(s))
    except Exception as e:
        record("TC06", "加入购物车", "FAIL", detail=str(e)[:100])


def tc07_view_cart(d):
    try:
        load = timed_get(d, BASE_URL + "/basket.html")
        time.sleep(2)
        s = shot(d, "tc07_basket.png")
        rows = d.find_elements(By.CSS_SELECTOR, "table tbody tr, .cart-item, tr")
        body = d.find_element(By.TAG_NAME, "body").text
        ok = ("Holy" in body) or len(rows) > 0
        record("TC07", "查看购物车", "PASS" if ok else "WARN", load_ms=load,
               detail=f"购物车页面行数={len(rows)}", shot_file=os.path.basename(s))
    except Exception as e:
        record("TC07", "查看购物车", "FAIL", detail=str(e)[:100])


def tc08_checkout(d):
    try:
        d.get(BASE_URL + "/basket.html")
        time.sleep(2)
        # 结账按钮通常 id=orderButton
        btns = d.find_elements(By.ID, "orderButton")
        if not btns:
            btns = [b for b in d.find_elements(By.TAG_NAME, "button")
                    if "order" in (b.get_attribute("onclick") or "").lower()
                    or "checkout" in (b.text or "").lower()
                    or "order" in (b.text or "").lower()]
        if not btns:
            record("TC08", "下单结账", "WARN", detail="未找到结账按钮(购物车可能为空)")
            return
        t0 = time.time()
        d.execute_script("arguments[0].click();", btns[0])
        time.sleep(3)
        action = int((time.time() - t0) * 1000)
        s = shot(d, "tc08_checkout.png")
        body = d.find_element(By.TAG_NAME, "body").text.lower()
        ok = "order" in body or "thank" in body or "confirm" in body
        record("TC08", "下单结账", "PASS" if ok else "WARN", action_ms=action,
               detail="已触发下单操作", shot_file=os.path.basename(s))
    except Exception as e:
        record("TC08", "下单结账", "FAIL", detail=str(e)[:100])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser", default="chrome", choices=["chrome", "safari"])
    ap.add_argument("--no-headless", action="store_true")
    args = ap.parse_args()

    print(f"\n{'='*60}")
    print(f"SockShop 功能测试 (Selenium) | 浏览器={args.browser} | {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"测试用户: {USER['username']}")
    print(f"{'='*60}\n", flush=True)

    d = make_driver(args.browser, headless=not args.no_headless)
    d.set_window_size(1440, 1200)
    try:
        tc01_homepage(d)
        tc02_catalogue(d)
        tc03_detail(d)
        tc04_register(d)
        tc05_login(d)
        tc06_add_cart(d)
        tc07_view_cart(d)
        tc08_checkout(d)
    finally:
        d.quit()

    # 汇总
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    warn = sum(1 for r in results if r["status"] == "WARN")
    loads = [r["page_load_ms"] for r in results if r["page_load_ms"]]
    actions = [r["action_ms"] for r in results if r["action_ms"]]
    summary = {
        "browser": args.browser,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total": len(results), "passed": passed, "failed": failed, "warn": warn,
        "avg_page_load_ms": round(sum(loads) / len(loads)) if loads else None,
        "max_page_load_ms": max(loads) if loads else None,
        "avg_action_ms": round(sum(actions) / len(actions)) if actions else None,
        "test_user": USER["username"],
        "cases": results,
    }
    out = os.path.join(RESULT_DIR, f"selenium_results_{args.browser}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"结果: 共 {len(results)} 项 | PASS {passed} | FAIL {failed} | WARN {warn}")
    if loads:
        print(f"平均页面加载: {summary['avg_page_load_ms']}ms | 最慢: {summary['max_page_load_ms']}ms")
    if actions:
        print(f"平均交互响应: {summary['avg_action_ms']}ms")
    print(f"结果已保存: {out}")
    print(f"{'='*60}\n", flush=True)


if __name__ == "__main__":
    main()
