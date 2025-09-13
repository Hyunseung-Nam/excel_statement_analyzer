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
        self.ui.btn_calculate.clicked.connect(self.filter_and_export)
        
        self.ui.btn_keyword_noraebang.clicked.connect(
            lambda: self.ui.input_keyword.setText("노래방")
        )

    def load_excel(self):
        """엑셀 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        self.file_path = file_path
        QMessageBox.information(self, "파일 선택됨", f"선택된 파일:\n{self.file_path}")

    def filter_and_export(self):
        """키워드 검색 후 합산 + CSV 저장"""
        if not self.file_path:
            QMessageBox.warning(self, "경고", "먼저 엑셀 파일을 선택하세요.")
            return

        keyword = self.ui.input_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, "경고", "검색할 키워드를 입력하세요.")
            return

        try:
            # 엑셀 읽기
            try:
                df = pd.read_excel(self.file_path, engine="openpyxl", header=1)
                logger.info("엑셀 로드 완료")
            except Exception as e:
                logger.exception("엑셀 파일 읽기 실패")
                QMessageBox.critical(self, "에러", f"엑셀 파일을 불러오지 못했습니다.\n\n{e}")
                return

            # 필수 컬럼 확인
            if "이용하신 가맹점" not in df.columns or "이용금액" not in df.columns:
                msg = "엑셀에 '이용하신 가맹점' 또는 '이용금액' 컬럼이 없습니다."
                QMessageBox.critical(self, "에러", msg)
                logger.error("필수 컬럼 누락: %s", msg)
                return

            # 이용금액을 안전하게 숫자로 변환(문자/빈값은 NaN→0)
            df["이용금액"] = pd.to_numeric(df["이용금액"], errors="coerce").fillna(0)
            
            col = df["이용하신 가맹점"].astype(str)
            col = (col
                .str.replace("\u200b", "", regex=False)  # zero-width space
                .str.replace("\xa0", " ", regex=False)   # non-breaking space
                .str.replace(r"\s+", " ", regex=True)    # 연속 공백 한 칸으로
                .str.strip()
            )
            mask = col.str.contains(keyword, case=False, regex=False, na=False)
            filtered = df[mask]
            matched = len(filtered)
            total = float(filtered["이용금액"].sum())
            self.ui.lbl_sum_result.setText(f"합산 결과: {total:,.0f} 원")
            
            # 매치 결과 확인
            if matched == 0:
                logger.warning("키워드 '%s'로 매칭된 행이 없습니다.", keyword)
                QMessageBox.information(
                self, " 검색 결과 없음", f"키워드 '{keyword}'와 관련된 내역이 없습니다."
                )
                return  # CSV 저장하지 않고 종료
            
            # CSV 저장
            now = pd.Timestamp.now()
            timestamp_str = now.strftime("%Y%m%d")
            filename = f"{keyword}_내역_{timestamp_str}.csv"
            try:
                filtered.to_csv(filename, encoding="utf-8-sig", index=False)
                QMessageBox.information(self, "저장 완료", f"CSV 파일로 저장되었습니다:\n{filename}")
            except Exception as e:
                logger.exception("CSV 저장 실패")
                QMessageBox.critical(self, "저장 실패", f"CSV 저장 중 오류 발생:\n{e}")
            
            if matched == 0:
                logger.warning("키워드 '%s' 로 매칭된 행이 없습니다.", keyword)

        except Exception as e:
            logger.exception("처리 중 알 수 없는 오류")
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
