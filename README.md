# 鳕烩烩网站

网站地址：[xhhbot.com](https://xhhbot.com/)。主页、指令帮助和更新日志由 `build.py` 从 `content/` 中的 JSON 生成，通过 GitHub Actions 发布到 GitHub Pages。

## 编辑网站

访问 [管理后台](https://xhhbot.com/admin/)，使用具有 `linglin520/xhhbot-website` 写入权限的 GitHub 账号登录。后台可以编辑首页介绍、帮助分类与指令、更新日志。保存会提交到 `main`，GitHub Actions 随后自动更新网站。后台入口不会显示在公开导航中。

网站内容分别存放在 `content/site.json`、`content/help.json`、`content/changelog.json`。帮助分类的 `id` 必须唯一，且只能包含小写英文、数字和横线。日志日期采用 `YYYY-MM-DD` 格式。

## 部署结构

- `.github/workflows/pages.yml`：运行 Python 3.12 构建并部署 GitHub Pages。
- `deploy.json`：仓库、域名及 OAuth Worker 地址，不包含凭据。
- `admin/config.json`：Decap CMS 编辑字段。
- `oauth-worker/index.js`：GitHub OAuth 回调服务，部署在 Cloudflare Workers。
- `wrangler.toml`：Cloudflare Worker 的公开部署配置。

GitHub OAuth 应用的 Client ID 和 Client Secret 只作为 Cloudflare Worker 的加密 Secret 保存，绝不能写入本仓库。Worker 验证 OAuth `state`，且只向 `https://xhhbot.com` 发送登录结果。后台编辑权限最终由 GitHub 仓库写入权限决定。

## 本地预览

使用 Python 3.12 或更新版本：

```sh
python3 build.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

打开 `http://127.0.0.1:4173/`。本地 CMS 登录不会完成，因为 GitHub OAuth 回调只允许正式域名。

本仓库仅包含网站文件；不要上传上层机器人目录、环境变量、数据库、备份或任何 API Token。
