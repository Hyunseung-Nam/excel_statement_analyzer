# 📊 엑셀 명세서 금액 합산기

PySide6 + pandas 기반 GUI 프로그램으로, 카드/은행사에서 내려받은 **엑셀 명세서**에서  
특정 가맹점 키워드를 검색하고 해당 **이용금액의 합계**를 계산해줍니다.  

---

## ✨ 기능
- 엑셀 파일 불러오기
- 가맹점 키워드 검색
- 해당 행의 이용금액 합산
- 결과 라벨에 표시
- 실행 로그 기록 (expense_sum.log)

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
