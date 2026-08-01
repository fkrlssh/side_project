# PPT 학습노트 도우미

PPT를 입력하면 로컬에서 돌아가는 오픈소스 VLM이 페이지(슬라이드)별 텍스트와 이미지를 읽고,
직전 페이지 위주로 가중치가 감쇠하는 방식(LSTM forget gate와 유사)으로 강의 흐름을 반영한
통합 학습노트와 퀴즈를 생성해주는 개인 사이드 프로젝트.

## 설계 요약

- **비용**: 유료 API 없음. 오픈소스 모델만 사용.
- **실행 환경**: 로컬 GPU (RTX 3060 Ti, 8GB VRAM) 기준으로 설계.
- **슬라이드 추출**: `python-pptx`로 텍스트/이미지 분리 추출 (텍스트는 정확 추출, 이미지는 VLM이 해석).
- **VLM**: `Qwen/Qwen2-VL-2B-Instruct` (fp16 기준 ~4-5GB, 8GB 카드에 여유 있음). 이미지 해석 품질이 부족하면 `MiniCPM-V 2.6`(4bit)로 교체 검토.
- **페이지 간 문맥**: 직전 페이지일수록 크게, 오래된 페이지일수록 `context_decay_rate ** k`로 지수 감쇠 반영.
- **출력**: PPT 전체를 합친 학습노트(markdown) + 퀴즈(객관식/주관식/OX, 소스는 원본 PPT 또는 학습노트 중 요청 시 선택).
- **아키텍처**: FastAPI 백엔드 + React(Vite) 프론트엔드 분리.

## 프로젝트 구조

```
backend/
  app/
    main.py              # FastAPI 엔트리포인트
    core/config.py        # 설정 (모델명, decay rate 등)
    models/schemas.py     # pydantic 스키마
    api/                   # 라우터 (upload / notes / quiz)
    services/
      ppt_extractor.py     # python-pptx 텍스트/이미지 추출
      vlm_client.py         # Qwen2-VL-2B-Instruct 래퍼
      summarizer.py         # 페이지별 요약 + decay 컨텍스트 + 학습노트 생성
      quiz_generator.py     # 퀴즈 생성 (TODO: 모델 연동 필요)
      deck_store.py          # 업로드된 덱 인메모리 저장소
  storage/uploads/, storage/outputs/
frontend/                 # React + Vite
```

## 실행 방법

### 백엔드

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

첫 실행 시 Hugging Face에서 `Qwen/Qwen2-VL-2B-Instruct` 가중치를 자동 다운로드합니다(수 GB, 인터넷 필요).
Windows에서 CUDA 가속을 쓰려면 PyTorch를 CUDA 빌드로 별도 설치해야 할 수 있습니다
(https://pytorch.org/get-started/locally/ 에서 본인 CUDA 버전에 맞는 설치 명령 확인).

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

기본적으로 `http://localhost:5173`에서 실행되며 `http://localhost:8000` 백엔드를 호출합니다.

## 아직 안 된 것 (다음 단계)

- `quiz_generator.py`: 실제 텍스트 생성 모델 연동 (현재 `NotImplementedError` 스텁)
- `summarizer.py`의 페이지 요약: 현재는 텍스트/이미지 설명을 구조적으로 이어붙이기만 함.
  실제 "정리/요약"을 하는 텍스트 생성 호출이 필요함.
- VLM 첫 로딩/추론 실측 (3060 Ti 8GB에서 안정적으로 도는지 검증)
- 인증/영속 저장소 없음 (단일 사용자 로컬 데모 전제, `deck_store.py`가 인메모리)
