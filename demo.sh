#!/bin/zsh
# ============================================================
#  现场演示一键脚本 —— 软件测试大作业 阶段三
#  用法: 在终端里 cd 到本项目目录后执行:  zsh demo.sh
#  作用: 按菜单选择, 现场演示 Selenium 功能测试 / JMeter 性能测试 / 看结果
# ============================================================

# 清掉可能存在的代理设置(否则连不上 localhost)
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy

# 自动定位脚本所在目录(换任何电脑都不用改路径)
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Python: 优先用 python3, 没有就用 python
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi

# JMeter: 优先用项目自带的, 没有就用系统 PATH 里的 jmeter
if [ -x "$DIR/tools/apache-jmeter-5.6.3/bin/jmeter" ]; then
  JMETER="$DIR/tools/apache-jmeter-5.6.3/bin/jmeter"
elif command -v jmeter >/dev/null 2>&1; then
  JMETER="jmeter"
else
  JMETER=""
fi

echo ""
echo "=============================================="
echo "   SockShop 测试演示  (阶段三: Selenium + JMeter)"
echo "=============================================="
echo ""

# 先确认网站在跑
echo "检查 SockShop 是否在运行..."
code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8079/ 2>/dev/null)
if echo "$code" | grep -q "200\|301"; then
  echo "  -> SockShop 正常运行 (http://localhost:8079)"
else
  echo "  -> 网站没起来, 正在启动 (大概等 20 秒)..."
  docker compose up -d >/dev/null 2>&1
  sleep 20
fi
echo ""

echo "请选择要演示的内容, 输入数字后按回车:"
echo "  1) Selenium 功能测试  (会弹出浏览器, 自动操作给大家看)"
echo "  2) JMeter  性能测试   (命令行压测, 实时打印结果)"
echo "  3) 直接看已经跑好的结果 (打开网页, 最快)"
echo ""
echo -n "你的选择 [1/2/3]: "
read choice

case "$choice" in
  1)
    echo ""
    echo ">> 启动 Selenium 功能测试(有界面慢速版), 请看弹出的浏览器窗口..."
    "$PY" "$DIR/selenium/demo_visible.py"
    ;;
  2)
    echo ""
    if [ -z "$JMETER" ]; then
      echo "!! 没找到 JMeter, 请先安装, 或确认项目 tools 目录里有 apache-jmeter"
    else
      echo ">> 启动 JMeter 性能测试(100 并发用户压一遍)..."
      "$JMETER" -n -t "$DIR/jmeter/load_gradient.jmx" -l /tmp/demo_result.jtl \
        -Jthreads=100 -Jloops=20 -Jramp=5 2>&1 | grep -E "summary"
      echo ""
      echo ">> 压测完成! 上面 Err 那一列就是错误率(0 表示全成功)"
    fi
    ;;
  3)
    echo ""
    echo ">> 打开 JMeter 可视化报告 和 性能图表..."
    open "$DIR/jmeter/html_report/index.html" 2>/dev/null || xdg-open "$DIR/jmeter/html_report/index.html" 2>/dev/null
    open "$DIR/results/chart_throughput.png" 2>/dev/null || xdg-open "$DIR/results/chart_throughput.png" 2>/dev/null
    open "$DIR/results/chart_response_time.png" 2>/dev/null || xdg-open "$DIR/results/chart_response_time.png" 2>/dev/null
    ;;
  *)
    echo "没识别到选择, 默认打开已有结果..."
    open "$DIR/jmeter/html_report/index.html" 2>/dev/null
    ;;
esac

echo ""
echo "演示结束。"
