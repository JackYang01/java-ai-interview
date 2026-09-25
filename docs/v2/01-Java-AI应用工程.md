# 01 Java AI 应用工程

> Java AI 面试题库 V2 主体文档。
> 聚焦 Java 在 AI 应用中的工程职责、框架选型、模型接入、结构化输出、流式交互、取消、测试、Prompt 与 Provider 治理。

## 本文件题目

- CORE-01【P0】Java 在现代 AI 应用系统里到底负责什么？
- CORE-02【P0】Spring AI、Spring AI Alibaba、LangChain4j、官方 SDK 到底怎么选？
- CORE-03【P1】多模型 Provider 和 Model Gateway 怎么设计？
- CORE-04【P1】Prompt 怎么做版本、评测、灰度和回滚？
- CORE-05【P0】LLM 的 Structured Output 怎么可靠进入 Java DTO？
- CORE-06【P0】Java AI 的流式输出应该怎么设计？
- CORE-07【P0】用户关闭页面以后，模型或 Agent 还在执行怎么办？
- CORE-08【P1】AI 功能怎么测试和做回归？

---

## 面试递进路线（冻结版）

这 8 道不是 8 个互不相关的知识点，而是一条典型 Java AI 应用面试追问链：

```text
CORE-01 Java 在 AI 系统里负责什么？
   ↓ 为什么不用 Python 全做 / Java 的边界在哪里
CORE-02 Spring AI / Spring AI Alibaba / LangChain4j / SDK 怎么选？
   ↓ 真实系统不会永远只有一个模型
CORE-03 Provider / Model Gateway 怎么设计？
   ↓ 模型、Prompt 和业务逻辑开始进入可发布状态
CORE-04 Prompt 怎么版本化、评测、灰度、回滚？
   ↓ 模型结果怎么稳定进入 Java 业务对象
CORE-05 Structured Output 怎么做到生产可用？
   ↓ 用户端怎么实时拿到结果
CORE-06 Streaming / SSE 怎么设计？
   ↓ 用户断开或任务终止怎么办
CORE-07 Cancel 怎么真正传播到下游？
   ↓ 最后怎么证明这套 AI 功能改完没有退化
CORE-08 AI 应用怎么测试和回归？
```

**练习方式**：每道母题先准备 30 秒主回答；面试官继续追时，再展开实现、失败场景、取舍和验证。不要把后面的深挖点一口气全背出来。

## 使用原则

- 先理解设计目标，再记 API；版本敏感 API 在真实开发前重新核对官方文档。
- 项目内容严格区分 REAL（真实做过）、DESIGN（设计方案）、LEARN（学习储备）、VERIFY（待核实）。
- 固定参数、QPS、准确率、P99、命中率等，没有真实数据就不写成项目事实。
- 英文术语首次出现时尽量给出中文含义，面试表达以中文工程逻辑为主。

---

## CORE-01【P0】Java 在现代 AI 应用系统里到底负责什么？

### 先用 30 秒回答

Java 在 AI 应用里主要负责**确定性的工程边界**。

大模型擅长理解自然语言、生成内容、做一定程度的推理和决策；Java 负责把这些不确定能力接进真实系统，包括 API、鉴权、数据库、事务、Redis、MQ、工具执行、限流、超时、幂等、审计和监控。

所以我理解的 Java AI 开发，不是“Java 调一个大模型接口”，而是：

> **把概率模型接进确定性业务系统，同时保证系统出错时还能控得住。**

---

### 把整个系统拆开就清楚了

```text
用户
 │
 ▼
Spring Boot API
 │
 ├─ 登录 / 租户 / 权限
 ├─ 限流 / 配额
 ├─ 会话 / 任务状态
 │
 ▼
AI Application Layer
 │
 ├─ Prompt / Context
 ├─ RAG
 ├─ Agent Runtime
 └─ Tool Calling
 │
 ▼
LLM / Embedding / Rerank
 │
 ▼
Java 业务能力
 ├─ MySQL
 ├─ Redis
 ├─ RabbitMQ / Kafka
 ├─ 订单 / 工单 / 审批
 └─ 外部 API
```

模型可以说：

> “我判断应该创建一个工单。”

但真正创建之前，Java 还要处理：

1. 当前用户有没有权限；
2. 参数是否合法；
3. 这次操作是不是重复请求；
4. 数据库事务怎么处理；
5. 下游接口超时怎么办；
6. 操作是否需要人工审批；
7. 最后怎么留审计记录。

这就是 Java 工程师在 AI 系统里的价值。

---

### 面试官继续追问：“那 Python 呢？”

不要回答成语言战争。

可以这样说：

- Python 在模型训练、推理服务、数据科学和部分 AI 生态上更强；
- Java 在成熟企业后端、业务系统、事务、权限、中间件、微服务治理上积累更深；
- 企业里常见的做法是各取所长，而不是必须二选一。

例如：

```text
Spring Boot 业务系统
       │ HTTP / gRPC
       ▼
Python Rerank / OCR / Model Service
```

Java 完全可以负责主业务系统，模型推理服务仍然由 Python 提供。

---

### 这道题真正考什么

不是考你会不会说：

> “Java 性能好、生态成熟。”

面试官更想知道你有没有理解：

> **模型产生建议，应用负责执行。**

这条边界在 Agent 场景尤其重要。

#### 一个容易说错的地方

不要说：

> “大模型负责业务逻辑，Java 只是调用接口。”

生产系统恰恰相反。

业务状态、资金、权限、事务、幂等这些核心约束，不能交给模型自由决定。

---

### 项目怎么挂

PMO 知识助手可以讲：

> 模型负责理解问题和生成回答，Java 负责文档入库、权限过滤、检索编排、Redis 会话、异步任务和引用溯源。

工单 Agent 可以讲：

> 模型负责理解用户意图、抽取工单字段和提出 Tool Call；Java 负责 DTO 校验、工具权限、状态流转、MQ、幂等和真正落库。

如果这些实现还没有经过项目事实确认，就说“设计上我会这样划分”，不要说成已经上线。

---


---

## CORE-02【P0】Spring AI、Spring AI Alibaba、LangChain4j、官方 SDK 到底怎么选？

这道题不要背“谁最好”。

框架选择其实是在回答：

> **我的项目需要什么能力，团队愿意承担多少框架复杂度？**

---

### 先建立一个简单判断

#### Spring AI

适合已经是 Spring Boot 技术栈，而且希望 AI 能力自然进入 Spring 体系的项目。

比较典型的能力包括：

- `ChatClient`
- Model API
- Embedding / Vector Store
- Structured Output
- Tool Calling
- Advisors
- MCP
- Observability

对于传统 Java 后端转 AI 应用，学习路径比较顺。

---

#### Spring AI Alibaba

它不是简单的“国产 Spring AI”。

更应该把它理解为：

> **在 Spring AI 基础上，进一步强化 Agent Framework、Graph、Multi-Agent、Skills、A2A、Sandbox 等智能体工程能力。**

如果系统已经进入：

- 状态图；
- 人机协同；
- Checkpoint；
- 多 Agent；
- Skills；
- 复杂工作流；

这一层，就值得重点看。

但如果只是一个简单 RAG Chat，没必要为了“高级”强行上 Graph。

---

#### LangChain4j

LangChain4j 是 Java AI 生态里另一条成熟路线。

它适合：

- 希望使用高层 AI Services 抽象；
- 需要丰富的模型、Embedding、Vector Store 集成；
- 项目不是强绑定 Spring AI；
- 团队已经有 LangChain4j 经验。

当前官方文档要求最低 JDK 17，所以旧题库里“JDK 8+”这种说法不能再用了。

---

#### 官方模型 SDK

有些场景最简单的方案反而是直接 SDK。

例如：

```text
业务只调用一个模型
没有复杂 RAG
没有 Agent
只有 2~3 个固定接口
```

这时：

```text
Spring Boot
   │
Official SDK
   │
Model API
```

完全可能比引入一整套 AI 框架更合适。

---

### 面试回答可以这样组织

> 我不会先问哪个框架最强，我会先看四件事：  
> 第一，项目是不是 Spring Boot；第二，需要到 Chat/RAG 还是已经进入 Agent/Graph；第三，要不要统一多模型和工具；第四，团队是否需要框架提供的治理能力。  
> 如果只是简单模型调用，官方 SDK 就够；Spring 项目做通用 AI 应用，我会优先看 Spring AI；复杂 Agent 和工作流我会进一步评估 Spring AI Alibaba；LangChain4j 则是 Java 生态里另一套成熟选择，最终按团队和现有代码栈选。

---

### 一个框架选择矩阵

| 场景 | 更值得优先评估 |
|---|---|
| 单模型简单调用 | 官方 SDK |
| Spring Boot + Chat/RAG/Tool | Spring AI |
| Agent / Graph / Multi-Agent / Skills | Spring AI Alibaba |
| 已有 LangChain4j 项目或偏 AI Services 抽象 | LangChain4j |

这不是硬规则，只是一个起点。

---

### 常见坑

#### 坑 1：把框架能力当模型能力

例如：

> “Spring AI 能让模型更聪明。”

不对。

框架解决的是接入、编排、工具、状态和工程治理。

模型本身的能力仍来自底层模型。

#### 坑 2：只背 API 名字

框架 API 更新很快。

面试更重要的是讲清：

```text
Model
Tool
Memory
RAG
Agent
State
Observability
```

这些抽象关系。

#### 坑 3：所有项目都上最重框架

复杂度本身也有成本。

一个 CRUD + 两次 LLM 调用的内部工具，没必要先画 20 个 Agent 节点。

---


---

## CORE-03【P1】多模型 Provider 和 Model Gateway 怎么设计？

### 30 秒回答

> “Model Gateway 的价值是把模型厂商差异隔离在业务层之外，同时集中处理能力匹配、路由、配额、健康检查、Fallback、成本和观测。它不能只是一个统一 `chat()` 接口，因为不同模型在 Tool Calling、Structured Output、Context Length、Streaming、多模态能力上并不等价。真正的 Fallback 必须先做 capability match（能力匹配），再谈价格和可用性。”

### 一张图

```text
Business Service
      │
      ▼
  Model Gateway
  ├─ Capability Match
  ├─ Routing
  ├─ Quota
  ├─ Health
  ├─ Retry
  ├─ Fallback
  └─ Observability
      │
 ┌────┼─────┐
 ▼    ▼     ▼
Qwen OpenAI Local
```

### Java 里不要只写接口抽象

最简单：

```java
interface ModelProvider {
    String name();
    ModelCapabilities capabilities();
    ChatResult chat(ChatRequest request);
}
```

能力模型可以明确：

```text
streaming
structuredOutput
toolCalling
multimodal
maxContext
```

路由时：

```text
Request Needs
     │
     ▼
Capability Filter
     │
     ▼
Healthy Providers
     │
     ▼
Policy Route
```

### 为什么“主模型挂了换备用模型”没那么简单

比如：

```text
Primary：支持 Tool Calling + JSON Schema
Fallback：只支持普通文本
```

如果工单 Agent 正在执行：

```text
CreateTicket Tool
```

Fallback 后整个工作流可能直接失效。

### 路由依据

可以考虑：

- task type；
- model capability；
- latency；
- cost；
- provider quota；
- tenant policy；
- data residency（数据驻留）。

但不要写成：

> 永远选择最便宜模型。

质量本身也是路由条件。

---


---

## CORE-04【P1】Prompt 怎么做版本、评测、灰度和回滚？

### 30 秒回答

> “Prompt 不应该只是配置中心里的一段字符串，而应该作为可发布资产管理。每次改动要有 promptId、version、owner、change reason，先跑固定评测集和结构化契约测试，再做灰度流量，观察质量、延迟、成本和安全指标，最后 Promote 或 Rollback。动态配置解决的是发布速度，不等于可以绕过测试和审批。”

### 生命周期

```text
Edit
 ↓
Version
 ↓
Review
 ↓
Offline Eval
 ↓
Gray
 ↓
Online Monitor
 ↓
Promote / Rollback
```

### Prompt 版本至少要关联什么

```text
prompt_version
model_version
schema_version
tool_version
knowledge_version
```

否则回归时很难解释：

> 到底是哪一层变了。

### 存在哪里？

可以：

- Git；
- DB；
- Nacos / Apollo；
- Prompt Registry。

没有固定答案。

关键是：

- 可追踪；
- 可审计；
- 可回滚。

### HTML Escape 不是 Prompt Injection 防御

这点旧题库要彻底删掉。

```text
HTML Escape → 解决 HTML 渲染安全
Prompt Injection → 解决模型指令边界
```

不是同一个问题。

---


---

## CORE-05【P0】LLM 的 Structured Output 怎么可靠进入 Java DTO？

这是 AI 应用里非常实用的一题。

模型返回文本很容易。

难的是让这段文本真正进入 Java 业务。

---

### 30 秒版本

我不会直接拿模型返回的 String 做业务判断。

我的链路会是：

```text
LLM
 ↓
JSON Schema / Structured Output
 ↓
Java DTO / Record
 ↓
Schema Validation
 ↓
Bean Validation
 ↓
Business Validation
 ↓
真正执行业务
```

格式正确只是第一关。

真正生产级还要验证业务含义。

---

### 举个工单例子

用户说：

> “电脑连不上公司 VPN，挺急的。”

我们想得到：

```java
public record TicketDraft(
    String category,
    String title,
    String description,
    String priority
) {}
```

模型输出即使是合法 JSON：

```json
{
  "category": "NETWORK",
  "title": "VPN 无法连接",
  "description": "用户无法连接公司 VPN",
  "priority": "P0"
}
```

也不代表可以直接创建工单。

因为还要继续问：

> P0 是不是允许模型自己决定？

如果公司规则规定 P0 必须满足生产全面中断，这个结果虽然 JSON 完美，业务上仍然是错的。

---

### 所以校验应该分层

```text
第一层：结构
字段、类型、JSON 格式是否正确？

第二层：Java Validation
@NotBlank
@Size
@Pattern
枚举范围

第三层：业务规则
用户是否有权限？
priority 是否符合规则？
项目是否存在？
状态是否允许？
```

这三个层次不要混在一起。

---

### Spring AI 当前应该怎么理解

当前 Spring AI 的 `ChatClient` 已经可以直接把结构化结果映射成 Java 类型，并支持 Schema Validation / Self-Correction 一类机制。

所以新版题库不再把：

> Regex 从一大段文本里抠 JSON

当成主方案。

Regex 最多是旧模型或异常输出下的兜底。

---

### Retry 怎么做？

可以重试，但不能：

```text
parse失败
 ↓
无限重试
 ↓
token烧完
```

更合理：

```text
Model Output
 ↓
Validate
 ├─ OK → Business
 └─ Error
      ↓
  给模型明确错误
      ↓
  bounded retry
      ↓
  fail / manual fallback
```

关键是 **bounded retry（有上限重试）**。

---

### 一个非常重要的面试追问

#### “如果模型把 `priority=P0` 写错了，Schema 明明是合法的，怎么办？”

答案：

> Schema 只能保证“形状对”，保证不了“业务对”。

所以要把：

```text
格式可靠性
```

和：

```text
业务正确性
```

分开。

这句话很值得记。

---

### 什么时候不必强上 Structured Output？

如果输出只是：

> 给用户看的一段普通自然语言回答

那就没有必要强制转 DTO。

当下游代码需要：

- 分支；
- 落库；
- 调 Tool；
- 修改状态；
- 参与审批；

Structured Output 才特别重要。

---


---

## CORE-06【P0】Java AI 的流式输出应该怎么设计？

很多人回答这道题只有一句：

> “用 SSE。”

这还不够。

真正的问题是：

> **后端到底要向前端传什么状态？**

---

### 普通 Chat 最简单

```text
Browser
  │
  │ SSE
  ▼
Spring Boot
  │
  ▼
Streaming Model
```

模型每返回一点文本，就向前端发一个增量。

例如：

```text
event: text_delta
data: {"text":"你好"}

event: text_delta
data: {"text":"，我查到..."}

event: completed
data: {}
```

---

### 到 Agent 就复杂了

Agent 不是一直输出文字。

它可能正在：

- 查询知识库；
- 调接口；
- 等审批；
- 执行工具；
- 重试。

所以事件协议不能只有一个 String。

建议至少区分：

```text
text_delta
tool_start
tool_end
citation
progress
approval_required
completed
error
```

例如：

```text
event: tool_start
data: {"tool":"queryTicket"}

event: tool_end
data: {"tool":"queryTicket","status":"success"}

event: text_delta
data: {"text":"我查到这张工单目前..."}

event: completed
data: {}
```

这样前端才能正确表达 Agent 当前状态。

---

### Spring MVC SSE 和 WebFlux 怎么选？

#### Spring MVC + SseEmitter

适合：

- 原项目就是 Spring MVC；
- 业务量不是极端规模；
- 大量下游 SDK 仍然是阻塞式；
- 团队更熟 Servlet 体系。

#### WebFlux

适合：

- 整条链路大量采用 Reactive API；
- 高并发 Streaming 很重要；
- 希望更系统地处理异步流和取消；
- 团队能承担响应式编程复杂度。

---

### 一个旧题库里必须纠正的点

不能再说：

> “每个 SSE 长连接永久占一个 Tomcat 请求线程，所以 1000 个连接就占 1000 个 Tomcat 线程。”

Spring MVC 异步处理会让 Servlet 请求线程退出，连接仍可以保持。

但这也不代表 SSE“没有资源成本”。

你仍然需要考虑：

- 连接；
- 写出线程/执行器；
- 内存；
- 下游模型连接；
- 反向代理；
- 超时；
- 客户端断开。

---

### 为什么 Virtual Thread 也不能直接解决所有问题？

Virtual Thread 可以降低大量阻塞 I/O 的线程成本。

但它解决不了：

```text
模型供应商只允许 100 RPM
```

也解决不了：

```text
数据库只有 50 个连接
```

所以：

> 线程模型 ≠ 下游容量。

这个点可以和后面的并发题 ENG-01 联动。

---

### SSE 断开以后怎么办？

要区分两件事：

#### 1. 前端连接断了

可以重新建立 SSE。

#### 2. 底层模型调用已经断了

不一定能从“第 523 个 Token”继续。

如果系统想支持真正恢复：

```text
Agent Event
 ↓
持久化 Event Store
 ↓
client lastEventId
 ↓
replay missed events
```

恢复的是**你保存过的系统事件**。

不是魔法般恢复第三方模型内部生成状态。

---


---

## CORE-07【P0】用户关闭页面以后，模型或 Agent 还在执行怎么办？

### 30 秒回答

> “取消要做成一条可传播的信号链。客户端断开后，服务端先标记 executionId 为 CANCEL_REQUESTED，再尽可能取消 Reactor Subscription / Future / HTTP 请求，并在 Agent 每一步执行前检查取消状态。对于已经发出的远端模型请求和已经发生的 Tool 副作用，`future.cancel(true)` 不保证它们真的停止，所以必须区分‘停止后续步骤’和‘撤销已经发生的业务动作’。”

### 图

```text
Client Disconnect
      ↓
Cancel(executionId)
      ↓
Execution Registry
      ↓
 ┌────┼─────┐
 ▼    ▼     ▼
LLM  Tool  Worker
Cancel/Stop Next Step
```

### Java 层面

可以有：

```text
executionId → CancellationToken / TaskState
```

每个长任务循环：

```java
if (taskState.isCancelRequested(executionId)) {
    throw new TaskCancelledException();
}
```

Streaming：

- Reactor subscription dispose/cancel；
- HTTP client request cancellation；
- SSE disconnect hook。

### 最容易说错的地方

#### 1. `CompletableFuture.cancel(true)` 不是万能的

它不能保证：

- 第三方模型服务器停止生成；
- Tool 已经执行的 DB 操作撤回；
- 外部邮件不发送。

#### 2. Cancel 和 Rollback 不是一回事

```text
Cancel：停止后续执行
Rollback/Compensation：处理已发生副作用
```

---


---

## CORE-08【P1】AI 功能怎么测试和做回归？

### 先说核心矛盾

LLM 输出具有非确定性，所以：

> 不能要求每次输出字符串完全一样。

但这不代表 AI 系统没法测试。

### 测试分层

```text
Unit Test
   ↓
Tool Contract Test
   ↓
Model Mock / Fixture
   ↓
Integration Test
   ↓
Golden Dataset
   ↓
Regression
   ↓
Online Eval
```

### Java 单元测试适合测什么

不需要真实调模型：

- DTO validation；
- Tool permission；
- Idempotency；
- Route policy；
- State transition；
- RRF merge；
- Chunk logic。

### Model Mock

比如模型返回固定：

```json
{"category":"NETWORK","priority":"P2"}
```

然后验证 Java 流程。

### Contract Test

尤其 Tool：

```text
Schema 是否兼容
参数类型是否正确
错误是否映射正确
```

### Golden Dataset

真正的模型/RAG 回归：

```text
Version A
Version B
 ↓
Same Dataset
 ↓
Compare Quality / Cost / Latency
```

### Record / Replay

生产 Trace 可以脱敏后形成 Case：

```text
Input
Retrieved Context
Tool Mock Result
Expected Constraint
```

重新跑新版本。

### 不要只测“最终答案漂亮不漂亮”

Agent 还应该测：

- Tool Selection；
- Tool Arguments；
- Step Count；
- Side Effect；
- Termination；
- Recovery。

---


---

---

## 附：V1 工程实现知识保留区

这一部分承接旧题库中原计划放入“工程实现参考”的内容。为了保证 00～06 自身闭环，不再把这些知识点悬空到一个未生成的额外文件。

### A. Spring AI 2.0.x Advisor 链当前怎么理解

Spring AI 2.0.1 的 Advisor 核心接口已经是：

- `CallAdvisor` / `CallAdvisorChain`：非流式；
- `StreamAdvisor` / `StreamAdvisorChain`：流式；
- `ChatClientRequest`：Advisor 可处理的请求；
- `ChatClientResponse`：Advisor 可处理的响应。

旧资料中的 `CallAroundAdvisor`、`AdvisedRequest`、`AdvisedResponse` 等旧 API 不再作为当前写法保留。

Advisor 可以用于：

- Memory；
- RAG；
- Observability；
- Safety；
- Tool Calling；
- 自定义拦截和增强。

关键点是顺序：

```text
ChatClientRequest
   ↓
Advisor A
   ↓
Advisor B
   ↓
ToolCallingAdvisor / Model
   ↓
ChatClientResponse
```

不同 Advisor 的顺序会影响 Memory、RAG 和 Tool Loop 能看到的上下文，所以不能只会“注册进去”。

### B. Spring AI Evaluation API

Spring AI 当前提供 `Evaluator` 抽象，以及用于响应相关性和基于上下文事实核验的实现，例如：

- `RelevancyEvaluator`；
- `FactCheckingEvaluator`。

典型使用场景是 Integration Test（集成测试）：

```text
Question
  ↓
RAG / Model
  ↓
Response + Retrieved Context
  ↓
EvaluationRequest
  ↓
Evaluator
  ↓
pass / fail + metadata
```

但必须注意：

> 框架提供 Evaluator，不等于项目已经有完整 Evaluation System。

真正生产化仍需要：

- Golden Dataset；
- 固定版本数据；
- Retrieval 指标；
- 生成指标；
- 阈值/门禁；
- Bad Case；
- 人工抽检；
- 版本回归。

### C. ToolCallback 和 Java 方法转 Tool Schema

Spring AI 2.0.x 已统一使用 Tool 术语，旧 `FunctionCallback` API 已被 `ToolCallback` 体系替代。

常见两条路径：

1. 方法/对象通过 Tool 注解和框架反射生成 Tool Definition；
2. 自己构造 `ToolCallback`，显式控制 name、description、input schema 和执行逻辑。

模型最终拿到的是 Tool Definition / Schema，不是直接获得 Java Service 对象权限。

这一点和 `TOOL-01` 的安全边界一致：

```text
Model requests tool
   ↓
Application validates
   ↓
ToolCallback / Java method
   ↓
Business Service
```

### D. 浏览器 SSE 和服务间 gRPC Streaming 不要混淆

浏览器 Chat UI 常见 SSE，因为 HTTP 生态简单、服务端单向推流适合 Token 输出。

Java 服务之间如果需要强类型 RPC，则可以评估 gRPC。gRPC 支持：

- Unary RPC；
- Server Streaming；
- Client Streaming；
- Bidirectional Streaming。

因此一种可能架构是：

```text
Browser
  │ SSE
  ▼
AI Gateway / BFF
  │ gRPC server streaming
  ▼
Internal AI Service
```

但这不是固定标准。内部服务已有 HTTP/WebFlux/Dubbo 时，不应为了“AI”强行换 gRPC。

### E. 模型基准测试不只测一次回答

模型选型至少需要固定一组业务样本，比较：

- task quality；
- Structured Output 成功率；
- Tool Calling 表现；
- TTFT；
- 总延迟；
- Token 消耗；
- 并发稳定性；
- 上下文长度；
- 失败和限流情况。

模型路由也应该建立在这种能力画像之上，而不是简单按“最便宜模型优先”。

### F. A/B Test / 灰度实验不能只看“新版本平均分更高”

旧题库 Appendix K18 的实验知识继续保留，重点包括：

- Consistent Assignment（稳定分组）：同一用户/会话不能今天进 A、明天进 B；
- Sample Size（样本量）：样本太小不要急着下结论；
- Guardrail Metrics（护栏指标）：质量变好但延迟、成本、投诉率恶化也不能直接放量；
- SRM（Sample Ratio Mismatch，样本比例失配）：实际分组比例异常时要先检查实验实现；
- Stop Rule（停止规则）：不要看到一次漂亮结果就提前结束；
- Prompt / Model / RAG / Agent Release Manifest 要能回溯。

AI 实验通常还要分层看：

```text
业务结果
+ 质量指标
+ 安全指标
+ 延迟
+ 成本
+ Tool 副作用
```

不能只挑一个“平均得分”做结论。
