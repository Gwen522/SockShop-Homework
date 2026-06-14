# 用 JMeter 和 Selenium 的结果画几张性能图(给报告用)
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 路径相对脚本位置, 换电脑不用改
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")

with open(os.path.join(RES, "jmeter_gradient_summary.json")) as f:
    g = json.load(f)

users = [r["并发用户数"] for r in g]
tput = [r["吞吐量/s"] for r in g]
avg = [r["平均响应ms"] for r in g]
p90 = [r["P90ms"] for r in g]
p95 = [r["P95ms"] for r in g]
p99 = [r["P99ms"] for r in g]
mx = [r["最大ms"] for r in g]
errs = [r["错误率%"] for r in g]

plt.rcParams.update({"font.size": 11, "figure.dpi": 130, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True})

# 图1: 吞吐量 vs 并发
fig, ax = plt.subplots(figsize=(6.4, 4))
ax.plot(users, tput, "o-", color="#1f77b4", linewidth=2, markersize=7)
for x, y in zip(users, tput):
    ax.annotate(f"{y:.0f}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
ax.set_xlabel("Concurrent Users")
ax.set_ylabel("Throughput (req/s)")
ax.set_title("Throughput vs Concurrent Users")
ax.set_xticks(users)
fig.tight_layout()
fig.savefig(os.path.join(RES, "chart_throughput.png"))
plt.close(fig)

# 图2: 响应时间(平均/P90/P95/P99) vs 并发
fig, ax = plt.subplots(figsize=(6.4, 4))
ax.plot(users, avg, "o-", label="Average", color="#1f77b4", linewidth=2)
ax.plot(users, p90, "s--", label="P90", color="#2ca02c", linewidth=1.6)
ax.plot(users, p95, "^--", label="P95", color="#ff7f0e", linewidth=1.6)
ax.plot(users, p99, "d--", label="P99", color="#d62728", linewidth=1.6)
ax.set_xlabel("Concurrent Users")
ax.set_ylabel("Response Time (ms)")
ax.set_title("Response Time vs Concurrent Users")
ax.set_xticks(users)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(RES, "chart_response_time.png"))
plt.close(fig)

# 图3: 错误率 vs 并发(柱状)
fig, ax = plt.subplots(figsize=(6.4, 4))
bars = ax.bar([str(u) for u in users], errs, color="#d62728", width=0.5)
ax.set_xlabel("Concurrent Users")
ax.set_ylabel("Error Rate (%)")
ax.set_title("Error Rate vs Concurrent Users")
ax.set_ylim(0, max(1, max(errs) * 1.5 + 1))
for b, e in zip(bars, errs):
    ax.annotate(f"{e:.1f}%", (b.get_x() + b.get_width()/2, e), textcoords="offset points",
                xytext=(0, 4), ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(RES, "chart_error_rate.png"))
plt.close(fig)

# 图4: Selenium 各用例页面加载/交互响应时间
with open(os.path.join(RES, "selenium_results_chrome.json")) as f:
    sel = json.load(f)
cases = sel["cases"]
labels = [c["id"] for c in cases]
loads = [c["page_load_ms"] or 0 for c in cases]
acts = [c["action_ms"] or 0 for c in cases]
import numpy as np
x = np.arange(len(labels))
w = 0.38
fig, ax = plt.subplots(figsize=(7.2, 4))
ax.bar(x - w/2, loads, w, label="Page Load (ms)", color="#1f77b4")
ax.bar(x + w/2, acts, w, label="Action Response (ms)", color="#ff7f0e")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Time (ms)")
ax.set_title("Selenium Functional Test - Timing per Case (Chrome)")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(RES, "chart_selenium_timing.png"))
plt.close(fig)

print("已生成 4 张图表:")
for n in ["chart_throughput.png", "chart_response_time.png", "chart_error_rate.png", "chart_selenium_timing.png"]:
    print("  -", n)
