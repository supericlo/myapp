import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import json
import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import matplotlib
from matplotlib.patches import Rectangle
import tempfile
import os
import requests
from bs4 import BeautifulSoup

# 设置 matplotlib 字体
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(
    page_title="專業美股診斷終端 - 專業版", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. CSS 样式（完整保留您的原始样式）
# ==========================================
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        min-width: 380px !important;
        width: 380px !important;
    }
    button[kind="header"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #e0f0ff 0%, #b8d4f0 100%) !important;
    }
    .right-top-logo {
        background-color: #000000;
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .right-logo-img {
        width: 45px;
        height: 45px;
        border-radius: 8px;
    }
    .right-logo-text {
        line-height: 1.2;
    }
    .right-logo-title {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: white !important;
        margin: 0 !important;
        padding: 0 !important;
        text-align: left;
    }
    .right-logo-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #cccccc !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .big-score { font-size: 100px !important; font-weight: 800 !important; line-height: 1.0; margin-bottom: 5px; }
    .score-label { font-size: 20px; color: #666; font-weight: bold; }
    .good-item { color: #228B22; margin: 0 !important; padding: 2px 0 !important; line-height: 1.3; }
    .neutral-item { color: #FFA500; margin: 0 !important; padding: 2px 0 !important; line-height: 1.3; }
    .bad-item { color: #FF4B4B; margin: 0 !important; padding: 2px 0 !important; line-height: 1.3; }
    
    .main-header {
        font-size: 28px !important;
        font-weight: 900 !important;
        margin: 0 0 5px 0 !important;
        padding: 5px 12px !important;
        background: #000000 !important;
        color: white !important;
        border-radius: 10px;
        text-align: left;
    }
    .main-header-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #cccccc !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .section-header-a {
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 0 5px 0 !important;
        padding: 5px 12px !important;
        background: linear-gradient(135deg, #2c5282 0%, #1a365d 100%) !important;
        color: white !important;
        border-radius: 10px;
        text-align: left;
    }
    .section-header-a-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #bee3f8 !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .section-header-b {
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 0 5px 0 !important;
        padding: 5px 12px !important;
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%) !important;
        color: white !important;
        border-radius: 10px;
        text-align: left;
    }
    .section-header-b-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #e2e8f0 !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .section-header-c {
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 0 5px 0 !important;
        padding: 5px 12px !important;
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%) !important;
        color: white !important;
        border-radius: 10px;
        text-align: left;
    }
    .section-header-c-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #e2e8f0 !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .report-header-a {
        font-size: 28px !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        margin-top: 0 !important;
        padding: 8px 15px !important;
        background: linear-gradient(135deg, #2c5282 0%, #1a365d 100%) !important;
        color: white !important;
        border-radius: 12px;
        text-align: left;
    }
    .report-header-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #bee3f8 !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .peer-header-b {
        font-size: 28px !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        margin-top: 15px !important;
        padding: 8px 15px !important;
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%) !important;
        color: white !important;
        border-radius: 10px;
        text-align: left;
    }
    .peer-header-sub {
        font-size: 20px !important;
        font-weight: normal !important;
        color: #e2e8f0 !important;
        margin-top: 2px !important;
        display: block;
        text-align: left;
    }
    .disclaimer {
        background-color: #1a1a2e;
        padding: 15px;
        border-radius: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
        font-size: 12px;
        color: #888;
        text-align: center;
        border-top: 1px solid #333;
    }
    
    hr {
        margin: 5px 0px !important;
    }
    .stSelectbox {
        margin-bottom: 5px !important;
    }
    .stButton button {
        margin-bottom: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 辅助函数 - 创建区块标题
# ==========================================
def create_section_header(icon: str, title_cn: str, title_en: str):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); border-radius: 15px; padding: 5px 20px 15px 20px; margin: 15px 0 20px 0; border-left: 5px solid #1a365d; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="padding: 5px 0;">
            <div style="font-size: 24px; font-weight: 800; margin: 0 0 5px 0; color: #1a365d; border-bottom: 2px solid #3182ce; display: inline-block;">
                {icon} {title_cn} 
                <span style="font-size: 14px; font-weight: normal; color: #4a5568; margin-left: 10px;">{title_en}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 数据定义（SECTOR_INDUSTRY_MAP, SECTOR_INDUSTRY_MAP_EN）
# ==========================================
SECTOR_INDUSTRY_MAP = {
    "科技": ["半導體", "軟體 - 基礎設施", "軟體 - 應用", "軟體 - 網路", "電腦硬體", "消費電子", "資訊科技服務", "電子元件"],
    "醫療保健": ["生物科技", "製藥 - 綜合", "製藥 - 專科", "醫療器械", "診斷與研究", "醫療設施", "健康資訊服務"],
    "金融服務": ["銀行 - 綜合", "銀行 - 區域", "資本市場", "信貸服務", "保險 - 綜合", "保險 - 人壽", "保險 - 產險", "資產管理"],
    "消費週期": ["汽車製造", "汽車零件", "網路零售", "餐廳", "專業零售", "奢侈品", "旅遊服務", "家居裝修零售"],
    "工業": ["航太與國防", "鐵路", "貨運", "機場與航空", "海運", "商業服務", "顧問服務", "工程與建設", "工業分銷"],
    "通訊服務": ["網路內容與資訊", "電信服務", "娛樂", "廣播", "出版", "廣告代理"],
    "消費防禦": ["飲料 - 非酒精", "飲料 - 酒精", "折扣商店", "包裝食品", "家居與個人用品", "菸草", "農產品"],
    "能源": ["石油與天然氣勘探", "石油與天然氣綜合", "石油與天然氣中游", "石油與天然氣煉製", "石油與天然氣設備", "可再生能源", "煤炭"],
    "基本材料": ["化學品", "黃金", "白銀", "銅", "鋼鐵", "鋁", "肥料與農業化學", "建材"],
    "房地產": ["REIT - 辦公室", "REIT - 工業", "REIT - 零售", "REIT - 住宅", "REIT - 醫療", "REIT - 專業", "房地產服務"],
    "公用事業": ["公用事業 - 電力", "公用事業 - 水務", "公用事業 - 可再生能源", "公用事業 - 獨立發電", "公用事業 - 綜合"]
}

SECTOR_INDUSTRY_MAP_EN = {
    "Technology": ["Semiconductors", "Software - Infrastructure", "Software - Application", "Software - Internet", "Computer Hardware", "Consumer Electronics", "Information Technology Services", "Electronic Components"],
    "Healthcare": ["Biotechnology", "Drug Manufacturers - General", "Drug Manufacturers - Specialty", "Medical Devices", "Diagnostics & Research", "Medical Care Facilities", "Health Information Services"],
    "Financial Services": ["Banks - Diversified", "Banks - Regional", "Capital Markets", "Credit Services", "Insurance - Diversified", "Insurance - Life", "Insurance - Property & Casualty", "Asset Management"],
    "Consumer Cyclical": ["Auto Manufacturers", "Auto Parts", "Internet Retail", "Restaurants", "Specialty Retail", "Luxury Goods", "Travel Services", "Home Improvement Retail"],
    "Industrials": ["Aerospace & Defense", "Railroads", "Trucking", "Airports & Air Services", "Marine Shipping", "Business Services", "Consulting Services", "Engineering & Construction", "Industrial Distribution"],
    "Communication Services": ["Internet Content & Information", "Telecom Services", "Entertainment", "Broadcasting", "Publishing", "Advertising Agencies"],
    "Consumer Defensive": ["Beverages - Non-Alcoholic", "Beverages - Alcoholic", "Discount Stores", "Packaged Foods", "Household & Personal Products", "Tobacco", "Farm Products"],
    "Energy": ["Oil & Gas E&P", "Oil & Gas Integrated", "Oil & Gas Midstream", "Oil & Gas Refining & Marketing", "Oil & Gas Equipment & Services", "Renewable Energy", "Coal"],
    "Basic Materials": ["Chemicals", "Gold", "Silver", "Copper", "Steel", "Aluminum", "Fertilizers & Agricultural Chemicals", "Construction Materials"],
    "Real Estate": ["REIT - Office", "REIT - Industrial", "REIT - Retail", "REIT - Residential", "REIT - Healthcare", "REIT - Specialized", "Real Estate Services"],
    "Utilities": ["Utilities - Regulated Electric", "Utilities - Regulated Water", "Utilities - Renewable", "Utilities - Independent Power Producers", "Utilities - Diversified"]
}

# ==========================================
# 4. 完整扩充的 INDUSTRY_PEERS 字典（涵盖所有行业）
# ==========================================
INDUSTRY_PEERS = {
    # 科技
    "Semiconductors": ["NVDA", "AVGO", "AMD", "TXN", "INTC", "QCOM", "MU", "ADI", "MRVL", "ON"],
    "Software - Infrastructure": ["MSFT", "ORCL", "ADBE", "CRM", "PANW", "SNPS", "CDNS", "PLTR", "CRWD", "FTNT"],
    "Software - Application": ["SAP", "INTU", "NOW", "UBER", "SHOP", "ADSK", "TEAM", "DOCU", "ZM", "WDAY"],
    "Software - Internet": ["GOOGL", "META", "BABA", "TCEHY", "BIDU", "SNAP", "PINS", "RBLX", "TWLO", "Z"],
    "Computer Hardware": ["AAPL", "DELL", "HPQ", "SMCI", "WDC", "STX", "LOGI", "NTAP", "PSTG", "IONQ"],
    "Consumer Electronics": ["AAPL", "SONY", "LG", "VZIO", "KODK", "HEAR", "VOXX", "UEIC", "GPRO", "BB"],
    "Information Technology Services": ["ACN", "IBM", "INFY", "CTSH", "CAP", "FIS", "FISV", "CDW", "DXC", "SAIC"],
    "Electronic Components": ["APH", "TEL", "GLW", "FLEX", "JBL", "CLS", "PLXS", "SANM", "KEM", "VSH"],
    # 医疗保健
    "Biotechnology": ["AMGN", "GILD", "REGN", "VRTX", "BIIB", "ILMN", "MRNA", "BNTX", "ALNY", "SRPT"],
    "Drug Manufacturers - General": ["JNJ", "PFE", "MRK", "ABBV", "BMY", "NVS", "SNY", "GSK", "AZN", "LLY"],
    "Drug Manufacturers - Specialty": ["TEVA", "ZTS", "VTRS", "RPRX", "CTLT", "ELAN", "RDY", "ITCI", "ARNA", "COLL"],
    "Medical Devices": ["SYK", "MDT", "ISRG", "BSX", "ABT", "EW", "BDX", "ZBH", "HOLX", "DXCM"],
    "Diagnostics & Research": ["IQV", "LH", "DGX", "WAT", "TMO", "A", "DHR", "MTD", "PKI", "RVTY"],
    "Medical Care Facilities": ["HCA", "UHS", "THC", "CYH", "ACHC", "FMS", "DVA", "ENSG", "SEM", "USPH"],
    "Health Information Services": ["CERN", "MDRX", "VEEV", "TDOC", "AMWL", "PINC", "EVH", "OMCL", "HCAT", "ONEM"],
    # 金融服务
    "Banks - Diversified": ["JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "COF"],
    "Banks - Regional": ["SIVB", "SBNY", "CMA", "KEY", "RF", "HBAN", "CFG", "MTB", "FITB", "ZION"],
    "Capital Markets": ["BLK", "KKR", "BX", "APO", "CG", "TPG", "ARES", "OWL", "BEN", "IVZ"],
    "Credit Services": ["V", "MA", "AXP", "PYPL", "SQ", "FISV", "GPN", "DFS", "ALLY", "SYF"],
    "Insurance - Diversified": ["BRK-B", "AIG", "MET", "PRU", "LNC", "HIG", "UNM", "THG", "ESGR", "GL"],
    "Insurance - Life": ["AFL", "MET", "PRU", "LNC", "UNM", "GNW", "BHF", "JXN", "FG", "ANAT"],
    "Insurance - Property & Casualty": ["PGR", "TRV", "ALL", "CB", "HIG", "WRB", "CINF", "AFG", "RLI", "KMPR"],
    "Asset Management": ["BLK", "KKR", "BX", "APO", "TROW", "STT", "BK", "IVZ", "BEN", "CG"],
    # 消费周期
    "Auto Manufacturers": ["TSLA", "GM", "F", "RIVN", "LCID", "HMC", "TM", "STLA", "NIO", "LI"],
    "Auto Parts": ["APTV", "MGA", "BWA", "LEA", "ALV", "DORM", "FOXF", "VC", "GNTX", "MOD"],
    "Internet Retail": ["AMZN", "JD", "BABA", "MELI", "ETSY", "CPNG", "SE", "CVNA", "W", "RVLV"],
    "Restaurants": ["MCD", "SBUX", "YUM", "CMG", "QSR", "DRI", "TXRH", "DPZ", "WING", "CAKE"],
    "Specialty Retail": ["HD", "LOW", "TSCO", "BBY", "TJX", "ROST", "GPS", "KSS", "M", "JWN"],
    "Luxury Goods": ["LVMUY", "PPRUY", "TIF", "CFRUY", "HESAY", "CL", "COH", "RACE", "FERRY", "MONRY"],
    "Travel Services": ["BKNG", "EXPE", "TCOM", "TRIP", "ABNB", "TNL", "MMYT", "DESP", "SABR", "VIZIO"],
    "Home Improvement Retail": ["HD", "LOW", "TSCO", "FND", "LL", "ARHS", "HVT", "TTSH", "WSM", "RH"],
    # 工业
    "Aerospace & Defense": ["RTX", "LMT", "NOC", "GD", "LHX", "HII", "BA", "TDG", "HEI", "SPR"],
    "Railroads": ["UNP", "CSX", "NSC", "CNI", "CP", "KSU", "WAB", "GBX", "RAIL", "TRN"],
    "Trucking": ["ODFL", "LSTR", "KNX", "SNDR", "WERN", "ARCB", "HTLD", "MRTN", "USX", "CVLG"],
    "Airports & Air Services": ["DAL", "UAL", "LUV", "AAL", "JBLU", "SAVE", "ALK", "SKYW", "ULCC", "PARA"],
    "Marine Shipping": ["ZIM", "GOGL", "NMM", "DAC", "SBLK", "CMRE", "MATX", "ESEA", "GLBS", "DSX"],
    "Business Services": ["EXPN", "EFX", "TRU", "MCO", "SPGI", "INFO", "DNB", "VRSK", "FICO", "VVI"],
    "Consulting Services": ["ACN", "IBM", "IT", "CTSH", "CACI", "SAIC", "PSN", "LDOS", "BRS", "FCN"],
    "Engineering & Construction": ["ACM", "EME", "PWR", "KBR", "FLR", "J", "MTRX", "STRL", "MYRG", "GVA"],
    "Industrial Distribution": ["FAST", "GWW", "MSM", "BECN", "WSO", "DNOW", "TITN", "FERG", "HD", "LOW"],
    # 通讯服务
    "Internet Content & Information": ["GOOGL", "META", "BABA", "TCEHY", "BIDU", "SNAP", "PINS", "RBLX", "TWLO", "Z"],
    "Telecom Services": ["T", "VZ", "TMUS", "CHTR", "CMCSA", "VOD", "TEF", "ORAN", "BTI", "PHI"],
    "Entertainment": ["DIS", "NFLX", "WBD", "PARA", "LYV", "LGF.A", "FOX", "NWSA", "ROKU", "AMC"],
    "Broadcasting": ["FOX", "NWS", "NXST", "GTN", "TGNA", "EVC", "SBGI", "CMLS", "SSP", "IHRT"],
    "Publishing": ["NYT", "GCI", "WLY", "LEE", "MNI", "SCHL", "RHC", "SGA", "QNST", "MOGO"],
    "Advertising Agencies": ["OMC", "IPG", "WPP", "PUBM", "MGNI", "TTGT", "ADTH", "DLX", "QNST", "CTV"],
    # 消费防御
    "Beverages - Non-Alcoholic": ["KO", "PEP", "KOF", "FIZZ", "MNST", "CELH", "CCEP", "COCO", "REED", "BRFH"],
    "Beverages - Alcoholic": ["ABEV", "STZ", "BF-B", "TAP", "SAM", "MGPI", "VWE", "NAPA", "WINED", "BEV"],
    "Discount Stores": ["WMT", "COST", "TGT", "DG", "DLTR", "BJ", "PSMT", "BIG", "ODP", "FRED"],
    "Packaged Foods": ["KHC", "GIS", "CPB", "CAG", "MDLZ", "HSY", "MKC", "SJM", "FLO", "HAIN"],
    "Household & Personal Products": ["PG", "CL", "KMB", "CHD", "EL", "COTY", "CLX", "ENR", "HELE", "ELF"],
    "Tobacco": ["MO", "PM", "BTI", "IMBBY", "UVV", "VGR", "XXII", "TPB", "RLX", "KAVL"],
    "Farm Products": ["ADM", "BG", "INGR", "FDP", "LND", "AGRO", "DOLE", "VFF", "VEG", "AAG"],
    # 能源
    "Oil & Gas E&P": ["XOM", "CVX", "COP", "EOG", "PXD", "OXY", "HES", "DVN", "FANG", "MRO"],
    "Oil & Gas Integrated": ["XOM", "CVX", "BP", "SHEL", "TTE", "EQNR", "ENI", "IMO", "SU", "CVE"],
    "Oil & Gas Midstream": ["KMI", "WMB", "OKE", "PAA", "ET", "MPLX", "ENB", "TRP", "LNG", "TGP"],
    "Oil & Gas Refining & Marketing": ["PSX", "VLO", "MPC", "DK", "CVR", "CLNE", "PBF", "HFC", "CSAN", "UGP"],
    "Oil & Gas Equipment & Services": ["SLB", "HAL", "BKR", "NOV", "CHX", "FTI", "WFRD", "TDW", "OII", "XPRO"],
    "Renewable Energy": ["ENPH", "SEDG", "FSLR", "RUN", "NOVA", "SPWR", "BE", "PLUG", "STEM", "NEE"],
    "Coal": ["BTU", "ARCH", "AMR", "ARLP", "METC", "HNRG", "CEIX", "NRP", "CNX", "CLF"],
    # 基本材料
    "Chemicals": ["LIN", "SHW", "APD", "ECL", "DD", "LYB", "DOW", "PPG", "CTVA", "IFF"],
    "Gold": ["NEM", "GOLD", "GFI", "SBSW", "AGI", "KGC", "IAG", "AEM", "AU", "EGO"],
    "Silver": ["PAAS", "HL", "MAG", "AG", "FSM", "EXK", "SVM", "BVN", "SSRM", "USAS"],
    "Copper": ["FCX", "SCCO", "TECK", "HBM", "LUNMF", "CS", "BHP", "RIO", "GLNCY", "TRQ"],
    "Steel": ["NUE", "STLD", "CLF", "X", "MT", "TX", "GGB", "SID", "PKX", "RS"],
    "Aluminum": ["AA", "CENX", "NHYDY", "KALU", "ARNC", "KNWN", "ADES", "CSEM", "BNZU", "ALMMF"],
    "Fertilizers & Agricultural Chemicals": ["MOS", "NTR", "CF", "UAN", "IPI", "SMG", "AVD", "BIOX", "CVR", "ICL"],
    "Construction Materials": ["MLM", "VMC", "CRH", "SUM", "CX", "EXP", "BCC", "JHX", "LOMA", "KNF"],
    # 房地产
    "REIT - Office": ["BXP", "VNO", "SLG", "KRC", "HIW", "PDM", "CUZ", "DEI", "EQC", "PGRE"],
    "REIT - Industrial": ["PLD", "DRE", "EGP", "FR", "STAG", "REXR", "TRNO", "LXP", "ILPT", "MPW"],
    "REIT - Retail": ["SPG", "O", "NNN", "ADC", "BRX", "KIM", "REG", "SITC", "ROIC", "MAC"],
    "REIT - Residential": ["EQR", "AVB", "ESS", "MAA", "UDR", "INVH", "CPT", "ACC", "AMH", "NXRT"],
    "REIT - Healthcare": ["WELL", "VTR", "DOC", "OHI", "SBRA", "HR", "LTC", "NHI", "CHCT", "CTRE"],
    "REIT - Specialized": ["IRM", "DLR", "EQIX", "CCI", "SBAC", "AMT", "UNIT", "GLPI", "VICI", "MPW"],
    "Real Estate Services": ["CBRE", "JLL", "CSGP", "Z", "ZG", "RDFN", "EXPI", "REAX", "BEKE", "OPEN"],
    # 公用事业
    "Utilities - Regulated Electric": ["NEE", "DUK", "SO", "D", "AEP", "EXC", "ED", "PPL", "FE", "EIX"],
    "Utilities - Regulated Water": ["AWK", "WTRG", "CWT", "AWR", "SJW", "YORW", "ARTNA", "MSEX", "GWRS", "CTWS"],
    "Utilities - Renewable": ["NEE", "BEP", "RNW", "CWEN", "NEP", "AY", "EBR", "TPIC", "ORA", "ELP"],
    "Utilities - Independent Power Producers": ["VST", "CEG", "NRG", "AES", "RWE", "BIPC", "CIG", "ENIC", "TLK", "EIX"],
    "Utilities - Diversified": ["CMS", "CNP", "LNT", "OGE", "PNW", "SRE", "WEC", "DTE", "ETR", "PEG"],
}

# ==========================================
# 5. 核心函数（完整保留，确保评分和图表正常）
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_robust_data(ticker):
    try:
        if not ticker:
            return None
        stock = yf.Ticker(ticker.strip().upper())
        info = stock.info
        if not info or 'shortName' not in info:
            return None
        
        mkt_cap = (info.get('marketCap', 0) or 0) / 1e9
        roe = (info.get('returnOnEquity', 0) or 0) * 100
        roi = (info.get('returnOnAssets', 0) or 0) * 100
        pe = info.get('trailingPE') or info.get('forwardPE') or 0
        peg = info.get('pegRatio') or (pe / 15 if pe > 0 else 0)
        curr = info.get('currentRatio', 0) or 0
        quick = info.get('quickRatio', 0) or 0
        
        revenue_growth = (info.get('revenueGrowth', 0) or 0) * 100
        earnings_growth = (info.get('earningsGrowth', 0) or 0) * 100
        
        net_margin = 0
        margin_fields = ['netMargin', 'profitMargins']
        for field in margin_fields:
            value = info.get(field, 0)
            if value and value != 0:
                net_margin = value * 100
                break
        
        if net_margin == 0:
            try:
                financials = stock.financials
                if not financials.empty and 'Net Income' in financials.index and 'Total Revenue' in financials.index:
                    net_income = financials.loc['Net Income'].iloc[0]
                    revenue = financials.loc['Total Revenue'].iloc[0]
                    if revenue != 0:
                        net_margin = (net_income / revenue) * 100
            except:
                pass
        
        obv_trend = calculate_obv_trend(ticker)
        
        # 计算 150 天移动平均线
        sma_150_value = None
        try:
            hist_for_sma = get_history_data(ticker, "1y")
            if len(hist_for_sma) >= 150 and not hist_for_sma.empty:
                sma_150_value = hist_for_sma['Close'].rolling(window=150).mean().iloc[-1]
        except Exception:
            sma_150_value = None
        
        roe_valid = check_data_valid(roe)
        if roe_valid:
            if roe > 20: roe_score, roe_status, roe_category = 15, "Excellent", "good"
            elif roe > 15: roe_score, roe_status, roe_category = 12, "Good", "good"
            elif roe > 10: roe_score, roe_status, roe_category = 8, "Fair", "neutral"
            elif roe > 5: roe_score, roe_status, roe_category = 4, "Average", "neutral"
            else: roe_score, roe_status, roe_category = 0, "Weak", "bad"
        else:
            roe_score, roe_status, roe_category = 0, "N/A", "missing"
        
        roi_valid = check_data_valid(roi)
        if roi_valid:
            if roi > 10: roi_score, roi_status, roi_category = 10, "Excellent", "good"
            elif roi > 7: roi_score, roi_status, roi_category = 7, "Good", "good"
            elif roi > 4: roi_score, roi_status, roi_category = 4, "Fair", "neutral"
            else: roi_score, roi_status, roi_category = 0, "Low", "bad"
        else:
            roi_score, roi_status, roi_category = 0, "N/A", "missing"
        
        margin_valid = check_data_valid(net_margin)
        if margin_valid:
            if net_margin > 20: margin_score, margin_status, margin_category = 10, "Excellent", "good"
            elif net_margin > 15: margin_score, margin_status, margin_category = 7, "Good", "good"
            elif net_margin > 10: margin_score, margin_status, margin_category = 4, "Fair", "neutral"
            else: margin_score, margin_status, margin_category = 0, "Low", "bad"
        else:
            margin_score, margin_status, margin_category = 0, "N/A", "missing"
        
        peg_valid = check_data_valid(peg) and peg > 0
        if peg_valid:
            if peg < 0.8: peg_score, peg_status, peg_category = 12, "Undervalued", "good"
            elif peg < 1.0: peg_score, peg_status, peg_category = 10, "Fair-Low", "good"
            elif peg < 1.2: peg_score, peg_status, peg_category = 7, "Fair", "neutral"
            elif peg < 1.5: peg_score, peg_status, peg_category = 4, "High", "bad"
            else: peg_score, peg_status, peg_category = 0, "Overvalued", "bad"
        else:
            peg_score, peg_status, peg_category = 0, "N/A", "missing"
        
        pe_valid = check_data_valid(pe) and pe > 0
        if pe_valid:
            if pe < 15: pe_score, pe_status, pe_category = 8, "Low", "good"
            elif pe < 20: pe_score, pe_status, pe_category = 6, "Fair", "good"
            elif pe < 25: pe_score, pe_status, pe_category = 4, "Slightly High", "neutral"
            elif pe < 30: pe_score, pe_status, pe_category = 2, "High", "bad"
            else: pe_score, pe_status, pe_category = 0, "Overvalued", "bad"
        else:
            pe_score, pe_status, pe_category = 0, "N/A", "missing"
        
        curr_valid = check_data_valid(curr)
        if curr_valid:
            if curr > 2.0: curr_score, curr_status, curr_category = 10, "Very Safe", "good"
            elif curr > 1.5: curr_score, curr_status, curr_category = 7, "Safe", "good"
            elif curr > 1.2: curr_score, curr_status, curr_category = 4, "Adequate", "neutral"
            elif curr > 1.0: curr_score, curr_status, curr_category = 2, "Marginal", "bad"
            else: curr_score, curr_status, curr_category = 0, "Risk", "bad"
        else:
            curr_score, curr_status, curr_category = 0, "N/A", "missing"
        
        quick_valid = check_data_valid(quick)
        if quick_valid:
            if quick > 1.5: quick_score, quick_status, quick_category = 8, "Very Safe", "good"
            elif quick > 1.0: quick_score, quick_status, quick_category = 5, "Safe", "good"
            elif quick > 0.8: quick_score, quick_status, quick_category = 3, "Adequate", "neutral"
            else: quick_score, quick_status, quick_category = 0, "Risk", "bad"
        else:
            quick_score, quick_status, quick_category = 0, "N/A", "missing"
        
        if mkt_cap > 100: cap_score, cap_status, cap_category = 7, "Large Cap", "good"
        elif mkt_cap > 50: cap_score, cap_status, cap_category = 5, "Mid-Large Cap", "good"
        elif mkt_cap > 10: cap_score, cap_status, cap_category = 3, "Mid Cap", "neutral"
        else: cap_score, cap_status, cap_category = 1, "Small Cap", "bad"
        
        if obv_trend == "Accumulating": obv_score, obv_status, obv_category = 10, "Inflow", "good"
        elif obv_trend == "Sideways": obv_score, obv_status, obv_category = 5, "Flat", "neutral"
        elif obv_trend == "Distributing": obv_score, obv_status, obv_category = 0, "Outflow", "bad"
        else: obv_score, obv_status, obv_category = 5, "N/A", "neutral"
        
        revenue_valid = check_data_valid(revenue_growth)
        if revenue_valid:
            if revenue_growth > 20: revenue_score, revenue_status, revenue_category = 5, "High Growth", "good"
            elif revenue_growth > 10: revenue_score, revenue_status, revenue_category = 3, "Steady Growth", "good"
            elif revenue_growth > 5: revenue_score, revenue_status, revenue_category = 1, "Moderate", "neutral"
            else: revenue_score, revenue_status, revenue_category = 0, "Stagnant", "bad"
        else:
            revenue_score, revenue_status, revenue_category = 0, "N/A", "missing"
        
        earnings_valid = check_data_valid(earnings_growth)
        if earnings_valid:
            if earnings_growth > 25: earnings_score, earnings_status, earnings_category = 5, "High Growth", "good"
            elif earnings_growth > 15: earnings_score, earnings_status, earnings_category = 3, "Steady Growth", "good"
            elif earnings_growth > 5: earnings_score, earnings_status, earnings_category = 1, "Moderate", "neutral"
            else: earnings_score, earnings_status, earnings_category = 0, "Stagnant", "bad"
        else:
            earnings_score, earnings_status, earnings_category = 0, "N/A", "missing"
        
        max_scores = {'roe': 15, 'roi': 10, 'margin': 10, 'peg': 12, 'pe': 8,
                      'curr': 10, 'quick': 8, 'cap': 7, 'obv': 10, 'revenue': 5, 'earnings': 5}
        actual_scores = {'roe': roe_score, 'roi': roi_score, 'margin': margin_score,
                         'peg': peg_score, 'pe': pe_score, 'curr': curr_score, 'quick': quick_score,
                         'cap': cap_score, 'obv': obv_score, 'revenue': revenue_score, 'earnings': earnings_score}
        valid_flags = {'roe': roe_valid, 'roi': roi_valid, 'margin': margin_valid, 'peg': peg_valid,
                       'pe': pe_valid, 'curr': curr_valid, 'quick': quick_valid, 'cap': True,
                       'obv': True, 'revenue': revenue_valid, 'earnings': earnings_valid}
        
        total_max_possible = sum(max_scores[k] for k in max_scores if valid_flags[k])
        total_actual_score = sum(actual_scores[k] for k in max_scores if valid_flags[k])
        final_score = round((total_actual_score / total_max_possible) * 100) if total_max_possible > 0 else 0
        
        good_items, neutral_items, bad_items = [], [], []
        
        if roe_category == "good": good_items.append(f"ROE: {roe:.2f}% ({roe_status})")
        elif roe_category == "neutral": neutral_items.append(f"ROE: {roe:.2f}% ({roe_status})")
        elif roe_category == "bad": bad_items.append(f"ROE: {roe:.2f}% ({roe_status})")
        
        if roi_category == "good": good_items.append(f"ROI: {roi:.2f}% ({roi_status})")
        elif roi_category == "neutral": neutral_items.append(f"ROI: {roi:.2f}% ({roi_status})")
        elif roi_category == "bad": bad_items.append(f"ROI: {roi:.2f}% ({roi_status})")
        
        if margin_category == "good": good_items.append(f"Net Margin: {net_margin:.2f}% ({margin_status})")
        elif margin_category == "neutral": neutral_items.append(f"Net Margin: {net_margin:.2f}% ({margin_status})")
        elif margin_category == "bad": bad_items.append(f"Net Margin: {net_margin:.2f}% ({margin_status})")
        
        if peg_category == "good": good_items.append(f"PEG: {peg:.2f} ({peg_status})")
        elif peg_category == "neutral": neutral_items.append(f"PEG: {peg:.2f} ({peg_status})")
        elif peg_category == "bad": bad_items.append(f"PEG: {peg:.2f} ({peg_status})")
        
        if pe_category == "good": good_items.append(f"P/E: {pe:.1f} ({pe_status})")
        elif pe_category == "neutral": neutral_items.append(f"P/E: {pe:.1f} ({pe_status})")
        elif pe_category == "bad": bad_items.append(f"P/E: {pe:.1f} ({pe_status})")
        
        if curr_category == "good": good_items.append(f"Current Ratio: {curr:.2f} ({curr_status})")
        elif curr_category == "neutral": neutral_items.append(f"Current Ratio: {curr:.2f} ({curr_status})")
        elif curr_category == "bad": bad_items.append(f"Current Ratio: {curr:.2f} ({curr_status})")
        
        if quick_category == "good": good_items.append(f"Quick Ratio: {quick:.2f} ({quick_status})")
        elif quick_category == "neutral": neutral_items.append(f"Quick Ratio: {quick:.2f} ({quick_status})")
        elif quick_category == "bad": bad_items.append(f"Quick Ratio: {quick:.2f} ({quick_status})")
        
        good_items.append(f"Market Cap: ${mkt_cap:.1f}B ({cap_status})")
        
        if obv_category == "good": good_items.append(f"OBV: {obv_trend} ({obv_status})")
        elif obv_category == "neutral": neutral_items.append(f"OBV: {obv_trend} ({obv_status})")
        else: bad_items.append(f"OBV: {obv_trend} ({obv_status})")
        
        if revenue_category == "good": good_items.append(f"Revenue Growth: {revenue_growth:.1f}% ({revenue_status})")
        elif revenue_category == "neutral": neutral_items.append(f"Revenue Growth: {revenue_growth:.1f}% ({revenue_status})")
        elif revenue_category == "bad": bad_items.append(f"Revenue Growth: {revenue_growth:.1f}% ({revenue_status})")
        
        if earnings_category == "good": good_items.append(f"Earnings Growth: {earnings_growth:.1f}% ({earnings_status})")
        elif earnings_category == "neutral": neutral_items.append(f"Earnings Growth: {earnings_growth:.1f}% ({earnings_status})")
        elif earnings_category == "bad": bad_items.append(f"Earnings Growth: {earnings_growth:.1f}% ({earnings_status})")
        
        return {
            "代號": ticker.upper(),
            "名稱": info.get('shortName', 'N/A'),
            "板塊": info.get('sector', 'N/A'),
            "行業": info.get('industry', 'N/A'),
            "綜合分數": final_score,
            "評級": get_score_rating(final_score),
            "圖示": get_score_icon(final_score),
            "市值(B)": round(mkt_cap, 2),
            "本益比": round(pe, 2) if pe > 0 else 0,
            "PEG": round(peg, 2),
            "ROE": f"{roe:.2f}%",
            "ROI": f"{roi:.2f}%",
            "淨利率": f"{net_margin:.2f}%",
            "流動比率": round(curr, 2),
            "速動比率": round(quick, 2),
            "營收成長": f"{revenue_growth:.1f}%",
            "盈利成長": f"{earnings_growth:.1f}%",
            "OBV走勢": obv_trend,
            "good_items": good_items,
            "neutral_items": neutral_items,
            "bad_items": bad_items,
            "顏色": get_score_color(final_score),
            "SMA150": sma_150_value
        }
    except Exception as e:
        return None

def calculate_obv_trend(ticker):
    try:
        df = get_history_data(ticker, "3mo")
        if len(df) < 10:
            df = get_history_data(ticker, "6mo")
        if len(df) < 10:
            df = get_history_data(ticker, "1y")
        if len(df) < 10:
            return "Insufficient Data"
        obv = [0]
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                obv.append(obv[-1] + df['Volume'].iloc[i])
            elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                obv.append(obv[-1] - df['Volume'].iloc[i])
            else:
                obv.append(obv[-1])
        obv_series = pd.Series(obv)
        if len(obv_series) < 10:
            return "Insufficient Data"
        recent_obv = obv_series.iloc[-5:].mean()
        prev_obv = obv_series.iloc[-10:-5].mean()
        if prev_obv == 0:
            return "Sideways"
        if recent_obv > prev_obv * 1.03:
            return "Accumulating"
        elif recent_obv < prev_obv * 0.97:
            return "Distributing"
        else:
            return "Sideways"
    except Exception:
        return "Unavailable"

def get_score_color(score):
    if score >= 85: return '#006400'
    elif score >= 70: return '#228B22'
    elif score >= 55: return '#FFA500'
    elif score >= 40: return '#FF8C00'
    else: return '#FF4B4B'

def get_score_icon(score):
    if score >= 70: return "🟢"
    elif score >= 55: return "🟡"
    else: return "🔴"

def get_score_rating(score):
    if score >= 85: return "Excellent"
    elif score >= 70: return "Good"
    elif score >= 55: return "Fair"
    elif score >= 40: return "Watch"
    else: return "Poor"

def check_data_valid(value):
    if value is None: return False
    if isinstance(value, (int, float)): return value != 0
    return True

# 技术指标函数
def calculate_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(close_prices, fast=12, slow=26, signal=9):
    exp1 = close_prices.ewm(span=fast, adjust=False).mean()
    exp2 = close_prices.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_dmi(high, low, close, period=14):
    try:
        high_shift = high.shift(1)
        low_shift = low.shift(1)
        close_shift = close.shift(1)
        tr1 = high - low
        tr2 = abs(high - close_shift)
        tr3 = abs(low - close_shift)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_temp = tr.rolling(window=period).mean()
        up_move = high - high_shift
        down_move = low_shift - low
        plus_dm = pd.Series(0, index=high.index)
        minus_dm = pd.Series(0, index=high.index)
        plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
        minus_dm[(down_move > up_move) & (down_move > 0)] = down_move
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr_temp)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr_temp)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx, plus_di, minus_di, atr_temp
    except Exception:
        default_series = pd.Series([20] * len(high), index=high.index)
        return default_series, default_series, default_series, default_series

def calculate_rvol(volume, period=20):
    avg_volume = volume.rolling(window=period).mean()
    rvol = volume / avg_volume
    return rvol

def calculate_cci(high, low, close, period=20):
    try:
        tp = (high + low + close) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - sma) / (0.015 * mad)
        return cci
    except Exception:
        return pd.Series([0] * len(high), index=high.index)

def calculate_atr(high, low, close, period=14):
    try:
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    except Exception:
        return pd.Series([0] * len(high), index=high.index)

# 保力加通道
def calculate_bollinger_bands(close_prices, period=20, std_dev=2):
    sma = close_prices.rolling(window=period).mean()
    std = close_prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

def calculate_bb_width(upper_band, lower_band, sma):
    width = (upper_band - lower_band) / sma * 100
    return width

def get_bb_slope(bb_series, periods=5):
    if len(bb_series) < periods:
        return 0
    slope = (bb_series.iloc[-1] - bb_series.iloc[-periods]) / bb_series.iloc[-periods] * 100
    return slope

def calculate_bb_score(close_price, upper_band, lower_band, sma, bb_width_history, upper_band_series, lower_band_series):
    current_width = calculate_bb_width(upper_band, lower_band, sma)
    avg_width = bb_width_history.mean() if len(bb_width_history) > 20 else current_width
    width_ratio = current_width / avg_width if avg_width > 0 else 1
    upper_slope = get_bb_slope(upper_band_series, 5)
    lower_slope = get_bb_slope(lower_band_series, 5)
    bb_score = 0
    bb_status = ""
    bb_signal = ""
    if close_price > upper_band and upper_slope > 0:
        bb_score = 10
        bb_status = "強勢突破 + 通道擴張"
        bb_signal = "強烈多頭 - 趨勢延續"
        if width_ratio < 0.5:
            bb_status += " + 擠壓突破信號"
    elif close_price > upper_band:
        bb_score = 8
        bb_status = "突破但通道收縮"
        bb_signal = "注意假突破 - 確認成交量"
    elif close_price > sma and close_price <= upper_band:
        bb_score = 7
        bb_status = "多頭區間運行"
        bb_signal = "偏多 - 持有"
    elif abs(close_price - sma) / sma * 100 < 1:
        bb_score = 5
        bb_status = "中軌附近"
        bb_signal = "方向不明 - 等待"
    elif close_price < sma and close_price >= lower_band:
        bb_score = 3
        bb_status = "空頭區間運行"
        bb_signal = "偏空 - 觀望"
    elif close_price < lower_band and lower_slope < 0:
        bb_score = 1
        bb_status = "強勢跌破 + 通道擴張"
        bb_signal = "超賣 - 等待反彈確認"
    elif close_price < lower_band:
        bb_score = 2
        bb_status = "跌破下軌"
        bb_signal = "超賣反彈機會"
    else:
        bb_score = 5
        bb_status = "其他"
        bb_signal = "正常波動"
    return bb_score, bb_status, bb_signal, current_width, width_ratio

# 量化交易评分函数
def calculate_trading_score(rsi_series, macd_line_series, signal_line_series, adx_value, 
                           plus_di_value, minus_di_value, rvol_value, close_prices, 
                           macd_hist_series, cci_series=None, 
                           bb_upper_series=None, bb_lower_series=None, bb_sma_series=None,
                           bb_width_history=None,
                           sma_150_value=None, current_price=None):
    score = 0
    details = {}
    if isinstance(rsi_series, pd.Series) and not rsi_series.empty:
        rsi_value = rsi_series.iloc[-1]
    else:
        rsi_value = 50
    if isinstance(macd_line_series, pd.Series) and not macd_line_series.empty:
        macd_line = macd_line_series.iloc[-1]
    else:
        macd_line = 0
    if isinstance(signal_line_series, pd.Series) and not signal_line_series.empty:
        signal_line = signal_line_series.iloc[-1]
    else:
        signal_line = 0
    if cci_series is not None and isinstance(cci_series, pd.Series) and not cci_series.empty:
        cci_value = cci_series.iloc[-1]
    else:
        cci_value = 0
    # DMI (25分)
    if adx_value >= 25 and plus_di_value > minus_di_value:
        dmi_score = 25
        dmi_status = "Strong Uptrend (+DI > -DI, ADX>=25)"
    elif adx_value >= 25 and minus_di_value > plus_di_value:
        dmi_score = 0
        dmi_status = "Strong Downtrend (-DI > +DI, ADX>=25)"
    elif 20 <= adx_value < 25 and plus_di_value > minus_di_value:
        dmi_score = 18
        dmi_status = "Weak Uptrend (+DI > -DI, 20<=ADX<25)"
    elif adx_value < 20:
        dmi_score = 8
        dmi_status = "Range Bound / No Trend (ADX<20)"
    else:
        dmi_score = 12
        dmi_status = "Neutral / Weak Trend"
    score += dmi_score
    details["DMI"] = {"score": dmi_score, "status": dmi_status, "adx": adx_value, 
                      "plus_di": plus_di_value, "minus_di": minus_di_value}
    # MACD (20分)
    if macd_line > signal_line and macd_line > 0 and signal_line > 0:
        macd_score = 20
        macd_status = "Bullish Strong (Above Zero, Golden Cross)"
    elif macd_line > signal_line:
        macd_score = 15
        macd_status = "Bullish (Golden Cross)"
    elif macd_line < signal_line:
        macd_score = 3
        macd_status = "Bearish (Death Cross)"
    else:
        macd_score = 8
        macd_status = "Neutral / Sideways"
    if isinstance(close_prices, pd.Series) and len(close_prices) >= 20 and isinstance(macd_line_series, pd.Series) and len(macd_line_series) >= 20:
        recent_close = close_prices.tail(20)
        recent_macd = macd_line_series.tail(20)
        price_lows = recent_close.rolling(5).min()
        macd_lows = recent_macd.rolling(5).min()
        if len(price_lows) >= 5 and len(macd_lows) >= 5:
            if price_lows.iloc[-1] < price_lows.iloc[-5] and macd_lows.iloc[-1] > macd_lows.iloc[-5]:
                macd_score += 5
                macd_status += " + Bottom Divergence"
            elif price_lows.iloc[-1] > price_lows.iloc[-5] and macd_lows.iloc[-1] < macd_lows.iloc[-5]:
                macd_score -= 5
                macd_status += " + Top Divergence"
    score += macd_score
    details["MACD"] = {"score": macd_score, "status": macd_status, 
                       "macd_line": macd_line, "signal_line": signal_line}
    # RVOL (15分)
    if rvol_value >= 2.0:
        rvol_score = 15
        rvol_status = f"Significant Volume Surge ({rvol_value:.2f}x >= 2.0)"
    elif 1.5 <= rvol_value < 2.0:
        rvol_score = 12
        rvol_status = f"Moderate Volume Increase ({rvol_value:.2f}x)"
    elif 0.8 < rvol_value < 1.5:
        rvol_score = 7
        rvol_status = f"Normal Volume ({rvol_value:.2f}x)"
    elif rvol_value <= 0.5:
        rvol_score = 0
        rvol_status = f"Significant Volume Contraction ({rvol_value:.2f}x <= 0.5)"
    else:
        rvol_score = 3
        rvol_status = f"Below Average Volume ({rvol_value:.2f}x)"
    score += rvol_score
    details["RVOL"] = {"score": rvol_score, "status": rvol_status, "rvol": rvol_value}
    # RSI (10分)
    if 40 <= rsi_value <= 60:
        rsi_score = 10
        rsi_status = "Neutral Zone"
    elif rsi_value > 70:
        rsi_score = 3
        rsi_status = f"Overbought ({rsi_value:.1f}>70)"
    elif rsi_value < 30:
        rsi_score = 3
        rsi_status = f"Oversold ({rsi_value:.1f}<30)"
    else:
        rsi_score = 6
        rsi_status = "Slightly Extended"
    # CCI (10分)
    if -100 <= cci_value <= 100:
        cci_score = 10
        cci_status = f"Neutral Zone ({cci_value:.1f})"
    elif cci_value > 200:
        cci_score = 2
        cci_status = f"Strongly Overbought ({cci_value:.1f}>200)"
    elif cci_value > 100:
        cci_score = 5
        cci_status = f"Overbought ({cci_value:.1f}>100)"
    elif cci_value < -200:
        cci_score = 2
        cci_status = f"Strongly Oversold ({cci_value:.1f}<-200)"
    elif cci_value < -100:
        cci_score = 5
        cci_status = f"Oversold ({cci_value:.1f}<-100)"
    else:
        cci_score = 7
        cci_status = f"Near Extreme ({cci_value:.1f})"
    divergence_bonus = 0
    if isinstance(close_prices, pd.Series) and len(close_prices) >= 20 and isinstance(rsi_series, pd.Series) and len(rsi_series) >= 20:
        recent_close_rsi = close_prices.tail(20)
        recent_rsi = rsi_series.tail(20)
        if len(recent_close_rsi) >= 10 and len(recent_rsi) >= 10:
            if recent_close_rsi.min() < recent_close_rsi.iloc[-10] and recent_rsi.min() > recent_rsi.iloc[-10]:
                rsi_score = 10
                rsi_status = "Bullish Divergence + Reversal"
                divergence_bonus = 5
            elif recent_close_rsi.max() > recent_close_rsi.iloc[-10] and recent_rsi.max() < recent_rsi.iloc[-10]:
                rsi_score = 0
                rsi_status = "Bearish Divergence"
    if cci_series is not None and isinstance(cci_series, pd.Series) and len(cci_series) >= 20:
        recent_cci = cci_series.tail(20)
        recent_close_cci = close_prices.tail(20)
        if len(recent_close_cci) >= 10 and len(recent_cci) >= 10:
            if recent_close_cci.min() < recent_close_cci.iloc[-10] and recent_cci.min() > recent_cci.iloc[-10]:
                if divergence_bonus == 0:
                    divergence_bonus = 5
                cci_score = 10
                cci_status = "Bullish Divergence + Reversal"
            elif recent_close_cci.max() > recent_close_cci.iloc[-10] and recent_cci.max() < recent_cci.iloc[-10]:
                cci_score = 0
                cci_status = "Bearish Divergence"
    score += rsi_score + cci_score + divergence_bonus
    details["RSI"] = {"score": rsi_score, "status": rsi_status, "rsi": rsi_value}
    details["CCI"] = {"score": cci_score, "status": cci_status, "cci": cci_value}
    details["Divergence"] = {"bonus": divergence_bonus}
    # SMA150 (10分)
    sma150_score = 0
    sma150_status = ""
    price_vs_sma = 0
    if sma_150_value and current_price and sma_150_value > 0:
        price_vs_sma = (current_price - sma_150_value) / sma_150_value * 100
        if current_price > sma_150_value:
            if price_vs_sma > 30:
                sma150_score = 10
                sma150_status = f"強勢多頭 (高於150天線 {price_vs_sma:.1f}%)"
            elif price_vs_sma > 15:
                sma150_score = 9
                sma150_status = f"健康多頭 (高於150天線 {price_vs_sma:.1f}%)"
            elif price_vs_sma > 5:
                sma150_score = 7
                sma150_status = f"初步多頭 (高於150天線 {price_vs_sma:.1f}%)"
            else:
                sma150_score = 5
                sma150_status = f"貼近150天線上方 (高於 {price_vs_sma:.1f}%)"
        else:
            if price_vs_sma < -30:
                sma150_score = 0
                sma150_status = f"深度空頭 (低於150天線 {abs(price_vs_sma):.1f}%)"
            elif price_vs_sma < -15:
                sma150_score = 1
                sma150_status = f"空頭趨勢 (低於150天線 {abs(price_vs_sma):.1f}%)"
            elif price_vs_sma < -5:
                sma150_score = 3
                sma150_status = f"弱勢整理 (低於150天線 {abs(price_vs_sma):.1f}%)"
            else:
                sma150_score = 4
                sma150_status = f"貼近150天線下方 (低於 {abs(price_vs_sma):.1f}%)"
    else:
        sma150_score = 5
        sma150_status = "數據不足 (需150天數據)"
    score += sma150_score
    details["SMA150"] = {"score": sma150_score, "status": sma150_status, 
                         "value": sma_150_value, "diff_pct": price_vs_sma if sma_150_value else None}
    # BB (10分)
    bb_score = 0
    bb_status = ""
    bb_signal = ""
    if (bb_upper_series is not None and not bb_upper_series.empty and 
        bb_lower_series is not None and not bb_lower_series.empty and
        bb_sma_series is not None and not bb_sma_series.empty and
        close_prices is not None and not close_prices.empty):
        current_close = close_prices.iloc[-1]
        current_upper = bb_upper_series.iloc[-1]
        current_lower = bb_lower_series.iloc[-1]
        current_sma = bb_sma_series.iloc[-1]
        bb_score, bb_status, bb_signal, bb_width, bb_width_ratio = calculate_bb_score(
            current_close, current_upper, current_lower, current_sma,
            bb_width_history, bb_upper_series, bb_lower_series
        )
        score += bb_score
        details["BB"] = {
            "score": bb_score,
            "status": bb_status,
            "signal": bb_signal,
            "width": bb_width,
            "width_ratio": bb_width_ratio,
            "upper": current_upper,
            "lower": current_lower,
            "middle": current_sma
        }
    else:
        details["BB"] = {"score": 0, "status": "數據不足", "signal": "無法計算"}
    total_score = score
    if total_score >= 90:
        recommendation = "強烈建議買入 / Strong Buy"
        rec_color = "#006400"
        rec_action = "Strongly Recommended to Buy - All indicators resonate perfectly"
    elif total_score >= 80:
        recommendation = "建議買入 / Buy"
        rec_color = "#228B22"
        rec_action = "Recommended to Buy - Bullish bias across multiple indicators"
    elif total_score >= 70:
        recommendation = "偏多 - 持有 / Bullish - Hold"
        rec_color = "#9ACD32"
        rec_action = "Bullish bias - Hold position, monitor for confirmation"
    elif total_score >= 60:
        recommendation = "觀察/等待（偏多）/ Watch (Bullish)"
        rec_color = "#FFD700"
        rec_action = "Watch / Wait (Bullish bias) - Incomplete signals"
    elif total_score >= 50:
        recommendation = "沒有明顯訊號 / No Clear Signal"
        rec_color = "#FFA500"
        rec_action = "No Clear Signal - Balanced or range-bound"
    elif total_score >= 40:
        recommendation = "觀察/等待（偏空）/ Watch (Bearish)"
        rec_color = "#FF8C00"
        rec_action = "Watch / Wait (Bearish bias) - Slight weakening"
    elif total_score >= 30:
        recommendation = "偏空 - 觀望 / Bearish - Wait"
        rec_color = "#FF6347"
        rec_action = "Bearish bias - Wait for reversal"
    elif total_score >= 20:
        recommendation = "建議賣出 / Sell"
        rec_color = "#FF4B4B"
        rec_action = "Recommended to Sell - Multiple bearish signals"
    elif total_score >= 10:
        recommendation = "強烈建議賣出 / Strong Sell"
        rec_color = "#8B0000"
        rec_action = "Strongly Recommended to Sell - Bearish breakdown"
    else:
        recommendation = "強制停損/清倉 / Force Stop Loss"
        rec_color = "#FF0000"
        rec_action = "Force Stop Loss / Liquidate - Extreme bearish condition"
    details["Total"] = {
        "score": total_score, 
        "recommendation": recommendation, 
        "rec_color": rec_color, 
        "rec_action": rec_action,
        "breakdown": {
            "DMI": dmi_score,
            "MACD": macd_score,
            "RVOL": rvol_score,
            "RSI": rsi_score,
            "CCI": cci_score,
            "SMA150": sma150_score,
            "BB": bb_score
        }
    }
    return total_score, recommendation, rec_color, rec_action, details

def calculate_trading_plan(current_price, atr_value, position_type="long"):
    if atr_value <= 0 or current_price <= 0:
        return None
    atr_pct = (atr_value / current_price) * 100
    stop_loss = current_price - (2 * atr_value)
    risk_per_share = current_price - stop_loss
    risk_pct = (risk_per_share / current_price) * 100
    take_profit_2r = current_price + (risk_per_share * 2)
    take_profit_3r = current_price + (risk_per_share * 3)
    trailing_stop = current_price - (1.5 * atr_value)
    trigger_price = current_price + (risk_per_share * 1.5)
    reward_2r = int(round((take_profit_2r - current_price) / risk_per_share, 0))
    reward_3r = int(round((take_profit_3r - current_price) / risk_per_share, 0))
    return {
        "current_price": round(current_price, 2),
        "atr_value": round(atr_value, 2),
        "atr_percentage": round(atr_pct, 2),
        "stop_loss": round(stop_loss, 2),
        "risk_per_share": round(risk_per_share, 2),
        "risk_percentage": round(risk_pct, 2),
        "take_profit_2r": round(take_profit_2r, 2),
        "take_profit_3r": round(take_profit_3r, 2),
        "reward_2r_ratio": f"1:{reward_2r}",
        "reward_3r_ratio": f"1:{reward_3r}",
        "trailing_stop": round(trailing_stop, 2),
        "trigger_price": round(trigger_price, 2),
        "trailing_advice": f"建議當股價上漲超過 ${round(risk_per_share * 1.5, 2)} (1.5倍風險) 至 ${round(trigger_price, 2)} 後啟動移動止蝕 @ ${round(trailing_stop, 2)}"
    }

def display_trading_plan_card_streamlit(plan):
    if not plan:
        return
    st.markdown("""
    <style>
    .atr-card-metrics div[data-testid="stMetricLabel"] { font-size: 16px !important; font-weight: 600 !important; }
    .atr-card-metrics div[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; }
    .atr-card-metrics div[data-testid="stMetricDelta"] { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); border-radius: 15px; padding: 5px 20px 15px 20px; margin: 15px 0 20px 0; border-left: 5px solid #1a365d; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="padding: 5px 0;">
            <div style="font-size: 28px; font-weight: 800; margin: 0 0 5px 0; color: #1a365d; border-bottom: 2px solid #3182ce; display: inline-block;">
                📐 ATR 黃金法則交易計劃 
                <span style="font-size: 16px; font-weight: normal; color: #4a5568; margin-left: 10px;">ATR Golden Rule Trading Plan</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="atr-card-metrics">', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(label="📊 入市價", value=f"${plan['current_price']}", help="建議買入價格")
        with col2:
            st.metric(label="🛑 止蝕位", value=f"${plan['stop_loss']}", delta=f"-{plan['risk_percentage']}%", delta_color="inverse")
        with col3:
            risk_emoji = "🔴" if plan['risk_percentage'] > 10 else ("🟠" if plan['risk_percentage'] > 5 else "🟢")
            st.metric(label=f"{risk_emoji} 風險", value=f"${plan['risk_per_share']}", delta=f"({plan['risk_percentage']}%)")
        with col4:
            target_2r_pct = ((plan['take_profit_2r'] - plan['current_price']) / plan['current_price']) * 100
            st.metric(label="🎯 目標① (1:2)", value=f"${plan['take_profit_2r']}", delta=f"+{target_2r_pct:.1f}%", help=f"風險回報比 {plan['reward_2r_ratio']}")
        with col5:
            target_3r_pct = ((plan['take_profit_3r'] - plan['current_price']) / plan['current_price']) * 100
            st.metric(label="🎯 目標② (1:3)", value=f"${plan['take_profit_3r']}", delta=f"+{target_3r_pct:.1f}%", help=f"風險回報比 {plan['reward_3r_ratio']}")
        st.markdown('</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
        <div style="background: #e6f3ff; border-radius: 10px; padding: 12px; text-align: center;">
            <span style="font-size: 16px; font-weight: bold;">📐 ATR 值</span><br>
            <span style="font-size: 26px; font-weight: 800; color: #1a365d;">${plan['atr_value']}</span>
            <span style="font-size: 15px;"> ({plan['atr_percentage']}%)</span>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div style="background: #e6ffe6; border-radius: 10px; padding: 12px; text-align: center;">
            <span style="font-size: 16px; font-weight: bold;">📈 風險回報比 (1:2)</span><br>
            <span style="font-size: 30px; font-weight: 800; color: #228B22;">{plan['reward_2r_ratio']}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div style="background: #e6ffe6; border-radius: 10px; padding: 12px; text-align: center;">
            <span style="font-size: 16px; font-weight: bold;">📈 風險回報比 (1:3)</span><br>
            <span style="font-size: 30px; font-weight: 800; color: #228B22;">{plan['reward_3r_ratio']}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: #fff3e0; border-radius: 10px; padding: 15px; margin-top: 15px; border-left: 5px solid #FFA500;">
        <div style="font-size: 16px; font-weight: bold; color: #FF8C00; margin-bottom: 8px;">🏃 移動止蝕建議 / Trailing Stop Advice</div>
        <div style="font-size: 15px; color: #333;">{plan['trailing_advice']}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 12px; color: #888; text-align: center; margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd;">
        ⚠️ 黃金法則：止蝕 = 2×ATR | 目標 = 風險 × (2 或 3) | 風險回報比 ≥ 1:2
    </div>
    """, unsafe_allow_html=True)

# 历史数据获取函数
@st.cache_data(ttl=300, show_spinner=False)
def get_history_data(ticker: str, period: str) -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, auto_adjust=False, timeout=30)
        if len(hist) < 20:
            if period == "3mo":
                hist = stock.history(period="6mo", auto_adjust=False, timeout=30)
                if len(hist) > 90:
                    hist = hist.tail(90)
            elif period == "6mo":
                hist = stock.history(period="1y", auto_adjust=False, timeout=30)
                if len(hist) > 180:
                    hist = hist.tail(180)
            elif period == "1y":
                hist = stock.history(period="2y", auto_adjust=False, timeout=30)
                if len(hist) > 365:
                    hist = hist.tail(365)
        return hist
    except Exception as e:
        print(f"History error: {e}")
        return pd.DataFrame()

# 图表生成函数
def create_candlestick_chart(ticker: str, period: str = "1y") -> Optional[bytes]:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        from matplotlib.dates import date2num, DateFormatter
        hist = get_history_data(ticker, period)
        if hist.empty or len(hist) < 5:
            return None
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        dates = date2num(hist.index)
        width = 0.6 * (dates[1] - dates[0]) if len(dates) > 1 else 0.6
        for i, (idx, row) in enumerate(hist.iterrows()):
            if row['Close'] >= row['Open']:
                color = 'green'
                body_bottom = row['Open']
                body_height = row['Close'] - row['Open']
            else:
                color = 'red'
                body_bottom = row['Close']
                body_height = row['Open'] - row['Close']
            ax1.plot([dates[i], dates[i]], [row['Low'], row['High']], color=color, linewidth=1)
            if body_height > 0:
                rect = Rectangle((dates[i] - width/2, body_bottom), width, body_height, facecolor=color, alpha=0.8, edgecolor=color)
                ax1.add_patch(rect)
        if period == "1y" and len(hist) >= 150:
            sma150 = hist['Close'].rolling(window=150).mean()
            sma150_dates = date2num(sma150.dropna().index)
            sma150_values = sma150.dropna().values
            if len(sma150_values) > 0:
                ax1.plot(sma150_dates, sma150_values, color='orange', linewidth=2, label='SMA150')
                ax1.legend(loc='best')
                current_price = hist['Close'].iloc[-1]
                current_sma150 = sma150.iloc[-1] if not pd.isna(sma150.iloc[-1]) else None
                if current_sma150 and not pd.isna(current_sma150):
                    diff_pct = ((current_price - current_sma150) / current_sma150) * 100
                    title_text = f'{ticker} - Candlestick Chart (SMA150: {diff_pct:+.1f}%)'
                else:
                    title_text = f'{ticker} - Candlestick Chart'
            else:
                title_text = f'{ticker} - Candlestick Chart'
        else:
            title_text = f'{ticker} - Candlestick Chart'
        ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_tick_params(rotation=45)
        n_ticks = min(10, len(dates))
        tick_indices = np.linspace(0, len(dates)-1, n_ticks, dtype=int)
        ax1.set_xticks(dates[tick_indices])
        ax1.set_xticklabels([hist.index[i].strftime('%Y-%m-%d') for i in tick_indices], rotation=45, ha='right', fontsize=8)
        ax1.set_ylabel('Price (USD)')
        ax1.set_title(title_text)
        ax1.grid(True, alpha=0.3)
        colors_vol = ['green' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else 'red' for i in range(len(hist))]
        ax2.bar(dates, hist['Volume'], color=colors_vol, alpha=0.7, width=width)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        ax2.set_xticks(dates[tick_indices])
        ax2.set_xticklabels([hist.index[i].strftime('%Y-%m-%d') for i in tick_indices], rotation=45, ha='right', fontsize=8)
        ax2.grid(True, alpha=0.3)
        period_label = {"1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year"}.get(period, period)
        fig.suptitle(f'{ticker} - {period_label}', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"Candlestick Chart Error: {e}")
        return None

def create_bollinger_chart(hist):
    try:
        if hist.empty or len(hist) < 20:
            return None
        upper, sma, lower = calculate_bollinger_bands(hist['Close'])
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(hist.index, hist['Close'], label='Close Price', color='black', linewidth=1)
        ax.plot(hist.index, upper, label='Upper Band (+2σ)', color='red', linewidth=1, linestyle='--')
        ax.plot(hist.index, sma, label='SMA(20)', color='blue', linewidth=1.5)
        ax.plot(hist.index, lower, label='Lower Band (-2σ)', color='green', linewidth=1, linestyle='--')
        ax.fill_between(hist.index, upper, lower, alpha=0.1, color='gray')
        ax.set_title('Bollinger Bands (20,2)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price (USD)')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"Bollinger Chart Error: {e}")
        return None

def create_dmi_chart(hist):
    try:
        if hist.empty or len(hist) < 20:
            return None
        adx, plus_di, minus_di, _ = calculate_dmi(hist['High'], hist['Low'], hist['Close'])
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(hist.index, plus_di, label='+DI (Bullish)', color='#228B22', linewidth=1.5)
        ax.plot(hist.index, minus_di, label='-DI (Bearish)', color='#FF4B4B', linewidth=1.5)
        ax.plot(hist.index, adx, label='ADX (Trend Strength)', color='#1a365d', linewidth=2)
        ax.axhline(y=25, color='#FFA500', linestyle='--', alpha=0.7, label='ADX=25 (Trend Threshold)')
        ax.axhline(y=20, color='gray', linestyle='--', alpha=0.5, label='ADX=20 (Range Threshold)')
        ax.set_title('DMI - Directional Movement Index', fontsize=12, fontweight='bold')
        ax.set_ylabel('Value')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"DMI Chart Error: {e}")
        return None

def create_volume_rvol_chart(hist):
    try:
        if hist.empty or len(hist) < 20:
            return None
        rvol = calculate_rvol(hist['Volume'])
        fig, ax = plt.subplots(figsize=(12, 5))
        colors_vol = ['green' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else 'red' for i in range(len(hist))]
        ax.bar(hist.index, hist['Volume'], color=colors_vol, alpha=0.7, label='Volume')
        current_rvol = rvol.iloc[-1] if not rvol.empty else 1.0
        ax.text(0.02, 0.95, f'RVOL = {current_rvol:.2f}x', transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        ax.set_title('Volume with RVOL (Relative Volume)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Volume')
        ax.set_xlabel('Date')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"Volume Chart Error: {e}")
        return None

def create_rsi_chart(hist):
    try:
        if hist.empty or len(hist) < 20:
            return None
        rsi = calculate_rsi(hist['Close'])
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(hist.index, rsi, label='RSI (14)', color='#FFA500', linewidth=2)
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax.axhline(y=50, color='gray', linestyle=':', alpha=0.5, label='Neutral (50)')
        ax.fill_between(hist.index, rsi, 70, where=(rsi >= 70), color='red', alpha=0.3)
        ax.fill_between(hist.index, rsi, 30, where=(rsi <= 30), color='green', alpha=0.3)
        ax.set_title('RSI - Relative Strength Index', fontsize=12, fontweight='bold')
        ax.set_ylabel('RSI Value')
        ax.set_ylim(0, 100)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"RSI Chart Error: {e}")
        return None

def create_macd_chart(hist):
    try:
        if hist.empty or len(hist) < 30:
            return None
        macd_line, signal_line, histogram = calculate_macd(hist['Close'])
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(hist.index, macd_line, label='MACD Line', color='#228B22', linewidth=1.5)
        ax.plot(hist.index, signal_line, label='Signal Line', color='#FF4B4B', linewidth=1.5)
        colors_hist = ['green' if h >= 0 else 'red' for h in histogram]
        ax.bar(hist.index, histogram, color=colors_hist, alpha=0.5, label='Histogram')
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        ax.set_title('MACD - Moving Average Convergence Divergence', fontsize=12, fontweight='bold')
        ax.set_ylabel('MACD Value')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"MACD Chart Error: {e}")
        return None

def create_cci_chart(hist, period=20):
    try:
        if hist.empty or len(hist) < period:
            return None
        cci = calculate_cci(hist['High'], hist['Low'], hist['Close'], period)
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(hist.index, cci, label=f'CCI ({period})', color='#9B59B6', linewidth=2)
        ax.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='Overbought (+100)')
        ax.axhline(y=-100, color='green', linestyle='--', alpha=0.7, label='Oversold (-100)')
        ax.axhline(y=200, color='darkred', linestyle=':', alpha=0.5, label='Strong Overbought (+200)')
        ax.axhline(y=-200, color='darkgreen', linestyle=':', alpha=0.5, label='Strong Oversold (-200)')
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        ax.fill_between(hist.index, cci, 100, where=(cci >= 100), color='red', alpha=0.3)
        ax.fill_between(hist.index, cci, -100, where=(cci <= -100), color='green', alpha=0.3)
        ax.set_title(f'CCI - Commodity Channel Index ({period})', fontsize=12, fontweight='bold')
        ax.set_ylabel('CCI Value')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"CCI Chart Error: {e}")
        return None

# PDF 报告生成（简略版，实际使用时请保留完整函数）
def generate_pdf_report(ticker: str, data: Dict, peer_data: List[Dict], chart_img: bytes, period: str = "1y") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.3*inch, bottomMargin=0.3*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1a365d'), spaceAfter=12, spaceBefore=6, alignment=1)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2c5282'), spaceAfter=6, spaceBefore=6)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=9, spaceAfter=3, spaceBefore=3)
    period_label = {"1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year"}.get(period, "1 Year")
    report_date = datetime.now().strftime("%Y-%m-%d")
    story.append(Paragraph(f"Stock Analysis Report - {data['代號']}", title_style))
    story.append(Paragraph(f"Report Date: {report_date}", normal_style))
    story.append(Spacer(1, 0.1*inch))
    info_data = [
        ['Ticker', data['代號']], ['Company', data['名稱']], 
        ['Sector', data.get('板塊', 'N/A')], ['Industry', data.get('行業', 'N/A')], 
        ['Score', f"{data['綜合分數']}/100 - {data['評級']}"]
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
    info_table.setStyle(TableStyle([('BACKGROUND', (0,0), (0,-1), colors.HexColor('#e0f0ff')), ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTSIZE', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    story.append(info_table)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Key Financial Metrics", heading_style))
    financial_data = [
        ['Metric', 'Value'], ['Market Cap', f"${data['市值(B)']}B"], 
        ['P/E Ratio', str(data['本益比'])], ['PEG', str(data['PEG'])], 
        ['ROE', data['ROE']], ['ROI', data['ROI']], 
        ['Net Margin', data['淨利率']], ['Current Ratio', str(data['流動比率'])], 
        ['Quick Ratio', str(data['速動比率'])], ['Revenue Growth', data['營收成長']],
        ['Earnings Growth', data['盈利成長']], ['OBV Trend', data['OBV走勢']]
    ]
    fin_table = Table(financial_data, colWidths=[2*inch, 3*inch])
    fin_table.setStyle(TableStyle([('BACKGROUND', (0,0), (0,-1), colors.HexColor('#2c5282')), ('TEXTCOLOR', (0,0), (0,-1), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('FONTSIZE', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    story.append(fin_table)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Strengths & Weaknesses", heading_style))
    if data['good_items']:
        good_text = "<br/>".join(data['good_items'][:10])
        story.append(Paragraph(f"<b>Strengths:</b><br/>{good_text}", normal_style))
    if data['neutral_items']:
        neutral_text = "<br/>".join(data['neutral_items'][:10])
        story.append(Paragraph(f"<b>Neutral:</b><br/>{neutral_text}", normal_style))
    if data['bad_items']:
        bad_text = "<br/>".join(data['bad_items'][:10])
        story.append(Paragraph(f"<b>Weaknesses:</b><br/>{bad_text}", normal_style))
    story.append(Spacer(1, 0.1*inch))
    if chart_img:
        story.append(KeepTogether([
            Paragraph(f"Candlestick Chart ({period_label})", heading_style),
            Image(io.BytesIO(chart_img), width=6*inch, height=4*inch),
            Spacer(1, 0.1*inch)
        ]))
    if peer_data:
        story.append(Paragraph("Peer Comparison", heading_style))
        peer_df = pd.DataFrame(peer_data[:8])
        peer_display = peer_df[['代號', '名稱', '綜合分數', '市值(B)', '本益比', 'ROE']].copy()
        peer_display = peer_display.sort_values('綜合分數', ascending=False)
        peer_table_data = [['Ticker', 'Name', 'Score', 'Mkt Cap(B)', 'P/E', 'ROE']] + peer_display.values.tolist()
        peer_table = Table(peer_table_data, colWidths=[0.7*inch, 1.2*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.8*inch])
        peer_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3182ce')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        story.append(peer_table)
    story.append(Spacer(1, 0.1*inch))
    disclaimer = '<para><font size="7" color="gray">DISCLAIMER: For informational purposes only. Not investment advice. Data source: Yahoo Finance.</font></para>'
    story.append(Paragraph(disclaimer, normal_style))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def get_stock_price_change(ticker: str, days_back: int = 1) -> Dict:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days_back + 5}d", auto_adjust=False, timeout=30)
        if len(hist) >= days_back + 1:
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-days_back - 1]
            change_pct = ((current_price - prev_price) / prev_price) * 100
            return {"ticker": ticker, "change_pct": change_pct, "current_price": current_price, "prev_price": prev_price}
    except:
        pass
    return {"ticker": ticker, "change_pct": 0, "current_price": 0, "prev_price": 0}

def get_common_change_reasons(change_pct: float) -> str:
    if change_pct > 10:
        return "Possible reasons: Earnings beat, Positive guidance, Analyst upgrade, Sector momentum, M&A news"
    elif change_pct < -10:
        return "Possible reasons: Earnings miss, Weak guidance, Analyst downgrade, Negative sector sentiment, Regulatory concerns"
    elif change_pct > 5:
        return "Possible reasons: Positive news flow, Technical breakout, Institutional buying"
    elif change_pct < -5:
        return "Possible reasons: Profit taking, Broader market weakness, Sector rotation"
    else:
        return "Normal trading range, no unusual activity detected"

def get_economic_context() -> str:
    try:
        url = "https://finance.yahoo.com/news/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = soup.find_all('h3', limit=5)
            news_list = []
            for h in headlines:
                text = h.get_text(strip=True)
                if text and len(text) > 10:
                    news_list.append(f"- {text}")
            if news_list:
                return "\n".join(news_list[:5])
    except:
        pass
    return """- Fed signals cautious approach to rate policy
- AI and semiconductor demand remains robust
- Oil prices show stability amid OPEC+ compliance
- Tech sector earnings resilience continues
- Global economic growth outlook moderate"""

def generate_market_report(period_name: str, days_back: int) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('DailyTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1a365d'), spaceAfter=10, spaceBefore=5, alignment=1)
    heading_style = ParagraphStyle('DailyHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2c5282'), spaceAfter=6, spaceBefore=8)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#3182ce'), spaceAfter=4, spaceBefore=5)
    normal_style = ParagraphStyle('DailyNormal', parent=styles['Normal'], fontSize=9, spaceAfter=3, spaceBefore=1)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, spaceAfter=1, spaceBefore=1)
    report_date = datetime.now().strftime("%Y-%m-%d")
    story.append(Paragraph(f"Grow Knowledge · Professional US Stock {period_name}", title_style))
    story.append(Paragraph(f"Report Date: {report_date}", normal_style))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(f"1. Top Performing Industries ({period_name})", heading_style))
    industry_scores = []
    all_industry_stocks = {}
    for sector_en, industries in SECTOR_INDUSTRY_MAP_EN.items():
        for industry in industries:
            stocks = get_industry_stocks(industry)
            if stocks:
                data_list = fetch_batch_data(stocks)
                if data_list:
                    avg_score = sum(d['綜合分數'] for d in data_list) / len(data_list)
                    industry_scores.append({"industry": industry, "avg_score": avg_score, "sector": sector_en})
                    all_industry_stocks[industry] = data_list
                    time.sleep(0.1)
    if industry_scores:
        industry_scores.sort(key=lambda x: x["avg_score"], reverse=True)
        top_industries = industry_scores[:5]
        for i, ind in enumerate(top_industries):
            story.append(Paragraph(f"{i+1}. {ind['industry']} ({ind['sector']}) - Average Score: {ind['avg_score']:.1f}/100", normal_style))
    else:
        story.append(Paragraph("Data unavailable at this time.", normal_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"2. Industries with Average Score > 60 ({period_name})", heading_style))
    high_score_industries = [ind for ind in industry_scores if ind["avg_score"] > 60] if industry_scores else []
    if high_score_industries:
        for ind in high_score_industries[:10]:
            story.append(Paragraph(f"- {ind['industry']} ({ind['sector']}): {ind['avg_score']:.1f}/100", normal_style))
    else:
        story.append(Paragraph("No industries with average score above 60 at this time.", normal_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"3. High-Score Stocks (>80 points) - {period_name}", heading_style))
    all_high_score_stocks = []
    for industry, stocks_data in all_industry_stocks.items():
        for stock in stocks_data:
            if stock['綜合分數'] >= 80:
                all_high_score_stocks.append(stock)
    seen_tickers = set()
    unique_high_score = []
    for stock in all_high_score_stocks:
        if stock['代號'] not in seen_tickers:
            seen_tickers.add(stock['代號'])
            unique_high_score.append(stock)
    unique_high_score.sort(key=lambda x: x["綜合分數"], reverse=True)
    if unique_high_score:
        for stock in unique_high_score[:15]:
            story.append(Paragraph(f"- {stock['代號']} - {stock['名稱']}: {stock['綜合分數']}/100 ({stock['評級']})", normal_style))
    else:
        story.append(Paragraph("No stocks with score above 80 at this time.", normal_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"4. Analysis of High-Score Stocks ({period_name})", heading_style))
    if unique_high_score:
        for stock in unique_high_score[:5]:
            story.append(Paragraph(f"<b>{stock['代號']} - {stock['名稱']} (Score: {stock['綜合分數']}/100)</b>", subheading_style))
            reasons = []
            for item in stock['good_items'][:4]:
                reasons.append(f"  - {item}")
            if reasons:
                story.append(Paragraph("<br/>".join(reasons), normal_style))
            else:
                story.append(Paragraph("  Strong fundamentals with high profitability and healthy financial ratios.", normal_style))
            story.append(Spacer(1, 0.05*inch))
    else:
        story.append(Paragraph("No high-score stocks available for detailed analysis.", normal_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"5. Stocks with Significant Price Movement ({period_name})", heading_style))
    price_change_stocks = []
    all_tickers = []
    for industry, stocks_data in all_industry_stocks.items():
        for stock in stocks_data:
            if stock['代號'] not in all_tickers:
                all_tickers.append(stock['代號'])
    for ticker in all_tickers[:60]:
        change_info = get_stock_price_change(ticker, days_back)
        if abs(change_info["change_pct"]) >= 10:
            data = fetch_robust_data(ticker)
            if data:
                price_change_stocks.append({
                    "ticker": ticker,
                    "name": data["名稱"],
                    "change_pct": change_info["change_pct"],
                    "current_price": change_info["current_price"],
                    "prev_price": change_info["prev_price"],
                    "score": data["綜合分數"]
                })
        time.sleep(0.05)
    if price_change_stocks:
        up_stocks = [s for s in price_change_stocks if s["change_pct"] > 0]
        down_stocks = [s for s in price_change_stocks if s["change_pct"] < 0]
        up_stocks.sort(key=lambda x: x["change_pct"], reverse=True)
        down_stocks.sort(key=lambda x: x["change_pct"])
        if up_stocks:
            story.append(Paragraph("<b>Upward Movement (>+10%):</b>", subheading_style))
            for s in up_stocks[:5]:
                story.append(Paragraph(f"  - {s['ticker']} - {s['name']}: +{s['change_pct']:.1f}% (from ${s['prev_price']:.2f} to ${s['current_price']:.2f}) (Score: {s['score']}/100)", normal_style))
        if down_stocks:
            story.append(Paragraph("<b>Downward Movement (<-10%):</b>", subheading_style))
            for s in down_stocks[:5]:
                story.append(Paragraph(f"  - {s['ticker']} - {s['name']}: {s['change_pct']:.1f}% (from ${s['prev_price']:.2f} to ${s['current_price']:.2f}) (Score: {s['score']}/100)", normal_style))
    else:
        story.append(Paragraph(f"No stocks with significant price movement detected (±10%) in the {period_name.lower()} scan.", normal_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"6. Market Context & Movement Analysis ({period_name})", heading_style))
    story.append(Paragraph("<b>Current Market Context:</b>", subheading_style))
    economic_context = get_economic_context()
    story.append(Paragraph(economic_context, normal_style))
    story.append(Spacer(1, 0.05*inch))
    if price_change_stocks:
        story.append(Paragraph("<b>Price Movement Analysis with Data:</b>", subheading_style))
        for s in price_change_stocks[:5]:
            story.append(Paragraph(f"<b>{s['ticker']}: {s['change_pct']:+.1f}% (from ${s['prev_price']:.2f} to ${s['current_price']:.2f})</b>", normal_style))
            story.append(Paragraph(f"  {get_common_change_reasons(s['change_pct'])}", normal_style))
            story.append(Spacer(1, 0.03*inch))
    else:
        story.append(Paragraph("<b>Price Movement Analysis:</b>", subheading_style))
        story.append(Paragraph(f"No significant price movements detected in the {period_name.lower()} scan. The market may be in a consolidation phase or awaiting catalysts.", normal_style))
        story.append(Paragraph("<b>Typical causes for price movements when they occur:</b>", normal_style))
        story.append(Paragraph("  - Earnings announcements (beat/miss)", normal_style))
        story.append(Paragraph("  - Guidance updates (positive/negative)", normal_style))
        story.append(Paragraph("  - Analyst rating changes (upgrade/downgrade)", normal_style))
        story.append(Paragraph("  - Sector-wide trends or regulatory news", normal_style))
        story.append(Paragraph("  - Macroeconomic data releases (CPI, Jobs, Fed decisions)", normal_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Spacer(1, 0.15*inch))
    disclaimer = '<para><font size="7" color="gray">DISCLAIMER: This report is for informational purposes only. Not investment advice. Market conditions change rapidly. Data source: Yahoo Finance. Past performance does not guarantee future results.</font></para>'
    story.append(Paragraph(disclaimer, small_style))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# 获取行业股票（使用 INDUSTRY_PEERS）
def get_industry_stocks(industry):
    if industry in INDUSTRY_PEERS:
        return INDUSTRY_PEERS[industry][:10]
    industry_lower = industry.lower()
    # 后备关键字匹配
    if "semiconductor" in industry_lower:
        return ["NVDA", "AVGO", "AMD", "TXN", "INTC", "QCOM", "MU", "ADI", "MRVL", "ON"]
    elif "software" in industry_lower:
        return ["MSFT", "ORCL", "ADBE", "CRM", "PANW", "SNPS", "CDNS", "PLTR", "CRWD", "FTNT"]
    elif "bank" in industry_lower:
        return ["JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "COF"]
    elif "insurance" in industry_lower:
        return ["BRK-B", "AIG", "MET", "PRU", "LNC"]
    elif "reit" in industry_lower:
        return ["SPG", "O", "PLD", "DLR", "CCI", "EQIX", "WELL", "AVB", "EQR", "VTR"]
    elif "utility" in industry_lower or "electric" in industry_lower or "water" in industry_lower:
        return ["NEE", "DUK", "SO", "D", "AEP", "EXC", "ED", "PPL", "FE", "EIX"]
    return []

def get_stock_sector_industry(ticker: str) -> tuple:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get('sector', '')
        industry = info.get('industry', '')
        if not industry:
            for ind, stocks in INDUSTRY_PEERS.items():
                if ticker.upper() in stocks:
                    return (sector, ind)
        return (sector, industry)
    except Exception:
        return ("", "")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_batch_data(tickers: List[str]) -> List[Dict]:
    results = []
    for ticker in tickers:
        data = fetch_robust_data(ticker)
        if data:
            results.append(data)
        time.sleep(0.05)
    return results

# 注意：这里移除了 @st.cache_data，因为进度条参数导致缓存冲突，且行业排名只需计算一次
def get_industry_average_scores(_progress_placeholder=None):
    industry_scores = []
    total_industries = sum(len(industries) for industries in SECTOR_INDUSTRY_MAP_EN.values())
    processed = 0
    for sector_en, industries in SECTOR_INDUSTRY_MAP_EN.items():
        for industry in industries:
            processed += 1
            if _progress_placeholder is not None:
                _progress_placeholder.progress(processed / total_industries, 
                                               text=f"正在分析 {industry} ({processed}/{total_industries})")
            stocks = get_industry_stocks(industry)
            if stocks:
                try:
                    data_list = fetch_batch_data(stocks)
                    if data_list:
                        avg_score = sum(d['綜合分數'] for d in data_list) / len(data_list)
                        industry_scores.append({
                            "sector": sector_en,
                            "industry": industry,
                            "avg_score": avg_score,
                            "stock_count": len(data_list)
                        })
                except Exception as e:
                    print(f"Error processing {industry}: {e}")
            time.sleep(0.05)
    industry_scores.sort(key=lambda x: x["avg_score"], reverse=True)
    return industry_scores

# ==========================================
# 10. Session State 初始化
# ==========================================
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = "NVDA"
if 'current_industry_stocks' not in st.session_state:
    st.session_state.current_industry_stocks = []
if 'current_industry_data' not in st.session_state:
    st.session_state.current_industry_data = []
if 'last_industry' not in st.session_state:
    st.session_state.last_industry = None
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False
if 'chart_period' not in st.session_state:
    st.session_state.chart_period = "1y"
if 'last_chart_period' not in st.session_state:
    st.session_state.last_chart_period = "1y"
if 'industry_loaded' not in st.session_state:
    st.session_state.industry_loaded = False
if 'industry_scores' not in st.session_state:
    st.session_state.industry_scores = None
if 'sync_sector' not in st.session_state:
    st.session_state.sync_sector = None
if 'sync_industry' not in st.session_state:
    st.session_state.sync_industry = None
if 'loading_industry_rankings' not in st.session_state:
    st.session_state.loading_industry_rankings = False
if 'industry_rankings_loading_started' not in st.session_state:
    st.session_state.industry_rankings_loading_started = False
if 'right_panel_mode' not in st.session_state:
    st.session_state.right_panel_mode = "stock"

# 新增：用于记住 B 部分的选择
if 'b_sector' not in st.session_state:
    st.session_state.b_sector = "Technology"
if 'b_industry' not in st.session_state:
    st.session_state.b_industry = "Semiconductors"

sector_options_zh = list(SECTOR_INDUSTRY_MAP.keys())
sector_options_en = list(SECTOR_INDUSTRY_MAP_EN.keys())
sector_display = [f"{zh} / {en}" for zh, en in zip(sector_options_zh, sector_options_en)]
sector_map = {f"{zh} / {en}": en for zh, en in zip(sector_options_zh, sector_options_en)}

# ==========================================
# 11. 侧边栏（A、B、C 模块）
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="main-header">
        診斷控制面板 🔍
        <span class="main-header-sub">Diagnostic Control Panel</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📌 使用說明 / instructions", use_container_width=True):
        st.session_state.show_instructions = not st.session_state.show_instructions
    if st.session_state.show_instructions:
        st.markdown("""
        **📖 使用說明**
        - 輸入股票代號查看分析（右侧显示个股报告）
        - 選擇板塊和行業，點擊「更新同業名單」查看詳細同業對照（右侧显示表格）
        - 點擊「載入行業排名」載入所有行業平均分數（需2-3分鐘），加载期间无法操作其他模块
        """)
    st.markdown("---")
    
    # ==========================================
    # A. 個股分析（支援 ENTER 鍵）
    # ==========================================
    st.markdown("""
    <div class="section-header-a">
        A. 個股分析 📌
        <span class="section-header-a-sub">    Stock Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    loading = st.session_state.get('loading_industry_rankings', False)
    if loading:
        st.info("⏳ 行業排名載入中，暫時無法切換股票，請稍候...")
        st.text_input("輸入代號 / stock name", value=st.session_state.current_ticker, disabled=True)
        st.button("🚀 更新結果 / refresh", use_container_width=True, disabled=True)
    else:
        # 使用 form 來支援 ENTER 鍵
        with st.form(key="ticker_form"):
            u_input = st.text_input("輸入代號 / stock name", value=st.session_state.current_ticker).upper()
            submit_button = st.form_submit_button("🚀 更新結果 / refresh", use_container_width=True)
            if submit_button:
                if u_input != st.session_state.current_ticker:
                    sector, industry = get_stock_sector_industry(u_input)
                    if industry:
                        for sector_en, industries in SECTOR_INDUSTRY_MAP_EN.items():
                            if industry in industries:
                                st.session_state.sync_sector = sector_en
                                st.session_state.sync_industry = industry
                                st.session_state.last_industry = industry
                                with st.spinner(f"正在載入 {industry} 行業的同業數據..."):
                                    st.session_state.current_industry_stocks = get_industry_stocks(industry)
                                    st.session_state.current_industry_data = fetch_batch_data(st.session_state.current_industry_stocks)
                                break
                st.session_state.current_ticker = u_input
                st.session_state.right_panel_mode = "stock"
                st.rerun()
    st.markdown("---")
    
    # ==========================================
    # B. 我想尋寶（記住上次選擇）
    # ==========================================
    st.markdown("""
    <div class="section-header-b">
        B. 我想尋寶 🔎
        <span class="section-header-b-sub">Sector Explorer</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 板塊選擇（記住上次選擇）
    sector_options_en = list(SECTOR_INDUSTRY_MAP_EN.keys())
    sector_index = sector_options_en.index(st.session_state.b_sector) if st.session_state.b_sector in sector_options_en else 0
    selected_sector = st.selectbox("選擇板塊 / sectors", sector_options_en, index=sector_index, disabled=loading)
    st.session_state.b_sector = selected_sector
    
    # 行業選擇（記住上次選擇）
    industries = SECTOR_INDUSTRY_MAP_EN[selected_sector]
    industry_index = industries.index(st.session_state.b_industry) if st.session_state.b_industry in industries else 0
    selected_industry = st.selectbox("選擇行業 / industries", industries, index=industry_index, disabled=loading)
    st.session_state.b_industry = selected_industry
    
    # 當行業改變時自動載入（非 loading 狀態）
    if not loading and selected_industry != st.session_state.last_industry:
        st.session_state.last_industry = selected_industry
        with st.spinner("載入中..."):
            st.session_state.current_industry_stocks = get_industry_stocks(selected_industry)
            st.session_state.current_industry_data = fetch_batch_data(st.session_state.current_industry_stocks)
        st.rerun()
    
    if st.button("🔄 更新同業名單 / related industry stocks", use_container_width=True, disabled=loading):
        with st.spinner("獲取中..."):
            st.session_state.current_industry_stocks = get_industry_stocks(selected_industry)
            st.session_state.current_industry_data = fetch_batch_data(st.session_state.current_industry_stocks)
        st.success(f"已獲取 {len(st.session_state.current_industry_data)} 支股票")
        st.session_state.right_panel_mode = "peer"
        st.rerun()
    
    if st.session_state.current_industry_data:
        st.markdown("---")
        avg_score = sum(p["綜合分數"] for p in st.session_state.current_industry_data) / len(st.session_state.current_industry_data)
        avg_icon = get_score_icon(avg_score)
        st.markdown(f"""
        <div style="font-size: 20px;">
        📊 同業平均分數: {avg_icon} {avg_score:.1f} 
        <span style="font-size: 20px; color: #666;">({get_score_rating(avg_score)})</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    
    # ==========================================
    # C. 最佳板塊及行業
    # ==========================================
    st.markdown("""
    <div class="section-header-c">
        C. 最佳板塊及行業 🏆
        <span class="section-header-c-sub">The best sectors and industries</span>
    </div>
    """, unsafe_allow_html=True)
    
    if loading:
        progress_bar = st.progress(0, text="準備載入...")
        cancel_button = st.button("❌ 取消載入", use_container_width=True)
        if cancel_button:
            st.session_state.loading_industry_rankings = False
            st.session_state.industry_rankings_loading_started = False
            st.rerun()
        try:
            if not st.session_state.get('industry_rankings_loading_started', False):
                st.session_state.industry_rankings_loading_started = True
                industry_scores = get_industry_average_scores(_progress_placeholder=progress_bar)
                st.session_state.industry_scores = industry_scores
                st.session_state.industry_loaded = True
                st.session_state.loading_industry_rankings = False
                st.session_state.industry_rankings_loading_started = False
                st.session_state.right_panel_mode = "ranking"
                st.rerun()
        except Exception as e:
            st.error(f"載入失敗: {e}")
            st.session_state.loading_industry_rankings = False
            st.session_state.industry_rankings_loading_started = False
            if st.button("🔄 重試載入", use_container_width=True):
                st.rerun()
    else:
        if st.button("🚀 載入行業排名 / Load Industry Rankings", use_container_width=True):
            st.session_state.loading_industry_rankings = True
            st.rerun()
    
    if st.session_state.get('industry_loaded', False) and st.session_state.industry_scores:
        industry_scores = st.session_state.industry_scores
        st.markdown("**📊 行業平均分數排名 (前10名)**")
        for i, ind in enumerate(industry_scores[:10]):
            if ind['avg_score'] >= 70:
                icon = "🟢"
            elif ind['avg_score'] >= 55:
                icon = "🟡"
            else:
                icon = "🔴"
            st.markdown(f"""
            <div style="margin-bottom: 8px; padding: 5px; border-bottom: 1px solid rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: bold; font-size: 14px;">{i+1}. {ind['industry']}</span>
                        <span style="font-size: 11px; color: #666; margin-left: 8px;">({ind['sector']})</span>
                    </div>
                    <div>
                        <span style="font-size: 16px; font-weight: bold; color: {'#228B22' if ind['avg_score'] >= 70 else '#FFA500' if ind['avg_score'] >= 55 else '#FF4B4B'};">{ind['avg_score']:.1f}</span>
                        <span style="font-size: 12px; margin-left: 5px;">{icon}</span>
                    </div>
                </div>
                <div style="font-size: 10px; color: #888;">📊 樣本數: {ind['stock_count']} 支股票</div>
            </div>
            """, unsafe_allow_html=True)
        st.caption(f"✅ 已載入 | 共 {len(industry_scores)} 個行業")
        if st.button("🗑️ 清除行業數據", use_container_width=True):
            st.session_state.industry_loaded = False
            st.session_state.industry_scores = None
            st.cache_data.clear()
            st.rerun()
    elif not loading:
        st.info("💡 點擊上方按鈕載入行業排名數據（首次載入約需2-3分鐘，之後會快取2小時）")

# ==========================================
# 12. 右侧主区域（根据模式显示内容，保留原有标题）
# ==========================================
st.markdown(f"""
<div class="right-top-logo">
    <img src="https://www.gkhaw.com/favicon.ico" class="right-logo-img" onerror="this.src='https://via.placeholder.com/45x45?text=GK'">
    <div class="right-logo-text">
        <div class="right-logo-title">自己學。專業美股選股器</div>
        <div class="right-logo-sub">Professional Stock Screener</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 模式1：个股分析
if st.session_state.right_panel_mode == "stock":
    st.markdown("""
    <div class="report-header-a">
        A. 個股分析結果 📊
        <span class="report-header-sub">Stock Analysis Report</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.status("分析中...", expanded=False) as status:
        status.update(label="獲取資料...", state="running")
        main_data = fetch_robust_data(st.session_state.current_ticker)
        if main_data:
            status.update(label="生成圖表...", state="running")
            hist = get_history_data(st.session_state.current_ticker, "1y")
            if not hist.empty and len(hist) >= 20:
                rsi = calculate_rsi(hist['Close'])
                macd_line, signal_line, macd_hist = calculate_macd(hist['Close'])
                adx, plus_di, minus_di, atr_temp = calculate_dmi(hist['High'], hist['Low'], hist['Close'])
                rvol = calculate_rvol(hist['Volume'])
                cci = calculate_cci(hist['High'], hist['Low'], hist['Close'], period=20)
                bb_upper, bb_sma, bb_lower = calculate_bollinger_bands(hist['Close'])
                bb_width_history = calculate_bb_width(bb_upper, bb_lower, bb_sma)
                current_adx = adx.iloc[-1] if not adx.empty else 20
                current_plus_di = plus_di.iloc[-1] if not plus_di.empty else 20
                current_minus_di = minus_di.iloc[-1] if not minus_di.empty else 20
                current_rvol = rvol.iloc[-1] if not rvol.empty else 1.0
                current_atr = atr_temp.iloc[-1] if not atr_temp.empty else 0
                sma150_value = main_data.get("SMA150")
                current_price = hist['Close'].iloc[-1] if not hist.empty else None
                trading_score, recommendation, rec_color, rec_action, details = calculate_trading_score(
                    rsi, macd_line, signal_line, current_adx, current_plus_di, current_minus_di,
                    current_rvol, hist['Close'], macd_hist, cci,
                    bb_upper, bb_lower, bb_sma, bb_width_history,
                    sma_150_value=sma150_value, current_price=current_price
                )
                volume_rvol_img = create_volume_rvol_chart(hist)
                dmi_img = create_dmi_chart(hist)
                rsi_img = create_rsi_chart(hist)
                macd_img = create_macd_chart(hist)
                cci_img = create_cci_chart(hist, period=20)
                bb_img = create_bollinger_chart(hist)
            else:
                volume_rvol_img = dmi_img = rsi_img = macd_img = cci_img = bb_img = None
                trading_score = 50
                recommendation = "沒有明顯訊號 / No Clear Signal"
                rec_color = "#FFA500"
                rec_action = "數據不足，無法進行技術分析"
                current_atr = 0
                details = {}
            status.update(label="完成報告", state="complete")
        else:
            status.update(label="獲取失敗", state="error")
    
    if main_data:
        display_cols = ['代號', '名稱', '板塊', '行業', '綜合分數', '評級', '市值(B)', '本益比', 'PEG', 'ROE', 'ROI', '淨利率', '流動比率', '速動比率', '營收成長', '盈利成長', 'OBV走勢']
        display_df = pd.DataFrame([main_data])[display_cols]
        st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        create_section_header("💰", "價值投資交易評分系統", "Value Investing Trading Score System")
        
        # 專業總分和診斷詳情（無論分數高低都顯示）
        col_score, col_tips = st.columns([1, 2])
        bg = main_data['顏色']
        with col_score:
            st.markdown(f'<p class="score-label">專業總分 / Score </p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-score" style="color: {bg};">{main_data["綜合分數"]}<span style="font-size: 50px;">/100</span></p>', unsafe_allow_html=True)
        with col_tips:
            st.markdown('<p class="score-label">🔍 診斷詳情 / Diagnosis </p>', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("##### ✅ 優勢 / Advantage")
                for item in main_data['good_items'][:10]: 
                    st.markdown(f"<p class='good-item'>{item}</p>", unsafe_allow_html=True)
            with col_b:
                st.markdown("##### ➡️ 中性 / Neutral")
                for item in main_data['neutral_items'][:10]: 
                    st.markdown(f"<p class='neutral-item'>{item}</p>", unsafe_allow_html=True)
            with col_c:
                st.markdown("##### ❌ 弱勢 / Disadvantaged")
                for item in main_data['bad_items'][:10]: 
                    st.markdown(f"<p class='bad-item'>{item}</p>", unsafe_allow_html=True)
        
        # 根據分數決定是否顯示量化交易、圖表、ATR
        if main_data['綜合分數'] < 60:
            st.warning(f"""
            ⚠️ **根據價值投資交易評分系統，您所選的股票 ({main_data['代號']}) 綜合分數為 {main_data['綜合分數']}/100，未能達到最低標準 (60分)。**
            
            建議您：
            1. 參考下方「B. 我想尋寶」中的同業對照，尋找同業中分數更高的股票
            2. 重新選擇其他股票進行分析
            """)
            show_advanced = False
        else:
            st.success(f"✅ 恭喜！{main_data['代號']} 綜合分數為 {main_data['綜合分數']}/100，你所選的股票具備價值投資的條件(≥60分)，現幫你用量化分析的方法看準出入市場的時機作參考。")
            show_advanced = True
            st.divider()
        
        # 只有分數 >= 60 才顯示以下內容
        if show_advanced:
            # ==========================================
            # 🎯 量化交易評分系統
            # ==========================================
            create_section_header("🎯", "量化交易評分系統", "Quantitative Trading Score System")
            
            col_score_left, col_status_mid, col_radar_right = st.columns([1, 1, 1])
            
            with col_score_left:
                st.markdown(f"""
                <div style="text-align: left;">
                    <div style="font-size: 20px; color: #666; font-weight: bold;">技術總分 / Technical Score</div>
                    <div style="font-size: 80px; font-weight: 800; color: {rec_color};">{trading_score}<span style="font-size: 40px;">/100</span></div>
                    <div style="font-size: 24px; font-weight: 700; color: {rec_color};">{recommendation}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 10px;">{rec_action}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_status_mid:
                st.markdown("##### 📊 交易狀態 / Transaction Status")
                status_list = [
                    {"range": "90-100", "status_cn": "強烈建議買入", "status_en": "Strong Buy", "color": "#006400"},
                    {"range": "80-89", "status_cn": "建議買入", "status_en": "Buy", "color": "#228B22"},
                    {"range": "70-79", "status_cn": "偏多 - 持有", "status_en": "Bullish - Hold", "color": "#9ACD32"},
                    {"range": "60-69", "status_cn": "觀察/等待（偏多）", "status_en": "Watch (Bullish)", "color": "#FFD700"},
                    {"range": "50-59", "status_cn": "沒有明顯訊號", "status_en": "No Clear Signal", "color": "#FFA500"},
                    {"range": "40-49", "status_cn": "觀察/等待（偏空）", "status_en": "Watch (Bearish)", "color": "#FF8C00"},
                    {"range": "30-39", "status_cn": "偏空 - 觀望", "status_en": "Bearish - Wait", "color": "#FF6347"},
                    {"range": "20-29", "status_cn": "建議賣出", "status_en": "Sell", "color": "#FF4B4B"},
                    {"range": "10-19", "status_cn": "強烈建議賣出", "status_en": "Strong Sell", "color": "#8B0000"},
                    {"range": "0-9", "status_cn": "強制停損/清倉", "status_en": "Force Stop Loss", "color": "#FF0000"}
                ]
                for s in status_list:
                    if s["status_cn"] in recommendation or s["status_en"] in recommendation:
                        st.markdown(f'<div style="padding: 2px 0;"><span style="color: {s["color"]}; font-weight: bold;">{s["range"]} 分 : {s["status_cn"]} / {s["status_en"]}</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="padding: 2px 0;"><span style="color: #808080;">{s["range"]} 分 : {s["status_cn"]} / {s["status_en"]}</span></div>', unsafe_allow_html=True)
            
            with col_radar_right:
                st.markdown("##### 📊 技術分析雷達圖 / Radar Chart")
                if details and len(details) > 0:
                    dmi_data = details.get("DMI", {})
                    macd_data = details.get("MACD", {})
                    rsi_data = details.get("RSI", {})
                    cci_data = details.get("CCI", {})
                    rvol_data = details.get("RVOL", {})
                    sma150_data = details.get("SMA150", {})
                    bb_data = details.get("BB", {})
                    dmi_score = dmi_data.get("score", 0)
                    macd_score = macd_data.get("score", 0)
                    rsi_score = rsi_data.get("score", 0)
                    cci_score = cci_data.get("score", 0)
                    rvol_score = rvol_data.get("score", 0)
                    sma150_score = sma150_data.get("score", 0)
                    bb_score = bb_data.get("score", 0)
                    dmi_max, macd_max, rsi_max, cci_max, rvol_max, sma150_max, bb_max = 25, 20, 10, 10, 15, 10, 10
                    dmi_pct = (dmi_score / dmi_max) * 100
                    macd_pct = (macd_score / macd_max) * 100
                    rsi_pct = (rsi_score / rsi_max) * 100
                    cci_pct = (cci_score / cci_max) * 100
                    rvol_pct = (rvol_score / rvol_max) * 100
                    sma150_pct = (sma150_score / sma150_max) * 100
                    bb_pct = (bb_score / bb_max) * 100
                    categories = ['DMI\n(25)', 'MACD\n(20)', 'RSI\n(10)', 'CCI\n(10)', 'RVOL\n(15)', 'SMA150\n(10)', 'BB\n(10)']
                    values = [dmi_pct, macd_pct, rsi_pct, cci_pct, rvol_pct, sma150_pct, bb_pct]
                    plt.close('all')
                    fig = plt.figure(figsize=(5, 5))
                    ax = fig.add_subplot(111, projection='polar')
                    angles = [n / float(len(categories)) * 2 * np.pi for n in range(len(categories))]
                    values += values[:1]
                    angles += angles[:1]
                    ax.fill(angles, values, alpha=0.25, color='#3182ce')
                    ax.plot(angles, values, 'o-', linewidth=2, color='#1a365d')
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(categories, fontsize=7)
                    ax.set_ylim(0, 100)
                    ax.set_yticks([20, 40, 60, 80, 100])
                    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    st.image(buf, use_container_width=True)
                    st.caption(f"💡 DMI: {dmi_score}/{dmi_max} | MACD: {macd_score}/{macd_max} | RSI: {rsi_score}/{rsi_max} | CCI: {cci_score}/{cci_max} | RVOL: {rvol_score}/{rvol_max} | SMA150: {sma150_score}/{sma150_max} | BB: {bb_score}/{bb_max}")
                    total_score = details.get("Total", {}).get("score", 0)
                    st.progress(total_score / 100, text=f"📊 技術總分: {total_score}/100")
                else:
                    st.info("⚠️ 技術分析數據不足，無法生成雷達圖。")
            
            # ATR 交易計劃（技術總分 >= 70 時顯示）
            if trading_score >= 70:
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
                if current_atr > 0 and current_price > 0:
                    trading_plan = calculate_trading_plan(current_price, current_atr)
                    display_trading_plan_card_streamlit(trading_plan)
                else:
                    st.info("📊 ATR 數據不足，無法生成交易計劃")
            else:
                st.info(f"📐 ATR 交易計劃將在技術總分 ≥ 70 時顯示 (當前分數: {trading_score}/100)")
            
            st.divider()
            
            # ==========================================
            # 📈 圖表技術分析
            # ==========================================
            create_section_header("📈", "圖表技術分析", "Technical Analysis")
            
            period_options = {"1 個月 / 1 mo": "1mo", "3 個月 / 3 mo": "3mo", "6 個月 / 6 mo": "6mo", "1 年 / 1 yr": "1y"}
            selected_period_label = st.selectbox("選擇週期 / Select cycle", list(period_options.keys()), index=3)
            st.session_state.chart_period = period_options[selected_period_label]
            hist = get_history_data(st.session_state.current_ticker, st.session_state.chart_period)
            if not hist.empty and len(hist) >= 20:
                volume_rvol_img = create_volume_rvol_chart(hist)
                dmi_img = create_dmi_chart(hist)
                rsi_img = create_rsi_chart(hist)
                macd_img = create_macd_chart(hist)
                cci_img = create_cci_chart(hist, period=20)
                bb_img = create_bollinger_chart(hist)
            else:
                volume_rvol_img = dmi_img = rsi_img = macd_img = cci_img = bb_img = None
            
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 陰陽燭圖", "📈 成交量+RVOL", "📉 DMI", "🎯 RSI", "📉 MACD", "📊 CCI", "📈 保力加通道"])
            with tab1:
                chart_img = create_candlestick_chart(st.session_state.current_ticker, st.session_state.chart_period)
                if chart_img:
                    st.image(chart_img, use_container_width=True)
                else:
                    st.warning("無法生成陰陽燭圖")
            with tab2:
                if volume_rvol_img:
                    st.image(volume_rvol_img, use_container_width=True)
                else:
                    st.warning("無法生成成交量圖")
            with tab3:
                if dmi_img:
                    st.image(dmi_img, use_container_width=True)
                else:
                    st.warning("無法生成 DMI 圖表")
            with tab4:
                if rsi_img:
                    st.image(rsi_img, use_container_width=True)
                else:
                    st.warning("無法生成 RSI 圖表")
            with tab5:
                if macd_img:
                    st.image(macd_img, use_container_width=True)
                else:
                    st.warning("無法生成 MACD 圖表")
            with tab6:
                if cci_img:
                    st.image(cci_img, use_container_width=True)
                else:
                    st.warning("無法生成 CCI 圖表")
            with tab7:
                if bb_img:
                    st.image(bb_img, use_container_width=True)
                else:
                    st.warning("無法生成保力加通道圖表")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                csv_data = pd.DataFrame([main_data])[display_cols].to_csv(index=False)
                st.download_button(label="📥 導出 CSV", data=csv_data, file_name=f"{main_data['代號']}_report.csv", mime="text/csv", use_container_width=True)
            with col2:
                if st.button("📄 生成 PDF 報告", use_container_width=True):
                    with st.spinner("生成中..."):
                        pdf_bytes = generate_pdf_report(st.session_state.current_ticker, main_data, st.session_state.current_industry_data, chart_img, st.session_state.chart_period)
                        st.download_button(label="✅ 下載 PDF", data=pdf_bytes, file_name=f"{main_data['代號']}_report.pdf", mime="application/pdf", key="pdf_download", use_container_width=True)
                        st.success("PDF 已生成！")
            with col3:
                if st.button("📰 美股日報", use_container_width=True):
                    with st.spinner("Generating daily report..."):
                        daily_report_pdf = generate_market_report("Daily Report (1-Day Change)", 1)
                        st.download_button(label="✅ Download Daily Report", data=daily_report_pdf, file_name=f"US_Stock_Daily_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", key="daily_report_download", use_container_width=True)
                        st.success("Daily report generated!")
            with col4:
                if st.button("📅 美股週報", use_container_width=True):
                    with st.spinner("Generating weekly report..."):
                        weekly_report_pdf = generate_market_report("Weekly Report (5-Day Change)", 5)
                        st.download_button(label="✅ Download Weekly Report", data=weekly_report_pdf, file_name=f"US_Stock_Weekly_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", key="weekly_report_download", use_container_width=True)
                        st.success("Weekly report generated!")
            with col5:
                if st.button("📆 美股月報", use_container_width=True):
                    with st.spinner("Generating monthly report..."):
                        monthly_report_pdf = generate_market_report("Monthly Report (20-Day Change)", 20)
                        st.download_button(label="✅ Download Monthly Report", data=monthly_report_pdf, file_name=f"US_Stock_Monthly_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", key="monthly_report_download", use_container_width=True)
                        st.success("Monthly report generated!")
    else:
        st.error(f"無法獲取 {st.session_state.current_ticker} 的數據")

# 模式2：同业对比
elif st.session_state.right_panel_mode == "peer":
    st.markdown("""
    <div class="peer-header-b">
        B. 我想尋寶：同業對照表 🏆
        <span class="peer-header-sub">Peer Comparison Table</span>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.current_industry_data:
        st.markdown("**📌 同業股票列表：**")
        peer_display_cols = ['代號', '名稱', '綜合分數', '評級', '市值(B)', '本益比', 'ROE', '營收成長']
        df_peers = pd.DataFrame(st.session_state.current_industry_data)[peer_display_cols].sort_values("綜合分數", ascending=False)
        df_peers["綜合分數"] = df_peers["綜合分數"].apply(lambda x: f"{get_score_icon(x)} {x}")
        st.dataframe(df_peers, hide_index=True, use_container_width=True)
        if st.button("🔙 返回個股分析", use_container_width=True):
            st.session_state.right_panel_mode = "stock"
            st.rerun()
    else:
        st.info("暫無同業數據，請先點擊左側「更新同業名單」")
        if st.button("🔙 返回個股分析", use_container_width=True):
            st.session_state.right_panel_mode = "stock"
            st.rerun()

# 模式3：行业排名
elif st.session_state.right_panel_mode == "ranking":
    st.markdown("""
    <div class="report-header-a">
        C. 十大最佳板塊及行業 🏆
        <span class="report-header-sub">Top 10 Industries Ranking</span>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.get('industry_loaded', False) and st.session_state.industry_scores:
        st.markdown("**📊 行業平均分數排名 (前10名)**")
        industry_scores = st.session_state.industry_scores
        for i, ind in enumerate(industry_scores[:10]):
            if ind['avg_score'] >= 70:
                icon = "🟢"
            elif ind['avg_score'] >= 55:
                icon = "🟡"
            else:
                icon = "🔴"
            st.markdown(f"""
            <div style="margin-bottom: 8px; padding: 5px; border-bottom: 1px solid rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: bold; font-size: 14px;">{i+1}. {ind['industry']}</span>
                        <span style="font-size: 11px; color: #666; margin-left: 8px;">({ind['sector']})</span>
                    </div>
                    <div>
                        <span style="font-size: 16px; font-weight: bold; color: {'#228B22' if ind['avg_score'] >= 70 else '#FFA500' if ind['avg_score'] >= 55 else '#FF4B4B'};">{ind['avg_score']:.1f}</span>
                        <span style="font-size: 12px; margin-left: 5px;">{icon}</span>
                    </div>
                </div>
                <div style="font-size: 10px; color: #888;">📊 樣本數: {ind['stock_count']} 支股票</div>
            </div>
            """, unsafe_allow_html=True)
        st.caption(f"✅ 共 {len(industry_scores)} 個行業")
        if st.button("🔙 返回個股分析", use_container_width=True):
            st.session_state.right_panel_mode = "stock"
            st.rerun()
    else:
        st.info("行業排名數據尚未載入，請點擊左側「載入行業排名」")
        if st.button("🔙 返回個股分析", use_container_width=True):
            st.session_state.right_panel_mode = "stock"
            st.rerun()

st.markdown("""
<div class="disclaimer">
    ⚠️ 本公司所提供之內容僅供參考與教育用途，不構成任何投資建議、買賣要約或招攬。<br>投資涉及風險，市場有起有落，過去表現不代表未來回報。投資人應自行判斷並承擔風險，必要時諮詢專業顧問。<br>本公司不對任何投資決策或損失負責。未經授權不得轉載或引用。<br>
    數據來源：Yahoo Finance
</div>
""", unsafe_allow_html=True)

if 'sel_sector_en' in locals() and 'sel_ind_en' in locals():
    current_sector_zh = [zh for zh, en in zip(sector_options_zh, sector_options_en) if en == sel_sector_en][0]
    st.caption(f"✅ 就緒 | 板塊: {current_sector_zh} | 行業: {sel_ind_en} | 同業數: {len(st.session_state.current_industry_data)}")