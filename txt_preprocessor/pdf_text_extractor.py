#!/usr/bin/env python3
"""
智能PDF文本提取器
专门处理两栏布局的PDF文档，确保正确的阅读顺序
"""

import fitz  # PyMuPDF
import pdfplumber
import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """文本块数据结构"""
    text: str
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    page_num: int
    column: int = 0  # 0=左栏, 1=右栏, -1=不确定


class TwoColumnPDFExtractor:
    """两栏PDF文本提取器"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.pages_text_blocks: List[List[TextBlock]] = []
        
    def extract_text_blocks(self, page_num: int) -> List[TextBlock]:
        """从指定页面提取文本块"""
        page = self.doc[page_num]
        blocks = []
        
        # 使用PyMuPDF提取文本块
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" in block:  # 文本块
                text_lines = []
                bbox = block["bbox"]  # (x0, y0, x1, y1)
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    if line_text.strip():
                        text_lines.append(line_text)
                
                if text_lines:
                    text = " ".join(text_lines)
                    if text.strip():
                        blocks.append(TextBlock(
                            text=text.strip(),
                            bbox=bbox,
                            page_num=page_num
                        ))
        
        return blocks
    
    def detect_columns(self, blocks: List[TextBlock]) -> List[TextBlock]:
        """检测并标记文本块的栏位"""
        if not blocks:
            return blocks
            
        # 计算页面宽度
        page_width = max(block.bbox[2] for block in blocks)
        
        # 尝试找到分栏点
        # 方法1: 基于x坐标的分布
        x_positions = [block.bbox[0] for block in blocks]
        x_positions.sort()
        
        # 寻找可能的栏位分界点
        column_boundary = self._find_column_boundary(x_positions, page_width)
        
        if column_boundary is None:
            logger.warning("无法检测到明显的两栏布局，使用启发式方法")
            column_boundary = page_width * 0.5
        
        # 标记每个文本块的栏位
        for block in blocks:
            if block.bbox[0] < column_boundary:
                block.column = 0  # 左栏
            else:
                block.column = 1  # 右栏
                
        return blocks
    
    def _find_column_boundary(self, x_positions: List[float], page_width: float) -> Optional[float]:
        """寻找栏位分界点"""
        if len(x_positions) < 4:
            return None
            
        # 创建x坐标的直方图
        bin_size = page_width / 20
        bins = [0] * 20
        
        for x in x_positions:
            bin_idx = min(int(x / bin_size), 19)
            bins[bin_idx] += 1
        
        # 寻找两个峰值之间的谷底
        max_bin = max(bins)
        threshold = max_bin * 0.3
        
        valleys = []
        for i in range(1, len(bins) - 1):
            if bins[i] < threshold and bins[i-1] >= threshold and bins[i+1] >= threshold:
                valleys.append(i)
        
        if valleys:
            # 选择中间的谷底作为分界点
            valley_idx = valleys[len(valleys) // 2]
            return valley_idx * bin_size
            
        return None
    
    def reorder_text_blocks(self, blocks: List[TextBlock]) -> List[TextBlock]:
        """重新排序文本块以保持正确的阅读顺序"""
        if not blocks:
            return blocks
        
        # 按页面分组
        pages = {}
        for block in blocks:
            if block.page_num not in pages:
                pages[block.page_num] = []
            pages[block.page_num].append(block)
        
        reordered_blocks = []
        
        # 处理每一页
        for page_num in sorted(pages.keys()):
            page_blocks = pages[page_num]
            
            # 按y坐标排序（从上到下）
            page_blocks.sort(key=lambda b: b.bbox[1])
            
            # 检测是否为两栏布局
            left_blocks = [b for b in page_blocks if b.column == 0]
            right_blocks = [b for b in page_blocks if b.column == 1]
            
            if left_blocks and right_blocks:
                # 两栏布局：交替读取左栏和右栏的内容
                reordered_blocks.extend(self._interleave_columns(left_blocks, right_blocks))
            else:
                # 单栏布局：直接按y坐标排序
                reordered_blocks.extend(page_blocks)
        
        return reordered_blocks
    
    def _interleave_columns(self, left_blocks: List[TextBlock], right_blocks: List[TextBlock]) -> List[TextBlock]:
        """交替排列两栏的内容"""
        result = []
        
        # 创建y坐标到文本块的映射
        left_y_map = {block.bbox[1]: block for block in left_blocks}
        right_y_map = {block.bbox[1]: block for block in right_blocks}
        
        # 获取所有y坐标并排序
        all_y_coords = sorted(set(left_y_map.keys()) | set(right_y_map.keys()))
        
        # 按行交替添加文本块
        for y in all_y_coords:
            if y in left_y_map:
                result.append(left_y_map[y])
            if y in right_y_map:
                result.append(right_y_map[y])
        
        return result
    
    def extract_text(self) -> str:
        """提取整个PDF的文本"""
        all_blocks = []
        
        # 提取所有页面的文本块
        for page_num in range(len(self.doc)):
            logger.info(f"处理第 {page_num + 1} 页")
            blocks = self.extract_text_blocks(page_num)
            all_blocks.extend(blocks)
        
        # 检测栏位
        all_blocks = self.detect_columns(all_blocks)
        
        # 重新排序
        ordered_blocks = self.reorder_text_blocks(all_blocks)
        
        # 合并文本
        text_parts = []
        for block in ordered_blocks:
            text_parts.append(block.text)
        
        return "\n".join(text_parts)
    
    def extract_with_pdfplumber(self) -> str:
        """使用pdfplumber作为备用方法"""
        logger.info("使用pdfplumber提取文本...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            text_parts = []
            
            for page_num, page in enumerate(pdf.pages):
                logger.info(f"处理第 {page_num + 1} 页 (pdfplumber)")
                
                # 尝试提取文本
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def close(self):
        """关闭PDF文档"""
        if self.doc:
            self.doc.close()


def convert_pdf_to_txt(pdf_path: str, output_path: str = None, use_pdfplumber: bool = False) -> str:
    """
    将PDF转换为文本文件
    
    Args:
        pdf_path: PDF文件路径
        output_path: 输出文本文件路径，如果为None则自动生成
        use_pdfplumber: 是否使用pdfplumber作为备用方法
    
    Returns:
        提取的文本内容
    """
    if output_path is None:
        output_path = pdf_path.replace('.pdf', '.txt')
    
    extractor = TwoColumnPDFExtractor(pdf_path)
    
    try:
        if use_pdfplumber:
            text = extractor.extract_with_pdfplumber()
        else:
            text = extractor.extract_text()
        
        # 清理文本
        text = clean_extracted_text(text)
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"文本已保存到: {output_path}")
        return text
        
    except Exception as e:
        logger.error(f"提取失败: {e}")
        logger.info("尝试使用pdfplumber备用方法...")
        
        try:
            text = extractor.extract_with_pdfplumber()
            text = clean_extracted_text(text)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"使用pdfplumber成功提取并保存到: {output_path}")
            return text
            
        except Exception as e2:
            logger.error(f"备用方法也失败: {e2}")
            raise
    
    finally:
        extractor.close()


def clean_extracted_text(text: str) -> str:
    """清理提取的文本"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # 多个换行符替换为两个
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符替换为单个空格
    text = re.sub(r'\n ', '\n', text)  # 换行符后的空格
    
    # 移除页眉页脚等常见噪音
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 跳过可能是页眉页脚的行（数字、页码等）
        if re.match(r'^\d+$', line) or re.match(r'^\d+\s*$', line):
            continue
            
        # 跳过过短的行（可能是噪音）
        if len(line) < 3:
            continue
            
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_text_extractor.py <pdf_file> [output_file]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        text = convert_pdf_to_txt(pdf_file, output_file)
        print(f"成功提取 {len(text)} 个字符的文本")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

