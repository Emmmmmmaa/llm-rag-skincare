# 简化的PDF转TXT工具

## 快速使用

### 单文件转换
```bash
python pdf2txt.py document.pdf
python pdf2txt.py document.pdf -o output.txt
```

### 批量转换
```bash
python pdf2txt.py --batch pdf_folder
python pdf2txt.py --batch pdf_folder -o output_folder
```

### 如果默认方法失败，使用备用方法
```bash
python pdf2txt.py document.pdf --pdfplumber
```

## 功能特点

- ✅ 自动处理两栏布局
- ✅ 保持正确的阅读顺序
- ✅ 自动降级处理（PyMuPDF → pdfplumber）
- ✅ 简洁易用的命令行界面
- ✅ 批量处理支持

## 安装依赖

```bash
pip install PyMuPDF pdfplumber
```

## 工作流程

1. **转换PDF**: `python pdf2txt.py your_file.pdf`
2. **移动到books文件夹**: `mv your_file.txt input-datasets/books/`
3. **使用原有RAG流程**: `python cli.py chunk` → `python cli.py embed` → `python cli.py load` → `python cli.py query`

就这么简单！
