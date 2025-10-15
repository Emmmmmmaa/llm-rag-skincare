# 🚀 LLM-RAG 端到端容器化管道

这是一个完整的端到端容器化RAG系统，支持从PDF文件到查询回答的全流程自动化处理。

## 🏗️ 架构概述

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF摄取       │ -> │  文本预处理     │ -> │  RAG处理        │ -> │  查询服务       │
│ pdf-ingestion   │    │ text-processor  │    │ rag-processor   │    │ query-service   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 文件监控        │    │ Redis消息队列   │    │ ChromaDB        │    │ FastAPI接口     │
│ Watchdog        │    │ Redis           │    │ Vector DB       │    │ REST API        │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 设置环境变量
export GCP_PROJECT="your-gcp-project-id"

# 确保服务账户文件存在
ls secrets/llm-service-account.json
```

### 2. 一键启动

```bash
# 方式1: 使用Makefile（推荐）
make start

# 方式2: 使用启动脚本
./run_pipeline.sh

# 方式3: 直接使用docker-compose
docker-compose -f docker-compose-pipeline.yml up -d
```

### 3. 验证部署

```bash
# 检查服务状态
make test

# 或手动检查
curl http://localhost/api/health
```

## 📊 服务组件

### 🔄 数据处理管道

| 服务 | 功能 | 端口 | 依赖 |
|------|------|------|------|
| `pdf-ingestion` | PDF文件监控和转换 | - | Redis |
| `text-processor` | 文本分块和嵌入生成 | - | Redis, GCP |
| `rag-processor` | 向量数据库加载 | - | Redis, ChromaDB |
| `query-service` | 查询API服务 | 8001 | ChromaDB, Redis |

### 🛠️ 支持服务

| 服务 | 功能 | 端口 | 用途 |
|------|------|------|------|
| `chromadb` | 向量数据库 | 8000 | 存储嵌入向量 |
| `redis` | 消息队列/缓存 | 6379 | 服务间通信 |
| `nginx` | API网关 | 80 | 负载均衡和路由 |
| `pipeline-controller` | 管道控制 | - | 协调整个流程 |

## 🔧 使用方法

### 📁 文件处理流程

1. **放入PDF文件**
   ```bash
   # 将PDF文件放入监控目录
   cp your_document.pdf input-datasets/pdf/
   ```

2. **自动处理**
   - 系统自动检测PDF文件
   - 转换为TXT格式
   - 进行文本分块
   - 生成嵌入向量
   - 存储到ChromaDB

3. **查询使用**
   ```bash
   # 向量搜索
   curl -X POST http://localhost/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "your question", "n_results": 5}'
   
   # 聊天模式
   curl -X POST http://localhost/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "chat: your question"}'
   ```

### 🌐 Web界面

- **主页**: http://localhost
- **API文档**: http://localhost/api/docs
- **健康检查**: http://localhost/api/health
- **ChromaDB管理**: http://localhost/chromadb

## 🎛️ 管道控制

### 启动模式

```bash
# 事件驱动模式（默认）
export PIPELINE_MODE=event-driven
make start

# 顺序执行模式
export PIPELINE_MODE=sequential
make start
```

### 监控和日志

```bash
# 查看所有服务日志
make logs

# 查看特定服务日志
docker-compose -f docker-compose-pipeline.yml logs -f query-service

# 查看服务状态
docker-compose -f docker-compose-pipeline.yml ps
```

## 🔍 API接口

### 查询接口

```bash
POST /api/query
{
  "query": "your question",
  "method": "char-split",
  "n_results": 10
}
```

### 健康检查

```bash
GET /api/health
```

### 集合管理

```bash
GET /api/collections
```

## 🛠️ 开发和管理

### 常用命令

```bash
# 构建镜像
make build

# 启动服务
make start

# 停止服务
make stop

# 重启服务
make restart

# 清理资源
make clean

# 测试功能
make test
```

### 调试模式

```bash
# 查看详细日志
docker-compose -f docker-compose-pipeline.yml logs -f --tail=100

# 进入容器调试
docker exec -it pdf-ingestion /bin/bash
docker exec -it query-service /bin/bash
```

## 🔧 配置选项

### 环境变量

```bash
# 必需配置
GCP_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json

# 可选配置
PIPELINE_MODE=event-driven  # 或 sequential
REDIS_URL=redis://redis:6379
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
API_PORT=8001
```

### 服务配置

每个服务都可以通过环境变量进行配置，详见各个服务的Dockerfile和环境变量设置。

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查日志
   make logs
   
   # 检查环境变量
   echo $GCP_PROJECT
   ```

2. **PDF处理失败**
   ```bash
   # 检查PDF文件格式
   # 确保文件不是损坏的
   # 检查文件权限
   ```

3. **API连接失败**
   ```bash
   # 检查服务状态
   docker-compose -f docker-compose-pipeline.yml ps
   
   # 测试网络连接
   curl http://localhost/api/health
   ```

### 性能优化

1. **调整批处理大小**
   ```bash
   export BATCH_SIZE=100
   ```

2. **调整分块大小**
   ```bash
   export CHUNK_SIZE=350
   ```

3. **增加Redis缓存**
   ```bash
   export REDIS_CACHE_TTL=3600
   ```

## 📈 扩展性

### 水平扩展

```bash
# 扩展查询服务
docker-compose -f docker-compose-pipeline.yml up -d --scale query-service=3
```

### 添加新服务

1. 创建新的Dockerfile
2. 添加到docker-compose-pipeline.yml
3. 配置服务间通信
4. 更新nginx配置

## 🔐 安全考虑

1. **API认证**: 可以添加JWT认证
2. **网络隔离**: 使用Docker网络隔离服务
3. **数据加密**: 敏感数据传输加密
4. **访问控制**: 限制API访问权限

## 📚 相关文档

- [PDF转换指南](./txt_preprocessor/PDF_CONVERSION_GUIDE.md)
- [API文档](http://localhost/api/docs)
- [ChromaDB文档](https://docs.trychroma.com/)
- [FastAPI文档](https://fastapi.tiangolo.com/)

---

🎉 **恭喜！您已经成功部署了LLM-RAG端到端容器化管道！**
