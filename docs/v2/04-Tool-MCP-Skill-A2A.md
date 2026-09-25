# 04 Tool / MCP / Skill / A2A

> Java AI 面试题库 V2 主体文档。
> 覆盖模型如何提出工具调用、Java 如何执行与治理、MCP 企业接入、Skill 分层、动态工具选择以及 A2A。

## 本文件题目

- TOOL-01【P0】Tool Calling 从模型到 Java 真正执行，中间发生了什么？
- TOOL-02【P0】Tool Calling 怎么做成生产级？
- TOOL-03【P1】系统有几百个 Tool 时怎么办？
- TOOL-04【P0】MCP 在 Java 企业系统里到底怎么落地？
- TOOL-05【P1】Skill、Tool、Prompt、MCP 分别解决什么？
- TOOL-06【P1】A2A 和 Tool / MCP 有什么区别？什么时候 Agent 调 Agent？

---

## 面试递进路线（冻结版）

Tool / MCP / Skill / A2A 不是四套孤立名词，面试通常从一次最普通的 Tool Call 一层层往外扩：

```text
TOOL-01 模型到 Java Tool 的完整调用链是什么？
   ↓ Demo 能调用以后，生产上怎么保证不出事
TOOL-02 权限、校验、幂等、超时、审计怎么做？
   ↓ Tool 从几个增长到几百个怎么办
TOOL-03 Tool Registry / Dynamic Tool Search 怎么做？
   ↓ 外部能力越来越多，如何标准化接入
TOOL-04 MCP 在 Java 企业系统里怎么落地？
   ↓ MCP、Tool、Prompt、Skill 经常被混用
TOOL-05 Skill / Tool / Prompt / MCP 如何分层？
   ↓ 如果调用对象不再是工具，而是另一个 Agent
TOOL-06 A2A 什么时候有意义？
```

**练习方式**：先把 TOOL-01、02 练成硬基础。MCP、Skill、A2A 都应该从“现有 Tool Calling 为什么开始不够用”自然追出来，而不是单独背概念。

## 使用原则

- 先理解设计目标，再记 API；版本敏感 API 在真实开发前重新核对官方文档。
- 项目内容严格区分 REAL（真实做过）、DESIGN（设计方案）、LEARN（学习储备）、VERIFY（待核实）。
- 固定参数、QPS、准确率、P99、命中率等，没有真实数据就不写成项目事实。
- 英文术语首次出现时尽量给出中文含义，面试表达以中文工程逻辑为主。

---

## TOOL-01【P0】Tool Calling 从模型到 Java 真正执行，中间发生了什么？

这是 Agent 最基础的一条链。

先纠正一个常见误解：

> **模型不会直接执行 Java 方法。**

模型只会返回：

> “我建议调用某个工具，参数是这些。”

真正调用代码的是应用。

---

### 完整链路

```text
Java 注册 Tool
    ↓
Tool name / description / JSON Schema
    ↓
发送给 LLM
    ↓
LLM 返回 Tool Call
    ↓
应用解析
    ↓
找到对应 Tool
    ↓
参数校验
    ↓
权限 / 风险检查
    ↓
执行 Java 方法
    ↓
Tool Result
    ↓
加入上下文
    ↓
再次调用 LLM
    ↓
最终回答
```

---

### 举一个 Java Tool

逻辑上类似：

```java
@Tool(description = "查询指定工单的当前状态")
public TicketStatus queryTicket(long ticketId) {
    return ticketService.queryStatus(ticketId);
}
```

框架会根据 Java 方法和描述产生模型可理解的 Tool Definition。

模型看到的不是 Java 源码。

它看到的是类似：

```text
name: queryTicket
description: 查询指定工单的当前状态
parameters:
  ticketId: integer
```

---

### 用户问

> “帮我看看 12345 这张工单现在到哪了。”

模型可能返回：

```json
{
  "name": "queryTicket",
  "arguments": {
    "ticketId": 12345
  }
}
```

这仍然没有执行任何数据库代码。

Java Runtime 才会：

```text
resolve tool
 ↓
validate arguments
 ↓
call queryTicket(12345)
 ↓
get result
```

然后再把结果送回模型。

---

### Spring AI 当前 Tool Calling 的一个重要变化

当前 Spring AI 2.x 把 Tool Calling Loop 做成了 `ChatClient` Advisor 链里的核心能力。

也就是说 Tool Calling 已经不是简单的：

```text
Model → function → return
```

而是一个可组合的循环：

```text
ChatClient
 ↓
ToolCallingAdvisor
 ↓
Model
 ↓
Tool Calls?
 ├─ No → final answer
 └─ Yes
      ↓
 ToolCallingManager
      ↓
 ToolCallback
      ↓
 Tool Result
      ↓
 Model again
```

这一点很适合作为框架深挖追问。

---

### Tool 描述为什么重要？

如果只有：

> `queryData`

模型根本不知道什么时候该用。

描述应该让模型知道：

- 什么时候调用；
- 输入是什么；
- 返回什么；
- 哪些情况不要调用。

但 Tool Description 再精确，也不能代替权限控制。

---

### 一条必须记住的安全边界

Tool Definition 可以告诉模型：

> “这个工具只能查询当前用户自己的订单。”

但真正的 Java 方法内部仍然要检查：

```java
currentUser
order.owner
permission
```

因为 Prompt 不是权限系统。

---

### 这题下一层会追什么？

通常马上进入 TOOL-02：

#### 参数错了怎么办？

Structured Output / Schema Validation / bounded retry。

#### Tool 超时怎么办？

Timeout / Circuit Breaker / fallback。

#### Tool 被重复调用怎么办？

业务 Idempotency Key。

#### 删除、付款、发邮件怎么办？

Risk Policy + HITL。

#### 返回十万条数据怎么办？

Projection / Pagination / Aggregation / Summary。

所以 TOOL-01 是理解“链路”，TOOL-02 才是理解“生产级治理”。

---


---

## TOOL-02【P0】Tool Calling 怎么做成生产级？

#### 一句话回答

> 生产级 Tool Calling 的关键不是 `@Tool` 注解，而是把模型请求和真实业务执行之间加上 Schema 校验、权限、风险策略、超时、重试、幂等、结果裁剪、审计和可观测性。

#### 模型不能直接拥有业务权限

正确理解：

```text
LLM
 │  “我希望调用 refundOrder”
 ▼
Tool Request
 │
 ▼
Java Tool Runtime
 ├─ Tool exists?
 ├─ Schema valid?
 ├─ User permitted?
 ├─ Risk allowed?
 ├─ Need approval?
 ├─ Idempotent?
 └─ Timeout / Retry?
 │
 ▼
Real Business Service
```

所以最重要的一句话是：

> **模型提出动作，Java 决定动作能不能执行。**

#### 一、Schema 校验

例如 Tool 定义：

```java
@Tool(description = "查询指定工单")
TicketSummary queryTicket(long ticketId) { ... }
```

除了模型侧 JSON Schema，还要做 Java 侧：

- 类型校验；
- Bean Validation；
- Enum 校验；
- 业务规则校验。

模型传：

```text
ticketId = "ABC"
```

不能让反射异常直接炸掉整条 Agent 链路。

#### 二、权限检查

权限一定要在 Tool 执行端再次检查。

不能因为 Prompt 写了：

> “只能查询自己的订单”

就认为安全了。

Tool 方法里要基于真实身份：

```text
Authentication
Tenant
Role
Resource ownership
```

做授权。

#### 三、Tool 结果不要返回 Entity 全量对象

例如：

```java
List<TicketEntity> findAllTickets();
```

几万条记录直接给模型是非常危险的设计。

更好的 Tool Contract：

```java
TicketSearchResult searchTickets(TicketSearchRequest request);
```

支持：

- 限定条件；
- limit；
- cursor；
- projection；
- summary。

#### 四、Timeout 和 Retry 要按 Tool 语义设计

只读查询：

> 部分情况下可以安全重试。

发送邮件：

> 超时以后不能确定邮件是否已经发送。

退款：

> 更不能盲目 Retry。

所以要区分：

```text
Retryable Read
Idempotent Write
Non-idempotent Write
```

#### 五、幂等不能简单用“Tool 名 + 参数 Hash”

因为：

```text
sendReminder(user=1, text=xxx)
```

业务上今天和明天可能就是要发送两次。

正确的幂等语义应该来自业务操作本身：

```text
operationId
requestId
businessKey
```

例如：

```text
create_ticket:execution-1001:operation-3
```

#### 六、Tool Error 怎么回给模型？

不要返回 Java Stack Trace。

可以定义结构化错误：

```json
{
  "status": "FAILED",
  "errorCode": "TICKET_NOT_FOUND",
  "retryable": false,
  "message": "工单不存在"
}
```

这样模型更容易决定下一步。

#### 七、Tool 调用也需要 Trace

建议 Span：

```text
agent.run
 └─ tool.call
     ├─ tool.name
     ├─ duration
     ├─ status
     ├─ retry_count
     └─ operation_id
```

敏感参数不要默认全量打日志。

#### 当前 Spring AI 怎么理解 Tool Calling？

截至当前稳定文档，Spring AI 2.0.x 的 `ChatClient` 会通过 `ToolCallingAdvisor` 驱动 Tool Call → Tool Result → 再次模型调用的循环。也就是说，Tool Calling 已经是运行时循环的一部分，而不是简单“一次函数调用”。正式代码实现时要按当时稳定版本 API 再核验。

#### 面试追问：Tool 失败要不要让模型自己重试？

回答可以分三层：

1. 参数格式错误：可以把明确校验错误返回模型，让它修正；
2. 临时只读网络错误：Java 层可以有限重试；
3. 有副作用操作：必须依据幂等和业务状态决定，不能让模型自由重试。

#### 项目关联

工单 Agent：非常核心。

PMO：也可用于 Jira / OA / 项目系统实时查询。

---


---

## TOOL-03【P1】系统有几百个 Tool 时怎么办？

### 核心问题

如果把 500 个 Tool Schema 全塞给模型：

- Context 变长；
- Token 成本高；
- Tool 选择准确率下降；
- 权限面变大。

### 正确架构

```text
500 Tools
   │
Tool Registry
   │
Permission Filter
   │
Tool Search / Router
   │
5 Relevant Tools
   │
LLM
```

### Tool Registry 里存什么

至少：

- name；
- description；
- schema；
- tags；
- owner；
- risk level；
- tenant scope；
- version。

### Tool Search

可以按：

- rule；
- intent；
- embedding similarity；
- LLM router；
- hybrid。

截至 Spring AI 2.0.1，已经存在 `ToolSearchToolCallingAdvisor`，可以对可用 Tool 做索引、搜索并把发现的 Tool 动态注入调用流程。这说明“动态 Tool Discovery”已经是现实工程能力，不只是趋势概念。

### 但是不要迷信 Tool Search

高风险场景：

```text
Search 结果
```

还必须经过：

```text
Permission / Risk Policy
```

搜索到不等于允许调用。

---


---

## TOOL-04【P0】MCP 在 Java 企业系统里到底怎么落地？

#### 一句话回答

> MCP（Model Context Protocol，模型上下文协议）解决的是 AI 应用与外部 Tool、Resource、Prompt 之间的标准化连接问题。Java 系统既可以作为 MCP Client 消费外部能力，也可以把自己的业务能力封装成 MCP Server 暴露出去，但业务鉴权、租户隔离和审计仍然必须由企业系统自己负责。

#### 先把 MCP 放到正确的位置

```text
                 ┌──────────────┐
                 │  Java Agent  │
                 └──────┬───────┘
                        │
                 MCP Client
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Jira MCP Server  Git MCP Server  Internal MCP Server
        │                               │
        ▼                               ▼
      Jira API                    ERP / CRM / OA
```

MCP 不等于 Agent。

MCP 解决：

> 怎么标准化发现和调用外部能力。

Agent 解决：

> 当前应该调用哪个能力、下一步怎么做。

#### MCP 里常见的能力类型

面试至少知道：

- Tools：可以执行的能力；
- Resources：可读取的上下文资源；
- Prompts：服务器提供的可复用 Prompt 能力。

具体协议字段和传输细节会演进，面试时不建议死背某一版字段名。

#### Java 可以有两种角色

#### 角色一：MCP Client

Java Agent 去消费外部 MCP Server：

```text
Java AI App
   ↓
MCP Client
   ↓
Discover Tools
   ↓
Tool Calling
   ↓
Remote MCP Server
```

例如连接：

- Jira；
- GitHub；
- 文件系统；
- 数据平台。

#### 角色二：MCP Server

把企业内部能力标准化暴露：

```text
Order Service
     │
 MCP Server Adapter
     │
 ┌───┴────────┐
 Tool         Resource
 │             │
queryOrder   order-schema
```

当前 Spring AI 已提供 Java MCP Client/Server 集成以及 MCP Server 注解能力，正式开发时直接使用当前稳定版本的 Starter 和 API，不建议自己手撸协议。

#### 企业内部最关键的不是“连通”，而是治理

如果把所有内部 Service 直接暴露成 MCP Tool，很快会出现安全问题。

需要：

```text
MCP Request
   ↓
Authentication
   ↓
Tenant Resolution
   ↓
Tool Permission
   ↓
Argument Validation
   ↓
Risk Policy
   ↓
Business Service
   ↓
Audit
```

#### MCP Server 自己说“用户可以调用”够吗？

不够。

真正权限必须来自企业身份体系：

- OAuth / OIDC；
- JWT；
- RBAC / ABAC；
- Tenant Context；
- Resource Permission。

模型和 MCP Client 都不能成为最终授权源。

#### 多 MCP Server 会带来什么问题？

例如一个 Agent 连了：

```text
GitHub  40 tools
Jira    30 tools
CRM     50 tools
ERP     60 tools
```

一共 180 个 Tool。

如果把所有 Schema 全塞给模型：

- Token 爆炸；
- 模型选错工具；
- 名称冲突；
- 权限面扩大。

所以需要：

```text
MCP Servers
    ↓
Tool Registry
    ↓
Permission Filter
    ↓
Tool Search / Selection
    ↓
Expose only relevant tools
```

这和 TOOL-03“几百个 Tool 怎么管理”直接连起来。

#### Untrusted MCP Server（不可信 MCP Server）怎么处理？

如果 MCP Server 来自第三方，不能默认：

> 它返回的内容可信、它声明的 Tool 描述可信。

需要考虑：

- Server allowlist；
- Tool allowlist；
- 网络隔离；
- Secret scope；
- Schema 校验；
- 返回内容视为不可信数据；
- 高风险 Tool 仍走审批；
- Audit。

MCP 标准化了连接方式，没有自动解决所有安全问题。

#### MCP 和普通 REST Tool 有什么区别？

普通 Tool：

```text
Agent Code
  ↓
写一个 Java Adapter
  ↓
REST API
```

MCP：

```text
Agent
 ↓
Standard MCP Client
 ↓
MCP Server
```

MCP 的价值主要在：

- 标准化发现；
- 统一 Tool / Resource 接入；
- 降低多客户端重复适配；
- 形成可复用生态。

但是：

> 如果系统内部只有两个固定 API，一个简单 Java Tool Adapter 完全够用，没必要为了“新”强行加 MCP。

#### MCP、Tool、A2A 怎么区分？

先记住：

```text
Tool：一个可执行能力
MCP：连接 Tool / Resource 的标准协议
A2A：Agent 和 Agent 之间协作
```

#### 项目怎么挂

工单 Agent 可以设计：

```text
Ticket Agent
 ├─ Local Tool → 本地工单 Service
 └─ MCP Client → Jira / 企业知识平台
```

如果你并没有在真实项目里部署 MCP，面试表达必须是：

> “这是我针对现有 Tool 接入方案研究的升级设计。”

而不是：

> “我们生产已经大规模用了 MCP。”

真实性：**LEARN / DESIGN。**

---


---

## TOOL-05【P1】Skill、Tool、Prompt、MCP 分别解决什么？

这几个词最容易被混成一团。

### 一张表

| 概念 | 主要回答的问题 |
|---|---|
| Prompt | 这次应该怎么理解/回答？ |
| Tool | 可以执行什么能力？ |
| Skill | 一类任务应该怎么完成？ |
| MCP | 外部能力如何标准化接入？ |

### Prompt

一次或一类模型调用的指令。

### Tool

一个可调用能力：

```text
queryOrder
sendEmail
searchKnowledge
```

### Skill

更像可复用任务包：

```text
Skill
 ├─ Instructions
 ├─ References
 ├─ Examples
 ├─ Scripts
 └─ Tool Guidance
```

不同框架对 Skill 的具体文件格式并不完全一样，所以不要把 `SKILL.md` 当成所有 Agent 平台的协议标准。

更稳妥的理解：

> Skill 是“任务方法与资源的可复用封装”。

### MCP

MCP 不告诉 Agent：

> “如何做好报销审核。”

它解决的是：

> “怎么标准化连接报销系统暴露的 Tool/Resource。”

---


---

## TOOL-06【P1】A2A 和 Tool / MCP 有什么区别？什么时候 Agent 调 Agent？

### 最简单记法

```text
Agent
 │
 ├─ Tool → 执行具体能力
 │
 ├─ MCP → 标准化连接工具/资源
 │
 └─ A2A → 和另一个独立 Agent 协作
```

### A2A 的对象不是普通函数

远程 Agent 可能：

- 自己有模型；
- 自己有 Tool；
- 自己有状态；
- 自己执行长任务；
- 返回 Artifact。

所以它更接近：

```text
Delegation / Collaboration
```

而不是：

```text
Function Call
```

### 什么时候有意义

例如：

```text
Enterprise Assistant
       │
       ├─ Finance Agent
       ├─ Legal Agent
       └─ IT Support Agent
```

这些 Agent 可能由不同团队、不同框架维护。

A2A 解决互操作。

### 当前标准认知

截至 2026-09，A2A 已发布 1.0.0 规范，目标就是让独立、甚至内部实现不透明的 Agent 能发现能力、协作任务并交换 Artifact。

### 学习优先级

对于 Java AI 应用面试：

```text
Tool Calling
   ↓
MCP
   ↓
Workflow / Agent Runtime
   ↓
Multi-Agent
   ↓
A2A
```

不要把 A2A 放在基础能力前面。

---


---

---

## 附：Tool Result 是否直接返回给用户

旧题库里关于 `returnDirect` 的问题继续保留。

有些 Tool Result 本身已经是最终答案，例如：

- 一个确定的查询结果；
- 一个已经格式化好的文件下载信息；
- 一个不需要模型再次解释的业务结果。

这类场景可以考虑让 Tool Result 直接结束 Tool Loop，避免再发给模型二次改写。

但高风险写操作不能因为“return direct”就跳过：

- 权限；
- 参数校验；
- 幂等；
- 审批；
- 审计。

Spring AI 2.0.x 的 Tool Calling 体系支持 Tool Metadata 层面的 direct-return 语义；正式代码仍应按项目使用版本核验 API。
