"""
엑셀 명세서 금액 합산기
----------------------
PySide6 GUI + pandas 기반 프로그램

기능:
1. 엑셀 파일 선택
2. "이용하신 가맹점" 컬럼에서 키워드 검색
3. 해당 행들의 "이용금액" 합산
4. 합산 결과를 GUI 라벨에 표시
"""

import sys, logging
import pandas as pd
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication
from ui_main_window import Ui_MainWindow

# ===== 로거 설정 =====
logging.basicConfig(
    level=logging.INFO,                          # 파일에는 INFO 이상 모두 기록
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='expense_sum.log',                  # 로그를 쓸 파일
    filemode='a'                                 # 이어쓰기 모드
)

logger = logging.getLogger(__name__)

class ExcelSumApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.file_path = None

        self.setWindowTitle("엑셀 명세서 금액 합산기")
        self.ui.btn_load_excel.clicked.connect(self.load_excel)
        self.ui.btn_calculate.clicked.connect(self.calculate_sum)

    def load_excel(self):
        """엑셀 파일 선택 다이얼로그를 띄우고 경로 저장"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            logger.info("파일 선택 취소됨")
            return

        self.file_path = file_path
        logger.info("파일 선택됨: %s", self.file_path)
        QMessageBox.information(self, "파일 선택됨", f"선택된 파일:\n{self.file_path}")

    def calculate_sum(self):
        """키워드로 가맹점 검색 후 이용금액 합산"""
        if not self.file_path:
            QMessageBox.warning(self, "경고", "먼저 엑셀 파일을 선택하세요.")
            logger.warning("엑셀 파일이 선택되지 않음")
            return

        keyword = self.ui.input_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, "경고", "검색할 키워드를 입력하세요.")
            logger.warning("키워드 미입력")
            return

        try:
            # header=1: 2행을 컬럼명으로 사용(1행 비어있는 파일 대응)
            df = pd.read_excel(self.file_path, engine="openpyxl", header=1)
            logger.info("엑셀 로드 완료")

            # '이용하신 가맹점', '이용금액' 컬럼 확인
            if "이용하신 가맹점" not in df.columns or "이용금액" not in df.columns:
                msg = "엑셀에 '이용하신 가맹점' 또는 '이용금액' 컬럼이 없습니다."
                QMessageBox.critical(self, "에러", msg)
                logger.error("필수 컬럼 누락: %s", msg)
                return

            # 이용금액을 안전하게 숫자로 변환(문자/빈값은 NaN→0)
            df["이용금액"] = pd.to_numeric(df["이용금액"], errors="coerce").fillna(0)

            # 키워드 포함된 행 필터링
            mask = df["이용하신 가맹점"].astype(str).str.contains(keyword, na=False)
            filtered = df[mask]
            matched = len(filtered)

            total = float(filtered["이용금액"].sum())
            self.ui.lbl_sum_result.setText(f"합산 결과: {total:,.0f} 원")
            
            logger.info(
                "키워드: '%s', 매칭 %d건, 합계 %s원",
                keyword, matched, f"{total:,.0f}"
            )
            
            if matched == 0:
                logger.warning("키워드 '%s' 로 매칭된 행이 없습니다.", keyword)

        except Exception as e:
            logger.exception("처리 중 예외 발생")
            QMessageBox.critical(self, "에러", f"처리 중 오류 발생:\n{e}")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 메시지박스 가독성 향상(흰 배경/검은 글씨)
    app.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: black;
            font-size: 12pt;
        }
        QMessageBox QPushButton {
            color: black;
        }
    """)
    window = ExcelSumApp()
    window.show()
    sys.exit(app.exec())
