# SuperStar 学习通刷课 · Home Assistant 加载项

把 [lispringing/SuperStar](https://github.com/lispringing/SuperStar) 打包成 Home Assistant 加载项，
部署在 HAOS 小主机上，**支持扫码登录（cookie 模式，无需明文账号密码）**。

---

## 一、本地安装（推荐，最省事）

> 与本机其它本地加载项（go_music_dl / ha_panel / go2rtc）同一套路。

1. 用 **Samba** 或 **SSH & Web Terminal** 进入 HA 主机，把整个目录复制到
   **`/addons/local/superstar/`**（注意是 `/addons` 里的 `local` 子目录，再套一层 `superstar`）：

   ```
   /addons/local/superstar/
   ├── config.yaml
   ├── Dockerfile
   ├── gen_config.py
   ├── run.sh
   ├── README.md
   └── repository.yaml      ← 本地安装用不到，仅以后推 GitHub 仓库用
   ```

   > ⚠️ 常见放错：放到 `/addons/superstar/`（缺 `local` 这层）、
   > 或者放成 `/addons/local/superstar/superstar/`（多套一层）——这两种都不会被扫描到。
   > 如果是通过 Samba 的 `addons` 共享复制的，共享根就对应 `/addons`。

2. 打开 **设置 → 加载项 → 加载项商店**，点右上角 ⋮ → **检查更新**，然后刷新页面（Ctrl+F5）。
3. 商店顶部会出现 **「本地加载项」（Local add-ons）** 分组，里面就是 **SuperStar 学习通刷课**。
4. 点进去 → **安装**（首次会构建镜像，小主机上可能要几分钟）。
5. 切到 **配置** 页填好参数（见下），**保存**。
6. 切到 **信息** 页 → **启动**，然后看 **日志**。
7. 想再跑一次：加载项页面点 **重启**。

## 二、加载项商店里看不到？按这个顺序排错

1. **确认路径**：SSH 进 HA 执行

   ```bash
   ls /addons/local/superstar/config.yaml /addons/local/superstar/Dockerfile
   ```

   两个文件都要在。不在就说明放错了目录。

2. **看 Supervisor 日志**（最关键）：**设置 → 系统 → 日志**，右上角来源选 **Supervisor**，
   翻到最底部，找带 `superstar` 的报错，常见的有：
   - `not a valid add-on / validation failed` → `config.yaml` 字段写错，按报错行号改；
   - `arch` 相关的 deprecated 警告 → 无害，已按 amd64/aarch64 精简；
   - 什么都没有 → 大概率路径不对（见第 1 步）。
3. **强刷页面缓存**：商店「检查更新」之后按 **Ctrl+F5**（macOS：Cmd+Shift+R），
   否则浏览器可能还缓存着旧的商店列表。
4. **slug 冲突**：`/addons/local/` 下如果有多个加载项的 `config.yaml` 写了同一个 `slug`，
   Supervisor 只会加载其中一个且**不报错**。确认没有残留目录。
5. **安装时构建失败**（能看到卡片但装不上）：构建日志里若报 `FROM` 为空，
   说明基础镜像没写死（本仓库已改为 `FROM alpine:3.20`，2026.04 起 Supervisor 不再注入 `BUILD_FROM`）。

## 三、放进 GitHub 仓库（可选，分享给别人用）

1. 把本目录上传为仓库里的一个子目录，仓库**根目录**放 `repository.yaml`（本仓库已带模板，填好 `url` / `maintainer` 即可）：

   ```
   <你的仓库>/
   ├── repository.yaml
   └── superstar/
       ├── config.yaml
       ├── Dockerfile
       ├── gen_config.py
       ├── run.sh
       └── README.md
   ```

2. 仓库必须是**公开**的（Supervisor 无法 clone 私有仓库）。
3. 在 **加载项商店** 右上角 ⋮ → **仓库** → 粘贴仓库 URL → 添加，即可看到加载项。

---

## 四、扫码登录（重点）

这个脚本**没有"显示二维码让你扫"的功能**，它只认 `cookies.txt`。
所以"扫码登录"的做法是：**你先在浏览器里扫码登录学习通，把登录后的 cookie 取出来**，再粘进加载项配置。

**步骤：**

1. 电脑浏览器打开学习通登录页，选「二维码登录」，用学习通 App 扫码登录。
2. 登录成功后，按 F12 打开开发者工具 → **Application（应用）→ Cookies**，
   把 `chaoxing.com` / `passport2.chaoxing.com` 等域名下的 cookie 复制成
   `name1=value1; name2=value2; ...` 这种一行格式。
   - 嫌麻烦可以用浏览器扩展 **Cookie-Editor** → 导出 → 「复制为字符串」，拿到的就是这种格式。
3. 在加载项 **配置** 页：
   - 把上面那串 cookie 粘进 **`cookies`** 字段；
   - **`use_cookies`** 不用管，有 cookie 会自动启用；
   - 账号密码留空即可。
4. 保存 → 重启加载项 → 看日志。

> ⚠️ 学习通 cookie 会过期。某天刷课报登录错误时，重新扫码、更新 `cookies` 字段即可。

**另一种放 cookie 的方式（可选）：** 把那串 `k=v;k=v` 写进
`/share/superstar/cookies.txt`（通过 Samba / SSH 加载项放进去），脚本也会自动读取。

---

## 五、配置项说明

| 配置项 | 说明 |
|------|------|
| `cookies` | 扫码登录拿到的 cookie 字符串（推荐） |
| `username` / `password` | 备选：明文账号密码登录（不如 cookie 安全） |
| `course_list` | 指定课程 ID，逗号分隔；留空=全部课程 |
| `speed` | 视频倍速，0.5~2 |
| `jobs` | 同时处理的章节数，1~16 |
| `notopen_action` | 遇到未开放任务点：retry / continue / ask |
| `auto_sign` | 是否自动签到 |
| `tiku_provider` / `tiku_tokens` | 章节测验答题题库；纯刷视频可不填 |
| `notification_*` | ServerChan / Bark 等推送通知（可选） |

---

## 六、注意事项

- `rootfs/` 是旧的 s6 启动方案，**已弃用**（Supervisor 新版本不再注入 `BUILD_FROM`、
  也改用 `CMD` 启动），现在生效的是 `run.sh`。保留它只是为了留档，不影响构建。

- **纯视频刷课**：留空题库即可。若课程含**必须作答的章节测验**，需要填 `tiku_provider` + `tiku_tokens`（见原仓库 README 的题库说明），否则遇到测验会卡住。
- **这是自定义加载项**，走官方 Add-on 机制，**不会**把 HA 标记为 unsupported。
- 刷课脚本跑完会正常退出，加载项会保持「运行中」以便你查看日志；重新运行点「重启」即可。
- 账号安全：cookie / 密码都存在你**本地 HA 实例**的配置里，不进 GitHub 仓库，比 fork 原仓库安全得多。
- 使用请遵守你所在学校与学习通平台的规定，后果自负。
