#!/usr/bin/env python3
"""
独立的PDF转TXT工具
专门处理两栏布局的PDF文档，确保正确的阅读顺序

使用方法:
1. 单文件转换: python pdf_to_txt.py input.pdf [output.txt]
2. 批量转换: python pdf_to_txt.py --batch input_folder [output_folder]
3. 预览结构: python pdf_to_txt.py --preview input.pdf
"""

import os
import argparse
import glob
from pathlib import Path
from pdf_text_extractor import convert_pdf_to_txt, TwoColumnPDFExtractor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_single_pdf(pdf_path: str, output_path: str = None, use_pdfplumber: bool = False):
    """
    转换单个PDF文件
    
    Args:
        pdf_path: PDF文件路径
        output_path: 输出文本文件路径，如果为None则自动生成
        use_pdfplumber: 是否使用pdfplumber作为备用方法
    
    Returns:
        提取的文本内容
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF文件不存在: {pdf_path}")
        return None
    
    if output_path is None:
        output_path = pdf_path.replace('.pdf', '.txt')
    
    logger.info(f"开始转换: {pdf_path}")
    logger.info(f"输出文件: {output_path}")
    
    try:
        text = convert_pdf_to_txt(pdf_path, output_path, use_pdfplumber)
        logger.info(f"✅ 转换成功!")
        logger.info(f"📄 提取了 {len(text)} 个字符")
        logger.info(f"💾 已保存到: {output_path}")
        return text
    except Exception as e:
        logger.error(f"❌ 转换失败: {e}")
        return None


def convert_pdfs_in_folder(input_folder: str, output_folder: str = None, use_pdfplumber: bool = False):
    """
    批量转换文件夹中的PDF文件
    
    Args:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径，如果为None则使用input_folder
        use_pdfplumber: 是否使用pdfplumber作为备用方法
    """
    if not os.path.exists(input_folder):
        logger.error(f"输入文件夹不存在: {input_folder}")
        return
    
    if output_folder is None:
        output_folder = input_folder
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 查找所有PDF文件
    pdf_files = glob.glob(os.path.join(input_folder, "**/*.pdf"), recursive=True)
    
    if not pdf_files:
        logger.warning(f"在 {input_folder} 中未找到PDF文件")
        return
    
    logger.info(f"📁 找到 {len(pdf_files)} 个PDF文件")
    logger.info(f"📂 输出目录: {output_folder}")
    
    success_count = 0
    failed_files = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"\n[{i}/{len(pdf_files)}] 处理: {os.path.basename(pdf_file)}")
        
        try:
            # 生成输出文件名
            pdf_path = Path(pdf_file)
            relative_path = pdf_path.relative_to(input_folder)
            output_path = Path(output_folder) / relative_path.with_suffix('.txt')
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换PDF
            text = convert_pdf_to_txt(pdf_file, str(output_path), use_pdfplumber)
            
            logger.info(f"✅ 成功: {os.path.basename(pdf_file)} -> {output_path.name}")
            logger.info(f"📄 提取了 {len(text)} 个字符")
            success_count += 1
            
        except Exception as e:
            logger.error(f"❌ 失败: {os.path.basename(pdf_file)} - {e}")
            failed_files.append(pdf_file)
    
    # 总结
    logger.info(f"\n🎉 批量转换完成!")
    logger.info(f"✅ 成功: {success_count}/{len(pdf_files)}")
    
    if failed_files:
        logger.warning(f"❌ 失败: {len(failed_files)} 个文件")
        for failed_file in failed_files:
            logger.warning(f"  - {failed_file}")


def preview_pdf_structure(pdf_path: str):
    """预览PDF结构，帮助用户了解文档布局"""
    if not os.path.exists(pdf_path):
        logger.error(f"PDF文件不存在: {pdf_path}")
        return
    
    logger.info(f"🔍 分析PDF结构: {pdf_path}")
    
    extractor = TwoColumnPDFExtractor(pdf_path)
    
    try:
        total_pages = len(extractor.doc)
        logger.info(f"📄 总页数: {total_pages}")
        
        # 分析前几页的结构
        pages_to_analyze = min(3, total_pages)
        logger.info(f"📊 分析前 {pages_to_analyze} 页的布局...")
        
        for page_num in range(pages_to_analyze):
            logger.info(f"\n=== 第 {page_num + 1} 页分析 ===")
            
            blocks = extractor.extract_text_blocks(page_num)
            blocks = extractor.detect_columns(blocks)
            
            left_blocks = [b for b in blocks if b.column == 0]
            right_blocks = [b for b in blocks if b.column == 1]
            
            logger.info(f"📝 左栏文本块: {len(left_blocks)} 个")
            logger.info(f"📝 右栏文本块: {len(right_blocks)} 个")
            
            if left_blocks:
                logger.info("📖 左栏示例文本:")
                for i, block in enumerate(left_blocks[:2]):  # 显示前2个块
                    preview_text = block.text[:80] + "..." if len(block.text) > 80 else block.text
                    logger.info(f"  {i+1}: {preview_text}")
            
            if right_blocks:
                logger.info("📖 右栏示例文本:")
                for i, block in enumerate(right_blocks[:2]):  # 显示前2个块
                    preview_text = block.text[:80] + "..." if len(block.text) > 80 else block.text
                    logger.info(f"  {i+1}: {preview_text}")
            
            # 判断布局类型
            if left_blocks and right_blocks:
                logger.info("📐 布局类型: 两栏布局")
            elif left_blocks or right_blocks:
                logger.info("📐 布局类型: 单栏布局")
            else:
                logger.info("📐 布局类型: 无法检测到文本块")
    
    except Exception as e:
        logger.error(f"分析失败: {e}")
    
    finally:
        extractor.close()


def main():
    parser = argparse.ArgumentParser(
        description="PDF转TXT工具 - 专门处理两栏布局的PDF文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 单文件转换
  python pdf_to_txt.py document.pdf
  python pdf_to_txt.py document.pdf output.txt
  
  # 批量转换
  python pdf_to_txt.py --batch input_folder
  python pdf_to_txt.py --batch input_folder output_folder
  
  # 预览PDF结构
  python pdf_to_txt.py --preview document.pdf
        """
    )
    
    parser.add_argument("input", help="输入PDF文件或文件夹路径")
    parser.add_argument("-o", "--output", help="输出文件或文件夹路径")
    parser.add_argument("--batch", action="store_true", help="批量处理文件夹中的所有PDF文件")
    parser.add_argument("--preview", action="store_true", help="预览PDF结构而不转换")
    parser.add_argument("--use-pdfplumber", action="store_true", help="使用pdfplumber作为备用提取方法")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = args.input
    output_path = args.output
    batch = args.batch
    preview = args.preview
    use_pdfplumber = args.use_pdfplumber
    
    logger.info("🚀 PDF转TXT工具启动")
    
    try:
        if preview:
            if os.path.isfile(input_path):
                preview_pdf_structure(input_path)
            else:
                logger.error("❌ 预览功能只支持单个PDF文件")
        elif batch or os.path.isdir(input_path):
            convert_pdfs_in_folder(input_path, output_path, use_pdfplumber)
        else:
            # 单文件转换
            text = convert_single_pdf(input_path, output_path, use_pdfplumber)
            if text:
                logger.info("🎉 转换完成!")
            else:
                logger.error("❌ 转换失败")
                exit(1)
                
    except KeyboardInterrupt:
        logger.info("\n⏹️  用户中断操作")
    except Exception as e:
        logger.error(f"❌ 程序错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()
