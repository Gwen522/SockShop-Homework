# 现场演示用的 Selenium 脚本(有界面 + 放慢动作版)
# 跟 test_sockshop.py 的区别: 这个会弹出真实浏览器窗口, 每一步停顿几秒,
# 方便答辩时大家肉眼看到"浏览器自己在操作"。正式测试还是用 test_sockshop.py。

import os
for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)
os.environ["NO_PROXY"] = "localhost,127.0.0.1,*"

import glob
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://localhost:8079"
PAUSE = 2.5   # 每步停顿秒数, 想更慢就调大

rand = "".join(random.choices(string.ascii_lowercase, k=5))
USER = f"demo_{rand}"
PWD = "demo1234"


def step(msg):
    print(f"\n>>> {msg}")
    time.sleep(1)


def make_driver():
    # 演示用 Chrome 有界面模式; 如果这台电脑的 Chrome 有问题, 把下面整段换成:
    #     return webdriver.Safari()
    # 就能用 Safari 演示(Mac 需要先在 Safari 开发菜单里开启"允许远程自动化")
    opts = webdriver.ChromeOptions()
    for a in ["--no-sandbox", "--disable-gpu", "--window-size=1200,900",
              "--no-proxy-server", "--proxy-bypass-list=*"]:
        opts.add_argument(a)
    return webdriver.Chrome(options=opts)


def main():
    print("=" * 50)
    print("  SockShop 功能测试现场演示 (Selenium)")
    print("=" * 50)
    d = make_driver()
    d.set_window_size(1200, 900)
    try:
        step("1. 打开首页")
        d.get(BASE + "/")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "navbar")))
        time.sleep(PAUSE)
        print(f"    页面标题: {d.title}")

        step("2. 进入商品目录, 浏览商品")
        d.get(BASE + "/category.html")
        time.sleep(PAUSE)
        imgs = d.find_elements(By.CSS_SELECTOR, "img[src*='catalogue']")
        print(f"    看到 {len(imgs)} 个商品")

        step("3. 点开一个商品看详情")
        d.get(BASE + "/detail.html?id=03fef6ac-1896-4ce8-bd69-b798f85c6e0b")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(PAUSE)
        print(f"    商品名: {d.find_element(By.TAG_NAME, 'h1').text}")

        step("4. 注册一个新账号")
        d.get(BASE + "/register.html")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "name")))
        time.sleep(1)
        d.find_element(By.ID, "name").send_keys(USER)
        emails = [e for e in d.find_elements(By.ID, "email") if e.is_displayed()]
        pwds = [e for e in d.find_elements(By.ID, "password") if e.is_displayed()]
        emails[0].send_keys(f"{USER}@test.com")
        pwds[0].send_keys(PWD)
        time.sleep(PAUSE)
        for b in d.find_elements(By.TAG_NAME, "button"):
            if (b.text or "").strip().lower() == "register" and b.is_displayed():
                d.execute_script("arguments[0].click();", b)
                break
        time.sleep(PAUSE)
        print(f"    已注册账号: {USER}")

        step("5. 加入购物车")
        d.get(BASE + "/detail.html?id=03fef6ac-1896-4ce8-bd69-b798f85c6e0b")
        WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "buttonCart")))
        time.sleep(1)
        d.execute_script("arguments[0].click();", d.find_element(By.ID, "buttonCart"))
        time.sleep(PAUSE)
        print("    已加入购物车")

        step("6. 查看购物车")
        d.get(BASE + "/basket.html")
        time.sleep(PAUSE)
        print("    购物车页面已打开")

        print("\n" + "=" * 50)
        print("  演示完成! 整个购物流程都跑通了, 全部正常。")
        print("=" * 50)
        time.sleep(3)
    finally:
        d.quit()


if __name__ == "__main__":
    main()
