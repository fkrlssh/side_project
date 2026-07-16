# A2A × VLM: 멀티에이전트 시각 정보 오염 방지 연구 프로젝트 기획서

## 1. 프로젝트 개요

**작업 제목(가안):** Visual-to-Textual Injection Relay: A2A 기반 멀티에이전트 시스템에서 VLM을 매개로 한 오염 전파 위협과 방어

**한 줄 요약:** A2A(Agent-to-Agent) 프로토콜로 연결된 멀티에이전트 시스템에서, VLM이 이미지 안의 악성/오염된 지시를 텍스트로 변환하는 순간 기존 텍스트 레벨 보안 필터를 우회하여 하위 에이전트(코드 실행, 파일 접근 등)로 전파되는 새로운 오염 경로를 규명하고, 이를 막기 위한 프로토콜 확장 및 방어 메커니즘을 제안한다.

---

## 2. 배경

### 2.1 A2A 프로토콜
- Google이 2025년 4월 발표, 이후 Linux Foundation 산하로 이관되어 오픈 거버넌스 체계로 운영 중
- Agent Card(JSON-LD 기반 능력 발견), Task(작업 위임 및 상태 관리), JSON-RPC 2.0 + SSE 기반 메시지 교환이 핵심 구성 요소
- MCP(에이전트-툴 연결)와 상호 보완적 관계이며, "MCP는 툴에 대한 렌치, A2A는 에이전트 간의 대화"로 비유됨
- 2026년 4월 기준 150개 이상 기업이 프로덕션에 도입, Python/JS/Java/Go/.NET SDK 지원

### 2.2 기존 A2A 보안 연구 동향
이미 다음과 같은 공격 유형들이 문서화되어 있음:

| 공격 유형 | 설명 |
|---|---|
| Agent Card Spoofing | 위조된 Agent Card로 신뢰를 얻어 작업 탈취 |
| Agent Session Smuggling | 상태 유지 세션에 숨은 지시를 끼워 넣어 컨텍스트 오염 |
| Transitive Prompt Injection | 하나의 오염된 입력이 연쇄적으로 여러 에이전트에 전파 |
| Cross-Agent Task Escalation | 위조 자격증명으로 권한 상승 |
| Multi-Agent 임의 코드 실행 | 에이전트 간 거짓 정보 전달로 코드 실행 에이전트가 악성 파일 실행 |

**공통점:** 위 사례들은 모두 텍스트/로그/문서/JSON 레벨에서 발생하는 오염이며, **이미지(시각 정보)가 오염의 진입점이 되는 경우는 아직 명시적으로 다뤄지지 않음.**

### 2.3 연구 공백 (Gap)
- VLM은 이미지 안에 숨겨진 텍스트, 스테가노그래피, 적대적 패턴을 "이미지에 대한 설명"으로 변환해 텍스트 출력을 만들어냄
- 이 텍스트 출력이 A2A 메시지로 하위 에이전트에 전달되면, 수신 에이전트는 이를 "다른 에이전트가 이미 검증한 시각 정보 요약"으로 신뢰
- 기존 텍스트 인젝션 필터/검증 로직은 이 경로를 놓칠 가능성이 높음 → **진짜 오염 진입점은 이미지인데, 방어는 텍스트 레벨에만 걸려 있는 비대칭 구조**

---

## 3. 오염(Contamination)의 정의 — 연구 범위 확정

본 연구에서 다루는 오염은 아래 4가지 중 **3번과 4번의 결합**에 집중한다.

1. ~~프롬프트 인젝션 전파~~ (기존 연구에서 다수 다룸 — 참고만)
2. ~~컨텍스트/상태 오염~~ (기존 연구에서 다수 다룸 — 참고만)
3. **환각(hallucination) 전파**: VLM의 잘못된 시각 해석이 "검증된 사실"처럼 텍스트화되어 전달
4. **적대적 시각 입력 오염**: 이미지 자체의 조작(은닉 텍스트, adversarial perturbation)이 VLM 판단을 왜곡시키고 체인 전체로 증폭

> **핵심 프레이밍:** "Visual-to-Textual Injection Relay" — 시각 정보가 텍스트로 변환되는 그 경계(modality boundary)가 새로운 공격 표면이자 방어 사각지대다.

---

## 4. 연구 질문 (Research Questions)

- **RQ1.** VLM이 이미지에서 추출한 악성/오염된 지시가 A2A 메시지 체인을 통해 하위 에이전트(코드 실행, 파일 접근 등)까지 전파되는 비율과 조건은 무엇인가?
- **RQ2.** 기존 텍스트 레벨 인젝션 탐지/필터링 메커니즘이 이 경로에 대해 어느 정도 실패하는가?
- **RQ3.** A2A 프로토콜 확장(메시지 스키마, Agent Card, Task 상태 등)을 통해 시각 유래(vision-derived) 콘텐츠에 대한 신뢰도 태깅 및 검증 절차를 추가했을 때, 오염 전파를 얼마나 줄일 수 있는가?

---

## 5. 방법론

### 5.1 위협 모델 정의
- 공격자는 이미지 콘텐츠(파일, 웹페이지 스크린샷, 문서 스캔본 등)에 은닉 지시를 삽입
- 멀티에이전트 파이프라인: [입력 수집 에이전트] → [VLM 해석 에이전트] → (A2A) → [의사결정/코드 실행/파일 접근 에이전트]
- 공격 성공 조건: 하위 에이전트가 VLM 출력을 검증 없이 신뢰하고 실행/행동으로 옮기는 경우

### 5.2 테스트베드 구축
- A2A SDK(Python 권장) + 오픈소스 VLM(LLaVA 계열 등)으로 프로토타입 파이프라인 구성
- 실험군: (a) 무방어 베이스라인, (b) 텍스트 레벨 필터만 적용, (c) 제안하는 시각 출처 태깅 + 재검증 메커니즘 적용

### 5.3 제안 방어 메커니즘 (초안)
1. **출처 태깅(Provenance Tagging):** A2A 메시지 스키마에 콘텐츠 출처(텍스트 직접 입력 vs. VLM 파생)와 신뢰도 점수를 필드로 추가
2. **재접지(Re-grounding) 절차:** 하위 에이전트가 중요 판단 전, 원본 이미지에 재접근하여 별도 VLM 인스턴스로 재검증
3. **교차 검증(Cross-modal Verification):** 동일 이미지를 서로 다른 VLM으로 재해석해 결과 불일치 시 플래그
4. **승인 게이트:** 시각 정보에서 파생된 명령이 코드 실행/파일 접근 등 고위험 행동으로 이어질 경우 별도 확인 단계 강제

### 5.4 평가 지표
- 오염 전파율(Contamination Propagation Rate)
- 탐지 지연(Detection Latency)
- 방어 적용 후 정상 태스크 정확도 저하폭(false positive에 따른 성능 손실)
- 프로토콜 오버헤드(추가 지연/메시지 크기)

---

## 6. 주요 참고 문헌 (초기 리스트)

- Google A2A Protocol 공식 문서 및 Linux Foundation 발표 자료
- "Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges" (arXiv:2510.23883)
- "Building A Secure Agentic AI Application Leveraging A2A Protocol" (arXiv:2504.16902) — MAESTRO 위협 모델링
- "When AI Agents Go Rogue: Agent Session Smuggling Attack in A2A Systems" (Unit42, Palo Alto Networks)
- "From Prompt Injections to Protocol Exploits" (arXiv:2506.23260)
- "A2AS: Agentic AI Runtime Security and Self-Defense" (arXiv:2510.13825)
- "Multi-Agent Systems Execute Arbitrary Malicious Code" (arXiv:2503.12188)
- "Governance Gaps in Agent Interoperability Protocols" (arXiv:2606.31498)
- "Beyond Message Passing: A Semantic View of Agent Communication Protocols" (arXiv:2604.02369)

> 위 목록은 초기 스캐닝 결과이며, 본격적인 집필 전 각 논문의 방법론/실험 설계를 상세히 리뷰할 필요가 있음.

---

## 7. 예상 기여점 (Contributions)

1. A2A 기반 멀티에이전트 시스템에서 VLM을 매개로 한 오염 전파를 최초로 체계화한 위협 분류(taxonomy)
2. 실증 테스트베드를 통한 전파율/탐지율 정량 분석
3. A2A 프로토콜 확장안(출처 태깅, 재접지 절차) 제안 및 오버헤드 대비 방어 효과 평가

---

## 8. 다음 단계 (Action Items)

- [ ] 선행 연구 상세 리뷰 및 갭 분석 표 작성
- [ ] 테스트베드용 VLM/A2A SDK 선정 및 개발 환경 구축
- [ ] 은닉 지시 삽입 기법(스테가노그래피/적대적 패턴) 조사 및 실험용 이미지셋 설계
- [ ] 위협 모델 다이어그램 작성
- [ ] 방어 메커니즘 프로토타입 구현 계획 수립
- [ ] 투고 학회/저널 후보 리스트업 (보안 학회 vs. AI/ML 학회 방향 결정)

---

*본 문서는 2026년 7월 기준 웹 검색 결과를 바탕으로 작성된 초기 기획서이며, 실제 집필 과정에서 스코프와 방법론은 조정될 수 있음.*
