# -*- coding: utf-8 -*-
"""
读取 Home Assistant 注入的 /data/options.json，
生成 SuperStar 脚本所需的 /app/config.ini 与 /app/cookies.txt。
"""
import json
import os
import shutil

OPT = "/data/options.json"
APP_DIR = "/app"
INI_PATH = os.path.join(APP_DIR, "config.ini")
COOKIES_PATH = os.path.join(APP_DIR, "cookies.txt")
SHARE_COOKIES = "/share/superstar/cookies.txt"

TPL = """[common]
use_cookies = {use_cookies}
username = {username}
password = {password}
course_list = {course_list}
speed = {speed}
jobs = {jobs}
notopen_action = {notopen_action}
auto_sign = {auto_sign}

[tiku]
provider = {tiku_provider}
tokens = {tiku_tokens}
submit = false
cover_rate = 0.9
delay = 1.0
true_list = 正确,对,√,是
false_list = 错误,错,×,否,不对,不正确

[notification]
provider = {notification_provider}
url = {notification_url}
"""


def b(v):
    return "true" if v else "false"


def fill(tpl, mapping):
    """逐键替换，避免值里含 { 或 } 时 str.format 报错。"""
    out = tpl
    for k, v in mapping.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def write_cookies(o):
    """把 cookies 写到 /app/cookies.txt，供 SuperStar 读取（cookie 登录 / 扫码登录）。"""
    cookies = (o.get("cookies") or "").strip()
    if cookies:
        with open(COOKIES_PATH, "w", encoding="utf-8") as f:
            f.write(cookies)
        print("[gen_config] 已写入 cookies.txt（来源：加载项配置，扫码登录模式）")
        return
    if os.path.isfile(SHARE_COOKIES):
        shutil.copyfile(SHARE_COOKIES, COOKIES_PATH)
        print("[gen_config] 已写入 cookies.txt（来源：/share/superstar/cookies.txt）")
        return
    if o.get("use_cookies"):
        print("[gen_config] 警告：已启用 use_cookies 但未提供 cookies，登录会失败")
    else:
        print("[gen_config] 未提供 cookies；若也未填账号密码，登录会失败")


def main():
    with open(OPT, "r", encoding="utf-8") as f:
        o = json.load(f)

    # 只要有 cookies 就走 cookie 登录（扫码登录）
    use_cookies = bool(o.get("cookies")) or bool(o.get("use_cookies"))

    cfg = fill(TPL, {
        "use_cookies": b(use_cookies),
        "username": o.get("username", "") or "",
        "password": o.get("password", "") or "",
        "course_list": o.get("course_list", "") or "",
        "speed": o.get("speed", 1.0),
        "jobs": o.get("jobs", 4),
        "notopen_action": o.get("notopen_action", "retry") or "retry",
        "auto_sign": b(o.get("auto_sign", False)),
        "tiku_provider": o.get("tiku_provider", "TikuYanxi") or "TikuYanxi",
        "tiku_tokens": o.get("tiku_tokens", "") or "",
        "notification_provider": o.get("notification_provider", "ServerChan") or "ServerChan",
        "notification_url": o.get("notification_url", "") or "",
    })

    with open(INI_PATH, "w", encoding="utf-8") as f:
        f.write(cfg)
    print("[gen_config] config.ini 已生成 (use_cookies=%s)" % use_cookies)

    write_cookies(o)


if __name__ == "__main__":
    main()
