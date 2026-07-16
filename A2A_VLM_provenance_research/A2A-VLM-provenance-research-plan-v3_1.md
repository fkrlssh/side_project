# Cross-Boundary Vision Provenance: A2A 프로토콜에서 VLM 파생 콘텐츠의 신뢰 표현과 검증

**부제:** 조직 경계를 넘는 표준 에이전트 프로토콜에서, 원본 이미지 접근 불가 상황을 전제로 한 시각 출처(vision-provenance) 스키마 확장 및 방어 메커니즘

**v3 변경사항:** 2026년 7월 15일 기준 재조사에서 "A2A + provenance"를 다루는 최근 논문 4건을 추가로 확인. 이들은 모두 provenance라는 용어를 쓰지만 대상(모델 신원/품질, 에이전트 빌드 출처, 민감데이터, 통신 그래프)이 본 연구의 대상(비전 파생 콘텐츠의 생성 방식)과 다름을 확인하고, 이를 서론에 명시하는 절(2.5절)을 신설함. 이 조합(A2A × VLM × vision-provenance)은 2026.7.15 기준으로도 비어있는 자리임을 재확인.

---

## 1. 프로젝트 개요

**한 줄 요약:** A2A(Agent-to-Agent) 프로토콜로 연결된, 서로 다른 조직이 구현한 에이전트 간 통신에서, 한쪽 에이전트의 VLM이 이미지를 해석해 만든 텍스트가 프로토콜 메시지에 실려 상대 조직의 에이전트로 전달될 때 — 원본 이미지 자체는 조직 경계를 넘지 않는 경우가 많다는 제약 아래 — 이 콘텐츠의 출처와 신뢰도를 어떻게 표준화된 방식으로 표현·검증할 것인지를 다룬다.

**이전 버전(v1) 대비 변경 이유:** 초기 기획서는 "VLM 매개 오염이 멀티에이전트 시스템에 전파된다"는 문제의식이었으나, 선행연구 조사 결과 이미 유사한 문제의식으로 방어 프레임워크를 제안한 논문(Syed et al., 2025)이 존재함을 확인했다. 다만 그 논문을 포함한 기존 연구들은 모두 **하나의 조직/코드베이스가 파이프라인 전체를 통제할 수 있다는 전제** 위에 있다. 반면 A2A는 서로 다른 벤더가 만든, 코드를 공유하지 않는 에이전트 간의 표준 통신 프로토콜이다. 이 차이가 실제로 프로토콜 스펙 수준에서 빈 자리를 만든다는 것을 확인했고(3절 참조), v2는 이 지점으로 스코프를 좁힌다.

---

## 2. 배경

### 2.1 A2A 프로토콜 현황 (2026년 7월 기준)

- Google이 2025년 4월 발표, 2025년 6월 Linux Foundation으로 이관되어 오픈 거버넌스 체계로 운영
- 2025년 8월 IBM의 ACP(Agent Communication Protocol)가 A2A로 합병
- 2026년 4월 **v1.0 정식 릴리스**: Signed Agent Card(암호서명 기반 발신자 인증), 멀티테넌시, JSON-RPC/gRPC 멀티프로토콜 바인딩, 버전 협상 기능 추가. Part 구조가 단일 통합형으로 재설계됨(TextPart/FilePart/DataPart 구분 → 하나의 Part 오브젝트로 통합, `kind` 필드 대신 멤버 존재 여부로 구분)
- 2026년 4월 기준 150개 이상 기업이 프로덕션에 도입(AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP, ServiceNow 등), Python/JS/Java/Go/.NET SDK 지원, GitHub 22,000+ 스타
- Agent Card, Task(상태 기반 생명주기), Message/Artifact(Part로 구성), JSON-RPC 2.0 + SSE가 핵심 구성요소
- **AgentExtension**: 코어 스펙을 넘어서는 추가 기능을 에이전트가 선언할 수 있는 공식 확장 메커니즘. Agent Card에서 특정 확장을 `required: true`로 표시하면, 이를 지원하지 않는 클라이언트는 표준 에러로 거부됨

### 2.2 핵심 스펙 확인 사항 — 이 연구의 출발점

A2A 명세를 직접 검토한 결과, 다음이 확인됨:

- Part(Message/Artifact의 최소 구성단위)는 `metadata: Record<string, any>`라는 **완전히 비정형(free-form)** 필드를 가질 수 있으나, "이 콘텐츠가 사람이 직접 입력한 것인지, 다른 에이전트의 VLM이 이미지를 해석해 생성한 것인지"를 나타내는 표준 어휘(vocabulary)가 프로토콜 차원에서 전혀 정의되어 있지 않음
- Signed Agent Card는 **발신자(sender)의 신원**은 암호학적으로 보증하지만, **콘텐츠의 생성 방식(provenance)**은 보증하지 않음 — 서명된 에이전트가 보낸 메시지라도 그 안의 텍스트가 VLM의 오독/환각에서 나온 것인지 여부는 알 수 없음
- FilePart는 원본 파일을 base64(`FileWithBytes`) 또는 URI(`FileWithUri`)로 전달할 수 있지만, 대역폭·프라이버시·컴플라이언스 상의 이유로 **원본 이미지를 보내지 않고 VLM이 생성한 텍스트 요약만 전달하는 것**이 실무적으로 흔한 설계 선택이 될 수 있음. 이 경우 하류 에이전트는 원본에 재접근할 방법이 구조적으로 없음

### 2.3 기존 A2A 보안 연구 동향

| 공격 유형 | 설명 | 출처 |
|---|---|---|
| Agent Card Spoofing | 위조된 Agent Card로 신뢰를 얻어 작업 탈취 (v1.0의 Signed Agent Card로 부분 완화) | Habler et al., 2504.16902 |
| Agent Session Smuggling | 상태 유지 세션에 숨은 지시를 끼워 넣어 컨텍스트 오염 | Unit42 (Palo Alto Networks), 2025.11 |
| Transitive Prompt Injection / Control-flow Hijacking | 오염된 입력이 여러 에이전트로 연쇄 전파, 임의 코드 실행까지 유발 | Triedman, Jha, Shmatikov, 2503.12188 (COLM 2025) |
| Cross-Agent Task Escalation | 위조 자격증명으로 권한 상승 | 다수 |
| Runtime 방어 프레임워크 | BASIC 보안모델(행위 인증서, 인증된 프롬프트, 보안 경계 등) | A2AS, 2510.13825 |

**공통점:** 위 사례는 모두 텍스트/세션/제어흐름 레벨에서 발생하는 오염이며, 이미지가 오염의 진입점이 되는 시나리오와 그 시각 콘텐츠의 출처를 프로토콜이 어떻게 표현할지는 다루지 않는다.

### 2.4 가장 근접한 선행연구와의 관계 (반드시 짚어야 할 지점)

**Syed, Abdel Moaty & Almutairi, "Toward Trustworthy Agentic AI: A Multimodal Framework for Preventing Prompt Injection Attacks" (arXiv:2512.23557, 2025.12)**

Cross-Agent Multimodal Provenance-Aware Defense Framework를 제안. Text Sanitizer Agent + Visual Sanitizer Agent(OCR+EXIF+CLIP) + Output Validator Agent를 Provenance Ledger(modality, source, trust score 기록)로 조율하며, LangChain/GraphChain의 PromptTemplate·BaseMessage·Agent Executor를 직접 확장해서 구현. 탐지 정확도 94%, 교차모달 신뢰 누출 0.24→0.07(70% 감소), 정상 태스크 정확도 96% 유지라는 실험 결과 보고.

**본 연구와의 차이:**

| | Syed et al. (2512.23557) | 본 연구 |
|---|---|---|
| 배포 전제 | 단일 코드베이스, LangChain/GraphChain 프로세스 전체를 직접 래핑 | 서로 다른 조직이 만든, 코드 공유 없는 에이전트 간 표준 프로토콜(A2A) |
| 방어 위치 | 애플리케이션 레이어의 Python 미들웨어 | 프로토콜 스키마 레이어(Part.metadata 표준 필드 + AgentExtension) |
| 원본 이미지 가정 | 항상 같은 시스템 내에서 재접근 가능 | **원본이 조직 경계를 넘지 않을 수 있다는 것을 핵심 제약으로 명시적으로 다룸** |
| 신원 vs 출처 | 구분하지 않음 | Signed Agent Card(신원 인증)와 vision-provenance 태그(콘텐츠 출처)를 별개 축으로 분리 |

이 차이를 논문 서론에서 명시적으로 서술하고, "Syed et al.의 방식이 어떤 조건에서 적용 불가능해지는가"를 정량적으로 보이는 것이 본 연구의 동기(motivation) 서술의 핵심이 되어야 한다.

**CrossInject (Manipulating Multimodal Agents via Cross-Modal Prompt Injection, arXiv:2504.14348)**은 공격 기법(시각 잠재 정렬을 통한 인젝션) 자체를 다루는 논문으로, 본 연구의 위협모델(3.2절 참고 공격 유형)로 인용하되 방어 설계와는 별개로 다룸.

### 2.5 "Provenance" 용어의 다의성 — 인접 연구와의 구분 (2026.7.15 재조사 반영)

A2A 커뮤니티 내에서 "provenance"라는 단어는 이미 여러 다른 대상을 가리키는 데 쓰이고 있다. 본 연구가 다루는 provenance(콘텐츠가 VLM 해석으로 생성됐는지 여부)와 혼동되지 않도록, 아래 4건을 명시적으로 구분한다.

| 연구 | Provenance의 대상 | 본 연구와 다른 점 |
|---|---|---|
| Prakash, "LDP: An Identity-Aware Protocol" (arXiv:2603.08852, 2026.3) 및 후속 "The Provenance Paradox" (arXiv:2603.18043) | **모델 정체성/품질** — 어떤 LLM이 위임받은 작업을 처리했고, 자기 신고 품질 점수가 진짜인지(claimed vs. attested) | 비전 모달리티를 전혀 다루지 않음. A2A를 확장하는 대신 신규 프로토콜(LDP)을 제안. 단독저자, arXiv/ResearchSquare 프리프린트로만 존재하며 정식 학회·저널 게재는 확인되지 않음 |
| sigstore-a2a (GitHub, 진행중) | **Agent Card 자체의 빌드·저장소 출처** — 이 에이전트 코드를 누가, 어느 CI/CD에서 서명·배포했는가(SLSA) | "콘텐츠가 어떻게 생성됐는가"가 아니라 "에이전트 코드가 어디서 왔는가" — 완전히 다른 층위 |
| Louck, Stulman & Dvir, "Improving Google A2A Protocol" (arXiv:2505.12490, 2025) | 결제정보·개인정보 등 민감데이터의 과다 노출 | 프라이버시 최소화 문제이며 환각/비전 위협과 무관 |
| Dangol, "From Privacy to Workflow Integrity" (arXiv:2606.07150, 2026.6) | 통신 그래프 메타데이터(누가 누구와 언제 통신하는지)의 노출 | 트래픽 분석/메타데이터 프라이버시 문제이며 메시지 내용 자체와 무관 |

**본 연구가 명시적으로 채택하는 정의:** *Vision-provenance*란 A2A 메시지의 Part에 담긴 텍스트 콘텐츠가 (a) 사람이 직접 입력한 것인지, (b) 다른 에이전트의 추론 결과인지, (c) VLM이 이미지를 해석해 생성한 것인지를 구분하는 것을 말하며, 위 4건 중 어느 것도 이 축을 다루지 않는다.

---

## 3. 오염(Contamination)의 정의 — 연구 범위

1. ~~프롬프트 인젝션 전파~~ (참고만)
2. ~~컨텍스트/상태 오염~~ (참고만)
3. **환각(hallucination) 전파**: VLM의 잘못된 시각 해석이 "검증된 사실"처럼 텍스트화되어 전달 (비적대적)
4. **적대적 시각 입력 오염**: 이미지 자체의 조작(텍스트 오버레이형 인젝션 등)이 VLM 판단을 왜곡

3번과 4번을 하나의 방어 메커니즘으로 통합해서 다루되(오염의 "원인"이 다를 뿐 "원본 미접근 상태에서 하류 에이전트가 검증 없이 신뢰한다"는 실패 양상은 동일하기 때문), 실험에서는 두 유형을 별도 조건으로 분리해 측정한다.

> **핵심 프레이밍:** Signed Agent Card는 "누가 보냈는가"를 보증하고, 본 연구가 제안하는 vision-provenance 확장은 "무엇으로 생성됐는가"를 보증한다. 이 둘은 서로 다른 신뢰 축이며, A2A는 현재 후자를 다루지 않는다.

---

## 4. 연구 질문

- **RQ1 (개정):** `raw_evidence.available = false`(원본 이미지가 조직 경계를 넘지 않는) 조건에서 vision-derived 콘텐츠가 A2A 체인을 통해 고위험 행동(코드실행/파일접근/결제 등)까지 승인 게이트 없이 도달하는 비율은, `raw_evidence.available = true`(원본 접근 가능) 조건 대비 얼마나 차이나는가?
- **RQ2:** 기존 텍스트 레벨 인젝션 탐지 및 Syed et al. 류의 애플리케이션 레벨 방어가, 원본 이미지 미접근 조건에서 어느 정도 실패하는가?
- **RQ3:** A2A의 AgentExtension 메커니즘을 통해 vision-provenance 스키마(출처, 생성방식, 신뢰도, 원본 가용성)를 표준화했을 때, 오염 전파율과 정상 태스크 처리 성능(오탐에 따른 손실)이 각각 어떻게 변하는가?

---

## 5. 방법론

### 5.1 위협 모델

- 공격자는 이미지 콘텐츠(파일, 웹페이지 스크린샷, 문서 스캔본 등)에 텍스트 오버레이형 지시를 삽입하거나(적대적, 4번 유형), 또는 별도 조작 없이 VLM이 자연스럽게 오독하는 상황을 이용(비적대적, 3번 유형)
- 파이프라인: [입력 수집 에이전트, 조직 A] → (A2A) → [VLM 해석 에이전트, 조직 A 또는 B] → (A2A) → [의사결정/코드실행/파일접근 에이전트, 조직 C]
- 원본 이미지는 조직 A 내부에만 존재하고 A2A 메시지에는 VLM이 생성한 TextPart만 실려 조직 C로 전달되는 것을 기본 시나리오로 설정 (대역폭·프라이버시 정책상 흔한 설계)
- 공격 성공 조건: 조직 C의 에이전트가 vision-derived 콘텐츠를 원본 검증 없이 신뢰하고 고위험 행동을 실행

### 5.2 제안 스키마 — Vision-Provenance Extension for A2A

Part.metadata 아래 등록되는 확장 네임스페이스(`https://a2a-vision-provenance.org/v1`)로 다음 필드를 정의:

```json
{
  "origin": "vlm_derived",           // user_input | agent_reasoning | vlm_derived
  "derivation_method": "vlm_caption", // direct_ocr | vlm_caption | vlm_reasoning
  "source_agent_id": "agent://vision-interpreter.example.com",
  "confidence_score": 0.62,
  "raw_evidence": {
    "available": false,
    "reason": "privacy_policy_no_forward"
  },
  "cross_verified": false
}
```

Agent Card의 `capabilities.extensions`에 이 확장을 `required: true`로 선언하면, 확장을 지원하지 않는 에이전트와의 통신은 표준 에러로 거부되어 하위 호환 문제를 프로토콜 차원에서 처리할 수 있다.

### 5.3 수신 에이전트 정책 (제안 알고리즘 초안)

```
if part.origin == "vlm_derived":
    if part.raw_evidence.available == false:
        if downstream_action.risk_level == "high":
            require_human_approval_gate()
        else:
            attenuate_trust(part, factor = f(part.confidence_score))
    else:  # 원본 접근 가능한 경우에만 재접지 시도
        re_ground(part.raw_evidence.uri)
        if cross_verify(part.raw_evidence.uri) != part.text:
            flag_discrepancy()
```

기존 v1 기획서의 4개 방어책(출처 태깅/재접지/교차검증/승인게이트)을 "원본 접근 가능 여부"를 첫 분기 조건으로 삼아 하나의 정책으로 통합한 것이 핵심 설계 결정이다.

### 5.4 테스트베드 구축

- A2A 공식 Python SDK + 오픈소스 VLM(LLaVA, BLIP-2)으로 3~5개 에이전트 체인 프로토타입 구성
- 공격 이미지셋은 텍스트 오버레이형 인젝션(FigStep 계열)으로 스코프 한정 — 픽셀 단위 스테가노그래피는 구현 난이도 대비 한계효용이 낮아 1차 스코프에서 제외하고 향후 과제로 명시
- 실험군 (2×2 설계):
  - (원본 접근 가능 / 불가능) × (제안 스키마·정책 적용 / 미적용 베이스라인)
  - 베이스라인 비교군에 Syed et al.의 애플리케이션 레벨 방어를 재구현해 포함(가능한 범위 내에서)

### 5.5 평가 지표

- 공격 성공률(ASR, %) — Triedman et al.(2503.12188) 방식 차용, 재현성·비교가능성 확보
- 오염 전파율(원본 접근 가능/불가능 조건별 분리 측정)
- 정상 태스크 정확도 저하폭(오탐에 따른 성능 손실)
- 프로토콜 오버헤드(메타데이터로 인한 메시지 크기·지연 증가분)

---

## 6. 예상 기여점 (재정의)

1. A2A와 같은 조직 간 표준 에이전트 프로토콜에서, 애플리케이션 레벨 provenance 방어(Syed et al. 류)가 원본 이미지 미접근 조건에서 구조적으로 성립하지 않음을 정량적으로 규명
2. Part.metadata 표준 스키마 및 AgentExtension 형태의 vision-provenance 확장안 설계·프로토타입 구현
3. 원본 접근 가능/불가능 조건을 분리한 2×2 실증 비교를 통해, 신원 인증(Signed Agent Card)과 콘텐츠 출처 인증이 별개 축임을 실험적으로 보임

*(주의: "최초로 체계화한 위협 분류"와 같은 과도한 최초성 주장은 지양하고, "기존 provenance 방어가 성립하지 않는 조건을 특정하고 그 조건에 맞는 확장을 제안했다"는 좁고 방어 가능한 주장으로 서술)*

---

## 7. 주요 참고 문헌 (검증 완료)

**직접 관련 — 반드시 상세 리뷰:**
- Syed, T. A., Abdel Moaty, M., & Almutairi, M. A. "Toward Trustworthy Agentic AI: A Multimodal Framework for Preventing Prompt Injection Attacks." arXiv:2512.23557, 2025.
- CrossInject: "Manipulating Multimodal Agents via Cross-Modal Prompt Injection." arXiv:2504.14348, 2025.

**A2A 프로토콜 및 보안:**
- Habler, I., Huang, K., Narajala, V. S., & Kulkarni, P. "Building A Secure Agentic AI Application Leveraging A2A Protocol." arXiv:2504.16902, 2025. (MAESTRO 위협모델링)
- Neelou, E. et al. "A2AS: Agentic AI Runtime Security and Self-Defense." arXiv:2510.13825, 2025.
- Unit42 (Palo Alto Networks). "When AI Agents Go Rogue: Agent Session Smuggling Attack in A2A Systems." 2025.11.
- Triedman, H., Jha, R., & Shmatikov, V. "Multi-Agent Systems Execute Arbitrary Malicious Code." arXiv:2503.12188 (COLM 2025).
- Chhabra, A. et al. "Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges." arXiv:2510.23883, 2025.
- A2A 공식 스펙: a2a-protocol.org/latest/specification/, "What's New in v1.0"

**VLM/멀티모달 프롬프트 인젝션 (배경):**
- Wolff, L. et al. "Multi-modal Prompt Injection Attacks against Vision-Language Models." arXiv:2403.04888, 2024.
- Liu, Y., Han, Z., Li, B., & Gong, N. Z. "Visual Prompt Injection Attacks and Defenses for Vision-Language Models." arXiv:2404.00562, 2024.
- Liu, Z. et al. "MM-SafetyBench: Evaluating Safety Risks of Multimodal Large Language Models with Generated Prompts." arXiv:2402.12323, 2024.
- "Invisible Injections: Exploiting Vision-Language Models Through Steganographic Prompt Embedding." arXiv:2507.22304, 2025. (스테가노그래피 ASR 24.3% — 정량 비교 기준점으로 활용 가능)

**참고만(직접 인용 시 성격 재확인 필요):**
- "Governance Gaps in Agent Interoperability Protocols: What MCP, A2A, and ACP Cannot Express." arXiv:2606.31498, 2026. — 거버넌스(투표/이의제기/감사) 갭 분석이지 보안 논문이 아니므로 위협모델 절이 아닌 배경 절에서만 인용
- "Beyond Message Passing: A Semantic View of Agent Communication Protocols." arXiv:2604.02369, 2026. — 18개 프로토콜의 통신/구문/의미 계층 서베이, 배경 설명용

**"Provenance" 인접 연구 (2.5절 대응, 용어 구분 목적으로 인용 — 방법론 재사용 대상 아님):**
- Prakash, S. "LDP: An Identity-Aware Protocol for Multi-Agent LLM Systems." arXiv:2603.08852, 2026.
- Prakash, S. "The Provenance Paradox in Multi-Agent LLM Routing: Delegation Contracts and Attested Identity in LDP." arXiv:2603.18043, 2026.
- sigstore-a2a. GitHub, sigstore/sigstore-a2a. (Agent Card 서명·SLSA provenance 도구)
- Louck, Y., Stulman, A., & Dvir, A. "Improving Google A2A Protocol: Protecting Sensitive Data and Mitigating Unintended Harms in Multi-Agent Systems." arXiv:2505.12490, 2025.
- Dangol, B. "From Privacy to Workflow Integrity: Communication-Graph Metadata in Autonomous Agent Interoperability." arXiv:2606.07150, 2026.
- Anbiaee, Z. et al. "Security threat modeling for emerging AI-agent protocols: A comparative analysis of MCP, A2A, Agora, and ANP." arXiv:2602.11327, 2026.

---

## 8. 다음 단계 (Action Items)

- [ ] Syed et al.(2512.23557) 실험 설계·베이스라인 4종을 상세 리뷰하고, 본 연구 베이스라인 재구현 범위 결정
- [ ] A2A 공식 Python SDK 설치 및 Agent Card / AgentExtension 등록 방식 실습
- [ ] Part.metadata 스키마 초안(5.2절)을 A2A 커뮤니티 컨벤션과 대조해 필드명·값 체계 확정
- [ ] FigStep류 텍스트 오버레이 공격 이미지셋 설계 (스테가노그래피는 향후 과제로 명시)
- [ ] 3~5개 에이전트 체인 프로토타입 구현 (원본 접근 가능/불가능 두 모드 스위치 포함)
- [ ] 2×2 실험 설계 확정 및 ASR 측정 스크립트 작성
- [ ] 투고처 후보: 톱티어 보안학회보다 워크숍(NDSS 부속 워크숍, AAAI/NeurIPS 에이전트 안전 워크숍) 또는 arXiv 프리프린트 선점 전략으로 현실적 목표 설정

---

*본 문서는 2026년 7월 기준 웹 검색 및 A2A 공식 스펙 대조 결과를 반영한 v2 기획서이며, 실제 집필 과정에서 스코프와 방법론은 조정될 수 있음.*
