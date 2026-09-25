# 00 Java AI 基础知识手册

> 定位：这是 V2 的“知识底座”，负责承接旧题库中不适合做核心母题、但面试和工程实践仍然需要掌握的基础知识。
>
> 它不是临场速查版，也不是总目录。01～05 负责核心工程母题；06 负责项目场景。这里负责概念、术语、原理、选型常识、易错点和进阶知识。

---

## 1. 大模型与 Transformer 基础

### 1.1 什么是大语言模型 LLM

LLM（Large Language Model，大语言模型）本质上是一个基于上下文预测后续 Token 的概率模型。

应用工程师不需要把重点放在“会不会从头训练模型”，而要理解：

- 模型输入是什么；
- 模型输出为什么不确定；
- 上下文窗口有什么约束；
- 模型为什么会幻觉；
- 如何通过 RAG、Tool、Structured Output、Validation 把不确定性约束在工程边界里。

### 1.2 Transformer 为什么重要

Transformer 通过 Attention（注意力）机制建模序列内部不同位置之间的关系。

应用岗需要知道它带来的工程结果：

- 模型可以处理长文本；
- 上下文越长，计算和成本通常越高；
- “能塞进去”不等于“模型能稳定利用所有信息”；
- 长上下文不能自动替代 RAG、Memory 和 Context Engineering。

### 1.3 Token 是什么

Token（词元）是模型处理文本的基本单位，不等于“一个汉字”或“一个英文单词”。

Token 直接影响：

- 上下文容量；
- 请求成本；
- 输出上限；
- 延迟；
- Agent 每轮循环预算。

### 1.4 Tokenizer 是什么

Tokenizer（分词器）负责把字符串编码成 Token ID。

普通 Java AI 应用调用模型 API 时，通常不会自己“修改 Tokenizer”。

只有在模型训练、持续预训练、特殊领域词表等更底层场景中，Tokenizer 设计才可能成为主要问题。

### 1.5 Context Window 是什么

Context Window（上下文窗口）是一次模型调用可以处理的上下文容量。

上下文通常包括：

- System Prompt；
- User Message；
- Chat History；
- RAG Context；
- Tool Schema；
- Tool Result；
- Agent State 的可见部分。

工程上的关键问题不是“窗口越大越好”，而是：

> 哪些信息此刻真的需要进入模型。

---

## 2. 采样、输出与幻觉

### 2.1 Temperature / Top-p / Top-k

这些参数控制生成随机性。

经验原则：

- 事实问答、结构化抽取、Tool 参数：偏低随机性；
- 创意生成：可以适当增加随机性；
- 不要同时乱调多个参数，再凭感觉判断效果。

它们不是“准确率旋钮”。

### 2.2 max_tokens / max_output_tokens

输出 Token 上限不仅影响回答长度，也影响：

- 成本；
- 超时概率；
- 流式持续时间；
- Agent 单步预算。

Agent 系统还应该有整个执行级别的 Token Budget（Token 预算），不能只限制一次调用。

### 2.3 什么是幻觉

Hallucination（幻觉）指模型生成了缺乏事实依据、与来源冲突或被错误推断出来的内容。

降低幻觉通常需要多层手段：

1. 提供可靠数据；
2. RAG；
3. Tool；
4. Structured Output；
5. Validation；
6. Citation；
7. 拒答；
8. Evaluation。

不要说“RAG 可以彻底消灭幻觉”。

### 2.4 System / User / Assistant / Tool Message

不同 Message（消息）代表不同上下文角色。

重要安全点：

> Tool Result、网页、邮件、RAG 文档都是数据来源，不应该因为进入 Context 就自动拥有 System Instruction（系统指令）的可信级别。

这与 Indirect Prompt Injection（间接提示词注入）直接相关。

---

## 3. 模型类型与选型

### 3.1 Base / Instruct / Chat Model

- Base Model：基础语言模型；
- Instruct Model：经过指令对齐；
- Chat Model：面向多轮聊天和角色消息优化。

企业应用通常使用已经对齐的 Instruct/Chat 模型，而不是直接拿 Base Model 做业务聊天。

### 3.2 推理模型与普通聊天模型

推理模型通常更适合：

- 复杂规划；
- 多约束分析；
- 复杂代码和数学；
- 较长决策链。

普通聊天模型往往更适合：

- 分类；
- 提取；
- Rewrite；
- 简单问答；
- 低成本高并发任务。

所以生产系统常见的是 Model Routing（模型路由），而不是“一种模型干所有事”。

### 3.3 开源与闭源模型

主要比较：

- 能力；
- 成本；
- 隐私；
- 部署；
- 运维；
- 更新速度；
- 合规；
- Vendor Lock-in（供应商绑定）。

不要把“开源=便宜”或“闭源=能力一定强”当绝对结论。

### 3.4 云模型与本地模型

云模型优势：

- 接入快；
- 运维简单；
- 能力更新快。

本地模型优势可能包括：

- 数据边界可控；
- 网络依赖少；
- 可定制部署。

但本地模型会增加：

- GPU 成本；
- 推理运维；
- 扩缩容；
- 模型升级；
- 监控。

### 3.5 为什么不默认自己训练大模型

大多数 Java AI 应用项目的业务问题不是“缺一个从头训练的大模型”。

通常优先级更高的是：

- Prompt；
- RAG；
- Tool；
- 数据治理；
- Model Routing；
- Evaluation；
- Workflow / Agent。

只有现成模型无法通过这些方式满足需求时，再考虑 Fine-tuning（微调）。

---

## 4. 训练与适配知识

### 4.1 Pretraining

Pretraining（预训练）是在大规模语料上学习通用语言和知识能力。

应用岗理解概念即可。

### 4.2 SFT

SFT（Supervised Fine-Tuning，监督微调）使用标注的输入输出样本，让模型更符合特定任务或行为。

### 4.3 RLHF

RLHF（Reinforcement Learning from Human Feedback，人类反馈强化学习）通过人类偏好等信号进一步对齐模型行为。

### 4.4 DPO

DPO（Direct Preference Optimization，直接偏好优化）是一种利用偏好样本训练模型的方法。

不要在应用岗面试里把 DPO 当成必须会落地的工程主线。

### 4.5 LoRA / PEFT

LoRA 属于 PEFT（Parameter-Efficient Fine-Tuning，参数高效微调）方法。

适合降低微调所需显存和训练成本，但它解决的是“模型参数适配”问题，不是 RAG、Tool、数据更新问题。

### 4.6 什么时候不建议微调

如果问题主要是：

- 知识需要频繁更新；
- 企业私有数据问答；
- 需要实时业务数据；
- 需要执行外部系统操作；

优先考虑 RAG / Tool / API，而不是先微调。

### 4.7 Prompt Engineering vs Fine-tuning

Prompt 适合：

- 约束行为；
- 格式；
- Few-shot；
- 任务描述。

Fine-tuning 更适合稳定改变模型行为分布。

两者不是互斥关系，但也不能把 Fine-tuning 当成“Prompt 调不好就训练”。

---

## 5. 推理性能基础

### 5.1 TTFT 和 TPS

TTFT（Time To First Token，首 Token 时间）决定用户多久看到第一段输出。

TPS（Tokens Per Second，每秒 Token 数）影响后续生成速度。

聊天产品通常同时关注：

- TTFT；
- 总响应时间；
- 流式稳定性。

### 5.2 KV Cache

KV Cache（键值缓存）保存 Transformer 推理中的中间注意力状态，减少生成后续 Token 时的重复计算。

这是模型推理服务层能力，不是 Redis 业务缓存。

### 5.3 Batch 与 Continuous Batching

Batching（批处理）把多请求放在一起计算，提高 GPU 利用率。

Continuous Batching（连续批处理）允许动态把新请求加入推理批次，更适合在线推理服务。

### 5.4 Prompt Caching

Prompt Cache（提示词缓存）复用重复前缀的模型计算。

它和 Semantic Cache（语义缓存）不是一回事：

- Prompt Cache：推理计算层复用；
- Semantic Cache：应用层根据语义近似复用答案。

### 5.5 长上下文为什么更贵

长 Context 会增加：

- 输入 Token 成本；
- Prefill 延迟；
- 注意力计算；
- 无关信息干扰。

因此 AGENT-06 的 Context Engineering 仍然必要。

### 5.6 Speculative Decoding

Speculative Decoding（推测解码）通过较小模型先提出候选 Token，再由主模型验证，从而提升生成速度。

应用岗理解原理和适用条件即可。

### 5.7 PagedAttention

PagedAttention 通过类似分页的方式更高效管理 KV Cache，典型用于高吞吐推理引擎。

不要把它说成 Java 应用代码中的缓存算法。

---

## 6. 模型部署基础

### 6.1 量化 Quantization

Quantization（量化）降低模型参数数值精度，以换取：

- 更低显存；
- 更快推理；
- 更低部署成本。

可能代价：

- 精度损失；
- 部分任务质量下降。

量化和微调是两个不同维度。

### 6.2 本地部署主要看什么

至少看：

- 模型参数规模；
- 权重精度；
- GPU 显存；
- Context Length；
- 并发；
- Batch；
- KV Cache；
- TTFT；
- TPS。

不能只问“这个模型需要几张卡”。

### 6.3 Ollama / llama.cpp / vLLM / Xinference

理解层次即可：

- Ollama：偏本地快速运行和模型管理；
- llama.cpp：强调轻量、CPU/多硬件后端；
- vLLM：偏高吞吐 GPU 推理服务；
- Xinference：多模型服务与管理能力。

实际选型必须看当前版本、部署环境和团队能力，不做永久排行榜。

### 6.4 私有化部署要问推理团队什么

应用团队至少需要明确：

- Endpoint；
- API 协议兼容性；
- 模型版本；
- Context Limit；
- Rate Limit；
- Timeout；
- Streaming；
- Structured Output；
- Tool Calling；
- Embedding 能力；
- 日志和计量方式；
- 灰度升级策略。

---

## 7. Prompt 基础

### 7.1 Zero-shot / Few-shot

- Zero-shot：只给任务说明；
- Few-shot：加入少量输入输出示例。

Few-shot 对格式、分类边界和特殊业务规则常有帮助。

### 7.2 Chain-of-Thought

应用系统不要把模型隐藏推理链当审计记录。

工程上应该记录的是可观察信息：

- 输入；
- 选了什么 Tool；
- 参数；
- Tool Result；
- 状态变化；
- 最终结论；
- 错误原因。

### 7.3 一个 System Prompt 应包含什么

常见内容：

- 角色；
- 任务范围；
- 数据边界；
- 输出要求；
- 禁止行为；
- Tool 使用规则；
- 无法回答时的处理方式。

Prompt 不是权限系统。

### 7.4 Prompt Chaining

Prompt Chaining（提示链）把复杂任务拆成多个确定步骤。

如果流程本身可以预先确定，它通常比完全自治 Agent 更可控。

---

## 8. RAG 基础概念

### 8.1 RAG 是什么

RAG（Retrieval-Augmented Generation，检索增强生成）：

> 先从外部知识源检索相关内容，再把它作为 Context 提供给模型生成答案。

它主要解决动态/私有知识问题。

### 8.2 RAG 与 Fine-tuning

RAG 适合知识更新。

Fine-tuning 更适合改变行为、格式、领域风格或特定任务能力。

### 8.3 RAG 与传统搜索

传统搜索的目标通常是“找文档”。

RAG 的目标通常是：

> 找证据 + 组织上下文 + 生成回答。

企业系统经常两者共存。

### 8.4 Embedding

Embedding（向量嵌入）把文本映射成向量，使语义相近的文本在向量空间中更接近。

### 8.5 Cosine / Dot Product / Euclidean

常见向量相似度：

- Cosine Similarity（余弦相似度）；
- Dot Product（点积）；
- Euclidean Distance（欧氏距离）。

使用哪一个要与 Embedding 模型及向量数据库索引设计匹配。

### 8.6 Flat / IVF / HNSW / PQ

这些是向量索引或压缩相关方法。

工程上理解：

- Flat：精确但规模大时成本高；
- IVF：通过聚类缩小搜索范围；
- HNSW：基于图结构做近似最近邻；
- PQ：压缩向量降低存储和计算。

不要说“HNSW 永远最好”。

### 8.7 Dense / Sparse Retrieval

Dense Retrieval（稠密检索）主要基于 Embedding 语义。

Sparse Retrieval（稀疏检索）更偏词项匹配，例如 BM25。

两者可以组合成 Hybrid Search（混合检索）。

### 8.8 BM25

BM25 是经典关键词相关性算法，会考虑词频、文档长度等因素。

它在：

- 编号；
- 专有名词；
- 错误码；
- 精确关键词；

这些场景里仍然非常有价值。

### 8.9 Recall / Rank / Rerank

三个阶段要区分：

1. Recall（召回）：先找一批候选；
2. Rank（排序）：按检索分数排序；
3. Rerank（重排）：使用更强模型重新判断候选相关性。

不要把“召回”和“重排”说成同一个东西。

### 8.10 Grounded Answer

Grounded Answer（有依据回答）强调最终答案可以由提供的证据支持。

它比“读起来合理”更重要。

### 8.11 Query Rewrite 与 Query Expansion

Query Rewrite：把问题重写成更完整、适合检索的查询。

Query Expansion：扩展同义词、相关概念或多个查询。

两者目标不同。

### 8.12 Long Context 会替代 RAG 吗

不会简单替代。

因为 RAG 仍然可以提供：

- 权限过滤；
- 动态知识；
- 精确召回；
- Citation；
- 更低 Token 成本；
- 知识更新。

### 8.13 Lost in the Middle

Lost in the Middle（中间信息利用下降）描述长上下文中位于中间部分的重要信息可能更难被模型有效利用的现象。

所以“把所有文档塞进去”不是可靠架构。

---

## 9. RAG 进阶知识

### 9.1 Self-RAG

Self-RAG 强调模型对“是否需要检索、检索结果是否足够”等过程进行反思或控制。

属于进阶路线，不是所有企业 RAG 的默认方案。

### 9.2 CRAG

CRAG（Corrective RAG，纠错式 RAG）核心思想是：

> 对检索结果质量做判断，质量不足时触发补充或替代检索路径。

### 9.3 GraphRAG

GraphRAG 把实体、关系或图结构加入检索和聚合。

更适合：

- 强关系问题；
- 跨文档关系；
- 全局主题总结。

不应因为“高级”就替代普通 RAG。

### 9.4 Multi-hop Retrieval

Multi-hop Retrieval（多跳检索）用于一个问题需要多步证据才能回答的场景。

常与 Query Decomposition（问题分解）结合。

### 9.5 HyDE

HyDE（Hypothetical Document Embeddings，假想文档嵌入）先生成一个可能的答案/文档，再用它帮助检索。

风险是模型生成的假设可能带偏检索。

### 9.6 Contextual Retrieval

Contextual Retrieval 强调给 Chunk 补充所在文档、章节或主题上下文，提高片段被独立检索时的可理解性。

### 9.7 ColBERT / Late Interaction

Late Interaction（后期交互）类方法对 Query 和 Document 保留更细粒度表示，再进行匹配。

质量可能优于单向量，但索引和计算更复杂。

### 9.8 Late Chunking

Late Chunking 是先在较长上下文中编码，再派生 Chunk 表示的一类思路。

属于进阶优化，不是标准默认方案。

### 9.9 RAPTOR

RAPTOR 一类方法构建多层摘要/聚类结构，支持跨粒度检索。

适合复杂长文档，但工程复杂度更高。

### 9.10 Multimodal RAG

Multimodal RAG（多模态 RAG）需要处理：

- 文本；
- 图片；
- 图表；
- 扫描页；
- 音视频信息。

关键不是“模型能看图”四个字，而是解析、索引、检索和引用如何统一。

### 9.11 Code RAG

Code RAG 需要理解：

- 文件；
- 类；
- 方法；
- 调用关系；
- 依赖；
- Symbol（符号）。

不能直接把代码仓库当普通文章切段。

---

## 10. Agent 基础 Pattern

### 10.1 Workflow

Workflow（工作流）适合路径可预先确定的任务。

优势：

- 可控；
- 可测试；
- 可恢复；
- 容易审计。

### 10.2 ReAct

ReAct 可抽象成循环：

```text
Observe → Decide → Tool → Observe → ...
```

生产实现重点是循环控制和可观察事件，不是暴露模型隐藏 Thought（思维链）。

### 10.3 Routing

Routing（路由）根据输入选择：

- Model；
- Agent；
- Workflow；
- Tool；
- RAG 路径。

### 10.4 Orchestrator-Workers

一个 Orchestrator（协调器）拆分任务，多个 Worker（执行者）完成子任务。

适合可以并行或按角色分工的复杂任务。

### 10.5 Evaluator-Optimizer

Evaluator-Optimizer（评估-优化）让一个模块执行、另一个模块评估并反馈。

由于会增加调用次数和成本，只适合高价值任务。

### 10.6 Plan-and-Execute

先制定计划，再按步骤执行。

适合多步骤任务，但计划并不保证正确，执行中仍需要状态、预算和错误处理。

### 10.7 Reflexion

Reflexion 类模式通过执行结果反馈来调整后续策略。

不要把它描述成“已经替代 ReAct”的新标准。

---

## 11. Evaluation 基础

### 11.1 LLM-as-a-Judge

LLM-as-a-Judge（用大模型做评审）适合辅助评测：

- Correctness；
- Relevance；
- Style；
- Faithfulness。

但 Judge 自己也有偏差，不是真值来源。

### 11.2 Golden Dataset

Golden Dataset（金标数据集）是稳定的测试样本集合。

用途：

- Prompt 回归；
- 模型升级；
- RAG 参数调整；
- Agent 版本发布。

### 11.3 RAGAS

RAGAS 是 RAG 评估工具/框架之一。

重要的是理解指标定义和自己的评测集，不要把“用了 RAGAS”当成“评估已经做好”。

---

## 12. 多模态与其他 AI 能力

### 12.1 多模态模型

Multimodal Model（多模态模型）可以处理文本之外的图片、音频、视频等输入。

工程重点包括：

- 文件处理；
- 大小限制；
- MIME；
- 存储；
- Prompt；
- 结果验证。

### 12.2 语音 AI

典型链路：

```text
Audio
 → ASR（语音识别）
 → LLM
 → TTS（语音合成）
 → Audio
```

实时语音还要处理：

- VAD；
- 打断；
- 流式传输；
- 延迟。

### 12.3 图像生成

图像生成和文本生成的工程差异包括：

- 输出不是 Token 文本；
- 任务耗时更长；
- 文件存储；
- 异步任务；
- 安全审核；
- GPU 资源。

### 12.4 代码模型

企业内使用代码模型时要考虑：

- Repo 权限；
- Secrets；
- Sandbox（沙箱）；
- 执行权限；
- 生成代码审查；
- Test。

---

## 13. Java AI 周边工程知识

### 13.1 Redis 在 AI 应用中的常见用途

Redis 可以用于：

- Chat History；
- Agent State；
- Cache；
- Semantic Cache 索引辅助；
- Rate Limit；
- Idempotency；
- Task Progress；
- Distributed Lock。

具体项目不能因为“AI 应用”就全都用 Redis。

### 13.2 gRPC / Dubbo

适合 Java 微服务内部高效 RPC。

是否使用取决于：

- 现有技术栈；
- 跨语言；
- 流式；
- 内网服务治理。

### 13.3 Docker / Kubernetes

AI 应用岗位会出现 Docker/K8s，是因为生产系统仍然需要：

- 部署；
- 扩缩容；
- 配置；
- 健康检查；
- 灰度；
- 资源限制。

### 13.4 MQ 的轻量替代不能混为一谈

JVM Queue、Redis Stream、RabbitMQ、Kafka、Resilience4j 解决的问题并不相同。

选型先问：

> 需要持久化吗？需要跨进程吗？需要重放吗？需要削峰吗？允许丢吗？

---

## 14. AI Coding 与研发效能

AI Coding 工具适合：

- 生成样板代码；
- 单元测试；
- 重构建议；
- 文档；
- 代码理解；
- 查 API。

不适合无审查直接执行：

- 安全敏感代码；
- 生产数据库变更；
- 权限设计；
- 大型架构决策；
- 未验证依赖升级。

原则：

> AI 可以提高编码速度，但 Review、Test、Security、Architecture 责任仍在工程团队。

---

## 15. 常见面试易错卡

### 错误 1

“Java 做不了 AI。”

应改为：

> Java 不适合承担主流大模型训练生态的核心角色，但非常适合企业 AI 应用层和生产系统集成。

### 错误 2

“RAG 就是向量库 + Prompt。”

应改为：

> 生产 RAG 包含文档处理、索引、检索、权限、版本、评测、可观测性和生成链路。

### 错误 3

“Agent 就是 ReAct。”

应改为：

> ReAct 是 Agent Pattern 之一；生产 Agent 更关键的是 Runtime、State、Tool、Budget、Checkpoint、HITL 和治理。

### 错误 4

“上了 MCP 就安全、统一了。”

应改为：

> MCP 统一连接方式，但权限、身份、租户、审计、超时和 Tool 风险仍由应用治理。

### 错误 5

“线程越多越快。”

应改为：

> 并发上限受下游容量、DB 连接、模型限额和服务延迟约束。

### 错误 6

“Virtual Thread 会让一次请求执行更快。”

应改为：

> Virtual Thread 主要提升大量阻塞 I/O 任务的并发承载能力，不保证单请求变快。

### 错误 7

“用了 Manual ACK 就 Exactly Once。”

应改为：

> MQ 重投仍然可能发生，真正防重复副作用要靠业务幂等。

### 错误 8

“Schema 合法就等于业务正确。”

应改为：

> Structured Output 只能保证结构，业务规则还需要 Validation 和权限检查。

---

## 16. 学习优先级

### P0：必须掌握

- Token / Context；
- Hallucination；
- Prompt / Message；
- Structured Output；
- RAG 基础；
- Embedding；
- Dense / Sparse；
- Workflow / Agent；
- Tool Calling；
- Java AI 工程边界。

### P1：面试加分

- HNSW / IVF；
- Rerank；
- GraphRAG；
- Agent Pattern；
- Evaluation；
- Model Routing；
- 推理性能术语。

### P2：理解即可

- RLHF / DPO；
- MoE；
- Speculative Decoding；
- PagedAttention；
- RAPTOR；
- DSPy；
- Embedding Fine-tuning。

---

## 17. 与后续文档的关系

- `01-Java-AI应用工程.md`：Java AI 应用核心题。
- `02-RAG与知识工程.md`：生产 RAG。
- `03-Agent-Runtime与Context-Engineering.md`：Agent Runtime。
- `04-Tool-MCP-Skill-A2A.md`：企业能力连接与调用。
- `05-Java企业工程与生产治理.md`：并发、MQ、一致性、安全、可观测性。
- `06-项目场景与工程实战.md`：把上面知识落到项目场景。

这份手册不替代 01～06；它只负责基础知识和查漏补缺。

---

## 18. 原题库保留的补充知识点

这一章专门承接 V1 迁移表里已经确定“保留，但不占 49 道核心母题”的知识点。它们不能因为不是高频主线就消失。

### 18.1 Alignment（对齐）和 Guardrail（应用护栏）不是一回事

Alignment（模型对齐）发生在模型训练/后训练层，目标是让模型行为更符合人类偏好、安全要求或任务目标。

Guardrail（应用护栏）发生在应用系统层，例如：

- 输入检查；
- 输出检查；
- Tool 权限；
- 数据权限；
- 审计；
- HITL；
- 敏感信息处理。

面试里不要说“模型做过 Alignment，所以应用层就安全了”。两层解决的问题不同。

### 18.2 Knowledge Distillation（知识蒸馏）

Knowledge Distillation（知识蒸馏）通常是让较小的 Student Model（学生模型）学习较强 Teacher Model（教师模型）的行为或分布。

应用岗理解它的价值即可：

- 降低推理成本；
- 降低延迟；
- 将能力迁移到更小模型；
- 私有化部署时减少硬件压力。

它不是 RAG、缓存或模型路由的替代品。

### 18.3 MoE（Mixture of Experts，混合专家模型）

MoE 会在多个 Expert（专家子网络）中按输入动态激活一部分，而不是每次把全部参数都参与计算。

应用岗主要理解：

- “总参数很大”不等于每 Token 都激活全部参数；
- 部署成本和吞吐不能只看模型总参数；
- 实际推理能力、显存、路由与服务实现仍要看具体模型。

不要把 MoE 直接理解成“多个 Agent”。两者层级完全不同。

### 18.4 本地模型 Cold Start（冷启动）

本地模型服务第一次加载可能受以下因素影响：

- 权重从磁盘加载；
- GPU 显存分配；
- Kernel 初始化；
- 模型 Warm-up（预热）；
- KV Cache / Runtime 初始化。

因此生产环境通常需要考虑：

- readiness probe（就绪探针）；
- warm-up；
- 预留实例；
- 扩容提前量；
- 首请求不要直接承担初始化成本。

### 18.5 Multilingual RAG（多语言 RAG）

多语言 RAG 不能只看“模型支持中文和英文”。还要检查：

- Embedding 是否跨语言对齐；
- Query 和 Document 是否同语言；
- BM25 分词是否支持对应语言；
- OCR / Parser 是否能正确识别语言；
- Reranker 是否支持多语言；
- Citation 原文是否需要翻译；
- 多语言 Golden Dataset 是否覆盖真实用户问题。

常见方案包括：

1. 使用多语言 Embedding；
2. Query 翻译后检索；
3. 多语言索引并行检索；
4. 原文检索，答案按用户语言生成。

具体选择必须通过业务数据评测。

### 18.6 Vector Memory（向量记忆）和经验复用

可以把历史事实、偏好、任务经验等向量化后按语义检索，但不能把向量记忆当作精确业务状态数据库。

适合：

- 召回相关历史；
- 找相似案例；
- 推荐过去处理经验。

不适合承担：

- 精确余额；
- 当前审批状态；
- 是否已经扣款；
- Agent 当前步骤。

精确状态仍应放在结构化 State / DB / Checkpoint 中。

### 18.7 Map-Reduce 长文档摘要

多文档或超长文档摘要可以使用 Map-Reduce 思路：

```text
Documents
  ↓
Map：分片摘要 / 局部抽取
  ↓
Intermediate Results
  ↓
Reduce：合并、去重、冲突处理
  ↓
Final Summary
```

它适合长度超过单次有效上下文预算的场景，但要注意：

- 中间摘要可能丢信息；
- 不同片段可能冲突；
- 多轮模型调用增加成本；
- 关键事实最好保留结构化 Evidence，而不是只剩摘要文本。

### 18.8 Semantic Kernel

Semantic Kernel 是一套面向 AI 应用编排的 SDK/框架思路，涉及模型连接、Plugin/Function、Prompt、Memory/Agent 等抽象。

Java AI 应用岗不必把它当主栈，但应理解：

> 它和 Spring AI、LangChain4j 一样，解决的是“如何把模型能力接进应用系统并进行编排”的一类问题。

选型依赖现有技术栈和团队生态，不做永久排名。

### 18.9 DSPy

DSPy 的核心价值可以理解为：

> 用程序化方式描述 LLM Pipeline，并基于数据和评价指标优化 Prompt / 模块，而不是完全手工调提示词。

应用岗理解思想即可。它不意味着“自动优化以后就不需要人工评测”。

### 18.10 Embedding Fine-tuning / Tuning

当通用 Embedding 在真实业务语料上表现不足时，可以考虑：

- 更换 Embedding 模型；
- 调整 Chunk；
- 改 Query；
- Hybrid Search；
- Rerank；
- 最后再评估 Embedding Fine-tuning。

Embedding 微调不是默认第一步。

要有：

- 正样本；
- Hard Negative（困难负样本）；
- 稳定 Retrieval Eval；
- 新旧模型双索引或可回滚迁移策略。

### 18.11 RAG 的演进方向，但不要当成必然替代路线

可以继续关注：

- Hybrid Retrieval；
- Rerank；
- Contextual Retrieval；
- GraphRAG；
- Agentic RAG；
- Multimodal RAG；
- Dynamic Source Selection；
- Evaluation-driven Optimization（评测驱动优化）。

这些是能力选项，不是“越新越高级、越应该全上”。

---

## 19. 2026 Java AI 工程现状与持续关注方向

这一节承接原 Appendix L，但不再写没有依据的年份预测和比例。

### 19.1 Tool Calling 正在升级成 Agent Runtime 问题

实际工程关注点已经从“模型能不能调函数”扩大到：

- Tool 发现；
- 状态；
- Checkpoint；
- Budget；
- Timeout；
- Retry；
- HITL；
- Cancel；
- Audit。

### 19.2 Tool Registry / Dynamic Tool Discovery

当 Tool 数量达到几十甚至几百个时，全部塞入 Prompt 并不合理，需要 Registry、Search、按需暴露和权限过滤。

### 19.3 MCP 已进入企业能力连接层

MCP 解决连接标准化问题，但不会自动解决：

- 身份；
- 权限；
- Tenant；
- 审计；
- 不可信 Server；
- Tool 风险。

### 19.4 Skills 成为可复用能力封装

Skill 可以包含说明、脚本、参考资料和资源，并通过渐进加载减少一次性 Context 压力。

### 19.5 State / Checkpoint / Durable Execution 更重要

长任务、审批任务和有副作用任务要求系统能暂停、恢复和确认已执行动作，而不是只保留 Chat History。

### 19.6 Multi-Agent / A2A 是能力选项，不是默认架构

优先顺序通常应是：

```text
单 Agent + Tool
  ↓ 不够再看
Multi-Agent
  ↓ 跨独立 Agent 系统再看
A2A
```

### 19.7 Context Engineering 已成为核心工程能力

重点从“写一个 Prompt”扩大为：

- History；
- RAG；
- Memory；
- Tool Result；
- State；
- Policy；
- Token Budget；
- Trust Boundary。

### 19.8 Evaluation 正在变成发布门禁

Prompt、Model、Embedding、Reranker、Agent Workflow 任何升级，都应该有回归评测和灰度指标，而不是上线后靠感觉判断。

---

## 20. 面试与架构表达原则（保留原题知识，不展开成独立面试稿）

这一节只保留原题库中的表达方法，不制作单独“项目面试稿”。

### 20.1 怎么证明不是只会调用 API

回答重点应落在：

- 数据如何进入系统；
- RAG 如何评测；
- Tool 如何治理；
- Java 如何处理权限、事务、状态、并发、MQ、可观测性；
- 模型失败时系统如何降级。

能说清这些，比展示一段 `chatModel.call()` 更有说服力。

### 20.2 遇到新名词怎么说才不虚

可以分三层：

1. 我实际做过；
2. 我做过 Demo / 设计；
3. 我研究过原理。

不要把三层混成“生产经验”。

### 20.3 平台化、工程化、业务化分别在说什么

- 业务化：解决真实业务任务；
- 工程化：可靠、可测、可观测、可运维；
- 平台化：让多个团队/应用复用统一能力和治理。

### 20.4 RAG 不是银弹

以下场景可能不需要 RAG：

- 精确实时数据可以直接 API / SQL；
- 固定业务规则；
- 纯创作任务；
- 数据量极小且上下文稳定；
- 权限和一致性要求更适合结构化查询。

### 20.5 为什么招聘越来越强调 RAG 优化和 Agent 平台

因为企业落地难点已经从“调用模型”转到：

- 私有知识；
- 工具接入；
- 权限；
- 稳定性；
- 评测；
- 成本；
- 状态和恢复；
- 复用和治理。

这也是 Java 后端能力能够发挥价值的地方。

---

## 21. 学习路线与资料使用原则

这一节承接旧题库中“经典资料、工程博客、前沿论文、面试前资料顺序”等学习路线内容。它们不是面试母题，但不应消失。

### 21.1 学习资料的优先级

建议顺序：

1. 官方文档 / Specification（规范）；
2. 官方示例 / 官方仓库；
3. 高质量工程博客；
4. 开源项目源码；
5. 论文；
6. 二手总结。

原因很简单：应用工程岗位首先要把“当前能怎么用、边界是什么”搞清楚，再决定是否深挖论文。

### 21.2 RAG 的经典起点

学习 RAG 时先掌握：

- Retrieval；
- Embedding；
- Chunk；
- Vector Search；
- Hybrid Search；
- Rerank；
- Evaluation。

不要一开始就跳 GraphRAG / Agentic RAG，把基础链路漏掉。

### 21.3 检索优化资料应该围绕问题找

遇到真实 Bad Case 后再查：

- 召回差 → Embedding / Query / Hybrid；
- 排序差 → Rerank / Fusion；
- Chunk 不完整 → Parent-Child / Neighbor；
- 多跳问题 → Query Decomposition；
- 长文档 → Contextual Retrieval / RAPTOR 等。

学习路线应被问题驱动，而不是按名词热度堆技术。

### 21.4 为什么工程博客仍然重要

论文告诉你方法，工程博客往往告诉你：

- 怎么上线；
- 什么会失败；
- 延迟在哪里；
- 成本如何；
- 如何降级；
- 如何评测。

但博客里的固定参数和结论必须回到自己的数据验证。

### 21.5 前沿论文怎么排优先级

Java AI 应用岗优先看与工作直接相关的论文/技术报告：

- Retrieval；
- Rerank；
- Long Context；
- Tool Use；
- Agent Evaluation；
- Context Engineering；
- Multimodal Retrieval。

纯模型训练论文可以按兴趣和岗位要求继续深入，但不应挤掉应用工程主线。

### 21.6 面试前资料复习顺序

优先：

```text
项目真实链路
→ 49 核心母题
→ Java 生产工程
→ 常见 Bad Case
→ 基础知识手册
→ P2 前沿知识
```

不要在面试前最后两天把时间都花在新名词上。

### 20.6 Java 后端 + AI 自我介绍怎么组织

保留旧题库这个表达题，但这里只给结构，不写个人成稿：

```text
Java 后端基础
→ 做过哪些业务系统
→ 为什么转向 AI 应用工程
→ RAG / Agent / Tool 里真正做过什么
→ Java 工程能力如何解决生产问题
```

重点不要变成：

> “我会很多模型名和框架名。”

更好的证明方式是把自己的 Java 后端能力与 AI 应用链路连起来，例如并发、缓存、MQ、权限、一致性、可观测性与模型/RAG/Tool 的结合。

---

## 22. AI 编程工具与人机协作研发

这一节保留 V1 `05-01~06` 的知识点。它不进入 49 个核心母题，但属于当前 Java AI 应用岗位常见的研发效能要求。

### 22.1 为什么招聘 JD 会写 Cursor、Claude Code、Codex 这类 AI 编程工具

企业关注的并不是“会不会让 AI 替你写代码”，而是能否把 AI 纳入正规的软件工程流程，提高需求分析、代码生成、测试、重构、排错和文档整理效率，同时仍由工程师对架构、安全和质量负责。

### 22.2 面试中怎么证明自己会用 AI 编程工具

不要只回答“我用过”。更有效的表达是说明完整工作流：

1. 先把需求、边界和验收条件说明白；
2. 让 AI 辅助生成样板代码、测试骨架或初步实现；
3. 人工检查业务规则、并发、事务、权限、安全和异常路径；
4. 运行单元测试、集成测试、静态检查和真实环境验证；
5. 对关键修改做 Code Review（代码审查），再进入正常发布流程。

### 22.3 哪些任务适合优先交给 AI

- CRUD、DTO、Mapper 等样板代码；
- 单元测试和测试数据初稿；
- 重复代码重构；
- 日志和异常的第一轮分析；
- 陌生代码解释；
- 文档、注释、接口示例整理；
- 在明确约束下生成小范围实现方案。

共同特点是：**上下文明确、结果容易验证、出错成本可控。**

### 22.4 哪些任务不能直接放手给 AI

- 核心业务规则和领域边界；
- 权限与安全策略；
- 分布式事务和一致性；
- 幂等与有副作用操作；
- 容量规划和性能瓶颈；
- 涉及真实法律、合规、资金和生产变更的决策。

AI 可以辅助分析，但最终工程责任仍然在开发者。

### 22.5 人机协作开发的核心能力

真正需要训练的是三件事：

1. **Intent Specification（意图规格化）**：把目标、约束、接口和验收标准说清楚；
2. **Verification（验证）**：知道如何证明 AI 生成的结果是对的；
3. **System Control（系统把控）**：知道哪些决策必须由人或确定性代码掌握。

这与 Java AI 应用工程本身是一致的：模型提供概率性能力，工程系统负责边界和最终质量。

### 22.6 常见错误

- 把“会用 Cursor/Claude Code/Codex”等同于“AI 工程能力强”；
- AI 生成代码后不运行测试就提交；
- 把密钥、客户数据、内部源码无边界地发送给外部工具；
- 因为 AI 写得快，就跳过架构设计、代码审查和发布流程；
- 面试时把 AI 生成的代码说成自己完全理解的生产经验。
