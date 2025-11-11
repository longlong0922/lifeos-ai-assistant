# Dockerfile for LifeOS AI Assistant

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p data logs

# 初始化数据库
RUN python scripts/init_db.py

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app/main.py"]
