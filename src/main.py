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
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt
from ui_main_window import Ui_MainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ===== 로거 설정 =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="expense_sum.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

# 최근 파일 저장 JSON 경로
RECENTS_PATH = "recent_files.json"

# 컬럼 상수
COL_STORE = "이용하신 가맹점"
COL_AMOUNT = "이용금액"

# 카테고리 분류 규칙
CATEGORY_MAP = OrderedDict({
    "오락": ["노래방", "노래연습", "코인노래", "PC방", "스크린", "볼링", "당구", "탁구"],
    "식비": ["카페", "커피", "스타벅스", "이디야", "투썸", "빽다방", "버거", "치킨", "KFC", "맥도날드", "피자", "이마트24", "GS25", "CU", "편의점"],
    "교통": ["주유소", "주유", "택시", "버스", "지하철", "고속도로", "하이패스", "SRT", "KTX", "ITX", "항공"],
    "쇼핑": ["마트", "백화점", "쿠팡", "G마켓", "11번가", "무신사"],
    "기타": []
})

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
            if keyword.lower() in name.lower():
                return cat
    return "기타"

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

        # 엑셀 데이터 저장용
        self.file_path = None
        self.df = None
        self.filtered = None

        self.setWindowTitle("엑셀 명세서 금액 합산기")
        logger.info("프로그램 실행 시작")

        # 버튼 이벤트 연결
        self.ui.btn_load_excel.clicked.connect(self.load_excel_dialog)
        self.ui.btn_calculate.setText("키워드 분석하기")
        self.ui.btn_calculate.clicked.connect(self.run_keyword_analysis)
        self.btn_save_category = QPushButton("카테고리 요약 저장하기")
        self.btn_save_category.clicked.connect(self.save_category_summary_action)
        self.ui.verticalLayout.addWidget(self.btn_save_category)

        # --------------------------
        # 동적 UI 삽입
        # --------------------------
        # 최근 파일 콤보박스 + 버튼
        top_row = QHBoxLayout()
        self.cmb_recent = QComboBox()
        self.cmb_recent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_open_recent = QPushButton("최근 파일 열기")
        self.btn_open_recent.clicked.connect(self.open_recent_selected)
        top_row.addWidget(QLabel("최근 파일:"))
        top_row.addWidget(self.cmb_recent)
        top_row.addWidget(self.btn_open_recent)
        self.ui.verticalLayout.insertLayout(1, top_row)

        # 키워드 체크박스
        kw_row = QHBoxLayout()
        self.chk_norae = QCheckBox("노래방")
        self.chk_cafe = QCheckBox("카페")
        kw_row.addWidget(QLabel("빠른 키워드:"))
        kw_row.addWidget(self.chk_norae)
        kw_row.addWidget(self.chk_cafe)
        kw_row.addStretch()
        self.ui.verticalLayout.insertLayout(4, kw_row)

        # 검색 결과 요약 라벨
        self.lbl_summary = QLabel("")
        self.lbl_summary.setAlignment(Qt.AlignCenter)
        self.ui.verticalLayout.insertWidget(7, self.lbl_summary)

        # 검색 결과 테이블
        self.table = QTableWidget()
        self.ui.verticalLayout.insertWidget(8, self.table)

        # 차트 버튼
        charts_row = QHBoxLayout()
        self.btn_chart_category = QPushButton("카테고리 차트")
        self.btn_chart_month = QPushButton("월별 지출 차트")
        self.btn_chart_category.clicked.connect(self.show_category_chart)
        self.btn_chart_month.clicked.connect(self.show_month_chart)
        charts_row.addWidget(self.btn_chart_category)
        charts_row.addWidget(self.btn_chart_month)
        self.ui.verticalLayout.insertLayout(9, charts_row)

        # 최근 파일 목록 로드
        self.load_recent_files()

        self.setStyleSheet("""
            QLabel, QPushButton, QLineEdit {
            color: white;
            font-size: 12pt;
            }
        """)

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
        if COL_STORE in df.columns:
            df[COL_STORE] = normalize_text_series(df[COL_STORE])
        if COL_AMOUNT in df.columns:
            df[COL_AMOUNT] = pd.to_numeric(df[COL_AMOUNT], errors="coerce").fillna(0)
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

            # 날짜 처리
            date_col_candidates = [c for c in df.columns if "일자" in c or "승인일" in c or "거래일" in c]
            date_col = date_col_candidates[0] if date_col_candidates else None
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

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
            self.populate_table(self.filtered, date_col)
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
    def populate_table(self, df, date_col):
        show_cols = []
        if date_col and date_col in df.columns:
            show_cols.append(date_col)
        for c in [COL_STORE, COL_AMOUNT]:
            if c in df.columns and c not in show_cols:
                show_cols.append(c)

        view = df[show_cols].copy()
        if COL_AMOUNT in view.columns:
            view[COL_AMOUNT] = view[COL_AMOUNT].map(lambda x: f"{x:,.0f}")

        self.table.clear()
        self.table.setColumnCount(len(view.columns))
        self.table.setRowCount(len(view))
        self.table.setHorizontalHeaderLabels([str(c) for c in view.columns])

        for r, (_, row) in enumerate(view.iterrows()):
            for c, col_name in enumerate(view.columns):
                item = QTableWidgetItem(str(row[col_name]))
                if col_name == COL_AMOUNT:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()

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
        date_col_candidates = [c for c in self.df.columns if "일자" in c or "승인일" in c or "거래일" in c]
        if not date_col_candidates:
            return
        date_col = date_col_candidates[0]
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
        df["YYYY-MM"] = df[date_col].dt.to_period("M").astype(str)
        month_summary = df.groupby("YYYY-MM", as_index=False)[COL_AMOUNT].sum()
        if month_summary.empty:
            return
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