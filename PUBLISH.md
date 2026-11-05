# GEO Handbook V2｜发布与线上验收

**状态：尚未创建 GitHub 仓库；以下是部署流程，不是已上线证明。** 默认目标 GitHub 所有者 `AIPMAndy`，仓库 `geo-handbook`。

## 1. 新建空仓库

打开 https://github.com/new ，Owner 选择 `AIPMAndy`，仓库名填 `geo-handbook`，Visibility 选 Public。不要勾选自动创建 README / License / .gitignore，因为源码包自带。

## 2. 上传 ZIP 解压后的所有源码

```bash
cd geo-handbook
python3 scripts/build.py
python3 scripts/check.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
git init
git add .
git commit -m "feat: release GEO Handbook v2"
git branch -M main
git remote add origin https://github.com/AIPMAndy/geo-handbook.git
git push -u origin main
```

GitHub Desktop 也可以。网页拖文件时，注意 `.github` 隐藏目录是否遗漏；若工作流文件不存在就不会自动部署。

## 3. GitHub Pages

打开 `https://github.com/AIPMAndy/geo-handbook/settings/pages` → Build and deployment → Source = **GitHub Actions** → 检查 Actions 中 `Deploy GEO Handbook` 是否成功。若启用 Pages 晚于首次提交，去 Actions 手动 Run workflow。

预期 URL：`https://aipmandy.github.io/geo-handbook/`。

**注意**：该 URL 只有 Pages 成功部署后才应对外宣传。若 fork 改名或使用自定义域名，请编辑 `scripts/build.py` 中 `SITE`，重新构建 sitemap/canonical 后提交。

## 4. 必须实际点开的路径

- `/` 首页；`/handbook.html` 课程列表；`/lessons/01.html` / `26.html`。
- `/labs.html` / `/labs/01.html` / `/labs/16.html`，实际能看到每个 Lab 的全部步骤。
- `/cases.html` / `/cases/01.html`，能清楚看到教学模拟标识。
- `/tools.html`：填写测试、导出 CSV、清空测试；再导入 `/measure.html`。
- `/diagnose.html`：加载故意缺陷样例、运行检测并出现 noindex 警告。
- `/pricing.html`：输入 20 工时 × 100 元 + 500 元其他 + 500 元 QA、50% 目标毛利，结果必须是 **¥6,000**。
- `/30days.html`：勾选第 1 天→刷新→仍已勾选→跳其他页面回来仍在。
- `/templates.html`：可见 25 套模板且下载可用。
- `/sitemap.xml`：地址正确且能公开打开；GSC/Bing 索引另测。**注意**：项目站点 `aipmandy.github.io/geo-handbook/robots.txt` 即使存在，也不是这个域名的正式抓取控制文件。真正生效的 robots.txt 位于域名根目录 `/robots.txt`，由 GitHub Pages 主机控制；本项目下的 `robots.txt` 只是教学示例，不要用它判断爬虫已放行。

分别在手机与桌面浏览器执行；记录实际日期、浏览器、预期/实际结果、截图以及失败 URL。

## 5. 搜索与 AI 效果（站点拥有者操作）

依照官方步骤验证 Google Search Console 和 Bing Webmaster Tools，提交真实 sitemap 并观察索引与 AI 效果报告。允许 OAI-SearchBot 需网站所有者根据策略自主决定；不要因为教程公开而开放隐私页面。自动抓取、索引、被引用、带来客户均为不同阶段。

## 6. 失败排查

- 404：首页发布前检查 Actions、Pages Source、仓库名和分支；不要把运行中的工作流当成成功。
- Actions 未运行：确认 `.github/workflows/pages.yml` 是否已随代码上传。
- 站点样式没加载：检查 `docs/assets/` 是否完整、HTML 相对路径及 Pages 的 URL base。
- sitemap 错域名：更新 `SITE` 并重建，不能直接把旧地址改在生成文件中。
- CSS/JS 浏览器出错：打开 DevTools Console，再对照 `RED_TEAM_V2.md` 中未验证事项。
- 浏览器进度丢失：localStorage 与具体域名及设备绑定；没有跨浏览器自动同步。

咨询与企业合作：https://metaver.vip/ · 微信 `AIPMAndy`。
