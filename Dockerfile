# SuperStar 学习通刷课 - Home Assistant 加载项
# 构建时从 GitHub 拉取 lispringing/SuperStar 源码并安装依赖。
#
# 注意：Supervisor 2026.04.0 起不再注入 BUILD_FROM，因此不能用
#      ARG BUILD_FROM / FROM $BUILD_FROM，直接写死基础镜像（与本机其它本地加载项一致）。
FROM alpine:3.20

SHELL ["/bin/sh", "-c"]

ENV LANG=C.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    PYTHONDONTWRITEBYTECODE=1

# Python 与编译 lxml 所需的依赖
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    build-base \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    tzdata \
    ca-certificates \
    git

# 拉取 SuperStar 源码到 /app
RUN git clone --depth 1 https://github.com/lispringing/SuperStar.git /app

WORKDIR /app

# 安装 Python 依赖（使用清华镜像加速）
RUN pip3 install --break-system-packages -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 放入配置生成脚本与启动脚本
COPY gen_config.py /app/gen_config.py
COPY run.sh /run.sh

RUN chmod +x /app/gen_config.py /run.sh

# 工作目录与源码一致即可；cookie 读取路径为 cwd 下的 cookies.txt
WORKDIR /app

CMD ["/run.sh"]
