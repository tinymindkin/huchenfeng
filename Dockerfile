FROM python:3.12-slim

# 避免生成 .pyc；实时输出日志
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安装编译依赖和 OpenCV 运行时依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libglib2.0-0 \
       libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖以利用缓存
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 需要在运行时通过环境变量提供 GOOGLE_API_KEY
ENV GOOGLE_API_KEY=""

# 默认执行生成脚本；如需其他入口，可在 docker run 时覆盖 CMD
CMD ["python", "generate_answer.py"]
