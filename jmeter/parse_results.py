# 处理 JMeter 跑出来的 jtl 结果, 算出各并发档位的指标(平均/百分位/吞吐等)
import csv, os, json
from collections import defaultdict

# 路径自动相对脚本所在位置, 换电脑不用改
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
GDIR = os.path.join(_HERE, "gradient")
OUT = os.path.join(_ROOT, "results")
os.makedirs(OUT, exist_ok=True)

def pct(sorted_list, p):
    if not sorted_list:
        return 0
    k = int(round((p / 100.0) * (len(sorted_list) - 1)))
    return sorted_list[k]

levels = [10, 50, 100, 200, 300]
rows = []
for lv in levels:
    f = os.path.join(GDIR, f"result_{lv}.jtl")
    if not os.path.exists(f):
        continue
    elapsed = []
    ok = err = 0
    ts_min = None; ts_max = None
    with open(f) as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            try:
                e = int(r["elapsed"]); elapsed.append(e)
                t = int(r["timeStamp"])
                ts_min = t if ts_min is None else min(ts_min, t)
                ts_max = t if ts_max is None else max(ts_max, t)
                if r["success"] == "true":
                    ok += 1
                else:
                    err += 1
            except (KeyError, ValueError):
                pass
    total = ok + err
    elapsed.sort()
    dur_s = (ts_max - ts_min) / 1000.0 if ts_max and ts_min and ts_max > ts_min else 1
    # 加上最后一个请求的耗时让吞吐更准
    tp = round(total / dur_s, 1) if dur_s > 0 else 0
    row = {
        "并发用户数": lv,
        "总请求数": total,
        "成功": ok,
        "失败": err,
        "错误率%": round(err / total * 100, 2) if total else 0,
        "平均响应ms": round(sum(elapsed) / len(elapsed), 1) if elapsed else 0,
        "最小ms": elapsed[0] if elapsed else 0,
        "最大ms": elapsed[-1] if elapsed else 0,
        "中位数ms": pct(elapsed, 50),
        "P90ms": pct(elapsed, 90),
        "P95ms": pct(elapsed, 95),
        "P99ms": pct(elapsed, 99),
        "吞吐量/s": tp,
    }
    rows.append(row)

# 写 CSV
csv_path = os.path.join(OUT, "jmeter_gradient_summary.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# 写 JSON
with open(os.path.join(OUT, "jmeter_gradient_summary.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

# 打印表格
print(f"{'并发':>5} {'请求':>6} {'错误率%':>7} {'平均ms':>7} {'P90':>5} {'P95':>5} {'P99':>5} {'最大ms':>7} {'吞吐/s':>8}")
print("-" * 70)
for r in rows:
    print(f"{r['并发用户数']:>5} {r['总请求数']:>6} {r['错误率%']:>7} {r['平均响应ms']:>7} "
          f"{r['P90ms']:>5} {r['P95ms']:>5} {r['P99ms']:>5} {r['最大ms']:>7} {r['吞吐量/s']:>8}")
print(f"\n汇总已保存: {csv_path}")
