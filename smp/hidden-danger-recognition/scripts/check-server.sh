#!/usr/bin/env bash
# check-server.sh — 探测隐患识别服务是否存活
# Usage: bash /path/to/check-server.sh <base_url>
#   e.g. bash check-server.sh http://101.204.230.42:2044
#
# Exit codes:
#   0 — ALIVE (服务正常)
#   1 — WARN  (TCP通但HTTP无响应)
#   2 — INFO  (端点404/其他状态码)
#   3 — FAIL  (服务完全不可达)

BASE="${1:-http://101.204.230.42:2044}"

# 1) TCP 可用性
if ! curl -s --connect-timeout 5 --max-time 8 "$BASE/" >/dev/null 2>&1; then
    echo "FAIL 无法建立 TCP 连接 — $BASE/"
    exit 3
fi

# 2) HTTP 响应状态码
CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$BASE/" 2>&1)

case "$CODE" in
    000)
        echo "WARN TCP 可达但服务端无 HTTP 响应（状态码 000）— 可能存在服务重启或应用层挂起"
        echo "INFO 建议等 10-30 秒后重试，或联系运维重启服务"
        exit 1
        ;;
    200|301|302|307|308|401|403|405)
        echo "ALIVE 服务正常运行（HTTP $CODE）"
        echo "INFO 端点可用列表："
        echo "      POST /ImageReco_HiddenDanger/   (JSON, imgfile=)"
        echo "      POST /streaming/hidden_danger   (文本, image_file=)"
        exit 0
        ;;
    404)
        echo "WARN 根路径返回 404，端点可能已迁移"
        echo "INFO 尝试 /docs 或 /openapi.json 发现实际端点"
        exit 2
        ;;
    *)
        echo "INFO 服务返回 HTTP $CODE — 非标准状态，检查服务端配置"
        exit 2
        ;;
esac
