# Exit Ticket - Multi-Agent Research System

**Student:** Le Hong Anh  
**Student ID:** 2A202600096  
**Date:** May 6, 2026

---

## Question 1: Case nào NÊN dùng multi-agent? Vì sao?

### ✅ Nên dùng multi-agent khi:

#### 1. **Complex Research Tasks**
**Ví dụ:** "Research GraphRAG state-of-the-art, compare with traditional RAG, analyze trade-offs, and write a comprehensive 1000-word report with citations"

**Lý do:**
- Task phức tạp cần nhiều bước xử lý khác nhau
- Mỗi agent chuyên môn hóa cho một phần (search → analyze → write)
- Quality improvement đáng giá hơn cost tăng thêm
- Cần traceability để debug từng bước

**Evidence từ benchmark:**
- Quality: 10/10 (multi-agent) vs 4/10 (single-agent) = **+150% improvement**
- Sources: 5 vs 0 = có citation đầy đủ
- Structure: Research notes → Analysis → Final answer (rõ ràng từng bước)

---

#### 2. **Tasks Requiring Source Attribution**
**Ví dụ:** Academic research, fact-checking, legal document analysis

**Lý do:**
- Researcher agent tập trung vào tìm và track sources
- Writer agent đảm bảo citations chính xác
- Audit trail rõ ràng: biết thông tin từ đâu

**Evidence:**
- Multi-agent có 5 sources với URLs
- Final answer có citations [Source 1], [Source 2]
- Single-agent không có sources

---

#### 3. **When Debugging/Traceability is Critical**
**Ví dụ:** Production systems cần monitor, enterprise applications

**Lý do:**
- Mỗi agent có trace riêng trên LangSmith
- Dễ identify agent nào fail, tốn bao nhiêu tokens
- Route history cho thấy workflow path
- Error tracking per agent

**Evidence:**
```
Route history: researcher → analyst → writer → done
Agent results: 3 agents với cost/tokens tracking
Trace events: 4 events logged
```

---

#### 4. **Tasks Needing Specialized Processing**
**Ví dụ:** Data analysis + visualization, code generation + testing

**Lý do:**
- Mỗi agent có prompt tối ưu cho task riêng
- Analyst agent focus vào critical thinking
- Writer agent focus vào structure và clarity
- Không bị "jack of all trades, master of none"

---

#### 5. **When Quality > Speed**
**Ví dụ:** Medical diagnosis support, financial analysis, strategic planning

**Lý do:**
- 25s latency chấp nhận được nếu quality cao hơn 2.5x
- $0.0027 cost chấp nhận được cho critical decisions
- Structured workflow giảm risk của sai sót

---

### 📊 Summary: Nên dùng multi-agent khi:

| Factor | Condition |
|--------|-----------|
| **Task Complexity** | High (multi-step, requires analysis) |
| **Quality Requirement** | Critical (accuracy matters) |
| **Budget** | Flexible (can afford 5x cost) |
| **Latency Tolerance** | High (can wait 20-30s) |
| **Traceability Need** | Important (need audit trail) |
| **Source Attribution** | Required (need citations) |

---

## Question 2: Case nào KHÔNG NÊN dùng multi-agent? Vì sao?

### ❌ Không nên dùng multi-agent khi:

#### 1. **Simple Factual Questions**
**Ví dụ:** "What is the capital of France?", "Define machine learning"

**Lý do:**
- Single LLM call đủ để trả lời
- Multi-agent overhead không cần thiết
- Latency tăng 4x (25s vs 6s) không đáng
- Cost tăng 5x ($0.0027 vs $0.0005) lãng phí

**Evidence:**
- Simple query không cần search
- Không cần analysis riêng
- Không cần specialized writing

---

#### 2. **Real-Time / Low-Latency Requirements**
**Ví dụ:** Chatbot responses, autocomplete, live customer support

**Lý do:**
- User expect response < 2-3 seconds
- Multi-agent: 25-30s không chấp nhận được
- Sequential workflow không thể optimize
- User experience bị ảnh hưởng nghiêm trọng

**Evidence từ benchmark:**
- Multi-agent: 25.72s (quá chậm cho real-time)
- Single-agent: 6.49s (vẫn chậm nhưng chấp nhận được)

---

#### 3. **Budget-Constrained Applications**
**Ví dụ:** Free tier services, high-volume batch processing, student projects

**Lý do:**
- Multi-agent cost 5.4x higher ($0.0027 vs $0.0005)
- Với 1000 queries: $2.70 vs $0.50 = $2.20 difference
- Với 100k queries: $270 vs $50 = $220 difference
- ROI không justify cho simple tasks

**Calculation:**
```
Single-agent: $0.0005 × 100,000 = $50
Multi-agent:  $0.0027 × 100,000 = $270
Difference: $220 (440% more expensive)
```

---

#### 4. **Tasks Without Clear Decomposition**
**Ví dụ:** Creative writing, brainstorming, open-ended exploration

**Lý do:**
- Không có clear separation of concerns
- Forced decomposition làm giảm creativity
- Handoff giữa agents mất context
- Single agent có better "flow"

**Example:**
- "Write a creative story about AI" → không cần research/analysis/writing separation
- Better với single agent có full creative control

---

#### 5. **Prototype/MVP Stage**
**Ví dụ:** Initial product development, proof of concept, hackathons

**Lý do:**
- Multi-agent complexity cao hơn (4 agents + workflow)
- Harder to debug và iterate
- Overkill cho validation phase
- Single-agent faster to implement và test

**Complexity comparison:**
```
Single-agent: 1 prompt + 1 LLM call = simple
Multi-agent: 4 agents + routing logic + state management = complex
```

---

#### 6. **When Intermediate Steps Not Valuable**
**Ví dụ:** Translation, summarization, format conversion

**Lý do:**
- Chỉ cần input → output
- Research notes và analysis notes không add value
- Extra steps chỉ tăng latency và cost
- No benefit từ specialization

---

### 📊 Summary: Không nên dùng multi-agent khi:

| Factor | Condition |
|--------|-----------|
| **Task Complexity** | Low (single-step, straightforward) |
| **Quality Requirement** | Moderate (good enough is fine) |
| **Budget** | Tight (cost-sensitive) |
| **Latency Tolerance** | Low (need fast response) |
| **Traceability Need** | Not important (just need answer) |
| **Development Stage** | Early (MVP/prototype) |

---

## Decision Framework

### Use this flowchart to decide:

```
Is task complex (multi-step)?
├─ NO → Single-agent
└─ YES
    ├─ Is latency critical (< 5s)?
    │   ├─ YES → Single-agent
    │   └─ NO
    │       ├─ Is budget tight?
    │       │   ├─ YES → Single-agent
    │       │   └─ NO
    │       │       ├─ Need source attribution?
    │       │       │   ├─ YES → Multi-agent ✅
    │       │       │   └─ NO
    │       │       │       ├─ Need traceability?
    │       │       │       │   ├─ YES → Multi-agent ✅
    │       │       │       │   └─ NO → Single-agent
```

---

## Real-World Examples

### ✅ Good Use Cases for Multi-Agent:

1. **Academic Research Assistant**
   - Search papers → Analyze findings → Write literature review
   - Quality critical, citations required

2. **Financial Analysis Report**
   - Gather market data → Analyze trends → Generate report
   - Accuracy critical, audit trail needed

3. **Legal Document Analysis**
   - Search precedents → Analyze relevance → Draft summary
   - Source attribution critical

4. **Technical Documentation**
   - Research APIs → Analyze patterns → Write docs
   - Comprehensive coverage needed

### ❌ Bad Use Cases for Multi-Agent:

1. **Simple Q&A Chatbot**
   - "What are your business hours?"
   - Speed matters, simple answer

2. **Email Auto-Reply**
   - "Thank you for your message..."
   - Template-based, no research needed

3. **Sentiment Analysis**
   - Classify text as positive/negative
   - Single-step task

4. **Language Translation**
   - Translate text from A to B
   - Direct transformation, no analysis needed

---

## Key Takeaway

**Multi-agent is a tool, not a solution.**

Use it when:
- ✅ Task complexity justifies the overhead
- ✅ Quality improvement worth the cost
- ✅ Traceability provides value
- ✅ Latency tolerance allows it

Don't use it when:
- ❌ Simple task doesn't need decomposition
- ❌ Speed is critical
- ❌ Budget is tight
- ❌ Complexity doesn't add value

**From our benchmark:**
- Multi-agent: 2.5x better quality, but 4x slower and 5.4x more expensive
- This trade-off makes sense for complex research, not for simple queries

---

## Personal Reflection

After implementing and benchmarking this system, I learned that:

1. **Architecture matters** - Clear agent roles prevent overlap and confusion
2. **Guardrails are essential** - Max iterations saved me from infinite loops
3. **Observability is key** - LangSmith traces made debugging much easier
4. **Trade-offs are real** - Quality vs speed vs cost is always a balance
5. **Context matters** - Same tool, different use cases, different outcomes

The multi-agent approach taught me to think about **when** to use a pattern, not just **how** to implement it.
