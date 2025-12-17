# Study Assistance Toolkit

PPTX 슬라이드 내용을 추출해 한국어 요약 PDF를 만들고, 원하면 객관식 연습 문제 PDF까지 자동으로 생성하는 간단한 CLI입니다.

## 기능
- **슬라이드 텍스트 추출**: python-pptx로 슬라이드별 텍스트를 읽고 빈 슬라이드는 건너뜁니다.
- **요약 PDF 생성**: 슬라이드별 핵심을 bullet point로 묶고, 별도 "핵심 정리" 섹션을 요청하도록 프롬프트를 구성합니다.
- **연습 문제 PDF 생성(옵션)**: 원하는 문항 수만큼 문제, 4지선다 선택지, 정답, 짧은 해설을 포함합니다.
- **기본값 제공**: 모델(gpt-4o-mini), 출력 파일 이름(summary.pdf), 문제 수(5문항) 기본 제공.

## 사전 준비
1. Python 3.10+ 환경
2. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
3. OpenAI API 키 설정
   ```bash
   export OPENAI_API_KEY="YOUR_API_KEY"
   ```

## 사용법
PPTX 요약 PDF 생성:
```bash
python main.py path/to/deck.pptx --summary-pdf output_summary.pdf
```

요약 + 연습 문제 PDF 생성:
```bash
python main.py path/to/deck.pptx \
  --summary-pdf output_summary.pdf \
  --quiz-pdf output_quiz.pdf \
  --questions 8 \
  --model gpt-4o-mini
```

## 주요 구현
- `extract_slide_text`: 슬라이드 텍스트 추출, 공백 슬라이드 무시
- `build_summary_prompt`, `build_quiz_prompt`: 한국어 요약/퀴즈 지시문 생성
- `run_llm`: OpenAI Chat Completions 호출 (환경 변수 또는 `--api-key` 사용)
- `write_pdf`: fpdf2로 제목+섹션 본문을 포함한 PDF 작성
- 기본적인 입력 검증: PPTX 미존재 시 오류, 텍스트가 없으면 실행 중단

## 참고
- 슬라이드 이미지의 텍스트는 추출되지 않습니다.
- 생성 결과는 모델 설정, 슬라이드 콘텐츠에 따라 달라질 수 있으니 프롬프트를 필요에 맞게 수정하세요.
