# Ciallo～(∠・ω< )⌒★

> 一个用纯 HTML/CSS 写的个人主页，部署在 GitHub Pages 上。

## 这是什么

[ChenQiuguo.github.io](https://ChenQiuguo.github.io/) 是秋果的个人主页，内容很朴素：

- **我的账号** —— Bilibili、GitHub
- **我玩的游戏** —— 原神、崩坏：星穹铁道、绝区零、明日方舟：终末地
- **术力口** —— 洛天依、初音未来
- **我看的动漫** —— 冰菓、紫罗兰永恒花园、葬送的芙莉莲、邻家天使、境界的彼方……
- **想扩列** —— 点击弹出联系方式

整个页面就是一个 [`index.html`](index.html)，无框架、无构建、无依赖，改完推上去就是新版本。

## 技术栈

| 项 | 说明 |
|---|---|
| 前端 | 原生 HTML + CSS + 少量 JavaScript |
| 部署 | GitHub Pages，通过 Actions 自动发布 |
| 样式 | 无外部 CSS 文件，全部内联在 `<style>` 里 |
| 依赖 | 无 |

## 仓库结构

```
├── index.html                  # 个人主页（唯一入口，共 1314 行）
├── LAYOUT_LOCK.md              # 行号锁定规则说明
├── lock_layout.py              # 校验/修复 index.html 行号的工具
├── .github/workflows/
│   ├── static.yml              # 部署静态站点到 GitHub Pages
│   └── jekyll-gh-pages.yml     # Jekyll 备用部署流程
└── ab92be07852a1f7746dc3c9a2301173f.txt
```

## 修改 `index.html` 前必读

`index.html` **总行数必须恰好是 1314 行**，且文件里有几个特定注释的行号是固定的，改动时需要保持它们的位置不变。

第 521 至 1313 行是 793 行缓冲空行，用于吸收正文增删带来的行数涨落。

改完 `index.html` 后，在仓库根目录运行：

```bash
# 只校验，不改文件
python lock_layout.py check index.html

# 自动修复：复位注释位置 + 调整缓冲空行使总行数回到 1314
python lock_layout.py fix index.html

# 查看当前布局概览
python lock_layout.py report index.html
```

详细规则见 [`LAYOUT_LOCK.md`](LAYOUT_LOCK.md)。

## 本地预览

不需要任何构建工具，直接用浏览器打开 `index.html` 即可：

```bash
# 方式一：直接打开
start index.html

# 方式二：起一个本地静态服务器
python -m http.server 8000
# 然后访问 http://localhost:8000
```

## 部署

推送到 `main` 分支后，GitHub Actions 会自动将整个仓库发布到 GitHub Pages：

- 工作流文件：[`.github/workflows/static.yml`](.github/workflows/static.yml)
- 触发条件：push 到 `main`，或手动在 Actions 页触发 `workflow_dispatch`
- 部署产物：整个仓库目录（不只是 `index.html`）

## 联系我

- Email: cqg110815@outlook.com
- WeChat: frierensummer
- Bilibili: https://space.bilibili.com/3546609252043157

---

### 另外

**关注洛天依喵，关注洛天依谢谢喵**

### Copyright © 2026 Qiuguo

Powered by GitHub · Made with ♡
