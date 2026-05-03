
import os
import json
import re
from io import BytesIO
from datetime import datetime

import pandas as pd
import plotly.express as px
import pymysql
import streamlit as st
import matplotlib.pyplot as plt

# =========================
# إعدادات عامة
# =========================
st.set_page_config(
    page_title="استبانة أولياء الأمور 2025-2026",
    page_icon="📝",
    layout="wide"
)

PDF_SUPPORT = True
ARABIC_SUPPORT = True

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:
    ARABIC_SUPPORT = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except Exception:
    PDF_SUPPORT = False

# =========================
# إعداد قاعدة البيانات
# =========================
import os
import pymysql

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST"),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE"),
    "port": int(os.getenv("MYSQLPORT", "3306")),
    "cursorclass": pymysql.cursors.DictCursor
}
# =========================
# إعدادات التطبيق
# =========================
APP_TITLE = "استبانة أولياء الأمور 2025-2026"
SCHOOL_NAME = "مدارس الكلية العلمية الإسلامية"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "IEC@4321"

LOGO_FILE = "logo.png"
BANNER_FILE = "banner.png"
ARABIC_FONT_FILE = "Amiri-Regular.ttf"
REPORTS_DIR = "reports"
TEMPLATES_FILE = "survey_templates.json"

PRIMARY_COLOR = "#0B3D91"
ACCENT_COLOR = "#D4A017"
BACKGROUND_COLOR = "#F3F6FB"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1F2937"

ANSWER_OPTIONS = ["موافق بشدة", "موافق", "محايد", "غير موافق", "غير موافق بشدة"]
ANSWER_SCORE_MAP = {
    "موافق بشدة": 5,
    "موافق": 4,
    "محايد": 3,
    "غير موافق": 2,
    "غير موافق بشدة": 1
}

# =========================
# CSS
# =========================
st.markdown(f"""
<style>
:root {{
    --primary: {PRIMARY_COLOR};
    --accent: {ACCENT_COLOR};
    --bg: {BACKGROUND_COLOR};
    --card: {CARD_COLOR};
    --text: {TEXT_COLOR};
    --muted: #6B7280;
    --border: #D7E1F0;
    --soft-blue: #EAF2FF;
    --soft-gold: #FFF8E6;
}}

html, body, [class*="css"] {{
    direction: rtl !important;
    text-align: right !important;
    background: linear-gradient(180deg, #F6F8FC 0%, #EEF3FB 100%);
    color: var(--text);
    font-size: 20px !important;
}}

.stApp {{
    background: linear-gradient(180deg, #F6F8FC 0%, #EEF3FB 100%);
}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2.4rem;
    max-width: 1320px;
}}

h1, h2, h3, h4, h5, h6, p, div, span, label {{
    text-align: right !important;
}}

.main-title {{
    text-align: right;
    font-size: 48px;
    font-weight: 900;
    color: var(--primary);
    margin-bottom: 4px;
    line-height: 1.3;
    letter-spacing: -0.4px;
}}

.sub-title {{
    text-align: right;
    font-size: 27px;
    font-weight: 800;
    color: var(--accent);
    margin-bottom: 16px;
    line-height: 1.5;
}}

.info-box {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F9FBFF 100%);
    border: 1px solid var(--border);
    border-right: 8px solid var(--primary);
    padding: 22px 24px;
    border-radius: 22px;
    box-shadow: 0 10px 24px rgba(11, 61, 145, 0.08);
    margin-bottom: 20px;
    font-size: 21px;
    font-weight: 600;
    line-height: 2;
}}

.section-card {{
    background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFF 100%);
    padding: 28px;
    border-radius: 24px;
    border: 1px solid var(--border);
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
    margin-bottom: 22px;
}}

.axis-title {{
    color: var(--primary);
    font-size: 35px;
    font-weight: 900;
    margin-bottom: 6px;
    line-height: 1.6;
}}

.question-text {{
    font-size: 25px !important;
    font-weight: 900 !important;
    color: var(--primary) !important;
    line-height: 1.9 !important;
    margin-top: 14px !important;
    margin-bottom: 14px !important;
    background: var(--soft-blue);
    border: 1px solid #D6E5FF;
    border-right: 6px solid var(--accent);
    border-radius: 18px;
    padding: 14px 18px;
}}

[data-testid="stForm"] {{
    background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFF 100%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 18px 18px 8px 18px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}}

label, .stSelectbox label, .stTextInput label, .stTextArea label, .stRadio label {{
    color: var(--primary) !important;
}}

[data-testid="stWidgetLabel"] p,
label p {{
    font-size: 20px !important;
    font-weight: 800 !important;
    margin-bottom: 2px !important;
    line-height: 1.55 !important;
}}

.stTextInput input, .stTextArea textarea {{
    direction: rtl !important;
    text-align: right !important;
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
    background: #FFFFFF !important;
    font-size: 20px !important;
    padding: 0.8rem 0.95rem !important;
    box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.03);
}}

.stTextInput input:focus, .stTextArea textarea:focus {{
    border: 1px solid var(--primary) !important;
    box-shadow: 0 0 0 0.18rem rgba(11, 61, 145, 0.12) !important;
}}

textarea {{
    font-size: 20px !important;
}}

div[data-baseweb="select"] > div {{
    direction: rtl !important;
    text-align: right !important;
    font-size: 19px !important;
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
    min-height: 52px !important;
    box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.03);
}}

/* تقريب الخيارات من السؤال وتحويلها إلى أزرار */
div[data-testid="stRadio"] {{
    margin-top: -14px !important;
    margin-bottom: 8px !important;
}}

div[data-testid="stRadio"] > div {{
    margin-top: 0 !important;
}}

div[role="radiogroup"] {{
    direction: rtl !important;
    text-align: right !important;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    justify-content: flex-start !important;
    align-items: center !important;
    background: transparent !important;
    border: none !important;
    border-radius: 18px;
    padding: 2px 0 0 0 !important;
    margin-top: 0 !important;
    margin-bottom: 10px !important;
}}

div[role="radiogroup"] > label {{
    min-height: 48px !important;
    padding: 8px 14px !important;
    border-radius: 999px !important;
    border: 1px solid var(--border) !important;
    background: #FFFFFF !important;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    transition: all 0.18s ease;
    margin: 0 !important;
}}

div[role="radiogroup"] > label:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(11, 61, 145, 0.10);
}}

div[role="radiogroup"] > label:nth-child(1) {{
    border-color: #B7DFC0 !important;
    background: #F2FBF4 !important;
}}

div[role="radiogroup"] > label:nth-child(2) {{
    border-color: #CFE7D5 !important;
    background: #F7FCF8 !important;
}}

div[role="radiogroup"] > label:nth-child(3) {{
    border-color: #F4DF9C !important;
    background: #FFF9E8 !important;
}}

div[role="radiogroup"] > label:nth-child(4) {{
    border-color: #F2C38A !important;
    background: #FFF4E8 !important;
}}

div[role="radiogroup"] > label:nth-child(5) {{
    border-color: #EDB0B0 !important;
    background: #FFF1F1 !important;
}}

div[role="radiogroup"] p {{
    margin: 0 !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    line-height: 1.25 !important;
}}

div[role="radiogroup"] svg {{
    display: none !important;
}}

div[role="radiogroup"] input {{
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}

div[role="radiogroup"] > label:has(input:checked) {{
    box-shadow: 0 0 0 2px rgba(11, 61, 145, 0.10), 0 10px 18px rgba(11, 61, 145, 0.10) !important;
    transform: translateY(-1px);
}}

div[role="radiogroup"] > label:nth-child(1):has(input:checked) {{
    background: #DDF3E3 !important;
    border-color: #2E7D32 !important;
    color: #1B5E20 !important;
}}

div[role="radiogroup"] > label:nth-child(2):has(input:checked) {{
    background: #EAF7EE !important;
    border-color: #5A9A66 !important;
    color: #1F5D2C !important;
}}

div[role="radiogroup"] > label:nth-child(3):has(input:checked) {{
    background: #FFF0BF !important;
    border-color: #F9A825 !important;
    color: #8A5A00 !important;
}}

div[role="radiogroup"] > label:nth-child(4):has(input:checked) {{
    background: #FFE4C7 !important;
    border-color: #F57C00 !important;
    color: #8A4700 !important;
}}

div[role="radiogroup"] > label:nth-child(5):has(input:checked) {{
    background: #FFD8D8 !important;
    border-color: #C62828 !important;
    color: #7A1111 !important;
}}

.stRadio label {{
    font-size: 18px !important;
    font-weight: 800 !important;
}}

.stButton > button {{
    width: 100%;
    border-radius: 16px;
    font-weight: 900;
    font-size: 19px;
    padding: 0.9rem 1rem;
    margin-top: 10px;
    border: 1px solid rgba(11, 61, 145, 0.12);
    background: linear-gradient(180deg, #0F4FB9 0%, #0B3D91 100%);
    color: white;
    box-shadow: 0 10px 18px rgba(11, 61, 145, 0.16);
    transition: all 0.2s ease;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 14px 24px rgba(11, 61, 145, 0.18);
    border-color: rgba(11, 61, 145, 0.18);
}}

.stDownloadButton > button {{
    width: 100%;
    border-radius: 16px;
    font-weight: 900;
    font-size: 18px;
    padding: 0.85rem 1rem;
    margin-top: 10px;
    border: 1px solid #D7E1F0;
    background: linear-gradient(180deg, #FFFFFF 0%, #F7FAFF 100%);
    color: var(--primary);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}}

.stDownloadButton > button:hover {{
    border-color: rgba(11, 61, 145, 0.28);
    background: linear-gradient(180deg, #F9FBFF 0%, #EEF4FF 100%);
}}

div[data-testid="stMetric"] {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F9FBFF 100%);
    border-radius: 20px;
    border: 1px solid var(--border);
    padding: 14px;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}}

div[data-testid="stMetric"] label {{
    font-size: 20px !important;
    font-weight: 800 !important;
}}

div[data-testid="stMetricValue"] {{
    font-size: 30px !important;
    font-weight: 900 !important;
    color: var(--primary) !important;
}}

[data-testid="stDataFrame"] {{
    background-color: var(--card);
    border-radius: 18px;
    border: 1px solid var(--border);
    padding: 8px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}}

[data-testid="stExpander"] {{
    border: 1px solid var(--border);
    border-radius: 18px;
    overflow: hidden;
}}

.streamlit-expanderHeader {{
    font-size: 20px !important;
    font-weight: 800 !important;
    color: var(--primary) !important;
    background: #F8FBFF !important;
}}

[data-testid="stAlert"] {{
    border-radius: 18px !important;
    border: 1px solid var(--border) !important;
}}

img {{
    border-radius: 18px;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# دوال مساعدة
# =========================
def ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)

def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def score_to_percentage(score):
    try:
        if pd.isna(score):
            return 0.0
        return round((float(score) / 5) * 100, 2)
    except Exception:
        return 0.0

def ar_text(text):
    text = "" if pd.isna(text) else str(text)
    if ARABIC_SUPPORT:
        try:
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text
    return text

def normalize_match_text(text):
    text = normalize_text(text)
    text = re.sub(r"\s+", " ", text)
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ـ": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip().lower()



def extract_axis_number(axis_name):
    axis_name = normalize_text(axis_name)
    if not axis_name:
        return 999

    mapping = {
        "الأول": 1,
        "الثاني": 2,
        "الثالث": 3,
        "الرابع": 4,
        "الخامس": 5,
        "السادس": 6,
        "السابع": 7,
        "الثامن": 8,
        "التاسع": 9,
        "العاشر": 10,
    }

    for word, number in mapping.items():
        if word in axis_name:
            return number

    match = re.search(r"(\d+)", axis_name)
    if match:
        return int(match.group(1))

    return 999

def sort_axes_dataframe(df, axis_col="المحور"):
    if df is None or df.empty or axis_col not in df.columns:
        return df

    work_df = df.copy()
    work_df["ترتيب_المحور"] = work_df[axis_col].apply(extract_axis_number)
    secondary_cols = [axis_col]
    if "رقم الفقرة" in work_df.columns:
        secondary_cols.append("رقم الفقرة")
    sort_cols = ["ترتيب_المحور"] + secondary_cols
    work_df = work_df.sort_values(sort_cols).reset_index(drop=True)
    return work_df.drop(columns=["ترتيب_المحور"], errors="ignore")


def clean_templates_dict(data):
    cleaned = {}
    if not isinstance(data, dict):
        return cleaned

    for survey_type, axes in data.items():
        survey_key = normalize_text(survey_type).upper()
        cleaned[survey_key] = {}
        if not isinstance(axes, dict):
            continue

        for axis_name, questions in axes.items():
            clean_axis = normalize_text(axis_name)
            cleaned_questions = [normalize_text(q) for q in (questions or []) if normalize_text(q)]
            cleaned[survey_key][clean_axis] = cleaned_questions

    return cleaned


def build_question_axis_map(templates):
    question_axis_map = {}
    for _, axes in templates.items():
        for axis_name, questions in axes.items():
            for question in questions:
                question_axis_map[normalize_match_text(question)] = axis_name
    return question_axis_map


def register_arabic_font():
    if not PDF_SUPPORT:
        return "Helvetica"

    font_path = os.path.join(os.getcwd(), ARABIC_FONT_FILE)
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
            return "ArabicFont"
        except Exception:
            return "Helvetica"
    return "Helvetica"

def dataframe_to_excel_bytes(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, index=False, sheet_name=str(sheet_name)[:31])
    output.seek(0)
    return output.getvalue()

def render_bar_chart(df, x_col, y_col, title, color_col=None):
    if df.empty:
        return

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col if color_col and color_col in df.columns else None,
        text=y_col,
        title=title,
        barmode="group"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=540,
        xaxis_title="",
        yaxis_title=y_col,
        font=dict(size=16),
        title=dict(font=dict(size=24)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=70, b=100),
    )
    st.plotly_chart(fig, use_container_width=True)

def _set_matplotlib_arabic_font():
    try:
        font_path = os.path.join(os.getcwd(), ARABIC_FONT_FILE)
        if os.path.exists(font_path):
            from matplotlib import font_manager
            font_manager.fontManager.addfont(font_path)
            plt.rcParams["font.family"] = "Amiri"
    except Exception:
        pass

def classification_text(pct):
    pct = 0 if pd.isna(pct) else float(pct)
    if pct >= 85:
        return "مرتفع"
    if pct >= 70:
        return "متوسط"
    return "منخفض"

def classification_color_name(pct):
    pct = 0 if pd.isna(pct) else float(pct)
    if pct >= 85:
        return "أخضر"
    if pct >= 70:
        return "أصفر"
    return "أحمر"

def classification_hex(pct):
    pct = 0 if pd.isna(pct) else float(pct)
    if pct >= 85:
        return "#2E7D32"
    if pct >= 70:
        return "#F9A825"
    return "#C62828"

def add_classification_columns(df, pct_col="النسبة المئوية"):
    work_df = df.copy()
    if pct_col in work_df.columns:
        work_df["التصنيف"] = work_df[pct_col].apply(classification_text)
        work_df["لون التصنيف"] = work_df[pct_col].apply(classification_color_name)
    return work_df

def build_axis_details(question_summary_df):
    details = []
    if question_summary_df is None or question_summary_df.empty:
        return details

    work_df = sort_axes_dataframe(question_summary_df.copy(), "المحور")
    work_df = add_classification_columns(work_df)

    axis_names = work_df["المحور"].dropna().astype(str).unique().tolist()
    axis_names = sorted(axis_names, key=extract_axis_number)

    for axis_name in axis_names:
        axis_df = work_df[work_df["المحور"] == axis_name].copy()
        axis_df = axis_df.sort_values(["رقم الفقرة"]).reset_index(drop=True)
        axis_avg = round(pd.to_numeric(axis_df["المتوسط"], errors="coerce").fillna(0).mean(), 2)
        axis_pct = score_to_percentage(axis_avg)
        top_items = axis_df.sort_values(["النسبة المئوية", "المتوسط"], ascending=[False, False]).head(2).copy()
        bottom_items = axis_df.sort_values(["النسبة المئوية", "المتوسط"], ascending=[True, True]).head(2).copy()
        details.append({
            "axis_name": axis_name,
            "axis_avg": axis_avg,
            "axis_pct": axis_pct,
            "classification": classification_text(axis_pct),
            "classification_color": classification_color_name(axis_pct),
            "axis_df": axis_df,
            "top_items": top_items,
            "bottom_items": bottom_items,
        })
    return details

def generate_smart_recommendation(axis_name, axis_pct, top_items, bottom_items):
    level = classification_text(axis_pct)

    strengths = "، ".join(top_items["الفقرة"].astype(str).tolist()) if top_items is not None and not top_items.empty else "لا توجد فقرات كافية"
    needs = "، ".join(bottom_items["الفقرة"].astype(str).tolist()) if bottom_items is not None and not bottom_items.empty else "لا توجد فقرات كافية"

    if level == "مرتفع":
        return (
            f"أظهر محور {axis_name} مستوى مرتفعًا، مما يدل على وجود ممارسات مستقرة وإيجابية. "
            f"يوصى بالحفاظ على نقاط القوة الظاهرة في الفقرات الأعلى مثل: {strengths}. "
            f"وفي الوقت نفسه، يفضّل متابعة الفقرات الأقل نسبيًا مثل: {needs}، "
            f"من خلال إجراءات تحسين خفيفة ومستمرة حتى يبقى الأداء العام مرتفعًا ومتوازنًا."
        )

    if level == "متوسط":
        return (
            f"أظهر محور {axis_name} مستوى متوسطًا، ما يعني وجود جوانب جيدة تحتاج إلى تعزيز منظم. "
            f"يمكن البناء على الفقرات الأعلى أداءً مثل: {strengths}، باعتبارها ممارسات ناجحة قابلة للتوسيع. "
            f"أما الفقرات الأدنى مثل: {needs}، فيوصى بوضع خطة تحسين واضحة لها تتضمن متابعة دورية، "
            f"وتحديد أسباب التفاوت، وتنفيذ تدخلات عملية ترفع مستوى الرضا والأثر."
        )

    return (
        f"أظهر محور {axis_name} مستوى منخفضًا نسبيًا، وهو ما يشير إلى حاجة المحور إلى تدخل تحسيني مباشر. "
        f"تُعد الفقرات الأعلى مثل: {strengths} نقاط انطلاق يمكن الاستفادة منها في دعم التحسين. "
        f"أما الفقرات الأدنى مثل: {needs}، فيوصى بإعطائها أولوية في خطط التطوير، مع تحليل الأسباب، "
        f"وتكثيف المتابعة، وتحديد إجراءات تنفيذية قابلة للقياس لتحسين النتائج في هذا المحور."
    )


def short_items_text(df, max_items=2, max_len=95):
    if df is None or df.empty or "الفقرة" not in df.columns:
        return "لا توجد فقرات كافية"
    items = [normalize_text(x) for x in df["الفقرة"].astype(str).tolist()[:max_items] if normalize_text(x)]
    text = "، ".join(items) if items else "لا توجد فقرات كافية"
    if len(text) > max_len:
        text = text[:max_len].rstrip(" ،،.") + "..."
    return text


def build_recommendation_paragraphs(axis_name, axis_pct, top_items, bottom_items):
    level = classification_text(axis_pct)
    strengths = short_items_text(top_items, max_items=2, max_len=100)
    needs = short_items_text(bottom_items, max_items=2, max_len=100)

    if level == "مرتفع":
        return [
            f"أظهر {axis_name} مستوى مرتفعًا؛ ويُوصى بالحفاظ على نقاط القوة: {strengths}.",
            f"وتُتابَع الفقرات الأقل نسبيًا: {needs}؛ من خلال تحسينات خفيفة ومستمرة."
        ]

    if level == "متوسط":
        return [
            f"أظهر {axis_name} مستوى متوسطًا؛ ويمكن البناء على الفقرات الأعلى أداءً: {strengths}.",
            f"وتُعطى الفقرات الأدنى أولوية متابعة: {needs}؛ ضمن خطة تحسين دورية وواضحة."
        ]

    return [
        f"أظهر {axis_name} مستوى منخفضًا نسبيًا؛ وتُعد الفقرات الأعلى نقطة انطلاق: {strengths}.",
        f"وتحتاج الفقرات الأدنى إلى أولوية تطوير: {needs}؛ مع إجراءات قابلة للقياس والمتابعة."
    ]


def compact_item_line(label, df):
    return f"{label}: {short_items_text(df, max_items=2, max_len=120)}"

def split_arabic_pdf_lines(text, max_chars=72):
    """
    تقسيم النص العربي إلى أسطر قصيرة قبل تطبيق bidi/reshaper.
    هذا يمنع ReportLab من عكس ترتيب الجمل عند التفاف السطر داخل PDF.
    """
    text = normalize_text(text)
    if not text:
        return []

    parts = re.split(r"(?<=[\.،؛:])\s+", text)
    lines = []
    current = ""

    for part in parts:
        part = normalize_text(part)
        if not part:
            continue

        words = part.split()
        piece = ""
        for word in words:
            candidate = (piece + " " + word).strip()
            if len(candidate) <= max_chars:
                piece = candidate
            else:
                if piece:
                    if current and len(current + " " + piece) <= max_chars:
                        current = (current + " " + piece).strip()
                    else:
                        if current:
                            lines.append(current)
                        current = piece
                piece = word

        if piece:
            if current and len(current + " " + piece) <= max_chars:
                current = (current + " " + piece).strip()
            else:
                if current:
                    lines.append(current)
                current = piece

    if current:
        lines.append(current)

    return lines


def add_pdf_arabic_lines(elements, text, style, max_chars=72, gap=0.055):
    for line in split_arabic_pdf_lines(text, max_chars=max_chars):
        elements.append(Paragraph(ar_text(line), style))
        elements.append(Spacer(1, gap * cm))

def create_question_chart_image(question_summary_df, title="متوسط الفقرات (النسبة المئوية)", limit=15):
    if question_summary_df is None or question_summary_df.empty:
        return None

    _set_matplotlib_arabic_font()

    work_df = sort_axes_dataframe(question_summary_df.copy(), "المحور").head(limit)
    labels = work_df["رقم الفقرة"].astype(str).tolist()
    values = pd.to_numeric(work_df["النسبة المئوية"], errors="coerce").fillna(0).tolist()
    colors_list = [classification_hex(v) for v in values]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(labels, values, color=colors_list)
    ax.set_title(ar_text(title), fontsize=14)
    ax.set_xlabel(ar_text("رقم الفقرة"), fontsize=12)
    ax.set_ylabel(ar_text("النسبة المئوية"), fontsize=12)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    img_buffer = BytesIO()
    plt.tight_layout()
    fig.savefig(img_buffer, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer

def create_axis_chart_image(axis_df, axis_name):
    if axis_df is None or axis_df.empty:
        return None

    _set_matplotlib_arabic_font()

    work_df = axis_df.copy()
    labels = work_df["رقم الفقرة"].astype(str).tolist()
    values = pd.to_numeric(work_df["النسبة المئوية"], errors="coerce").fillna(0).tolist()
    colors_list = [classification_hex(v) for v in values]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(labels, values, color=colors_list)
    ax.set_title(ar_text(f"الرسم البياني لمحور: {axis_name}"), fontsize=14)
    ax.set_xlabel(ar_text("رقم الفقرة"), fontsize=12)
    ax.set_ylabel(ar_text("النسبة المئوية"), fontsize=12)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    img_buffer = BytesIO()
    plt.tight_layout()
    fig.savefig(img_buffer, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer

def count_table_rows(table_name):
    conn = get_connection()
    if conn is None:
        return 0

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM parent_survey.{table_name}")
            row = cursor.fetchone()
            return int(row["cnt"]) if row else 0
    except Exception:
        return 0
    finally:
        conn.close()

def sanitize_results_df(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "id", "student_id", "student_name", "grade", "school", "survey_type",
            "respondent_type", "other_respondent_text", "is_bus_subscribed",
            "bus_number", "notes", "overall_avg", "overall_pct", "created_at"
        ])

    work_df = df.copy()

    text_cols = [
        "student_id", "student_name", "grade", "school", "survey_type",
        "respondent_type", "other_respondent_text", "is_bus_subscribed",
        "bus_number", "notes"
    ]

    for col in text_cols:
        if col in work_df.columns:
            work_df[col] = work_df[col].fillna("").astype(str).str.strip()

    if "id" in work_df.columns:
        work_df["id"] = pd.to_numeric(work_df["id"], errors="coerce")

    if "overall_avg" in work_df.columns:
        work_df["overall_avg"] = pd.to_numeric(work_df["overall_avg"], errors="coerce").fillna(0)

    if "overall_pct" in work_df.columns:
        work_df["overall_pct"] = pd.to_numeric(work_df["overall_pct"], errors="coerce").fillna(0)

    if "id" in work_df.columns:
        work_df = work_df[work_df["id"].notna()].copy()

    if "school" in work_df.columns:
        work_df["school"] = work_df["school"].replace("", "غير محدد")

    if "survey_type" in work_df.columns:
        work_df["survey_type"] = work_df["survey_type"].replace("", "عام").astype(str).str.upper()

    if {"school", "survey_type"}.issubset(work_df.columns):
        work_df = work_df[
            ~(
                work_df["school"].astype(str).str.strip().str.lower().eq("school") |
                work_df["survey_type"].astype(str).str.strip().str.upper().eq("SURVEY_TYPE")
            )
        ].copy()

    work_df.reset_index(drop=True, inplace=True)
    return work_df

# =========================
# القوالب
# =========================
def load_survey_templates():
    if not os.path.exists(TEMPLATES_FILE):
        st.error(f"ملف قوالب الاستبانات غير موجود: {TEMPLATES_FILE}")
        return {}

    try:
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            st.error("ملف قوالب الاستبانات غير صالح.")
            return {}

        return clean_templates_dict(data)
    except Exception as e:
        st.error(f"تعذر قراءة ملف قوالب الاستبانات: {e}")
        return {}

SURVEY_TEMPLATES = load_survey_templates()
QUESTION_AXIS_MAP = build_question_axis_map(SURVEY_TEMPLATES)

def get_student_survey_type(student):
    survey_type = normalize_text(student.get("survey_type", "E1")).upper()
    if survey_type not in SURVEY_TEMPLATES:
        survey_type = next(iter(SURVEY_TEMPLATES.keys()), "")
    return survey_type

def get_survey_questions_by_student(student):
    survey_type = get_student_survey_type(student)
    template = SURVEY_TEMPLATES.get(survey_type, {})
    questions_dict = {axis_name: list(questions) for axis_name, questions in template.items()}

    if st.session_state.get("is_bus_subscribed", "") == "لا":
        bus_keywords = ["النقل المدرسي", "النقل", "الباص", "الحافلة", "المواصلات"]
        filtered_questions = {}

        for axis_name, questions in questions_dict.items():
            axis_text = str(axis_name).strip()
            axis_is_bus = any(keyword in axis_text for keyword in bus_keywords)
            questions_have_bus = any(
                any(keyword in str(q) for keyword in bus_keywords)
                for q in questions
            )

            if not axis_is_bus and not questions_have_bus:
                filtered_questions[axis_name] = questions

        return filtered_questions

    return questions_dict

# =========================
# قاعدة البيانات
# =========================
def get_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

def fetch_df(query, params=None):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def ensure_db_columns():
    conn = get_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM parent_survey.survey_answers")
            answer_cols = {row["Field"] for row in cursor.fetchall()}
            answer_needed = {
                "response_id": "INT NOT NULL",
                "survey_type": "VARCHAR(20)",
                "axis": "VARCHAR(255)",
                "axis_name": "VARCHAR(255)",
                "question_id": "INT",
                "question_text": "TEXT",
                "answer_text": "VARCHAR(100)",
                "answer_value": "INT",
                "answer_score": "INT",
            }
            for col_name, col_def in answer_needed.items():
                if col_name not in answer_cols:
                    cursor.execute(f"ALTER TABLE parent_survey.survey_answers ADD COLUMN {col_name} {col_def}")

            cursor.execute("SHOW COLUMNS FROM parent_survey.survey_responses")
            response_cols = {row["Field"] for row in cursor.fetchall()}
            response_needed = {
                "is_bus_subscribed": "VARCHAR(10)",
                "bus_number": "VARCHAR(100)",
                "other_respondent_text": "VARCHAR(255)",
                "overall_avg": "DECIMAL(6,2)",
                "overall_pct": "DECIMAL(6,2)",
            }
            for col_name, col_def in response_needed.items():
                if col_name not in response_cols:
                    cursor.execute(f"ALTER TABLE parent_survey.survey_responses ADD COLUMN {col_name} {col_def}")
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def get_student(student_id, password):
    conn = get_connection()
    if conn is None:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT student_id, password, student_name, grade, school, survey_type
                FROM parent_survey.students
                WHERE student_id = %s AND password = %s
                LIMIT 1
                """,
                (str(student_id).strip(), str(password).strip()),
            )
            result = cursor.fetchone()
        return result
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة بيانات الطالب: {e}")
        return None
    finally:
        conn.close()

def student_already_submitted(student_id):
    conn = get_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM parent_survey.survey_responses WHERE student_id = %s LIMIT 1",
                (str(student_id).strip(),),
            )
            result = cursor.fetchone()
        return result is not None
    except Exception as e:
        st.error(f"حدث خطأ أثناء التحقق من تعبئة الاستبانة: {e}")
        return False
    finally:
        conn.close()

def get_school_totals_df():
    df = fetch_df("SELECT school, total_students FROM parent_survey.school_totals")
    if df.empty:
        return pd.DataFrame(columns=["school", "total_students"])

    df["school"] = df["school"].fillna("").astype(str).str.strip()
    df["total_students"] = pd.to_numeric(df["total_students"], errors="coerce").fillna(0)
    df = df[df["school"].str.lower() != "school"].copy()
    return df

def load_results():
    try:
        df = fetch_df(
            """
            SELECT
                id,
                student_id,
                student_name,
                grade,
                school,
                survey_type,
                respondent_type,
                other_respondent_text,
                is_bus_subscribed,
                bus_number,
                notes,
                overall_avg,
                overall_pct,
                created_at
            FROM parent_survey.survey_responses
            ORDER BY id DESC
            """
        )

        if df.empty:
            return pd.DataFrame(columns=[
                "id", "student_id", "student_name", "grade", "school", "survey_type",
                "respondent_type", "other_respondent_text", "is_bus_subscribed",
                "bus_number", "notes", "overall_avg", "overall_pct", "created_at"
            ]), None

        df["id"] = pd.to_numeric(df.get("id"), errors="coerce")
        df["overall_avg"] = pd.to_numeric(df.get("overall_avg"), errors="coerce").fillna(0)
        df["overall_pct"] = pd.to_numeric(df.get("overall_pct"), errors="coerce").fillna(0)

        text_cols = [
            "student_id", "student_name", "grade", "school", "survey_type",
            "respondent_type", "other_respondent_text", "is_bus_subscribed",
            "bus_number", "notes"
        ]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()

        df = df[df["id"].notna()].copy()
        if "school" in df.columns:
            df["school"] = df["school"].replace("", "غير محدد")
        if "survey_type" in df.columns:
            df["survey_type"] = df["survey_type"].replace("", "عام").astype(str).str.upper()

        return df, None
    except Exception as e:
        return None, f"حدث خطأ أثناء قراءة النتائج: {e}"

def load_answers():
    try:
        df = fetch_df(
            """
            SELECT
                a.id,
                a.response_id,
                UPPER(COALESCE(a.survey_type, r.survey_type, '')) AS survey_type,
                COALESCE(NULLIF(TRIM(a.axis), ''), NULLIF(TRIM(a.axis_name), ''), '') AS axis,
                COALESCE(a.question_id, a.id) AS question_id,
                COALESCE(a.question_text, '') AS question_text,
                COALESCE(a.answer_text, '') AS answer_text,
                COALESCE(a.answer_value, a.answer_score) AS answer_value
            FROM parent_survey.survey_answers a
            LEFT JOIN parent_survey.survey_responses r
                ON r.id = a.response_id
            ORDER BY a.id DESC
            """
        )

        if df.empty:
            return pd.DataFrame(columns=[
                "id", "response_id", "survey_type", "axis", "question_id",
                "question_text", "answer_text", "answer_value"
            ]), None

        df["response_id"] = pd.to_numeric(df["response_id"], errors="coerce")
        df["question_id"] = pd.to_numeric(df["question_id"], errors="coerce")
        df["answer_value"] = pd.to_numeric(df["answer_value"], errors="coerce")
        df["survey_type"] = df["survey_type"].fillna("").astype(str).str.strip().str.upper()
        df["axis"] = df["axis"].fillna("").astype(str).str.strip()
        df["question_text"] = df["question_text"].fillna("").astype(str).str.strip()
        df["answer_text"] = df["answer_text"].fillna("").astype(str).str.strip()

        df["axis"] = df.apply(
            lambda row: QUESTION_AXIS_MAP.get(
                normalize_match_text(row["question_text"]),
                normalize_text(row["axis"])
            ),
            axis=1
        )

        df = df[
            (df["response_id"].notna()) &
            (df["axis"] != "") &
            (df["question_text"] != "") &
            (df["answer_value"].notna())
        ].copy()

        df = df[
            ~(
                df["axis"].str.lower().eq("axis") |
                df["question_text"].str.lower().eq("question_text") |
                df["survey_type"].str.upper().eq("SURVEY_TYPE")
            )
        ].copy()

        return df, None
    except Exception as e:
        return None, f"حدث خطأ أثناء قراءة الإجابات: {e}"

def refresh_summary_tables():
    conn = get_connection()
    if conn is None:
        return False, "تعذر الاتصال بقاعدة البيانات"

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM parent_survey.school_axis_summary")
            cursor.execute("DELETE FROM parent_survey.school_summary")

            cursor.execute(
                """
                INSERT INTO parent_survey.school_summary (
                    school, survey_type, responses_count, overall_avg, overall_pct, updated_at
                )
                SELECT
                    COALESCE(NULLIF(TRIM(school), ''), 'غير محدد') AS school,
                    COALESCE(NULLIF(UPPER(TRIM(survey_type)), ''), 'عام') AS survey_type,
                    COUNT(*) AS responses_count,
                    ROUND(AVG(COALESCE(overall_avg, 0)), 2) AS overall_avg,
                    ROUND(AVG(COALESCE(overall_pct, 0)), 2) AS overall_pct,
                    NOW() AS updated_at
                FROM parent_survey.survey_responses
                WHERE TRIM(COALESCE(school, '')) <> 'school'
                  AND TRIM(COALESCE(UPPER(survey_type), '')) <> 'SURVEY_TYPE'
                GROUP BY COALESCE(NULLIF(TRIM(school), ''), 'غير محدد'),
                         COALESCE(NULLIF(UPPER(TRIM(survey_type)), ''), 'عام')
                """
            )

            cursor.execute(
                """
                INSERT INTO parent_survey.school_axis_summary (
                    school, survey_type, axis_name, responses_count, axis_avg, axis_pct, updated_at
                )
                SELECT
                    COALESCE(NULLIF(TRIM(r.school), ''), 'غير محدد') AS school,
                    COALESCE(NULLIF(UPPER(TRIM(COALESCE(a.survey_type, r.survey_type))), ''), 'عام') AS survey_type,
                    COALESCE(NULLIF(TRIM(COALESCE(a.axis_name, a.axis)), ''), 'غير محدد') AS axis_name,
                    COUNT(*) AS responses_count,
                    ROUND(AVG(COALESCE(a.answer_value, a.answer_score)), 2) AS axis_avg,
                    ROUND(AVG(COALESCE(a.answer_value, a.answer_score)) * 20, 2) AS axis_pct,
                    NOW() AS updated_at
                FROM parent_survey.survey_answers a
                INNER JOIN parent_survey.survey_responses r
                    ON r.id = a.response_id
                WHERE COALESCE(a.answer_value, a.answer_score) IS NOT NULL
                  AND TRIM(COALESCE(r.school, '')) <> 'school'
                  AND TRIM(COALESCE(UPPER(COALESCE(a.survey_type, r.survey_type)), '')) <> 'SURVEY_TYPE'
                  AND TRIM(COALESCE(a.question_text, '')) <> ''
                GROUP BY COALESCE(NULLIF(TRIM(r.school), ''), 'غير محدد'),
                         COALESCE(NULLIF(UPPER(TRIM(COALESCE(a.survey_type, r.survey_type))), ''), 'عام'),
                         COALESCE(NULLIF(TRIM(COALESCE(a.axis_name, a.axis)), ''), 'غير محدد')
                """
            )

        conn.commit()
        return True, "تم تحديث جداول التحليل بنجاح"
    except Exception as e:
        conn.rollback()
        return False, f"حدث خطأ أثناء تحديث جداول التحليل: {e}"
    finally:
        conn.close()

def load_school_summary_table():
    conn = get_connection()
    if conn is None:
        return None, "تعذر الاتصال بقاعدة البيانات"

    try:
        query = """
            SELECT
                school,
                survey_type,
                responses_count,
                overall_avg,
                overall_pct,
                updated_at
            FROM parent_survey.school_summary
            ORDER BY school, survey_type
        """
        df = pd.read_sql(query, conn)

        if not df.empty:
            df["school"] = df["school"].fillna("غير محدد").astype(str).str.strip()
            df["survey_type"] = df["survey_type"].fillna("عام").astype(str).str.strip().str.upper()
            df["responses_count"] = pd.to_numeric(df["responses_count"], errors="coerce").fillna(0).astype(int)
            df["overall_avg"] = pd.to_numeric(df["overall_avg"], errors="coerce").fillna(0).round(2)
            df["overall_pct"] = pd.to_numeric(df["overall_pct"], errors="coerce").fillna(0).round(2)

            df = df[
                ~(
                    df["school"].str.lower().eq("school") |
                    df["survey_type"].str.upper().eq("SURVEY_TYPE")
                )
            ].copy()

        return df, None
    except Exception as e:
        return None, f"حدث خطأ أثناء قراءة school_summary: {e}"
    finally:
        conn.close()

def load_school_axis_summary_table():
    conn = get_connection()
    if conn is None:
        return None, "تعذر الاتصال بقاعدة البيانات"

    try:
        query = """
            SELECT
                school,
                survey_type,
                axis_name,
                responses_count,
                axis_avg,
                axis_pct,
                updated_at
            FROM parent_survey.school_axis_summary
            ORDER BY school, survey_type, axis_name
        """
        df = pd.read_sql(query, conn)

        if not df.empty:
            df["school"] = df["school"].fillna("غير محدد").astype(str).str.strip()
            df["survey_type"] = df["survey_type"].fillna("عام").astype(str).str.strip().str.upper()
            df["axis_name"] = df["axis_name"].fillna("").astype(str).str.strip()
            df["responses_count"] = pd.to_numeric(df["responses_count"], errors="coerce").fillna(0).astype(int)
            df["axis_avg"] = pd.to_numeric(df["axis_avg"], errors="coerce").fillna(0).round(2)
            df["axis_pct"] = pd.to_numeric(df["axis_pct"], errors="coerce").fillna(0).round(2)

            df = df[
                ~(
                    df["school"].str.lower().eq("school") |
                    df["survey_type"].str.upper().eq("SURVEY_TYPE") |
                    df["axis_name"].str.lower().eq("axis_name")
                )
            ].copy()

        return df, None
    except Exception as e:
        return None, f"حدث خطأ أثناء قراءة school_axis_summary: {e}"
    finally:
        conn.close()

# =========================
# الحسابات
# =========================
def get_overall_average(student):
    current_survey_questions = get_survey_questions_by_student(student)
    all_questions = [q for axis_questions in current_survey_questions.values() for q in axis_questions]

    scores = [
        ANSWER_SCORE_MAP[st.session_state.answers.get(q)]
        for q in all_questions
        if st.session_state.answers.get(q) in ANSWER_SCORE_MAP
    ]

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 2)

def build_axis_summary(filtered_answers_df):
    if filtered_answers_df is None or filtered_answers_df.empty:
        return pd.DataFrame(columns=["المحور", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"])

    axis_summary = (
        filtered_answers_df.groupby("axis", as_index=False)["answer_value"]
        .mean()
        .rename(columns={"axis": "المحور", "answer_value": "المتوسط"})
    )

    axis_summary["المتوسط"] = pd.to_numeric(axis_summary["المتوسط"], errors="coerce").fillna(0).round(2)
    axis_summary["النسبة المئوية"] = axis_summary["المتوسط"].apply(score_to_percentage)
    axis_summary["التصنيف"] = axis_summary["النسبة المئوية"].apply(classification_text)
    axis_summary["لون التصنيف"] = axis_summary["النسبة المئوية"].apply(classification_color_name)
    return sort_axes_dataframe(axis_summary, "المحور")

def build_question_summary(filtered_answers_df):
    if filtered_answers_df is None or filtered_answers_df.empty:
        return pd.DataFrame(columns=["رقم الفقرة", "المحور", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"])

    question_summary = (
        filtered_answers_df.groupby(["question_id", "axis", "question_text"], as_index=False)["answer_value"]
        .mean()
        .rename(
            columns={
                "question_id": "رقم الفقرة",
                "axis": "المحور",
                "question_text": "الفقرة",
                "answer_value": "المتوسط",
            }
        )
    )

    question_summary["المتوسط"] = pd.to_numeric(question_summary["المتوسط"], errors="coerce").fillna(0).round(2)
    question_summary["النسبة المئوية"] = question_summary["المتوسط"].apply(score_to_percentage)
    question_summary["التصنيف"] = question_summary["النسبة المئوية"].apply(classification_text)
    question_summary["لون التصنيف"] = question_summary["النسبة المئوية"].apply(classification_color_name)
    question_summary = sort_axes_dataframe(question_summary, "المحور")
    return question_summary[["رقم الفقرة", "المحور", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"]]

def build_school_summary(results_df):
    empty_cols = [
        "اسم المدرسة",
        "نوع الاستبانة",
        "عدد الاستجابات",
        "عدد الطلبة الكلي",
        "نسبة الاستجابة",
        "المتوسط الكلي",
        "النسبة المئوية",
    ]

    if results_df is None or results_df.empty:
        return pd.DataFrame(columns=empty_cols)

    work_df = sanitize_results_df(results_df)

    summary = (
        work_df.groupby(["school", "survey_type"], dropna=False)
        .agg(
            عدد_الاستجابات=("id", "count"),
            المتوسط_الكلي=("overall_avg", "mean"),
        )
        .reset_index()
        .rename(columns={
            "school": "اسم المدرسة",
            "survey_type": "نوع الاستبانة",
            "عدد_الاستجابات": "عدد الاستجابات",
            "المتوسط_الكلي": "المتوسط الكلي",
        })
    )

    summary["المتوسط الكلي"] = pd.to_numeric(summary["المتوسط الكلي"], errors="coerce").fillna(0).round(2)
    summary["النسبة المئوية"] = summary["المتوسط الكلي"].apply(score_to_percentage)

    totals_df = get_school_totals_df()
    if not totals_df.empty:
        summary = summary.merge(
            totals_df.rename(columns={"school": "اسم المدرسة", "total_students": "عدد الطلبة الكلي"}),
            on="اسم المدرسة",
            how="left"
        )

        summary["عدد الطلبة الكلي"] = pd.to_numeric(summary["عدد الطلبة الكلي"], errors="coerce").fillna(0)
        summary["نسبة الاستجابة"] = summary.apply(
            lambda row: round((row["عدد الاستجابات"] / row["عدد الطلبة الكلي"]) * 100, 2)
            if row["عدد الطلبة الكلي"] > 0 else 0,
            axis=1
        )
    else:
        summary["عدد الطلبة الكلي"] = 0
        summary["نسبة الاستجابة"] = 0

    return summary[empty_cols].sort_values(["اسم المدرسة", "نوع الاستبانة"])

# =========================
# PDF
# =========================
def build_pdf_report_bytes(filtered_df, axis_summary_df, question_summary_df, school_summary_df):
    if not PDF_SUPPORT:
        raise Exception("مكتبات PDF غير مثبتة")

    ensure_reports_dir()
    output = BytesIO()
    font_name = register_arabic_font()

    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="ArabicTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=24,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        name="ArabicHeading",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=13,
        leading=18,
        alignment=TA_RIGHT
    )
    normal_style = ParagraphStyle(
        name="ArabicNormal",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=TA_RIGHT
    )
    small_style = ParagraphStyle(
        name="ArabicSmall",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=9,
        leading=13,
        alignment=TA_RIGHT
    )

    elements = []

    banner_path = os.path.join(os.getcwd(), BANNER_FILE)
    if os.path.exists(banner_path):
        try:
            elements.append(Image(banner_path, width=26 * cm, height=4.0 * cm))
            elements.append(Spacer(1, 0.3 * cm))
        except Exception:
            pass

    elements.append(Paragraph(ar_text("تقرير نتائج استبانة أولياء الأمور"), title_style))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(ar_text(f"تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), normal_style))
    elements.append(Spacer(1, 0.25 * cm))

    total_responses = len(filtered_df) if filtered_df is not None else 0
    totals_df = get_school_totals_df()
    total_students_all = pd.to_numeric(totals_df.get("total_students"), errors="coerce").fillna(0).sum() if not totals_df.empty else 0
    overall_response_rate = round((total_responses / total_students_all) * 100, 2) if total_students_all > 0 else 0
    overall_avg = round(pd.to_numeric(filtered_df.get("overall_avg"), errors="coerce").fillna(0).mean(), 2) if filtered_df is not None and not filtered_df.empty else 0
    overall_pct = score_to_percentage(overall_avg)

    intro_text = (
        f"تم تطبيق استبانة أولياء الأمور للعام الدراسي 2025-2026، وكان عدد الاستجابات "
        f"({total_responses}) من أصل ({int(total_students_all) if pd.notna(total_students_all) else 0}) طالبًا/طالبة، "
        f"بنسبة استجابة كلية بلغت ({overall_response_rate}%)، وبلغ المتوسط العام ({overall_avg}) "
        f"بنسبة مئوية ({overall_pct}%)."
    )
    elements.append(Paragraph(ar_text(intro_text), normal_style))
    elements.append(Spacer(1, 0.35 * cm))

    general_summary_df = pd.DataFrame([{
        "عدد الاستجابات الكلي": total_responses,
        "مجموع الطلبة في جميع المدارس": int(total_students_all) if pd.notna(total_students_all) else 0,
        "نسبة الاستجابة الكلية": overall_response_rate,
        "المتوسط العام": overall_avg,
        "المتوسط المئوي": overall_pct,
    }])

    def make_table_from_df(df, title, selected_cols=None, max_rows=20, col_widths=None, row_colorizer=None):
        if df is None or df.empty:
            return

        work_df = df.copy()
        if selected_cols:
            available_cols = [col for col in selected_cols if col in work_df.columns]
            if not available_cols:
                return
            work_df = work_df[available_cols]

        work_df = work_df.head(max_rows).fillna("")

        elements.append(Paragraph(ar_text(title), heading_style))
        elements.append(Spacer(1, 0.2 * cm))

        headers = [Paragraph(ar_text(col), small_style) for col in work_df.columns]
        data = [headers]

        for _, row in work_df.iterrows():
            data.append([Paragraph(ar_text(val), small_style) for val in row])

        if not col_widths:
            col_width = (27 * cm) / max(len(work_df.columns), 1)
            col_widths = [col_width] * len(work_df.columns)

        table = Table(data, colWidths=col_widths, repeatRows=1)
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5B9BD5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F8FAFC")]),
        ]

        if row_colorizer:
            for row_idx, row in enumerate(work_df.itertuples(index=False), start=1):
                bg_color = row_colorizer(row)
                if bg_color:
                    style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor(bg_color)))

        table.setStyle(TableStyle(style_cmds))
        elements.append(table)
        elements.append(Spacer(1, 0.4 * cm))

    make_table_from_df(
        general_summary_df,
        "الملخص العام لجميع المدارس",
        ["عدد الاستجابات الكلي", "مجموع الطلبة في جميع المدارس", "نسبة الاستجابة الكلية", "المتوسط العام", "المتوسط المئوي"]
    )
    make_table_from_df(
        axis_summary_df,
        "ملخص المحاور",
        ["المحور", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"],
        row_colorizer=lambda row: classification_hex(getattr(row, 4 if False else "النسبة_المئوية", 0)) if False else None
    )
    make_table_from_df(
        question_summary_df,
        "ملخص الفقرات",
        ["رقم الفقرة", "المحور", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"],
        max_rows=25,
        col_widths=[1.8 * cm, 5.3 * cm, 10.8 * cm, 2.5 * cm, 3.0 * cm, 2.4 * cm, 2.4 * cm]
    )
    make_table_from_df(
        school_summary_df,
        "ملخص المدارس",
        ["اسم المدرسة", "نوع الاستبانة", "عدد الاستجابات", "عدد الطلبة الكلي", "نسبة الاستجابة", "المتوسط الكلي", "النسبة المئوية"],
        col_widths=[5.0 * cm, 3.0 * cm, 2.2 * cm, 3.0 * cm, 3.0 * cm, 2.8 * cm, 2.8 * cm]
    )

    chart_buffer = create_question_chart_image(question_summary_df)
    if chart_buffer is not None:
        elements.append(Paragraph(ar_text("الرسم البياني لمتوسط الفقرات"), heading_style))
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(Image(chart_buffer, width=22 * cm, height=9 * cm))
        elements.append(Spacer(1, 0.4 * cm))

    axis_details = build_axis_details(question_summary_df)
    for idx, detail in enumerate(axis_details, start=1):
        elements.append(PageBreak())
        axis_title = (
            f"{detail['axis_name']} - المتوسط: {detail['axis_avg']} - "
            f"النسبة المئوية: {detail['axis_pct']}% - التصنيف: {detail['classification']} ({detail['classification_color']})"
        )
        elements.append(Paragraph(ar_text(axis_title), heading_style))
        elements.append(Spacer(1, 0.2 * cm))

        recommendation_paragraphs = build_recommendation_paragraphs(
            detail["axis_name"],
            detail["axis_pct"],
            detail["top_items"],
            detail["bottom_items"],
        )
        elements.append(Paragraph(ar_text("توصية المحور"), heading_style))
        elements.append(Spacer(1, 0.06 * cm))
        for para_text in recommendation_paragraphs:
            add_pdf_arabic_lines(elements, para_text, normal_style, max_chars=118, gap=0.015)
        elements.append(Spacer(1, 0.06 * cm))

        add_pdf_arabic_lines(elements, compact_item_line("أعلى فقرتين", detail["top_items"]), normal_style, max_chars=125, gap=0.012)
        add_pdf_arabic_lines(elements, compact_item_line("أدنى فقرتين", detail["bottom_items"]), normal_style, max_chars=125, gap=0.012)
        elements.append(Spacer(1, 0.10 * cm))

        make_table_from_df(
            detail["axis_df"],
            f"تفاصيل {detail['axis_name']}",
            ["رقم الفقرة", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"],
            max_rows=100,
            col_widths=[1.8 * cm, 14.5 * cm, 2.2 * cm, 2.8 * cm, 2.5 * cm, 2.5 * cm]
        )

        axis_chart = create_axis_chart_image(detail["axis_df"], detail["axis_name"])
        if axis_chart is not None:
            elements.append(Paragraph(ar_text(f"الرسم البياني المستقل للمحور: {detail['axis_name']}"), heading_style))
            elements.append(Spacer(1, 0.2 * cm))
            elements.append(Image(axis_chart, width=22 * cm, height=9 * cm))
            elements.append(Spacer(1, 0.3 * cm))

    doc.build(elements)
    pdf_bytes = output.getvalue()

    stamped_name = f"survey_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    with open(os.path.join(REPORTS_DIR, stamped_name), "wb") as f:
        f.write(pdf_bytes)

    output.seek(0)
    return pdf_bytes

# =========================
# Session State
# =========================
def init_session():
    defaults = {
        "page": "home",
        "logged_in_parent": False,
        "logged_in_admin": False,
        "student_data": None,
        "current_axis": 0,
        "answers": {},
        "notes": "",
        "respondent_type": "",
        "other_respondent_text": "",
        "is_bus_subscribed": "",
        "bus_number": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_parent_session():
    st.session_state.logged_in_parent = False
    st.session_state.student_data = None
    st.session_state.current_axis = 0
    st.session_state.answers = {}
    st.session_state.notes = ""
    st.session_state.respondent_type = ""
    st.session_state.other_respondent_text = ""
    st.session_state.is_bus_subscribed = ""
    st.session_state.bus_number = ""
    st.session_state.page = "home"

def reset_admin_session():
    st.session_state.logged_in_admin = False
    st.session_state.page = "home"

# =========================
# الحفظ
# =========================
def save_survey():
    student = st.session_state.student_data
    student_id = normalize_text(student.get("student_id", ""))

    if student_already_submitted(student_id):
        return False, "هذا الطالب قام بتعبئة الاستبانة مسبقًا"

    conn = get_connection()
    if conn is None:
        return False, "تعذر الاتصال بقاعدة البيانات"

    current_survey_questions = get_survey_questions_by_student(student)
    overall_avg = get_overall_average(student)
    overall_pct = score_to_percentage(overall_avg)
    survey_type = get_student_survey_type(student)
    other_text = st.session_state.other_respondent_text.strip() if st.session_state.respondent_type == "أخرى" else ""
    bus_number = st.session_state.bus_number.strip() if st.session_state.is_bus_subscribed == "نعم" else ""

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO parent_survey.survey_responses (
                    student_id, student_name, grade, school, survey_type,
                    respondent_type, other_respondent_text, is_bus_subscribed, bus_number,
                    notes, overall_avg, overall_pct
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    student.get("student_id", ""),
                    student.get("student_name", ""),
                    student.get("grade", ""),
                    student.get("school", ""),
                    survey_type,
                    st.session_state.respondent_type,
                    other_text,
                    st.session_state.is_bus_subscribed,
                    bus_number,
                    st.session_state.notes.strip(),
                    overall_avg,
                    overall_pct,
                ),
            )

            response_id = cursor.lastrowid
            inserted_answers = 0
            question_counter = 1

            for axis_name, questions in current_survey_questions.items():
                for q in questions:
                    answer_text = st.session_state.answers.get(q)
                    answer_value = ANSWER_SCORE_MAP.get(answer_text)

                    cursor.execute(
                        """
                        INSERT INTO parent_survey.survey_answers (
                            response_id,
                            survey_type,
                            axis,
                            axis_name,
                            question_id,
                            question_text,
                            answer_text,
                            answer_value,
                            answer_score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            response_id,
                            survey_type,
                            axis_name,
                            axis_name,
                            question_counter,
                            q,
                            answer_text,
                            answer_value,
                            answer_value,
                        ),
                    )

                    inserted_answers += 1
                    question_counter += 1

        conn.commit()

        refresh_ok, refresh_msg = refresh_summary_tables()

        if inserted_answers == 0:
            return False, "تم حفظ الاستبانة لكن لم يتم حفظ إجابات الأسئلة داخل survey_answers"

        if refresh_ok:
            return True, f"تم حفظ الاستبانة وتحديث التحليل تلقائيًا بنجاح. عدد الإجابات المحفوظة: {inserted_answers}"

        return True, f"تم حفظ الاستبانة، لكن لم يتم تحديث التحليل تلقائيًا: {refresh_msg}"

    except Exception as e:
        conn.rollback()
        return False, f"حدث خطأ أثناء حفظ النتائج: {e}"

    finally:
        conn.close()

# =========================
# الواجهة
# =========================
def render_header():
    banner_path = os.path.join(os.getcwd(), BANNER_FILE)
    logo_path = os.path.join(os.getcwd(), LOGO_FILE)

    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)

    c1, c2 = st.columns([1, 4])
    with c1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
    with c2:
        st.markdown(f'<div class="main-title">{APP_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-title">{SCHOOL_NAME}</div>', unsafe_allow_html=True)

def render_home():
    render_header()
    st.markdown('<div class="section-card" style="text-align:center;">اختر نوع الدخول المناسب</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="section-card" style="border-top: 5px solid {PRIMARY_COLOR}; min-height: 180px;"><div class="axis-title">دخول ولي الأمر</div><div style="font-size:22px;">لتعبئة الاستبانة باستخدام رقم الطالب وكلمة المرور.</div></div>',
            unsafe_allow_html=True
        )
        if st.button("فتح صفحة ولي الأمر", key="parent_btn", use_container_width=True):
            st.session_state.page = "parent_login"
            st.rerun()

    with col2:
        st.markdown(
            f'<div class="section-card" style="border-top: 5px solid {ACCENT_COLOR}; min-height: 180px;"><div class="axis-title">دخول الإدارة</div><div style="font-size:22px;">لعرض النتائج والتحليل وتنزيل الملفات.</div></div>',
            unsafe_allow_html=True
        )
        if st.button("فتح صفحة الإدارة", key="admin_btn", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()

def render_parent_login():
    render_header()
    st.markdown('<div class="section-card"><div class="axis-title">تسجيل دخول ولي الأمر</div></div>', unsafe_allow_html=True)

    with st.form("parent_login_form"):
        student_id = st.text_input("رقم الطالب")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")

    if st.button("العودة للرئيسية", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    if submitted:
        if not student_id.strip() or not password.strip():
            st.warning("يرجى إدخال رقم الطالب وكلمة المرور")
            return

        student = get_student(student_id.strip(), password.strip())
        if student is None:
            st.error("رقم الطالب أو كلمة المرور غير صحيحة")
            return

        if student_already_submitted(student_id.strip()):
            st.warning("هذا الطالب قام بتعبئة الاستبانة مسبقًا")
            return

        st.session_state.student_data = student
        st.session_state.logged_in_parent = True
        st.session_state.current_axis = 0
        st.session_state.answers = {}
        st.session_state.notes = ""
        st.session_state.page = "student_info"
        st.rerun()

def render_student_info_page():
    student = st.session_state.student_data
    render_header()

    st.markdown('<div class="section-card"><div class="axis-title">بيانات تعبئة الاستبانة</div></div>', unsafe_allow_html=True)

    st.markdown(
        f"""<div class="info-box"><b>رقم الطالب:</b> {student.get('student_id', '')}<br><b>اسم الطالب:</b> {student.get('student_name', '')}<br><b>الصف:</b> {student.get('grade', '')}<br><b>المدرسة:</b> {student.get('school', '')}</div>""",
        unsafe_allow_html=True,
    )

    respondent_options = ["الأب", "الأم", "الاثنان معًا", "أخرى"]
    current_respondent = st.session_state.respondent_type if st.session_state.respondent_type in respondent_options else None

    st.session_state.respondent_type = st.selectbox(
        "من يعبئ الاستبانة؟",
        respondent_options,
        index=respondent_options.index(current_respondent) if current_respondent in respondent_options else None,
        placeholder="اختر",
    )

    if st.session_state.respondent_type == "أخرى":
        st.session_state.other_respondent_text = st.text_input(
            "يرجى التحديد",
            value=st.session_state.other_respondent_text
        )
    else:
        st.session_state.other_respondent_text = ""

    bus_options = ["نعم", "لا"]
    current_bus = st.session_state.is_bus_subscribed if st.session_state.is_bus_subscribed in bus_options else None

    st.session_state.is_bus_subscribed = st.selectbox(
        "هل الطالب/ـة مشترك في النقل المدرسي؟",
        bus_options,
        index=bus_options.index(current_bus) if current_bus in bus_options else None,
        placeholder="اختر",
    )

    if st.session_state.is_bus_subscribed == "نعم":
        st.session_state.bus_number = st.text_input("رقم/اسم الباص", value=st.session_state.bus_number)
    else:
        st.session_state.bus_number = ""

    col1, col2 = st.columns(2)

    with col1:
        if st.button("خروج", use_container_width=True):
            reset_parent_session()
            st.rerun()

    with col2:
        if st.button("التالي إلى الاستبانة", use_container_width=True):
            if not st.session_state.respondent_type:
                st.warning("يرجى تحديد من يعبئ الاستبانة")
                return
            if st.session_state.respondent_type == "أخرى" and not st.session_state.other_respondent_text.strip():
                st.warning("يرجى إدخال وصف في خانة أخرى")
                return
            if not st.session_state.is_bus_subscribed:
                st.warning("يرجى تحديد هل الطالب/ـة مشترك في النقل أم لا")
                return

            st.session_state.page = "survey"
            st.rerun()

def render_survey_page():
    student = st.session_state.student_data
    current_survey_questions = get_survey_questions_by_student(student)
    current_axes_list = list(current_survey_questions.keys())

    if not current_axes_list:
        st.error("لا يوجد قالب استبانة صالح لهذا الطالب.")
        return

    axis_index = st.session_state.current_axis
    axis_name = current_axes_list[axis_index]
    questions = current_survey_questions[axis_name]

    render_header()

    st.markdown(
        f"""<div class="info-box"><b>رقم الطالب:</b> {student.get('student_id', '')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>الاسم:</b> {student.get('student_name', '')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>الصف:</b> {student.get('grade', '')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>المدرسة:</b> {student.get('school', '')}</div>""",
        unsafe_allow_html=True,
    )

    total_axes = len(current_axes_list)
    st.progress((axis_index + 1) / total_axes, text=f"المحور {axis_index + 1} من {total_axes}")
    st.markdown(f'<div class="section-card"><div class="axis-title">{axis_name}</div></div>', unsafe_allow_html=True)

    start_q_num = sum(len(current_survey_questions[a]) for a in current_axes_list[:axis_index]) + 1

    for i, q in enumerate(questions):
        q_num = start_q_num + i
        previous_answer = st.session_state.answers.get(q, "")

        st.markdown(f'<div class="question-text">{q_num}. {q}</div>', unsafe_allow_html=True)
        answer = st.radio(
            label="",
            options=ANSWER_OPTIONS,
            index=ANSWER_OPTIONS.index(previous_answer) if previous_answer in ANSWER_OPTIONS else None,
            key=f"q_{axis_index}_{i}",
            horizontal=True,
            label_visibility="collapsed"
        )
        st.session_state.answers[q] = answer

    if axis_index == total_axes - 1:
        st.session_state.notes = st.text_area("ملاحظات إضافية", value=st.session_state.notes, height=140)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("خروج", use_container_width=True):
            reset_parent_session()
            st.rerun()

    with col2:
        if axis_index > 0 and st.button("السابق", use_container_width=True):
            st.session_state.current_axis -= 1
            st.rerun()

    with col3:
        current_axis_answered = all(st.session_state.answers.get(q) in ANSWER_SCORE_MAP for q in questions)

        if axis_index < total_axes - 1:
            if st.button("التالي", use_container_width=True):
                if not current_axis_answered:
                    st.warning("يرجى اختيار إجابة لكل سؤال قبل الانتقال")
                else:
                    st.session_state.current_axis += 1
                    st.rerun()
        else:
            if st.button("حفظ الاستبانة", use_container_width=True):
                all_questions = [q for axis in current_axes_list for q in current_survey_questions[axis]]
                unanswered = [q for q in all_questions if st.session_state.answers.get(q) not in ANSWER_SCORE_MAP]

                if unanswered:
                    st.warning("يرجى اختيار إجابة لكل الأسئلة قبل الحفظ")
                    return

                success, msg = save_survey()
                if success:
                    st.success(msg)
                    st.balloons()
                    reset_parent_session()
                    st.rerun()
                else:
                    st.error(msg)

def render_admin_login():
    render_header()
    st.markdown('<div class="section-card"><div class="axis-title">دخول الإدارة</div></div>', unsafe_allow_html=True)

    with st.form("admin_login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")

    if st.button("العودة للرئيسية", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    if submitted:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in_admin = True
            st.session_state.page = "admin_dashboard"
            st.rerun()
        else:
            st.error("بيانات دخول الإدارة غير صحيحة")

def render_admin_dashboard():
    render_header()
    st.markdown('<div class="section-card"><div class="axis-title">لوحة التحليل</div></div>', unsafe_allow_html=True)

    top1, top2 = st.columns([1, 1])
    with top1:
        if st.button("تسجيل خروج الإدارة", use_container_width=True):
            reset_admin_session()
            st.rerun()
    with top2:
        if st.button("العودة للرئيسية", use_container_width=True):
            reset_admin_session()
            st.rerun()

    results_df, results_error = load_results()
    if results_error:
        st.error(results_error)
        return

    if results_df is None or results_df.empty:
        st.warning("لا توجد نتائج محفوظة بعد داخل survey_responses.")
        return

    refresh_ok, refresh_msg = refresh_summary_tables()
    if not refresh_ok:
        st.warning(refresh_msg)

    answers_df, answers_error = load_answers()
    if answers_error:
        st.warning(answers_error)
        answers_df = pd.DataFrame(columns=["response_id", "survey_type", "axis", "question_id", "question_text", "answer_value"])

    school_summary_raw, school_summary_error = load_school_summary_table()
    if school_summary_error:
        st.warning(school_summary_error)
        school_summary_raw = pd.DataFrame(columns=["school", "survey_type", "responses_count", "overall_avg", "overall_pct"])

    axis_summary_raw, axis_summary_error = load_school_axis_summary_table()
    if axis_summary_error:
        st.warning(axis_summary_error)
        axis_summary_raw = pd.DataFrame(columns=["school", "survey_type", "axis_name", "responses_count", "axis_avg", "axis_pct"])

    schools = sorted(results_df["school"].dropna().astype(str).str.strip().unique().tolist())
    survey_types = sorted(results_df["survey_type"].dropna().astype(str).str.strip().str.upper().unique().tolist())

    f1, f2 = st.columns(2)
    with f1:
        selected_school = st.selectbox("اختر المدرسة", ["جميع المدارس"] + schools, index=0)
    with f2:
        selected_survey_type = st.selectbox("اختر نوع الاستبانة", ["جميع الأنواع"] + survey_types, index=0)

    filtered_df = results_df.copy()

    if selected_school != "جميع المدارس":
        filtered_df = filtered_df[filtered_df["school"] == selected_school]
    if selected_survey_type != "جميع الأنواع":
        filtered_df = filtered_df[filtered_df["survey_type"] == selected_survey_type]

    if filtered_df.empty:
        st.warning("لا توجد بيانات مطابقة للفلاتر المختارة.")
        return

    filtered_response_ids = (
        pd.to_numeric(filtered_df["id"], errors="coerce")
        .dropna()
        .astype(int)
        .tolist()
    )

    filtered_answers_df = answers_df[answers_df["response_id"].isin(filtered_response_ids)].copy() if answers_df is not None else pd.DataFrame()

    if selected_survey_type != "جميع الأنواع" and not filtered_answers_df.empty and "survey_type" in filtered_answers_df.columns:
        filtered_answers_df = filtered_answers_df[
            filtered_answers_df["survey_type"].astype(str).str.strip().str.upper() == selected_survey_type
        ]

    filtered_school_summary = school_summary_raw.copy()
    if not filtered_school_summary.empty:
        if selected_school != "جميع المدارس":
            filtered_school_summary = filtered_school_summary[filtered_school_summary["school"] == selected_school]
        if selected_survey_type != "جميع الأنواع":
            filtered_school_summary = filtered_school_summary[filtered_school_summary["survey_type"] == selected_survey_type]

    filtered_axis_summary_raw = axis_summary_raw.copy()
    if not filtered_axis_summary_raw.empty:
        if selected_school != "جميع المدارس":
            filtered_axis_summary_raw = filtered_axis_summary_raw[filtered_axis_summary_raw["school"] == selected_school]
        if selected_survey_type != "جميع الأنواع":
            filtered_axis_summary_raw = filtered_axis_summary_raw[filtered_axis_summary_raw["survey_type"] == selected_survey_type]

    overall_avg = round(filtered_df["overall_avg"].mean(), 2) if not filtered_df.empty else 0
    overall_pct = score_to_percentage(overall_avg)
    responses_count = len(filtered_df)
    unique_schools = filtered_df["school"].nunique() if "school" in filtered_df.columns else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("عدد الاستجابات", responses_count)
    m2.metric("المتوسط الكلي", overall_avg)
    m3.metric("النسبة المئوية", f"{overall_pct}%")
    m4.metric("عدد المدارس", unique_schools if selected_school == "جميع المدارس" else 1)

    st.markdown("## ملخص المدارس حسب الفلتر")
    if filtered_school_summary is not None and not filtered_school_summary.empty:
        school_summary_df = filtered_school_summary.rename(columns={
            "school": "اسم المدرسة",
            "survey_type": "نوع الاستبانة",
            "responses_count": "عدد الاستجابات",
            "overall_avg": "المتوسط الكلي",
            "overall_pct": "النسبة المئوية",
        }).copy()

        totals_df = get_school_totals_df()
        if not totals_df.empty:
            school_summary_df = school_summary_df.merge(
                totals_df.rename(columns={"school": "اسم المدرسة", "total_students": "عدد الطلبة الكلي"}),
                on="اسم المدرسة",
                how="left"
            )
            school_summary_df["عدد الطلبة الكلي"] = pd.to_numeric(school_summary_df["عدد الطلبة الكلي"], errors="coerce").fillna(0)
            school_summary_df["نسبة الاستجابة"] = school_summary_df.apply(
                lambda row: round((row["عدد الاستجابات"] / row["عدد الطلبة الكلي"]) * 100, 2)
                if row["عدد الطلبة الكلي"] > 0 else 0,
                axis=1
            )
        else:
            school_summary_df["عدد الطلبة الكلي"] = 0
            school_summary_df["نسبة الاستجابة"] = 0

        school_summary_df = school_summary_df[[
            "اسم المدرسة", "نوع الاستبانة", "عدد الاستجابات", "عدد الطلبة الكلي",
            "نسبة الاستجابة", "المتوسط الكلي", "النسبة المئوية"
        ]].sort_values(["اسم المدرسة", "نوع الاستبانة"])
    else:
        school_summary_df = build_school_summary(filtered_df)

    st.dataframe(school_summary_df, use_container_width=True)

    if not school_summary_df.empty:
        school_chart_df = school_summary_df.copy()
        school_chart_df["المدرسة والنوع"] = (
            school_chart_df["اسم المدرسة"].astype(str) + " - " + school_chart_df["نوع الاستبانة"].astype(str)
        )

        st.markdown("### الرسم البياني لمتوسطات المدارس حسب الفلتر")
        render_bar_chart(
            school_chart_df,
            "المدرسة والنوع",
            "النسبة المئوية",
            "النسبة المئوية لمتوسطات المدارس حسب الفلتر"
        )

        st.markdown("### الرسم البياني لنسبة الاستجابة حسب الفلتر")
        render_bar_chart(
            school_chart_df,
            "المدرسة والنوع",
            "نسبة الاستجابة",
            "نسبة الاستجابة حسب الفلتر"
        )

    st.markdown("## متوسطات المحاور")
    axis_summary_df = build_axis_summary(filtered_answers_df)

    if axis_summary_df.empty:
        st.warning("لا توجد بيانات تحليل للمحاور لهذه الفلاتر.")
    else:
        st.dataframe(axis_summary_df[["المحور", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"]], use_container_width=True)
        render_bar_chart(axis_summary_df, "المحور", "النسبة المئوية", "النسبة المئوية لمتوسطات المحاور", color_col="لون التصنيف")

    st.markdown("## متوسطات الفقرات")
    question_summary_df = build_question_summary(filtered_answers_df)
    if question_summary_df.empty:
        st.info("لا توجد تفاصيل فقرات مرتبطة بهذه الفلاتر داخل survey_answers.")
    else:
        st.dataframe(question_summary_df[["رقم الفقرة", "المحور", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"]], use_container_width=True, height=500)

    axis_details = build_axis_details(question_summary_df)
    if axis_details:
        st.markdown("## تفاصيل المحاور والتوصيات الذكية")
        for detail in axis_details:
            st.markdown(
                f"### {detail['axis_name']} — المتوسط: {detail['axis_avg']} — النسبة: {detail['axis_pct']}% — التصنيف: {detail['classification']} ({detail['classification_color']})"
            )
            st.info("\n\n".join(build_recommendation_paragraphs(
                detail["axis_name"],
                detail["axis_pct"],
                detail["top_items"],
                detail["bottom_items"]
            )))

            top_cols = st.columns(2)
            with top_cols[0]:
                st.markdown("**أعلى فقرتين**")
                st.dataframe(
                    detail["top_items"][["رقم الفقرة", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"]],
                    use_container_width=True,
                    hide_index=True
                )
            with top_cols[1]:
                st.markdown("**أدنى فقرتين**")
                st.dataframe(
                    detail["bottom_items"][["رقم الفقرة", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"]],
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("**جدول المحور**")
            st.dataframe(
                detail["axis_df"][["رقم الفقرة", "الفقرة", "المتوسط", "النسبة المئوية", "التصنيف", "لون التصنيف"]],
                use_container_width=True,
                hide_index=True
            )

            chart_df = detail["axis_df"].copy()
            chart_df["الفقرة"] = chart_df["رقم الفقرة"].astype(str)
            render_bar_chart(
                chart_df,
                "الفقرة",
                "النسبة المئوية",
                f"الرسم البياني للمحور: {detail['axis_name']}",
                color_col="لون التصنيف"
            )

    with st.expander("عرض بيانات المعبئ", expanded=False):
        cols = [
            "student_id", "student_name", "school", "survey_type",
            "respondent_type", "is_bus_subscribed", "bus_number", "other_respondent_text"
        ]
        available = [c for c in cols if c in filtered_df.columns]
        st.dataframe(filtered_df[available], use_container_width=True)

    with st.expander("عرض النتائج الخام", expanded=False):
        st.dataframe(filtered_df, use_container_width=True, height=350)

    st.markdown("## تنزيل الملفات")
    pdf_bytes = None
    pdf_error = None

    if PDF_SUPPORT:
        try:
            pdf_bytes = build_pdf_report_bytes(filtered_df, axis_summary_df, question_summary_df, school_summary_df)
        except Exception as e:
            pdf_error = str(e)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button(
            "تنزيل النتائج الخام Excel",
            dataframe_to_excel_bytes({"Results": filtered_df}),
            "filtered_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col2:
        excel_sheets = {
            "Axis Summary": axis_summary_df,
            "Question Summary": question_summary_df,
            "School Summary": school_summary_df
        }
        for idx, detail in enumerate(axis_details, start=1):
            excel_sheets[f"Axis_{idx}"] = detail["axis_df"]

        st.download_button(
            "تنزيل ملخص التحليل Excel",
            dataframe_to_excel_bytes(excel_sheets),
            "analysis_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col3:
        st.download_button(
            "تنزيل النتائج CSV",
            filtered_df.to_csv(index=False).encode("utf-8-sig"),
            "filtered_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col4:
        if pdf_bytes is not None:
            st.download_button(
                "تنزيل التقرير PDF",
                pdf_bytes,
                "survey_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("تعذر إنشاء PDF")
            if pdf_error:
                st.caption(pdf_error)

# =========================
# التشغيل
# =========================
ensure_db_columns()
init_session()

if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "parent_login":
    render_parent_login()
elif st.session_state.page == "student_info":
    render_student_info_page()
elif st.session_state.page == "survey":
    render_survey_page()
elif st.session_state.page == "admin_login":
    render_admin_login()
elif st.session_state.page == "admin_dashboard":
    render_admin_dashboard()
