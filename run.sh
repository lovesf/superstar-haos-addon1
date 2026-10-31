#!/usr/bin/env bash
# SuperStar 加载项启动脚本（alpine + CMD，不依赖 s6 / bashio）
set -uo pipefail

cd /app || exit 1

echo "[superstar] 根据加载项配置生成 config.ini ..."
python3 /app/gen_config.py
if [ $? -ne 0 ]; then
    echo "[superstar] ✗ 生成 config.ini 失败，加载项终止"
    exit 1
fi

echo "[superstar] 开始刷课 ..."
python3 /app/main.py -c /app/config.ini
RC=$?
if [ $RC -ne 0 ]; then
    echo "[superstar] ✗ 刷课进程异常退出（exit=$RC），请查看上方日志"
else
    echo "[superstar] ✓ 刷课任务结束。"
fi

echo "[superstar] 加载项保持运行以便查看日志；如需再次运行，请在加载项页面点「重启」。"
exec sleep infinity
