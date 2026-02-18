import nbformat
import base64
import os

NOTEBOOK_FILE = 'analysis_shap_lime.ipynb'
OUTPUT_TEX = 'report.tex'
IMAGE_DIR = 'images'

def convert_notebook_to_latex(notebook_path, output_path, image_dir):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    latex_content = []
    
    # Header for Overleaf / XeLaTeX with Persian support
    latex_content.append(r"""\documentclass{article}
\usepackage{graphicx}
\usepackage{float}
\usepackage{listings}
\usepackage{color}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{xepersian}

\settextfont{Yas} % You might need to upload a font like Yas.ttf or Tahoma.ttf to Overleaf
% Or use a font available on Overleaf's system if you don't upload one.
% For example: \settextfont{FreeFarsi} if available, or just upload a .ttf file.

\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize\setLTR,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2
}
\lstset{style=mystyle}

\title{Breast Cancer Analysis with SHAP and LIME}
\author{Mina}
\date{\today}

\begin{document}

\maketitle
\tableofcontents
\newpage

""")

    img_count = 0

    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            text = cell.source
            # Basic Markdown to LaTeX conversion (very simple)
            text = text.replace('# ', r'\section{').replace('## ', r'\subsection{').replace('### ', r'\subsubsection{')
            if text.startswith(r'\section') or text.startswith(r'\subsection') or text.startswith(r'\subsubsection'):
                text += '}'
            latex_content.append(text + '\n\n')
        
        elif cell.cell_type == 'code':
            latex_content.append(r'\begin{latin}')
            latex_content.append(r'\begin{lstlisting}[language=Python]')
            latex_content.append(cell.source)
            latex_content.append(r'\end{lstlisting}')
            latex_content.append(r'\end{latin}' + '\n')

            # Process outputs
            if 'outputs' in cell:
                for output in cell.outputs:
                    if output.output_type == 'stream':
                        latex_content.append(r'\begin{latin}')
                        latex_content.append(r'\begin{verbatim}')
                        latex_content.append(output.text)
                        latex_content.append(r'\end{verbatim}')
                        latex_content.append(r'\end{latin}' + '\n')
                    
                    elif output.output_type == 'display_data' or output.output_type == 'execute_result':
                        if 'image/png' in output.data:
                            img_data = base64.b64decode(output.data['image/png'])
                            img_filename = f'img_{img_count}.png'
                            img_path = os.path.join(image_dir, img_filename)
                            with open(img_path, 'wb') as img_f:
                                img_f.write(img_data)
                            
                            latex_content.append(r'\begin{figure}[H]')
                            latex_content.append(r'\centering')
                            latex_content.append(f'\\includegraphics[width=0.8\\textwidth]{{{image_dir}/{img_filename}}}')
                            latex_content.append(r'\caption{Output Image}')
                            latex_content.append(r'\end{figure}' + '\n')
                            img_count += 1
                        elif 'text/plain' in output.data:
                            # Only include text if not image (often image comes with text repr)
                            if 'image/png' not in output.data:
                                latex_content.append(r'\begin{latin}')
                                latex_content.append(r'\begin{verbatim}')
                                latex_content.append(output.data['text/plain'])
                                latex_content.append(r'\end{verbatim}')
                                latex_content.append(r'\end{latin}' + '\n')

    # Add Persian Conclusion
    latex_content.append(r'\newpage')
    latex_content.append(r'\section{نتیجه‌گیری و مقایسه SHAP و LIME}')
    latex_content.append(r"""
در این پروژه، ما از مدل Random Forest برای پیش‌بینی سرطان سینه استفاده کردیم و سپس تلاش کردیم تا با استفاده از دو روش SHAP و LIME مدل را تفسیر کنیم.

\subsection{تفاوت SHAP و LIME}

\textbf{LIME (Local Interpretable Model-agnostic Explanations):}
روش LIME سعی می‌کند با تقریب زدن مدل پیچیده اصلی با یک مدل ساده (مثل رگرسیون خطی) در اطراف یک نمونه خاص، رفتار مدل را به صورت محلی توضیح دهد. 
مزیت LIME سرعت بالاتر آن است و اینکه می‌تواند برای هر مدلی استفاده شود. اما مشکل آن این است که توضیحات آن ممکن است ناپایدار باشند (با تغییرات کوچک در نمونه، توضیح تغییر کند).

\textbf{SHAP (SHapley Additive exPlanations):}
روش SHAP بر اساس تئوری بازی‌ها (Game Theory) کار می‌کند و سهم دقیق هر ویژگی را در خروجی نهایی مدل محاسبه می‌کند. 
SHAP از نظر تئوری قوی‌تر و پایدارتر است و توضیحات سراسری (Global) و محلی (Local) منسجم‌تری ارائه می‌دهد. 
اما محاسبه آن، به خصوص برای مدل‌های پیچیده و داده‌های حجیم، بسیار زمان‌برتر از LIME است.

\textbf{نتیجه‌گیری نهایی:}
اگر به دنبال دقت و پایداری درتفسیر هستید، \textbf{SHAP} گزینه بهتری است. اما اگر سرعت اولویت دارد یا نیاز به یک توضیح سریع و تقریبی برای یک نمونه خاص دارید، \textbf{LIME} می‌تواند مفید باشد.
""")

    latex_content.append(r'\end{document}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(latex_content))

    print(f"Report generated: {output_path}")
    print(f"Images extracted to: {image_dir}/")

if __name__ == "__main__":
    convert_notebook_to_latex(NOTEBOOK_FILE, OUTPUT_TEX, IMAGE_DIR)
