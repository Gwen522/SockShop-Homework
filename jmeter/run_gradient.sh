#!/bin/zsh
# 梯度负载测试: 在不同并发用户数下分别压测, 采集各档性能数据用于对比分析
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy

# 路径自动定位, 换电脑不用改
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$DIR")"
# JMeter: 优先用项目自带的, 没有就用系统 PATH 里的
if [ -x "$ROOT/tools/apache-jmeter-5.6.3/bin/jmeter" ]; then
  JM="$ROOT/tools/apache-jmeter-5.6.3/bin/jmeter"
else
  JM="jmeter"
fi
cd "$DIR"
mkdir -p gradient
rm -f gradient/*.jtl

# 各档位: threads(并发) loops(每线程循环) ramp(爬坡秒)
threads_list=(10 50 100 200 300)
loops_list=(100 40 20 10 7)
ramp_list=(2 5 5 8 10)

for i in {1..5}; do
  t=${threads_list[$i]}
  l=${loops_list[$i]}
  r=${ramp_list[$i]}
  echo ""
  echo "===== 压测档位: ${t} 并发用户 (每用户 ${l} 次, ramp ${r}s) ====="
  "$JM" -n -t load_gradient.jmx -l "gradient/result_${t}.jtl" \
    -Jthreads=$t -Jloops=$l -Jramp=$r \
    2>&1 | grep -E "^summary =" | tail -1
done

echo ""
echo "所有梯度压测完成"
