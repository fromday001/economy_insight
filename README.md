# 📈 에코노미 인사이트 (EconInsight)
> **초보자를 위한 경제 공부 & 데일리 마켓 브리핑 플랫폼**  
> 100% 클라우드 완전 무료 자동화 (PC를 꺼둬도 24시간 작동)

---

## 🌟 주요 특징

1. **완전 무료 & 서버리스 (Zero-Cost, Zero-Server)**
   - 별도의 유료 서버(AWS, Vercel 등) 필요 없음
   - **GitHub Pages**(무료 웹 호스팅) + **GitHub Actions**(무료 클라우드 스케줄러) 기반 작동
   - 사용자의 **PC나 노트북을 꺼두어도 깃허브 클라우드가 24시간 365일 자동으로 실행**

2. **매일 아침 8시 자동 업데이트 (KST)**
   - 매일 글로벌 6대 시장 지표(나스닥, S&P500, 코스피, 원·달러 환율, 미 국채 10년물, WTI 유가) 자동 수집
   - Google News 경제 RSS 헤드라인 수집
   - Google Gemini AI(무료 티어)를 통해 3줄 핵심 요약 및 초보자를 위한 공부 포인트 자동 작성
   - 결과 데이터를 `data/daily_briefings.json`에 자동 커밋 & 푸시하여 웹 화면 갱신

3. **초보자를 위한 경제 시뮬레이터 & 인터랙티브 기능**
   - 핵심 경제 개념(금리, 환율, 인플레이션 등) 탭별 학습
   - "금리가 오르면 주가는 어떻게 될까?" 경제 인과관계 시뮬레이터
   - 3분 경제 상식 퀴즈 & 투자 성향 테스트
   - 다크 모드 / 라이트 모드 지원 및 반응형 모바일 최적화

---

## 🚀 3분 만에 내 깃허브에 배포하고 자동화 켜기

### 1단계: 깃허브(GitHub) 새 저장소 만들기
1. [GitHub.com](https://github.com)에 로그인 후 우측 상단의 **[+] -> [New repository]** 클릭
2. 저장소 이름(Repository name)에 `econ-insight` (또는 원하는 이름) 입력
3. **Public**(공개)으로 설정 후 **[Create repository]** 클릭

### 2단계: 코드 업로드 (푸시)
이 폴더(`econ-learning-platform`)에서 터미널을 열고 아래 명령어를 순서대로 실행합니다:

```bash
git init
git add .
git commit -m "feat: 에코노미 인사이트 자동화 플랫폼 첫 배포"
git branch -M main
git remote add origin https://github.com/당신의깃허브아이디/저장소이름.git
git push -u origin main
```

*(Git CLI가 없는 경우: 깃허브 저장소 화면에서 **"uploading an existing file"**을 눌러 폴더 내 파일들을 통째로 드래그 앤 드롭하셔도 됩니다)*

---

### 3단계: GitHub Pages 켜기 (무료 웹사이트 주소 생성)
1. 깃허브 저장소 상단 메뉴의 **[Settings]** 클릭
2. 좌측 메뉴에서 **[Pages]** 클릭
3. **Branch** 설정에서 `None` -> **`main`** 브랜치로 변경 후 **[Save]** 클릭
4. 1~2분 후 상단에 생성된 무료 웹사이트 주소(`https://<아이디>.github.io/<저장소이름>/`)로 접속 가능합니다!

---

### 4단계: 깃허브 액션 권한 설정 (자동 커밋 허용)
클라우드 스케줄러가 매일 데이터를 자동 업데이트하고 저장할 수 있도록 권한을 허용합니다:
1. 저장소 **[Settings]** -> 좌측 **[Actions]** -> **[General]** 클릭
2. 화면 맨 아래의 **Workflow permissions** 섹션으로 이동
3. **`Read and write permissions`** 체크 선택 후 **[Save]** 클릭

---

### 5단계 (선택사항): Gemini API 무료 키 등록
> 💡 **참고**: API 키를 등록하지 않아도 내장된 **규칙 기반 분석 엔진(Rule-based NLP)**이 자동으로 작동하므로 바로 실행 가능합니다! 더 정교한 AI 요약을 원하실 경우 무료 API 키를 등록하세요.

1. [Google AI Studio](https://aistudio.google.com/)에서 무료 API Key 발급 (비용 0원)
2. 깃허브 저장소 **[Settings]** -> **[Secrets and variables]** -> **[Actions]** 클릭
3. **[New repository secret]** 버튼 클릭:
   - Name: `GEMINI_API_KEY`
   - Secret: 발급받은 API 키 붙여넣기
4. **[Add secret]** 클릭

---

## ⏰ 자동화 실행 주기 및 수동 실행

- **자동 실행**: 매일 한국 시간 **오전 08:00 (UTC 23:00)**에 클라우드에서 자동 실행됩니다.
- **수동 즉시 실행**:
  1. 깃허브 저장소 상단 **[Actions]** 탭 클릭
  2. 좌측 목록에서 **[Daily Economic Briefing Auto Updater]** 클릭
  3. 우측의 **[Run workflow]** 버튼 클릭 후 초록색 버튼 클릭
  4. 약 30초 후 최신 경제 뉴스와 지표로 즉시 갱신됩니다!
