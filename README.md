<div align="center">

# GEO Handbook · 生成式 AI 搜索实战开源指南

![GEO Handbook 宣传封面](docs/assets/social-preview.svg)

**让值得被看见的内容，被 AI 找到；让真实的用户问题，变成可核验的商业结果。**

**26 章课程 · 16 个手把手实验 · 6 种行业演练 · 25 套模板 · 30 天执行 · 61 个静态页面 · 3 个额外免费工具 · 对抗式审核**

[🌐 在线网站](https://aipmandy.github.io/geo-handbook/) · [📍 三分钟上手](GEO_OPERATING_MANUAL.md) · [🧪 实操实验](labs/) · [🔬 GEO 实验室](https://aipmandy.github.io/geo-handbook/operations.html) · [📚 完整章节](chapters/) · [🧩 下载模板](templates/) · [🔍 官方依据](docs/sources.html) · [🚀 发布说明](PUBLISH.md)

作者：**AI 酋长 Andy** · [官网](https://metaver.vip/) · 合作联系：微信 `AIPMAndy`

</div>

## GEO 实验室：可复核的实验而不是宣传结论

新增 [六步实验室](https://aipmandy.github.io/geo-handbook/operations.html)：从真实用户问题、网页技术体检、改动前答案记录，到单因素内容修改、同条件复测和商业事件核验。包含六套标记为 DEMO 的 CSV 示例与本地实验记录卡。详情见 [实验说明](operations/README.md) 与 [内容标准](EDITORIAL_STANDARDS.md)。

## 先看这三个真实事实

1. **GEO 不是一套特殊排名开关。** Google 2026 年发布的官方指南仍建议以 SEO 基础、优质原创和可访问内容为主，明确说不需要 `llms.txt`、特殊的 AI schema 或机械地切碎文章。来源：[Google 官方](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)。
2. **搜索爬虫和训练爬虫并不相同。** OpenAI 的 OAI-SearchBot 用于 ChatGPT Search 相关的自动抓取，GPTBot 关联模型训练，ChatGPT-User 代表用户触发的访问；规则应分别核对。来源：[OpenAI Crawlers](https://developers.openai.com/api/docs/bots)。
3. **AI 可见性已有官方数据入口。** Google 于 2026-06-03 宣布生成式 AI Search Console 效果报告，2026-08-31 前推出至全球网站；Bing AI Performance 提供引用、页面、查询等数据，并在 2026-10 推出 Topics Portfolio Beta。来源：[Google 公告](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports) · [Bing 说明](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c) · [Topics Portfolio](https://blogs.bing.com/webmaster/2026/10/introducing-topics-portfolio-beta-in-ai-performance/)。

**GitHub Pages 特别注意：**项目位于 `/geo-handbook/` 子路径，该目录内的 `robots.txt` **不会成为域名根目录的有效 robots 规则**；它仅作示例。参考 [发布说明](PUBLISH.md)。

**不要混淆：**「页面能抓取」≠「被索引」≠「AI 在回答中引用」≠「用户点击」≠「咨询/付费」。网站及工具不承诺外部平台一定出现结果。

## 新手只有 15 分钟，现在开始

1. 打开 [LAB 01：找到首个购买前问题](labs/01.md)，只选一个有商业价值的目标客户问题。
2. 打开 [30 问模板](templates/02-question-bank-30.csv)，选 10 个实际有人问的问题；表中的 30 例只是教学素材，必须用客户原话验证。
3. 打开 `docs/diagnose.html`，粘贴自己网站的**查看网页源代码**内容，检测 title / H1 / canonical / noindex / JSON-LD 等结构风险。
4. 打开 `docs/tools.html`，手动记录 ChatGPT Search / Google / Bing 的自然问题、品牌提及和真实自有 URL 引用，导出 CSV。
5. 打开 `docs/measure.html` 导入 CSV，并配合 [30 天清单](docs/30days.html) 优先修复一页真正对成交有帮助的内容。

无后台权限者先做问题研究和公开页面的结构检查，不需要把任何账号密码交给作者。

## 完整资源

| 资源 | 数量 | 最终能拿到的东西 |
|---|---:|---|
| 系统教程 | 26 | 从定位、技术、内容、平台到测量和企业交付的完整知识地图 |
| 保姆级实验 | 16 | 每个实验都有具体操作入口、前置条件、逐步动作、常见失败、完成凭证 |
| 行业案例 | 6 | 个人 AI 品牌、B2B SaaS、本地汽车服务、电商、咨询教育、开源技术产品；全部清楚标明教学模拟 |
| 可编辑模板 | 25 | 目标卡、问题池、原始可见性日志、技术审查、SOW、交付周报、线索归因、成本报价等 |
| 30 天计划 | 30 | 每天一个可交付动作，浏览器本地记录勾选 |
| 浏览器工具 | 4 | 原有监测/红队自评 + 新增 HTML 检查、CSV 分析、企业报价测算（合计四类入口） |
| Python 脚本 | 2 核心工具 | `site_audit.py` 与 `geo_report.py`；不需要第三方依赖或联网 |
| Prompt | 12 | 辅助需求提取、证据审查、页面构建与交付，不伪造事实 |
| 网站页面 | 60 | 静态可爬取 HTML 页面，可直接用 GitHub Pages 部署 |
| 自动化检查 | 15 单测 | 源数据、样例、技术诊断、指标分母、导航和生成质量门禁 |

**注意**：模板 `templates/25-pricing-estimation.csv` 内有表格公式，供你在兼容电子表格工具中使用；报价中的成本、工时与毛利率全部由使用者输入，不是市场行情或收益预测。

## 先选适合自己的路线

- **个人和自由职业者**：LAB 01 → 02 → 08 → 13 → 15，完成一条从真实客户问题到咨询的闭环。
- **网站维护与开发人员**：LAB 06 → 07 → 10 → 04 → 05，解决可读性、抓取、搜索与后台数据问题。
- **企业 GEO 服务商**：LAB 01 → 03 → 04 → 05 → 14 → 16，建立 SOW、权责、证据、验收和月度复盘。
- **技术开源产品**：LAB 06 → 08 → 12 → 13，先提供可运行的文档、演示与技术证据。
- **跨境业务**：LAB 02 → 09 → 11 → 13 → 15，先确定真实可交付地区和客户问法。

## 直接运行（Python 标准库，无需 npm）

如果只想阅读，双击 `docs/index.html` 即可；某些浏览器对本地数据访问限制较严格，推荐在解压目录里启动静态服务：

```bash
python3 -m http.server 8000 --directory docs
# 在浏览器打开 http://localhost:8000
```

结构检查（**离线**，请先保存有权限的网站源代码）：

```bash
python3 scripts/site_audit.py --file examples/sample-broken.html --json
python3 scripts/site_audit.py --file examples/sample-good.html --url https://example.com/article
# --file 可替换成你自己的 HTML；不会自动抓取网站
```

CSV 观察报告（**离线**，不调用任何 AI 搜索 API）：

```bash
python3 scripts/geo_report.py examples/synthetic-visibility.csv
python3 scripts/geo_report.py examples/synthetic-visibility.csv --json
# 示例数据是手工合成的，不能当作客户成果
```

更改正文/模板后的构建与检查：

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
node --check docs/assets/app.js     # 可选，需 Node.js
node --check docs/assets/extras.js  # 可选，需 Node.js
# 如已安装 Playwright 和 Chromium，再运行：
python3 scripts/browser_smoke_v2.py
```

## 仓库结构

```text
geo-handbook/
├── README.md · GEO_OPERATING_MANUAL.md · PROMPT_LIBRARY.md
├── GROWTH_AND_MONETIZATION.md · RED_TEAM_V2.md · PUBLISH.md
├── chapters/                26 章 Markdown
├── labs/                    16 个独立动手实验
├── cases/                   6 个明确标注模拟的行业案例
├── templates/               25 个可编辑模板
├── playbooks/               4 个行业策略补充
├── examples/                故意完好/故意缺陷 HTML、合成 CSV
├── scripts/                 生成器、CLI 工具、质量门禁、单测和浏览器烟测
├── docs/                    GitHub Pages 静态网站（60 页面）
│   ├── labs/ · cases/ · lessons/
│   ├── tools.html · diagnose.html · measure.html · pricing.html
│   ├── assets/app.js · assets/extras.js · assets/style.css
│   └── downloads/
└── .github/workflows/pages.yml
```

## 衡量指标的正确分母

**自然提及率 = 自然提问且真实触发 AI 回答中提及品牌的次数 / 同类有效测试回答数。**

**自有 URL 引用率 = 同类有效回答中附有真实自有引用 URL 的次数 / 同类有效测试回答数。**

手工记录、Google 生成式 AI 展示量、Bing AI 引用、网站访问、有效咨询和订单来自不同渠道，不要直接相加。后测还需固定平台、地区与问题；即便观察到变化，也不直接证明因果。

## 对抗式审核与真实状态

- ✅ 2026-11-05：本地构建、60 个 HTML 页面内部链接检查、15 项 Python 单测、JS 语法检查通过。
- ✅ 2026-11-05：Chromium DOM 注入环境对 6 个代表性页面及 4 类实际交互进行测试，390px 移动端无横向溢出。
- ⏳ **未验证**：GitHub Pages 线上可访问、真实浏览器页面导航及刷新后 localStorage 持久化、客户网站收录、AI 实际引用和商业转化。执行环境禁止直接浏览本地/测试网址。参见 [RED_TEAM_V2.md](RED_TEAM_V2.md)。
- 所有案例演练和 sample CSV 都标注了模拟性质；没有伪造用户数、客户、引用成功率或 GEO 营收。

## 发布与参与

**GitHub 源码已公开发布**：[`AIPMAndy/geo-handbook`](https://github.com/AIPMAndy/geo-handbook)，106 个源文件已提交到 `main`。GitHub Actions 的重建、内容校验、15 项单测和 JavaScript 检查已通过。**GitHub Pages 仍需仓库管理员在 [Settings → Pages](https://github.com/AIPMAndy/geo-handbook/settings/pages) 选择 `GitHub Actions` 作为 Source**，再重新运行 [Deploy GEO Handbook](https://github.com/AIPMAndy/geo-handbook/actions/workflows/pages.yml)。正式部署成功前，在线网站 URL 仅为预期地址。

项目采用 [MIT 开源协议](LICENSE)。问题反馈可在部署后使用 GitHub Issue，也可以参考 [贡献指南](CONTRIBUTING.md)。提交真实案例请提供可验证来源和使用许可，不要上传未脱敏的客户隐私信息。

**AI 酋长 Andy** · [个人和企业服务官网](https://metaver.vip/) · 微信 `AIPMAndy`
