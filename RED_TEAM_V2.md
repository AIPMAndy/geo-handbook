# GEO Handbook V2.0 对抗式审核与边界说明

审核时间：2026-11-05。对象：**此 ZIP 内的源码与生成页面**，而非已上线网站。

## 第一关：反 GEO 玄学

| 假设/宣传语 | 证据审查与修正 | 当前状态 |
|---|---|---|
| llms.txt、特殊 JSON-LD 一键让 Google AI 引用 | Google 2026 官方指南明确否定 GEO 专用文件与特殊 Schema 要求；以可索引内容与原创价值为重 | 已修复 |
| GPTBot 允许就等于 ChatGPT Search 搜得到 | 把 OAI-SearchBot / GPTBot / ChatGPT-User 拆开，分别对照 OpenAI 官方定义 | 已修复 |
| Google AI 没有单独效果数据 | 已核验 2026 年 Google 新版 Search Console 生成式 AI 效果报告及全球推出日期 | 已修复 |
| Bing 只能靠手工截图 | 加入 Bing AI Performance / Topics Portfolio Beta 与指标含义 | 已修复 |
| 客户看完教程自动有增长与收入 | 所有指标都分环节；无已核实的客户成果不填数字 | 已修复 |

官方证据：
- Google https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google GSC https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- OpenAI https://developers.openai.com/api/docs/bots
- Bing https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c
- Bing Topics Portfolio https://blogs.bing.com/webmaster/2026/10/introducing-topics-portfolio-beta-in-ai-performance/

## 第二关：从「看懂」到「能照做」

**发现的 V1 问题**：每章的 5 个动作有时写得像专家待办事项，零基础读者不知道点哪里、交什么、失败了怎么办。

**V2 修复**：另外制作 16 个完整实验，每个包括操作入口、输入、5 个按顺序动作、独立完成凭证、失败处理及来源。自带 30 问模板、两份结构不同的测试 HTML、合成 CSV、离线 CLI。新增 6 个行业场景明确写「教学模拟」，不冒充真实成交案例。

## 第三关：代码执行与测试

| 检查 | 验证手段 | 结果 |
|---|---|---|
| 26 课程、16 Labs、6 Cases、25 模板、30 天 | `scripts/check.py` | 通过 |
| 60 个站点 HTML H1 和内部链接 | HTMLParser 静态质量门禁 | 通过 |
| 用户可提交的 JSON-LD 错误 | 故意缺陷样例 + `site_audit.py` | 通过 |
| noindex、缺失 canonical、title、H1 | 故意缺陷样例 + `site_audit.py` | 通过 |
| 排除品牌直搜和未触发样本 | `geo_report.py` + 单元测试 | 通过 |
| JSON-LD 后面普通脚本污染解析 | 添加失败样例后修复状态跟踪，回归测试 | 通过 |
| 15 项 Python 单元测试 | `python3 -m unittest ...` | 通过 |
| 两份站点 JS 语法 | `node --check` | 通过 |
| HTML 页面浏览器 DOM 代表性渲染 | Chromium 内存 DOM 注入（6 页） | 通过 |
| HTML 诊断按钮、CSV 解析与展示 | Chromium 表单/按钮操作 | 通过 |
| 成本测算输入和结果 | 输入 20h×100 + 500+500，50% 毛利 → ¥6,000 | 通过 |
| 30 天任务状态即时更新 | Chromium 点击检查 | 通过 |
| 监测表即时分母与结果 | Chromium 输入检查 | 通过 |
| 390px 移动页面无横向溢出 | Chromium layout width 检查 | 通过 |

## 第四关：刻意保留的未验证事项

1. **尚未创建 GitHub 仓库 / 公开网址尚不存在**：当前连接的 GitHub 账号下 `AIPMAndy/geo-handbook` 不存在（核查时返回 404）；不能假称已部署。
2. Chromium 在当前受限容器中禁止导航本地文件、localhost 和测试域名。浏览器测试通过 DOM 内存注入完成，**不代表真实 URL 跳转、跨页/刷新后的 localStorage 持久化、GitHub Pages 部署已通过**。
3. **GitHub Pages 的项目子路径并不拥有域名根目录 robots.txt 控制权**；`/geo-handbook/robots.txt` 仅是教学样例，不代表正式爬虫规则。HTML 自检是静态结构检查；**不能验证 robots.txt 的实时匹配、CDN、真实 HTTP 状态、Google/Bing 是否实际抓取索引、AI 是否引用**。
4. CSV 分析要求使用者人工录入真实自有 URL 与截图；程序不会自动登录 AI 平台，也不能判定某个域名所有权。
5. 教学案例和合成数据不能用于对外宣传客户效果；尚未用真实客户网站与原始 GSC/Bing/CRM 数据验证可见性提升和商业转化。
6. 没有公开第三方基准比较支撑「全网第一/最完整/排名第一」等绝对说法；项目的价值以可执行程度、代码和持续迭代衡量。

## 发布后的 P0 验收（负责者需记录 URL 与截图）

- 在 Pages 实际打开首页、首个 Lab、案例、课程页和三个扩展工具，确认导航、下载、全部静态资源加载。
- 在真实 URL 下完成 30 天勾选 → 页面刷新 → 跨页返回的保存测试；清空和 CSV 导出的确认动作也要实测。
- 手机与桌面 Chrome/Safari 检查字体、链接可触控与工具表单。
- 检查 sitemap 的每个 URL 都是 HTTP 200、canonical 同源、robots 访问与目标域名一致；Pages 域名变化要重建。
- 用已有权限的 Google Search Console、Bing Webmaster Tools 验证索引和真实 AI 效果报告，再开展自然问法基线。

## 未来升级优先级（按成本/收益评估）

1. 取得合法、脱敏、经许可的真实企业 GEO 项目数据，发布一份完整前后报告（同时公开失败样本）。
2. 在不泄露账号权限的前提下支持 GSC/Bing CSV 导入并和手工观测分开展示。
3. 取得不同年龄/专业背景的新手复现实验结果，逐个修复不清楚的步骤。
4. 累积基于实际项目的 FAQ 和技术错误诊断样例，按官方更新日期维护证据链。

**结论**：V2 已达到本地交付包可运行、可测量、可作为真实项目起点的门槛；线上发布和商业成效还需实际验证。未宣称拥有虚构客户或已获得 AI 排名。
