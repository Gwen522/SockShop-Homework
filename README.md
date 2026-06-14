# SockShop 微服务系统测试（Selenium + JMeter）

软件测试与维护（2026 年春）大作业 · 阶段三

本项目在本地部署 [SockShop](https://github.com/microservices-demo/microservices-demo) 微服务系统，使用 **Selenium** 做前端功能测试、**JMeter** 做后端性能测试。

## 目录说明

```
sockshop-testing/
├── docker-compose.yml        # SockShop 部署文件（已适配 Apple 芯片）
├── demo.sh                   # 现场演示一键脚本
├── requirements.txt          # Python 依赖
├── selenium/
│   ├── test_sockshop.py      # 功能测试主脚本（8 个用例）
│   └── demo_visible.py       # 演示用（有界面、放慢动作）
├── jmeter/
│   ├── sockshop_test_plan.jmx   # 多微服务综合测试计划
│   ├── load_gradient.jmx        # 梯度负载测试计划
│   ├── run_gradient.sh          # 批量压测脚本
│   ├── parse_results.py         # 结果解析
│   └── make_charts.py           # 画图
├── screenshots/              # Selenium 截图
└── results/                  # 测试结果与图表
```

## 环境要求

- Docker / Docker Compose
- Python 3.9+，装依赖：`pip install -r requirements.txt`
- Chrome 浏览器（功能测试用）
- JMeter 5.6.3 + Java 11+（性能测试用）

## 怎么跑

### 1. 启动 SockShop

```bash
docker compose up -d
# 浏览器打开 http://localhost:8079 确认能访问
```

### 2. 功能测试（Selenium）

```bash
python selenium/test_sockshop.py                # Chrome（默认）
python selenium/test_sockshop.py --browser safari --no-headless   # Safari
```

### 3. 性能测试（JMeter）

```bash
zsh jmeter/run_gradient.sh      # 跑 5 档并发压测
python jmeter/parse_results.py  # 解析结果
python jmeter/make_charts.py    # 生成图表
```

## 测试结果概览

- **功能测试**：8 个用例（首页 / 浏览 / 详情 / 注册 / 登录 / 加购 / 购物车 / 下单），Chrome 与 Safari 双浏览器均 100% 通过。
- **性能测试**：10～300 并发梯度压测，错误率全程 0%，平均响应时间均在 10ms 以内，峰值吞吐量约 800 req/s。

详见 `report/` 下的测试报告。
