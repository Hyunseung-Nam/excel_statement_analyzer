# 📊 엑셀 명세서 금액 합산기

PySide6 + pandas 기반 GUI 프로그램으로, 카드/은행사에서 받은 엑셀 명세서에서 특정 가맹점을 검색해
이용금액 합계를 계산하며, 결과는 화면에 표시되고 동시에 CSV 파일로 저장됩니다.

---

## ✨ 기능
- 엑셀 파일 불러오기
- 가맹점 키워드 검색
- 해당 행의 이용금액 합산
- 합산 결과를 화면에 표시
- 실행 로그 기록 (expense_sum.log)
- 결과를 CSV 파일로 저장

---

## 🖥️ 실행 화면
- 상단: 프로그램 제목 라벨
- 버튼 1: **엑셀 파일 불러오기**
- 입력창: **검색할 가맹점 키워드 입력**
- 버튼 2: **합산하기**
- 하단 라벨: **합산 결과 출력**

---

## 🚀 설치 및 실행 방법

### 1. 저장소 클론
```bash
1. 레포지토리 복사
git clone https://github.com/Hyunseung-Nam/ExpenseCalculator.git
cd ExpenseCalculator

2. 가상환경 설정(선택사항이지만 권장)
python -m venv .venv
source .venv/bin/activate    # Mac/Linux
.venv/Scripts/activate       # Windows

3. 라이브러리 설치
pip install -r requirements.txt

4. 실행
python src/main.py
```

---

## 📝 로그(logging)

- 실행 로그가 **`expense_sum.log`** 파일에 저장됩니다.    
- 로그에 기록되는 내용:  
  - 선택한 엑셀 파일 경로  
  - 입력한 키워드  
  - 매칭된 행 개수  
  - 합산 금액  
  - 오류 발생 시 예외 메시지

---

## 💾 CSV 저장
- 검색 결과는 키워드_내역_YYYYMMDD.csv 형식으로 저장됩니다.
- 매칭된 행이 없을 경우, CSV는 생성되지 않고 안내 메시지가 표시됩니다.
- CSV 저장 시 인코딩은 utf-8-sig로 지정되어, Excel에서 바로 열 수 있습니다.

---
