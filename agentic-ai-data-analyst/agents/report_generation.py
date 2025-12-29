from state import ReportState
from fpdf import FPDF
import os
from datetime import datetime
import matplotlib
import re

# Ensure a non-interactive backend is used
matplotlib.use('Agg')

# 新增：定义中文字体路径（确保SimHei.ttf已放到fonts目录）
FONT_DIR = os.path.join(os.path.dirname(__file__), "../fonts")
SIMHEI_FONT_PATH = os.path.join(FONT_DIR, "SimHei.ttf")
# 确保字体目录存在
os.makedirs(FONT_DIR, exist_ok=True)

def clean_text_for_pdf(text: str) -> str:
    """
    Cleans text by removing common LLM conversational filler and markdown,
    and ensures UTF-8 encoding for Chinese characters.
    """
    # Remove markdown formatting
    text = text.replace('**', '').replace('*', '').replace('#', '')
    # 处理中文特殊字符，避免编码错误
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    # Strip leading/trailing whitespace and newlines
    return text.strip()

class PDF(FPDF):
    """
    Custom PDF class with Chinese font support and standard header/footer.
    """
    def __init__(self):
        super().__init__()
        # 新增：添加中文字体（SimHei）
        if os.path.exists(SIMHEI_FONT_PATH):
            self.add_font(
                family='SimHei',  # 字体名称，后续调用需一致
                fname=SIMHEI_FONT_PATH,
                uni=True  # 启用Unicode支持，必须设为True才能显示中文
            )
        else:
            print(f"警告：中文字体文件未找到（路径：{SIMHEI_FONT_PATH}），中文将显示为方框")

    def header(self):
          # Set font (使用中文字体SimHei，若不存在则回退到Arial)
        if os.path.exists(SIMHEI_FONT_PATH):
            self.set_font('SimHei', '', 12)
        else:
            self.set_font('Arial', 'B', 12)
        
        if self.page_no() > 1:
            self.cell(0, 10, 'NSCLC数据分析报告', 0, 0, 'C')  # 中文标题
            self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font (支持中文)
        if os.path.exists(SIMHEI_FONT_PATH):
            self.set_font('SimHei', '', 8)
        else:
            self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'第{self.page_no()}页', 0, 0, 'C')  # 中文页码

def create_title_page(pdf):
    """
    Creates the title page for the PDF report (support Chinese).
    """
    pdf.add_page()
    # 标题使用中文字体，加大字号
    if os.path.exists(SIMHEI_FONT_PATH):
        pdf.set_font('SimHei', '', 24)
    else:
        pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 80, 'NSCLC（非小细胞肺癌）数据分析报告', 0, 1, 'C')  # 替换为NSCLC专属标题
    
    # 日期行
    if os.path.exists(SIMHEI_FONT_PATH):
        pdf.set_font('SimHei', '', 16)
    else:
        pdf.set_font('Arial', '', 16)
    today_date = datetime.now().strftime("%Y年%m月%d日")  # 替换为中文日期格式
    pdf.cell(0, 20, f"生成时间：{today_date}", 0, 1, 'C')

def report_generation_node(state: ReportState) -> dict:
    """
    Generates a PDF report from the generated content and visualizations.
    """
    print("\n==========================================")
    print("I am in the report generation node ... ")
    print("============================================")

    report_content = state['report_content']
    output_dir = "output/"
    os.makedirs(output_dir, exist_ok=True)
    # PDF命名为NSCLC专属名称
    pdf_filename = "NSCLC_Data_Analysis_Report.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    pdf = PDF()
    
    # Create the title page
    create_title_page(pdf)
    
    # Add a new page for the main content
    pdf.add_page()

    for content in report_content:
        analysis_name_raw = content.get('analysis_name', '未命名分析')
        narrative_raw = content.get('narrative', '无分析描述.')
        original_result = content.get('original_result')

        # --- FIXES ---
        # 1. Handle cases where the analysis name is a list
        if isinstance(analysis_name_raw, list):
            analysis_name = ' '.join(analysis_name_raw)
        else:
            analysis_name = str(analysis_name_raw)

        # 2. Ensure narrative is a string before cleaning
        if not isinstance(narrative_raw, str):
            narrative_text = str(narrative_raw)
        else:
            narrative_text = narrative_raw

        # 3. Clean both the title and the narrative for the PDF
        cleaned_analysis_name = clean_text_for_pdf(analysis_name)
        cleaned_narrative = clean_text_for_pdf(narrative_text)

        # --- 添加分析标题 ---
        if os.path.exists(SIMHEI_FONT_PATH):
            pdf.set_font("SimHei", '', size=16)
        else:
            pdf.set_font("Arial", 'B', size=16)
        pdf.multi_cell(0, 10, txt=cleaned_analysis_name, align='L')
        pdf.ln(2)

        # --- 添加分析描述 ---
        if os.path.exists(SIMHEI_FONT_PATH):
            pdf.set_font("SimHei", size=12)
        else:
            pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, txt=cleaned_narrative)
        pdf.ln(5)

        # If the original result was a plot image, embed it
        if isinstance(original_result, str) and original_result.lower().endswith('.png'):
            if os.path.exists(original_result):
                page_width = pdf.w - 2 * pdf.l_margin
                img_width = page_width * 0.9
                x_pos = (pdf.w - img_width) / 2
                pdf.image(original_result, x=x_pos, w=img_width)
                pdf.ln(5)
            else:
                if os.path.exists(SIMHEI_FONT_PATH):
                    pdf.set_font("SimHei", 'I', size=10)
                else:
                    pdf.set_font("Arial", 'I', size=10)
                pdf.multi_cell(0, 10, txt=f"[图片未找到：{original_result}]")

        # Add a separator line between sections
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(10)

    pdf.output(pdf_path)
    print(f"PDF report generated successfully at: {pdf_path}")
    
    # Return the updated state key
    return {"pdf_path": pdf_path}
