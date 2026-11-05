# 参与维护

欢迎贡献真实可复现的技术修复、最新一手官方来源、获得授权的行业实践与新手体验。

1. 创建 Issue：写明影响页面、复现输入、**预期 vs 实际**、相关官方原始来源与核查日期。
2. 课程与实验分别编辑 `content/chapters.py`、`labs/`、`cases/`；修改网站结构时同步更新 `scripts/build.py`。
3. `python3 scripts/build.py && python3 scripts/check.py && python3 -m unittest discover -s scripts -p 'test_*.py' -v`。
4. 有可用 Chromium 时运行 `python3 scripts/browser_smoke_v2.py`；若浏览器受阻，请明确说明未验证范围。
5. 通过 Pull Request 提交修改，注明任何无法直接验证的断言。

新案例必须写清 **真实/模拟**、公开许可、可核查原始记录和日期。不要提交密钥、客户明文身份信息、未授权截图、虚构收入或不真实评价。

作者：AI 酋长 Andy · 官网 https://metaver.vip/
