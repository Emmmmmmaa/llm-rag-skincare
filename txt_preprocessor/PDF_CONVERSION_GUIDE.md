# PDF转TXT使用指南

这个工具专门解决两栏布局PDF转换为文本时内容混乱的问题。

## 安装依赖

首先安装所需的Python包：

```bash
# 使用uv安装依赖（推荐）
uv sync

# 或者使用pip
pip install pymupdf pdfplumber pillow
```

## 使用方法

### 1. 单文件转换

```bash
# 基本用法 - 自动生成输出文件名
python pdf_to_txt.py document.pdf

# 指定输出文件名
python pdf_to_txt.py document.pdf output.txt
```

### 2. 批量转换

```bash
# 转换文件夹中所有PDF
python pdf_to_txt.py --batch input_folder

# 指定输出文件夹
python pdf_to_txt.py --batch input_folder output_folder
```

### 3. 预览PDF结构

在转换前，可以先预览PDF的布局结构：

```bash
python pdf_to_txt.py --preview document.pdf
```

### 4. 使用备用方法

如果默认方法失败，可以尝试使用pdfplumber：

```bash
python pdf_to_txt.py document.pdf --use-pdfplumber
```

## 完整工作流程

### 步骤1: PDF转TXT

```bash
# 转换您的PDF文件
python pdf_to_txt.py your_document.pdf

# 或者批量转换
python pdf_to_txt.py --batch pdf_folder
```

### 步骤2: 使用原有RAG流程

转换完成后，将生成的txt文件放入`input-datasets/books/`文件夹，然后使用原有的处理流程：

```bash
# 分块处理
python cli.py chunk

# 生成嵌入
python cli.py embed

# 加载到向量数据库
python cli.py load

# 查询
python cli.py query
```

## 技术特性

### 智能两栏检测
- 自动检测PDF中的两栏布局
- 基于x坐标分布分析栏位分界点
- 处理复杂的页面布局

### 正确的阅读顺序
- 按行交替读取左栏和右栏内容
- 保持文本的逻辑连贯性
- 避免内容混乱

### 多种提取方法
- 主要使用PyMuPDF进行精确提取
- 备用pdfplumber方法处理特殊情况
- 自动降级和错误恢复

### 文本清理
- 移除多余的空白字符
- 过滤页眉页脚等噪音
- 保持文本格式整洁

## 示例输出

转换前的PDF（两栏布局）：
```
左栏内容1    右栏内容1
左栏内容2    右栏内容2
左栏内容3    右栏内容3
```

转换后的TXT（正确顺序）：
```
左栏内容1
右栏内容1
左栏内容2
右栏内容2
左栏内容3
右栏内容3
```

## 故障排除

### 常见问题

1. **转换结果仍然混乱**
   - 尝试使用`--use-pdfplumber`参数
   - 使用`--preview`检查PDF结构
   - 检查PDF是否为扫描版（需要OCR）

2. **提取的文本不完整**
   - 确保PDF不是加密的
   - 检查PDF是否包含图片而非文本

3. **程序崩溃**
   - 检查PDF文件是否损坏
   - 尝试重新下载PDF文件

### 日志信息

程序会显示详细的处理日志：
- ✅ 成功操作
- ❌ 错误信息
- 📄 提取的字符数
- 📁 文件处理进度

## 集成到现有项目

这个工具与您现有的RAG系统完全兼容：

1. 使用`pdf_to_txt.py`转换PDF为TXT
2. 将TXT文件放入`input-datasets/books/`
3. 使用原有的`cli.py`进行后续处理

这样保持了原有工作流程的完整性，同时解决了PDF两栏布局的问题。
