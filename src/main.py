"""
엑셀 명세서 금액 합산기
--------------------------------
PySide6 + pandas + matplotlib
"""

import sys, os, json, logging
from collections import OrderedDict
import pandas as pd
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QApplication,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt
from ui_main_window import Ui_MainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ===============================
# config.json 불러오기
# ===============================
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

APP_TITLE = CONFIG["APP_TITLE"]
LOG_PATH = CONFIG["LOG_PATH"]
RECENTS_PATH = CONFIG["RECENTS_PATH"]

COL_STORE = CONFIG["COL_STORE"]
COL_AMOUNT = CONFIG["COL_AMOUNT"]
COL_DT = CONFIG["COL_DT"]

DATE_COL_KEYS = CONFIG["DATE_COL_KEYS"]
CATEGORY_MAP = CONFIG["CATEGORY_MAP"]

# ===============================
# 한글 폰트 설정
# ===============================
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 깨짐 방지

# ===============================
# 로거 설정
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_PATH,
    filemode="a",
)
logger = logging.getLogger(__name__)

# ===============================
# 유틸 함수 (데이터 처리)
# ===============================
def normalize_text_series(series: pd.Series) -> pd.Series:
    """텍스트 정리: 특수공백 제거, 연속 공백 압축, 좌우 trim"""
    series = series.astype(str)
    return (series.str.replace("\u200b", "", regex=False)
                  .str.replace("\xa0", " ", regex=False)
                  .str.replace(r"\s+", " ", regex=True)
                  .str.strip())

def infer_category(name: str) -> str:
    """가맹점 이름을 카테고리로 분류"""
    for cat, keywords in CATEGORY_MAP.items():
        for keyword in keywords:
            if keyword.lower() in str(name).lower():
                return cat
    return "기타"

def normalize_DT_column(df: pd.DataFrame) -> pd.DataFrame:
    """여러 날짜 후보 컬럼을 검사하여 DT 컬럼 생성"""
    candidates = [c for c in df.columns if any(k in c for k in DATE_COL_KEYS)]
    dt = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")

    for col in candidates:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            parsed = pd.to_datetime(s, unit="d", origin="1899-12-30", errors="coerce")
        else:
            ss = s.astype(str)
            ss = (ss.str.replace("년", ".", regex=False)
                    .str.replace("월", ".", regex=False)
                    .str.replace("일", "", regex=False))
            ss = ss.str.replace(r"[^0-9\.\-\/]", "", regex=True)
            parsed = pd.to_datetime(ss, errors="coerce", format="%y.%m.%d")
        dt = dt.fillna(parsed)

    df[COL_DT] = dt
    return df

# ===============================
# matplotlib 그래프 다이얼로그
# ===============================
class MplDialog(QWidget):
    def __init__(self, title: str, plot_fn):
        super().__init__()
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)

        figure = Figure(figsize=(6, 4))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        ax = figure.add_subplot(111)
        plot_fn(ax)
        canvas.draw()

# ===============================
# 메인 앱 클래스
# ===============================
class ExcelSumApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.chart_windows = []

        self.file_path = None
        self.df = None
        self.filtered = None

        self.setWindowTitle(APP_TITLE)
        logger.info("프로그램 실행 시작")

        # 버튼 이벤트 연결
        self.ui.btn_load_excel.clicked.connect(self.load_excel_dialog)
        self.ui.btn_calculate.setText("키워드 분석하기")
        self.ui.btn_calculate.clicked.connect(self.run_keyword_analysis)
        self.btn_save_category = QPushButton("카테고리 요약 저장하기")
        self.btn_save_category.clicked.connect(self.save_category_summary_action)
        self.ui.verticalLayout.addWidget(self.btn_save_category)

        # UI 요소 삽입
        self.setup_recent_files_ui()
        self.setup_quick_keywords_ui()
        self.setup_result_ui()

        self.load_recent_files()
        self.setStyleSheet("""
            QLabel, QPushButton, QLineEdit {
            color: white;
            font-size: 12pt;
            }
        """)

    # --------------------------
    # UI 초기화
    # --------------------------
    def setup_recent_files_ui(self):
        top_row = QHBoxLayout()
        self.cmb_recent = QComboBox()
        self.cmb_recent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_open_recent = QPushButton("최근 파일 열기")
        self.btn_open_recent.clicked.connect(self.open_recent_selected)
        top_row.addWidget(QLabel("최근 파일:"))
        top_row.addWidget(self.cmb_recent)
        top_row.addWidget(self.btn_open_recent)
        self.ui.verticalLayout.insertLayout(1, top_row)

    def setup_quick_keywords_ui(self):
        kw_row = QHBoxLayout()
        self.chk_norae = QCheckBox("노래방")
        self.chk_cafe = QCheckBox("카페")
        kw_row.addWidget(QLabel("빠른 키워드:"))
        kw_row.addWidget(self.chk_norae)
        kw_row.addWidget(self.chk_cafe)
        kw_row.addStretch()
        self.ui.verticalLayout.insertLayout(4, kw_row)

    def setup_result_ui(self):
        self.lbl_summary = QLabel("")
        self.lbl_summary.setAlignment(Qt.AlignCenter)
        self.ui.verticalLayout.insertWidget(7, self.lbl_summary)

        self.table = QTableWidget()
        self.ui.verticalLayout.insertWidget(8, self.table)

        charts_row = QHBoxLayout()
        self.btn_chart_category = QPushButton("카테고리 차트")
        self.btn_chart_month = QPushButton("월별 지출 차트")
        self.btn_chart_category.clicked.connect(self.show_category_chart)
        self.btn_chart_month.clicked.connect(self.show_month_chart)
        charts_row.addWidget(self.btn_chart_category)
        charts_row.addWidget(self.btn_chart_month)
        self.ui.verticalLayout.insertLayout(9, charts_row)


    # ======================
    # 공통 유틸 메서드
    # ======================
    def load_excel_from_path(self, path: str) -> pd.DataFrame:
        """엑셀 파일을 읽어서 DataFrame 반환"""
        try:
            try:
                df = pd.read_excel(path, engine="openpyxl", header=1)
            except:
                df = pd.read_excel(path, engine="openpyxl")
            logger.info("엑셀 파일 로드 성공: %s", path)
            return df
        except Exception as e:
            logger.exception("엑셀 파일 로드 실패: %s", path)
            raise

    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """가맹점/금액/날짜 전처리"""
        df.columns = df.columns.str.strip()
        if COL_STORE in df.columns:
            df[COL_STORE] = normalize_text_series(df[COL_STORE])
            df = df[~df[COL_STORE].isin(["이용하신 가맹점", "올라운드 선택1 할인"])]
        if COL_AMOUNT in df.columns:
            df[COL_AMOUNT] = pd.to_numeric(df[COL_AMOUNT], errors="coerce").fillna(0)
            
        df = normalize_DT_column(df)
        
        df["_is_tx"] = True
        if COL_STORE in df.columns:
            df["_is_tx"] &= df[COL_STORE].astype(str).str.strip().ne("") & df[COL_STORE].notna()
        if COL_AMOUNT in df.columns:
            amt = pd.to_numeric(df[COL_AMOUNT], errors="coerce").fillna(0)
            df["_is_tx"] &= amt.abs() > 0
            
        return df

    def show_chart(self, title: str, plot_fn):
        """공통 차트 다이얼로그 표시"""
        dlg = MplDialog(title, plot_fn)
        self.chart_windows.append(dlg)
        dlg.show()
        dlg.raise_()

    # ======================
    # 최근 파일 관리
    # ======================
    def load_recent_files(self):
        self.cmb_recent.clear()
        files = []
        if os.path.exists(RECENTS_PATH):
            try:
                with open(RECENTS_PATH, "r", encoding="utf-8") as f:
                    files = json.load(f)
            except:
                files = []
        for p in files:
            if os.path.exists(p):
                self.cmb_recent.addItem(p)
        if self.cmb_recent.count() == 0:
            self.cmb_recent.addItem("(기록 없음)")

    def save_recent_file(self, path: str):
        files = []
        if os.path.exists(RECENTS_PATH):
            try:
                with open(RECENTS_PATH, "r", encoding="utf-8") as f:
                    files = json.load(f)
            except:
                files = []
        files = [path] + [p for p in files if p != path]
        files = files[:10]
        with open(RECENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
        self.load_recent_files()

    def open_recent_selected(self):
        text = self.cmb_recent.currentText()
        if text and text != "(기록 없음)" and os.path.exists(text):
            try:
                self.df = self.load_excel_from_path(text)
                self.df = self.preprocess_dataframe(self.df)
                self.file_path = text
                QMessageBox.information(self, "파일 선택됨", f"선택된 파일:\n{self.file_path}")
            except Exception as e:
                QMessageBox.critical(self, "에러", f"최근 파일을 불러오는 중 오류 발생:\n{e}")
        else:
            QMessageBox.warning(self, "알림", "열 수 있는 최근 파일이 없습니다.")

    # ======================
    # 파일 불러오기
    # ======================
    def load_excel_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        try:
            self.df = self.load_excel_from_path(file_path)
            self.df = self.preprocess_dataframe(self.df)
            self.file_path = file_path
            self.save_recent_file(file_path)
            QMessageBox.information(self, "파일 선택됨", f"선택된 파일:\n{self.file_path}")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"엑셀 파일을 불러오는 중 오류 발생:\n{e}")

    # ======================
    # 키워드 분석
    # ======================
    def run_keyword_analysis(self):
        if self.df is None:
            QMessageBox.warning(self, "경고", "먼저 엑셀 파일을 불러오세요.")
            return

        df = self.df.copy()
        manual_kw = self.ui.input_keyword.text().strip()
        keywords = []
        if self.chk_norae.isChecked():
            keywords.append("노래방")
        if self.chk_cafe.isChecked():
            keywords.append("카페")
        if manual_kw:
            keywords.extend([k.strip() for k in manual_kw.split(",") if k.strip()])

        try:
            if COL_STORE not in df.columns or COL_AMOUNT not in df.columns:
                raise ValueError(f"'{COL_STORE}' 또는 '{COL_AMOUNT}' 컬럼이 없습니다.")

            # 키워드 필터
            if keywords:
                mask = pd.Series(False, index=df.index)
                for kw in keywords:
                    mask |= df[COL_STORE].str.contains(kw, case=False, regex=False, na=False)
                self.filtered = df[mask].copy()
            else:
                self.filtered = df.copy()

            matched = len(self.filtered)
            total = float(self.filtered[COL_AMOUNT].sum())
            logger.info("키워드 분석 완료: 매칭 %d건, 합계 %.0f원", matched, total)

            # 결과 표시
            self.populate_table(self.filtered, "DT")
            self.ui.lbl_sum_result.setText(f"합산 결과: {total:,.0f} 원")
            self.lbl_summary.setText(f"매칭 {matched}건, 합계 {total:,.0f}원")

            # CSV 저장
            self.save_filtered_csv(self.filtered, keywords)

        except Exception as e:
            logger.exception("키워드 분석 중 오류")
            QMessageBox.critical(self, "에러", str(e))

    # ======================
    # 카테고리 요약 저장
    # ======================
    def save_category_summary_action(self):
        if self.df is None:
            QMessageBox.warning(self, "경고", "먼저 엑셀 파일을 불러오세요.")
            return

        try:
            summary = self.generate_category_summary()
            if summary.empty:
                QMessageBox.warning(self, "알림", "카테고리 요약 결과가 없습니다.")
                return
            self.save_category_summary_csv(summary)
            QMessageBox.information(self, "완료", "카테고리 요약 CSV가 저장되었습니다.")
        except Exception as e:
            logger.exception("카테고리 요약 저장 중 오류")
            QMessageBox.critical(self, "에러", str(e))

    # ======================
    # 보조 함수들
    # ======================
    def populate_table(self, df, date_col="DT"):
        show_cols = []
        if date_col and date_col in df.columns:
            show_cols.append(date_col)
        if COL_STORE in df.columns:
            show_cols.append(COL_STORE)
        if COL_AMOUNT in df.columns:
            show_cols.append(COL_AMOUNT)
            
        view = df[show_cols].copy()
        
        if date_col and date_col in view.columns:
            view[date_col] = pd.to_datetime(view[date_col], errors="coerce").dt.strftime("%y-%m-%d")
        
        if COL_AMOUNT in view.columns:
            view[COL_AMOUNT] = view[COL_AMOUNT].map(lambda x: f"{x:,.0f}")

        self.table.clear()
        self.table.setColumnCount(len(view.columns))
        self.table.setRowCount(len(view))
        self.table.setHorizontalHeaderLabels([str(c) for c in view.columns])

        for r, (_, row) in enumerate(view.iterrows()):
            for c, col_name in enumerate(view.columns):
                item = QTableWidgetItem(str(row[col_name]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)
                
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)

    def save_filtered_csv(self, df, keywords):
        out_df = df.copy()
        total = out_df[COL_AMOUNT].sum()
        total_row = {col: "" for col in out_df.columns}
        total_row[COL_STORE] = "합계"
        total_row[COL_AMOUNT] = total
        out_df = pd.concat([out_df, pd.DataFrame([total_row])], ignore_index=True)

        now = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
        kw_text = "_".join(keywords) if keywords else "전체"
        filename = f"{kw_text}_내역_{now}.csv"
        out_df.to_csv(filename, encoding="utf-8-sig", index=False)

    def generate_category_summary(self):
        df = self.preprocess_dataframe(self.df.copy())
        df["카테고리"] = df[COL_STORE].apply(infer_category)
        return df.groupby("카테고리", as_index=False)[COL_AMOUNT].sum()

    def save_category_summary_csv(self, summary):
        now = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
        filename = f"카테고리_요약_{now}.csv"
        summary.to_csv(filename, encoding="utf-8-sig", index=False)

    # --------------------------
    # 차트 표시
    # --------------------------
    def show_category_chart(self):
        if self.df is None or self.filtered is None:
            QMessageBox.warning(self, "경고", "먼저 엑셀 파일을 불러오고 키워드 분석을 실행하세요.")
            return
        summary = self.generate_category_summary()
        if summary.empty:
            return
        self.show_chart("카테고리 차트", lambda ax: (
            ax.bar(summary["카테고리"], summary[COL_AMOUNT]),
            ax.set_title("카테고리별 지출"),
            ax.tick_params(axis="x", rotation=20)
        ))

    def show_month_chart(self):
        if self.df is None or self.filtered is None:
            QMessageBox.warning(self, "경고", "먼저 엑셀 파일을 불러오고 키워드 분석을 실행하세요.")
            return
        base = self.df.copy()
        if "DT" not in base.columns:
            base = self.preprocess_dataframe(base)

        # 실제 거래만 사용
        base = base[base.get("_is_tx", True)].copy()

        # 차트를 그리려면 날짜가 필요하므로, DT가 있는 행만 집계(원본 삭제 아님)
        chart_df = base.dropna(subset=["DT"]).copy()
        if chart_df.empty:
            QMessageBox.information(self, "알림", "차트로 표시할 유효한 날짜가 없습니다.")
            return

        chart_df["YYYY-MM"] = chart_df["DT"].dt.strftime("%Y-%m")
        month_summary = (chart_df.groupby("YYYY-MM", as_index=False)[COL_AMOUNT]
                                .sum()
                                .sort_values("YYYY-MM"))

        self.show_chart("월별 지출 차트", lambda ax: (
            ax.bar(month_summary["YYYY-MM"], month_summary[COL_AMOUNT]),
            ax.set_title("월별 지출"),
            ax.tick_params(axis="x", rotation=45)
        ))

# ===============================
# 실행부
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelSumApp()
    window.show()
    sys.exit(app.exec())