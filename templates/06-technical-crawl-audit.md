# 网站 GEO 技术体检表

注意：在公开网站执行，不要把客户后台凭据上传 GitHub。

| URL | HTTP 200 | 未登录可读 | robots 允许 | 非 noindex | canonical | HTML 主体可读 | 移动端 | 问题/复测 |
|---|---|---|---|---|---|---|---|---|
| https://example.com/your-page | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 〔〕 |

## 手工与命令行验证
```bash
curl -IL https://example.com/your-page
curl -L https://example.com/robots.txt
curl -L https://example.com/sitemap.xml
curl -L https://example.com/your-page | head -c 2000
```
确认是否意外出现 `noindex`，是否页面主要内容只靠前端 JS 加载。

## OpenAI 官方爬虫
- OAI-SearchBot：ChatGPT 搜索展示相关。
- GPTBot：训练相关，可独立管理。
- ChatGPT-User：用户触发的访问，与自动 Search 抓取并非相同。
- 不要把允许 robots 抓取解释为保证收录/引用。

官方： https://developers.openai.com/api/docs/bots
