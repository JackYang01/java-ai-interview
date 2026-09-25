# 02 RAG 与知识工程

> Java AI 面试题库 V2 主体文档。
> 覆盖从文档进入知识库，到在线检索、权限、评测、更新、性能与大规模架构的完整 RAG 工程链路。

## 本文件题目

- RAG-01【P0】一个生产级 RAG 的完整链路是什么？
- RAG-02【P0】PDF、Word、Excel、扫描件到底怎么解析？
- RAG-03【P0】Chunk 到底怎么切？Chunk Size 和 Overlap 怎么定？
- RAG-04【P1】Embedding 模型和向量数据库怎么选？
- RAG-05【P0】为什么企业 RAG 经常需要 Hybrid Search？
- RAG-06【P1】TopK、Threshold、RRF、Rerank 怎么一起调？
- RAG-07【P0】多轮对话为什么容易把检索搞坏？Query Rewrite 怎么设计？
- RAG-08【P1】Excel、数据库、报表这些结构化数据应该怎么处理？
- RAG-09【P0】权限、版本和 Citation 怎么进入 RAG 链路？
- RAG-10【P1】文档更新、删除、Embedding 模型升级怎么处理？
- RAG-11【P0】RAG 回答错了，怎么定位到底哪一层出了问题？
- RAG-12【P0】RAG 怎么建立 Golden Dataset 和 Bad Case 闭环？
- RAG-13【P1】RAG 怎么做性能、稳定性和成本治理？
- RAG-14【P1】什么时候应该升级成 Agentic RAG？
- RAG-15【P1】百万级甚至千万级 Chunk 怎么做系统设计？

---

## 面试递进路线（冻结版）

RAG 的 15 道母题按一套真实系统从“能跑”到“生产化、规模化”的顺序组织：

```text
RAG-01 一套生产 RAG 的完整链路是什么？
   ↓ 数据怎么真正进入知识库
RAG-02 PDF / Word / Excel / 扫描件怎么解析？
   ↓ 文本拿到了以后怎么切
RAG-03 Chunk 怎么设计？
   ↓ 切完以后怎么表示和存储
RAG-04 Embedding 和 Vector DB 怎么选？
   ↓ 单一向量检索够不够
RAG-05 Hybrid Search 怎么做？
   ↓ TopK / 阈值 / RRF / Rerank 怎么调
RAG-06 检索漏斗怎么调优？
   ↓ 多轮对话的问题为什么越来越难搜
RAG-07 Query Rewrite 怎么做、改错怎么办？
   ↓ 如果数据本来就是结构化数据呢
RAG-08 RAG / Text-to-SQL / API / OLAP 怎么选？
   ↓ 企业知识不能只谈效果，还要谈权限和证据
RAG-09 权限、版本、Citation 怎么保证？
   ↓ 文档更新、删除、Embedding 升级怎么办
RAG-10 索引生命周期怎么治理？
   ↓ 用户还是说答错了，怎么定位
RAG-11 RAG 错答怎么分层排查？
   ↓ 怎么证明修复真的有效
RAG-12 RAG 怎么评测并形成 Bad Case 闭环？
   ↓ 生产上还要看性能、稳定性、成本
RAG-13 RAG 怎么做生产治理？
   ↓ 固定检索链不够时是否需要 Agentic RAG
RAG-14 什么时候上 Agentic RAG？
   ↓ 数据规模继续扩大怎么办
RAG-15 百万 / 千万级 Chunk 怎么设计？
```

**练习方式**：先把 RAG-01 说成总图，面试官随后问到哪一层，就进入对应母题；这样不会把 15 道题背成 15 段孤立答案。

## 使用原则

- 先理解设计目标，再记 API；版本敏感 API 在真实开发前重新核对官方文档。
- 项目内容严格区分 REAL（真实做过）、DESIGN（设计方案）、LEARN（学习储备）、VERIFY（待核实）。
- 固定参数、QPS、准确率、P99、命中率等，没有真实数据就不写成项目事实。
- 英文术语首次出现时尽量给出中文含义，面试表达以中文工程逻辑为主。

---

## RAG-01【P0】一个生产级 RAG 的完整链路是什么？

这道题是整个 RAG 章节的总纲。

建议不要从：

> “RAG 是 Retrieval-Augmented Generation……”

开始背定义。

直接讲系统。

---

### RAG 有两条链

#### 第一条：离线知识入库

```text
文档上传
  ↓
原文件保存
  ↓
解析 Parse
  ↓
清洗 Clean
  ↓
结构识别
  ↓
Chunk
  ↓
Metadata
  ↓
Embedding
  ↓
Index
```

这里真正麻烦的是：

- PDF；
- Word；
- Excel；
- OCR；
- 表格；
- 标题层级；
- 文档版本；
- 权限；
- 增量更新。

---

#### 第二条：在线问答

```text
User Query
    ↓
Query理解 / Rewrite
    ↓
Permission Filter
    ↓
Retrieve
 ┌──────┴──────┐
Vector        BM25
 └──────┬──────┘
        ↓
      Fusion
        ↓
      Rerank
        ↓
 Context Build
        ↓
       LLM
        ↓
 Answer + Citation
```

---

### 生产系统还要再加一层“横切能力”

```text
             RAG
              │
 ┌────────────┼─────────────┐
 │            │             │
Permission  Version      Observability
 │            │             │
Citation    Eval         Cost / Latency
```

所以完整 RAG 远远不是：

> “把文档切块，存向量库，然后搜 TopK。”

---

### Java 里通常怎么拆？

一种比较清楚的分层：

```text
API Layer
   ↓
RAG Orchestrator
   │
   ├─ QueryRewriteService
   ├─ RetrievalService
   ├─ RerankService
   ├─ ContextBuilder
   └─ AnswerService
          │
          ▼
Infrastructure
 ├─ Vector Store
 ├─ Search Engine
 ├─ Redis
 ├─ Object Storage
 ├─ DB
 └─ Model Provider
```

好处是：

- 换 Embedding 不影响业务层；
- 换向量库不会把整个 Service 改烂；
- Rerank 可以独立开关；
- 每一层都可以单独 Trace。

---

### 面试官会继续问：“最容易出问题的是哪？”

不要只说模型。

RAG 很多问题其实出在模型之前：

1. 文档解析错；
2. Chunk 切断语义；
3. Metadata 缺失；
4. 权限 Filter 错；
5. Query Rewrite 跑偏；
6. 正确 Chunk 没召回；
7. Rerank 把正确结果压下去；
8. Context 塞太多噪声。

所以：

> RAG 的核心能力之一其实是 Retrieval Failure Analysis（检索失败分析）。

---

### 一个很实用的判断

如果问题是：

> “公司报销制度规定什么？”

适合 RAG。

如果问题是：

> “我的报销单现在审批到谁了？”

更适合：

```text
Tool / API / Database
```

而不是把实时状态做成静态向量。

---

### PMO 项目怎么挂

PMO 知识助手可以沿着这条链连续讲：

```text
项目文档
 ↓
解析
 ↓
Chunk
 ↓
Embedding
 ↓
Hybrid Search
 ↓
Rerank
 ↓
Query Rewrite
 ↓
权限
 ↓
Citation
 ↓
Evaluation
```

但哪些环节是你真实做过的，要等 Project Fact Sheet 确认。

---


---

## RAG-02【P0】PDF、Word、Excel、扫描件到底怎么解析？

很多 RAG 项目一上来就讨论 Embedding。

真实项目里，第一个大坑经常更早：

> **原文都没解析对，后面的向量检索再高级也没意义。**

---

### 先给面试答案

企业文档解析我不会只找一个“万能 Parser”。

我会把流程拆成：

```text
Upload
 ↓
File Type Detect
 ↓
Parse
 ↓
Structure Recovery
 ↓
Clean
 ↓
Normalize
 ↓
Chunk
```

不同文件类型走不同策略。

例如：

| 类型 | 常见方案 |
|---|---|
| Word | Apache POI / Tika |
| Excel | Apache POI |
| 文本型 PDF | PDFBox / 专业解析服务 |
| 扫描 PDF | OCR / Vision |
| 图片/流程图 | Vision Model / OCR + Caption |
| HTML/Markdown | DOM/Markdown Parser |

Tika 可以作为统一入口，但不能理解成：

> “Tika 一把梭就能把所有复杂文档解析完。”

---

### 为什么 PDF 最麻烦？

PDF 更接近：

> “页面上这些字画在哪里。”

它不天然等于：

> “这是第一章、这是第二列、这是一个表格。”

因此 PDF 常见问题有：

- 阅读顺序错乱；
- 页眉页脚混进正文；
- 两栏排版串行；
- 表格结构丢失；
- 扫描页根本没有文本层；
- 标题层级消失。

所以：

```text
PDF → String
```

通常只适合非常简单的文档。

复杂文档还需要做结构恢复。

---

### Word 的重点不是“能读出来”

真正应该关注：

- Heading 1 / Heading 2；
- Paragraph；
- List；
- Table；
- 图片位置；
- 页眉页脚；
- 文档顺序。

例如：

```text
第一章 商务条款
 └─ 1.1 付款条件
      └─ 表格：付款节点
```

如果解析以后变成：

```text
付款30%
第一章商务条款
终验
1.1付款条件
```

RAG 后面已经废了一半。

---

### Excel 为什么不能简单“一行一个 Chunk”或“绝对不能按行切”？

两种绝对说法都不对。

关键要看：

> **一行是不是完整业务单元。**

例如库存表：

| SKU | 商品 | 库存 | 仓库 |
|---|---|---:|---|
| A01 | 电源 | 20 | 上海 |

这一行本身就是完整记录。

可以转换为：

```text
SKU: A01
商品: 电源
库存: 20
仓库: 上海
```

但如果是财务报表或跨多行 WBS：

```text
项目阶段
 ├─ 任务组
 │   ├─ 子任务1
 │   └─ 子任务2
```

机械逐行切就可能破坏父子关系。

---

### 大 Excel 怎么避免内存问题？

旧题库有一个明确错误：

> 用 `SXSSFWorkbook` 做大 XLSX 的流式读取。

`SXSSFWorkbook` 主要是为了**低内存写大型 XLSX**。

大文件读取要考虑 XSSF 的事件模型 / SAX 式读取等方案。

这个点面试里不需要背 API 到方法级。

记住：

```text
SXSSF → 主要解决大文件写
Event/SAX → 大文件读的重要思路
```

---

### 扫描 PDF 怎么处理？

先判断有没有文本层。

```text
PDF
 ↓
Text Layer?
 ├─ Yes → text parser
 └─ No
      ↓
     OCR / VLM
      ↓
  page/block structure
```

OCR 以后仍然不是结束。

还要处理：

- OCR 错字；
- 表格；
- 标题；
- 页码；
- 图文关系。

---

### 大文件不要把 Web 请求拖死

一个 300MB 文件：

```text
上传接口
 ↓
直接解析20分钟
 ↓
HTTP一直等
```

很差。

更合理：

```text
Upload
 ↓
Object Storage
 ↓
Document Record
 ↓
MQ / Task Queue
 ↓
Parser Worker
 ↓
Chunk / Embedding
 ↓
INDEXED
```

消息中最好传：

- docId
- objectKey
- metadata

而不是把整个文件塞进 MQ。

---

### 面试官追问：“解析失败怎么办？”

建议有显式状态：

```text
UPLOADED
 ↓
PARSING
 ├─ FAILED
 └─ PARSED
      ↓
  EMBEDDING
      ↓
   INDEXED
```

不能：

> 解析一半失败，但最后文档状态仍然显示“已完成”。

这会直接污染知识库。

---


---

## RAG-03【P0】Chunk 到底怎么切？Chunk Size 和 Overlap 怎么定？

Chunk 的本质不是：

> 把文本限制在 500 Token。

真正的问题是：

> **检索需要多小的知识单元，生成又需要多少上下文。**

这两件事天然有冲突。

---

### 一个最直观的例子

原文：

```text
2.3 验收条件

系统上线后进入 30 天试运行期。
试运行期间不得出现 P0 故障。
满足上述条件后支付尾款 20%。
```

如果机械切成：

```text
Chunk A：
系统上线后进入30天试运行期。
试运行期间不得出现P0故障。

Chunk B：
满足上述条件后支付尾款20%。
```

用户问：

> “什么时候支付尾款？”

Chunk B 虽然有答案，却丢失了“上述条件”。

所以 Chunk 不能只看长度。

---

### 常见策略

#### 1. Fixed / Recursive Chunk

简单。

适合：

- 普通连续文本；
- MVP；
- 结构不明显的数据。

#### 2. Header-based

```text
H1
 └─ H2
     └─ H3
```

优先保持章节结构。

适合：

- PRD；
- 制度；
- 技术文档；
- 合同。

#### 3. Table-aware

表格作为特殊结构处理。

#### 4. FAQ

问题和答案通常应该绑定。

#### 5. Parent-Child / Small-to-Big

这是特别值得掌握的方案。

```text
Parent
"完整的 2.3 验收条件"
   │
   ├─ Child A
   └─ Child B
```

检索时：

```text
小 Child
```

更容易精准命中。

生成时：

```text
返回 Parent
```

获得更完整上下文。

一句话：

> **小块负责找得到，大块负责看得懂。**

---

### Chunk Size 怎么定？

不要背：

> “512 最好。”

应该这样回答：

我会先考虑：

1. 文档自然结构；
2. Embedding 模型输入限制；
3. 用户问题粒度；
4. Rerank；
5. 最终 Context Budget；
6. 评测结果。

然后建立几个 Baseline：

```text
方案A
较小 Chunk

方案B
中等 Chunk

方案C
Header / Parent-Child
```

跑同一批 Golden Dataset。

比较：

- Recall@K；
- Precision / nDCG；
- 重复率；
- 最终答案；
- Token；
- Latency。

最后再选。

---

### Overlap 有什么用？

主要解决边界损失。

```text
Chunk A
AAAA BBBB CCCC

       overlap
         ↓↓↓
Chunk B
     CCCC DDDD EEEE
```

但 overlap 太大也有问题：

- 大量重复向量；
- 存储增加；
- TopK 里全是重复内容；
- 模型误以为同一句被多个来源重复证实。

所以：

> overlap 是可调参数，不是“固定 10%～20% 的规则”。

---

### 一个非常实用的小技巧：Metadata 不要丢标题路径

例如：

```json
{
  "document": "项目A合同",
  "title_path": [
    "第三章 付款",
    "3.2 验收与尾款"
  ],
  "page": 18
}
```

最终给模型时可以组织成：

```text
【项目A合同 > 第三章付款 > 3.2验收与尾款】

……
```

这往往比单独继续加 overlap 更有用。

---

### Stable Chunk ID 怎么做？

不要简单：

```text
docId + seq
```

因为前面插一段文字：

```text
seq 50
```

以后可能全变成：

```text
seq 51
```

版本更新、引用和增量同步都会受影响。

更好的方向可以考虑：

```text
documentVersion
+ semanticPath
+ contentHash
```

实际实现仍要按更新策略设计。

---


---

## RAG-04【P1】Embedding 模型和向量数据库怎么选？

### 30 秒回答

> “Embedding 不能脱离实际语料和 Chunk 策略单独选。我会先根据语言、领域、最大输入长度、向量维度、吞吐、部署方式筛候选模型，再在自己的 Golden Dataset 上用 Recall@K、MRR、nDCG 评估。向量库则看数据规模、metadata filter、事务/SQL需求、分布式扩展、运维成本和现有技术栈。中等规模系统如果已经是 PostgreSQL，可以先评估 pgvector；独立大规模向量检索再考虑 Milvus/Qdrant/ES 等，不需要一上来就上最重方案。”

### Embedding 看什么

- language；
- domain；
- max input；
- dimension；
- query/document instruction；
- throughput；
- self-host / API；
- cost。

### 数据库看什么

#### pgvector

优点：

- PostgreSQL 生态；
- SQL/事务；
- 运维简单。

#### Milvus / Qdrant 等

适合：

- 专门向量服务；
- 大规模 ANN；
- 分布式需求；
- 更强向量索引治理。

#### Elasticsearch / OpenSearch

如果本来就需要：

- BM25；
- filter；
- search analytics；

可能很自然。

### 最关键一句

> Embedding 排行榜不是你的业务评测集。

---


---

## RAG-05【P0】为什么企业 RAG 经常需要 Hybrid Search？

只做向量检索最大的误区：

> “既然 Embedding 能理解语义，就没必要关键词搜索了。”

真实企业数据里恰恰有大量向量不擅长的东西：

- 项目编号；
- SKU；
- API 名称；
- 错误码；
- 人名；
- 缩写；
- 内部黑话。

---

### 两路各自擅长什么？

#### Dense / Vector

用户问：

> “怎么处理员工离职后的权限回收？”

文档写：

> “人员退出项目后应撤销系统访问授权。”

词不一样，但语义接近。

Vector 擅长。

#### BM25 / Sparse

用户问：

> “ERR-2049”

这个错误码最好一字不差地命中。

BM25 更稳。

---

### 所以常见架构

```text
          Query
        /       \
       /         \
Vector Search   BM25
       \         /
        \       /
          Fusion
            ↓
         Rerank
            ↓
          Top N
```

---

### 为什么不能直接把两个 score 相加？

假设：

```text
Vector score = 0.82
BM25 score = 12.7
```

这两个分数根本不是一个量纲。

直接：

```text
0.82 + 12.7
```

没有意义。

---

### RRF 为什么常用？

RRF（Reciprocal Rank Fusion，倒数排名融合）不太关心原始 score。

它看排名：

```text
Vector:
A #1
B #2

BM25:
B #1
C #2
```

B 同时在两路排名靠前，融合以后自然被抬高。

典型形式：

```text
1 / (k + rank)
```

但：

> `k=60` 是常见基线，不是宇宙常数。

---

### Java 怎么做两路并行？

逻辑上：

```text
CompletableFuture
 ├─ Vector
 └─ BM25
      ↓
    combine
      ↓
      RRF
```

关键不是会写 `CompletableFuture`。

而是继续考虑：

- 两路各自 timeout；
- 一路失败是否降级；
- 两路都失败怎么办；
- Context/MDC/Tenant 是否跨线程丢失；
- Future 超时后底层 HTTP 是否还在跑。

---

### 一个合理的降级

```text
Vector OK
BM25 timeout
 ↓
只使用 Vector
 ↓
标记 degraded
 ↓
继续回答
```

不一定因为一个通道挂了，就让整个 Chat 返回 500。

---

### Rerank 放在哪里？

```text
Hybrid Recall
   ↓
例如先拿一批候选
   ↓
Reranker
   ↓
少量高质量 Context
```

Rerank 更贵。

所以一般不是：

> 对百万条文档直接 Rerank。

而是：

> 先召回，再重排。

---

## RAG-06【P1】TopK、Threshold、RRF、Rerank 怎么一起调？

### 30 秒回答

> “这些参数不是互相独立的。TopK 决定候选池大小，Threshold 决定最低相关性门槛，RRF 解决多路排名融合，Rerank 再对较小候选集做更精细排序。调参时我不会一次同时改四个变量，而是固定 Golden Dataset，先看 Recall@K 保证正确证据能进候选，再评估融合与 Rerank，最后看最终答案、延迟和成本。”

### 调优顺序

```text
Embedding / Query
      ↓
Recall@K
      ↓
Hybrid Fusion
      ↓
Rerank
      ↓
Final Context
      ↓
Answer
```

### TopK 太小

风险：

- 正确证据进不来。

### TopK 太大

风险：

- 候选噪声增加；
- Rerank 成本增加；
- Context 更长。

### Threshold 的坑

不要把：

```text
similarity > 0.8
```

当统一标准。

不同：

- embedding model；
- metric；
- index；
- corpus；

score 分布完全不同。

### Rerank 也会错

所以 Trace 最好保留：

```text
before_rerank
score/rank

after_rerank
score/rank
```

否则只看到最终 Top3，很难知道正确文档到底在哪一步丢了。

---


---

## RAG-07【P0】多轮对话为什么容易把检索搞坏？Query Rewrite 怎么设计？

这是 RAG 真正上线以后很容易遇到的问题。

用户第一轮：

> “A 项目目前有哪些延期风险？”

第二轮只会说：

> “那人员方面呢？”

如果直接 Embedding：

```text
那人员方面呢？
```

检索系统不知道：

- 哪个项目？
- 什么主题？
- “那”指什么？

---

### 所以需要 Query Rewrite

```text
History
 +
Current Query
      ↓
Query Rewriter
      ↓
Standalone Query
```

改成：

> “A 项目当前存在哪些与人员相关的延期风险？”

然后拿这个 Query 去检索。

---

### 但 Rewrite 本身也会错

例如用户：

> “那 B 项目呢？”

历史全在讲 A。

模型可能错误重写为：

> “A 项目的 B 阶段有什么问题？”

这时 Rewrite 把用户真实意图改坏了。

---

### 所以不能迷信模型返回的 confidence

旧方案喜欢：

```json
{
  "query": "...",
  "confidence": 0.94
}
```

然后：

```text
> 0.8 就用
```

没有意义。

这是模型自己对自己打分。

并不是经过校准的概率。

---

### 更稳的几个办法

#### 方案 1：保留原 Query

永远 Trace：

```text
originalQuery
rewrittenQuery
```

出了问题可以对照。

#### 方案 2：双路召回

```text
Original Query
      │
      ├─────┐
      ▼     ▼
Retrieve  Rewritten Query
           ↓
        Retrieve
      │     │
      └──┬──┘
         ↓
       Merge
```

适合 Rewrite 错误代价比较大的场景。

#### 方案 3：规则触发

不是所有 Query 都 Rewrite。

比如：

```text
“Java线程池参数怎么设置？”
```

已经非常完整。

没必要先花一次 LLM。

#### 方案 4：评测

专门建立：

```text
multi_turn_cases
```

评估：

- 指代；
- 省略；
- 主题切换；
- 新实体引入。

---

### Chat History 也不能无限塞

Query Rewrite 需要历史。

但不代表：

> 把全部历史发给模型。

可以使用：

- Recent Window；
- Summary；
- Relevant Memory；
- Current Task State。

这是 Context Engineering 的内容。

---

### 项目怎么挂？

PMO 这题很好讲。

项目经理可能问：

```text
这个需求是谁提的？
```

然后：

```text
什么时候提的？
```

第二句话必须恢复成：

```text
这个需求是什么时候提出的？
```

再去知识库检索。

如果 PMO 项目已经真实实现，标 REAL。

如果只是设计，就说 DESIGN。

---


---

## RAG-08【P1】Excel、数据库、报表这些结构化数据应该怎么处理？

### 30 秒回答

> “我不会把所有结构化数据都硬塞向量库。说明型、小规模表格可以保留表头和行语义转成文本做 RAG；需要聚合、排序、精确数值和实时状态的场景，更适合 SQL、API、OLAP 或 Semantic Layer；混合问题则可以让 Agent / Router 先判断去 RAG 还是 Data/API Tool。系统可以先做 Query Routing，把问题分成 Knowledge Question、Data Query 和 Mixed Query，再分别走 RAG、SQL/API 或组合流程。Text-to-SQL 是一种手段，不是结构化问答的终极方案。”

### 一个简单 Router

```text
User Query
   │
   ▼
Intent / Query Router
   │
 ┌─┼─────────┐
 ▼ ▼         ▼
RAG SQL/API  Mixed
```

### Excel 能不能按行切？

能。

条件是：

> 一行本身就是完整业务记录，并且补齐表头语义。

例如：

```text
任务=登录功能 | 负责人=张三 | 状态=已完成
```

这就是合理 Chunk。

所以不能写：

> Excel 绝对不能按行切。

### Text-to-SQL 的风险

- SQL injection / unsafe SQL；
- 表结构权限；
- 多租户；
- 大查询；
- 语义口径；
- aggregation correctness。

生产系统更可能：

```text
Semantic Layer / Predefined API
```

而不是让模型随便生成任意 SQL。

---


---

## RAG-09【P0】权限、版本和 Citation 怎么进入 RAG 链路？

企业 RAG 真正上线以后，相关性不是唯一要求。

还有三个问题：

1. **能不能看？**
2. **看的是否是当前有效版本？**
3. **答案依据到底在哪？**

---

### 权限应该放在哪里？

最重要的一句话：

> **权限尽量前置到检索阶段。**

不要：

```text
全库检索
 ↓
把敏感 Chunk 送给模型
 ↓
生成答案
 ↓
最后再隐藏
```

因为数据已经进入模型上下文。

更合理：

```text
JWT / Current User
       ↓
Permission Scope
       ↓
Metadata Filter
       ↓
Vector / BM25
       ↓
Allowed Chunks
       ↓
LLM
```

---

### Metadata 可以带什么？

例如：

```json
{
  "tenant_id": "T01",
  "project_id": "P1001",
  "department_id": "D20",
  "version": 7,
  "is_latest": true,
  "classification": "INTERNAL"
}
```

检索时先缩小合法范围。

---

### Milvus Filter 不要继续手工危险拼字符串

旧代码经常：

```java
"project_id == '" + projectId + "'"
```

至少会带来：

- 转义问题；
- 表达式错误；
- 注入风险；
- 复杂列表解析成本。

Milvus 当前文档已经有 Filter Templating：

```text
filter:
project_id IN {projectIds}

filter params:
projectIds = [...]
```

正式代码应优先按当前 SDK 支持方式使用模板/参数，而不是自己把所有值拼进表达式。

---

### 为什么还需要后置校验？

权限是高风险边界。

可以做纵深防御：

```text
Permission Service
 ↓
Pre-filter
 ↓
Retrieve
 ↓
Post-check
 ↓
LLM
```

Post-check 不是主防线。

它是兜底和告警点。

如果大量结果在后置阶段被过滤：

> 说明前面的 Filter 可能已经有问题。

---

### 版本怎么处理？

企业知识库最容易出现：

```text
制度 V1
制度 V2
制度 V3
```

三个都在。

如果不做版本治理，RAG 会同时找到互相冲突的答案。

所以 Metadata 里至少需要考虑：

- version；
- effective_time；
- expire_time；
- is_latest；
- status。

检索规则可以是：

```text
默认只搜已发布 + 当前有效版本
```

但对“历史追溯”类问题，再显式允许查旧版本。

---

### Citation 不只是展示一个文件名

真正有用的 Citation 最好能定位：

```text
documentId
documentVersion
page
chunkId
titlePath
sourceUrl/objectKey
```

这样用户才能回到证据。

---

### Citation 为什么不能完全让模型自己编？

如果你告诉模型：

> “请使用 [1][2] 引用。”

它仍可能：

- 引错 ID；
- 编不存在的 ID；
- 把两个来源混在一起。

更稳：

```text
Context chunks
每个都有系统生成ID
       ↓
LLM只能引用允许的ID
       ↓
Java校验ID
       ↓
Frontend resolve citation
```

也就是说：

> 引用 ID 的真实性应该由系统验证，而不是相信模型。

---


---

## RAG-10【P1】文档更新、删除、Embedding 模型升级怎么处理？

### 30 秒回答

> “知识库要版本化，不要把向量索引当唯一真相源。原文和元数据保留在主存储，索引可以重建。普通文档更新用 documentVersion + stable chunk identity 做 Diff，只 Upsert/Delete 变化片段；Embedding 模型升级因为向量空间通常不兼容，我会建新索引或新 collection 双写/回放，完成离线评测后灰度切读流量，再下线旧索引。”

### Index 不是 Source of Truth

```text
Object Storage / DB
       │
       ▼
   Index Pipeline
       │
       ▼
Vector Index
```

Vector Index 可以丢，可以重建。

### Stable Chunk ID

不要简单：

```text
docId + seq
```

因为前面插一段，后面 seq 全变。

可以考虑：

```text
documentId
semanticPath
contentHash
version
```

具体按需求设计。

### Embedding 升级

不要直接在同一向量字段里混：

```text
old embedding
new embedding
```

因为向量空间不同，距离不可比。

推荐：

```text
Old Index ← production
    │
    ├─ rebuild
    ▼
New Index ← evaluate
    │
    ▼
Gray Read
    │
    ▼
Switch
```

---


---

## RAG-11【P0】RAG 回答错了，怎么定位到底哪一层出了问题？

这是比：

> “怎么优化 RAG？”

更重要的一题。

因为生产上你面对的通常不是：

> “请设计最优系统。”

而是：

> “这个问题昨天还能答，今天怎么答错了？”

---

### 第一原则：不要先怪 LLM

固定排查链：

```text
Source
 ↓
Parser
 ↓
Chunk
 ↓
Metadata
 ↓
Embedding
 ↓
Retriever
 ↓
Fusion
 ↓
Rerank
 ↓
Context
 ↓
Prompt
 ↓
LLM
```

一层层看。

---

### Case 1：原文里根本没有答案

那不是检索问题。

应该：

- 拒答；
- 推荐补知识；
- 转人工。

---

### Case 2：原文有，但 Parser 没解析出来

例如 PDF 表格解析乱了。

你在向量库里永远检不到。

处理：

> 回到入库链路。

---

### Case 3：Parser 有，Chunk 切坏了

例如答案条件在上一块，结论在下一块。

处理：

- Header；
- Parent-Child；
- Neighbor Expansion；
- Chunk 策略。

---

### Case 4：正确 Chunk 在库里，但没召回

看：

- Query；
- Rewrite；
- Embedding；
- BM25；
- Metadata Filter；
- TopK。

这属于 Retrieval Failure。

---

### Case 5：召回了，但 Rerank 把它压下去

要保留：

```text
Before Rerank
After Rerank
```

否则根本不知道是哪层把正确结果弄丢了。

---

### Case 6：正确 Context 已经给了 LLM，但答案仍然错

这时才进入：

- Prompt；
- Context 太长；
- 冲突来源；
- 模型能力；
- Structured Output；
- Faithfulness。

---

### 所以 Trace 至少记录什么？

排障环境可以保留：

```text
originalQuery
rewrittenQuery
filters
vectorTopK
bm25TopK
fusionRanking
rerankRanking
finalContextIds
promptVersion
modelVersion
latency
```

敏感原文是否记录、记录多少，要按隐私和日志策略控制。

---

### 面试可以直接说的排查法

> 我会先确认原始知识是否正确，再看解析和 Chunk，然后看检索是否召回正确片段，再看 Rerank 是否把正确片段压下去，最后才看 Prompt 和模型。这样可以把“回答错”从一个黑盒问题拆成多个可验证环节，而不是一上来就调 Prompt。

这个回答非常实用。

---


---

## RAG-12【P0】RAG 怎么建立 Golden Dataset 和 Bad Case 闭环？

没有评测集的 RAG 优化很容易变成：

> “我试了一下，感觉好像更准了。”

生产系统不能靠感觉。

---

### 评测至少分两层

#### Retrieval

问题：

> 正确证据有没有找回来？

典型指标：

- Recall@K；
- Precision@K；
- MRR；
- nDCG。

#### Generation

问题：

> 有了这些证据以后，答案有没有说对？

可以看：

- Correctness；
- Faithfulness；
- Relevance；
- Citation Accuracy。

---

### Golden Dataset 长什么样？

最简单可以是：

```json
{
  "query": "项目A的尾款支付条件是什么？",
  "reference_answer": "...",
  "relevant_chunk_ids": [
    "doc12#chunk88"
  ],
  "category": "合同条款"
}
```

最好再标：

- 难度；
- 业务分类；
- 是否多跳；
- 是否无答案；
- 权限场景。

---

### 数据从哪来？

新项目：

- 领域专家人工出题；
- 从文档反向构造问题；
- LLM 辅助生成，再人工审核。

已有系统：

- 真实用户 Query；
- 点踩；
- 重复追问；
- 转人工；
- 客服修正记录。

最有价值的往往是：

> 真用户踩过的坑。

---

### Bad Case 闭环

```text
线上/离线失败
     ↓
Bad Case
     ↓
分类
 ┌────┼─────┬──────┐
Parse Chunk Retrieve Generate
     ↓
Fix
     ↓
加入 Regression Set
     ↓
下次改动自动重跑
```

关键点：

> 修过一次的问题，不能下个版本又坏回来。

所以 Bad Case 最终应该进入回归集。

---

### 每次改什么都要跑同一批数据

例如：

- 换 Embedding；
- Chunk 变了；
- TopK 变了；
- 加 Rerank；
- Prompt 更新；
- 模型升级。

都跑：

```text
Baseline
   vs
Candidate
```

然后比较：

```text
Quality
Latency
Cost
```

不能只看准确率。

---

### RAGAS 怎么看？

可以使用 RAGAS 之类框架辅助做：

- Context Precision；
- Context Recall；
- Faithfulness；
- Response Relevancy。

但不要回答成：

> “用了 RAGAS，所以评测就科学了。”

LLM-as-a-Judge 本身也可能偏。

因此重要样本最好结合：

- 人工评审；
- 规则；
- 业务指标；
- 多评估器。

---

### 旧题库里最大的真实性问题

旧稿里有：

> “50～100 条 QA，两天搞完。”

以及：

> “命中率从 75% 提到 85%。”

如果这些不是你真实项目记录，全部不能进入项目话术。

可以改成：

> “我会先构建覆盖核心场景的评测集，再用 Recall@K、MRR 等指标建立 Baseline；具体数据必须以实际评测结果为准。”

这才安全。

---

### PMO 项目怎么挂？

这 7 道题可以直接组成一个很强的项目追问链：

```text
PMO 文档
 ↓
RAG-02 怎么解析
 ↓
RAG-03 怎么切
 ↓
RAG-05 怎么检索
 ↓
RAG-07 多轮怎么改写
 ↓
RAG-09 怎么做权限/引用
 ↓
RAG-11 错了怎么排
 ↓
RAG-12 怎么证明优化有效
```

如果这一条能讲顺，PMO 项目就不再是“我用了 RAG”。

而是：

> 你能从数据入库一直讲到生产评测。

---


---

## RAG-13【P1】RAG 怎么做性能、稳定性和成本治理？

这题可以把前面所有 RAG 工程点串起来。

### 性能

优先看阶段耗时：

```text
Rewrite
Embedding
Vector Search
BM25
Rerank
LLM TTFT
Generation
```

优化：

- Vector/BM25 并行；
- 控制候选池；
- cache；
- stream；
- request batching（离线）。

### 稳定性

```text
Vector fail → BM25 degrade
Rerank fail → recall order
Rewrite fail → original query
```

模型失败：

- timeout；
- retry classification；
- compatible fallback。

### 成本

- Embedding 批量；
- 避免重复重算；
- Context 控制；
- Rerank 按需；
- model routing；
- cache correctness。

### 关键坑

`CompletableFuture.orTimeout()` 让 Future 超时：

> 不代表底层 HTTP 或数据库查询一定停止。

所以底层 Client 本身也必须配置 timeout/cancel。

---


---

## RAG-14【P1】什么时候应该升级成 Agentic RAG？

### 普通 RAG

```text
Query
 ↓
Retrieve
 ↓
Generate
```

适合：

- FAQ；
- 制度问答；
- 单知识源；
- 路径明确。

### Agentic RAG

```text
Question
 ↓
Need Search?
 ↓
Choose Source
 ↓
Retrieve
 ↓
Enough?
 ├─ Yes → Answer
 └─ No → Rewrite / Another Source / Tool
```

### 30 秒回答

> “只有当检索路径本身不确定时，我才考虑 Agentic RAG，例如问题需要动态决定知识源、多跳检索、SQL + 文档混合、检索结果不足时继续补查。普通 FAQ 如果一次 Hybrid + Rerank 已经稳定，Agent 化只会增加 latency、token、调试和评估复杂度。”

### 判断标准

问四个问题：

1. 固定一次检索能解决吗？
2. 是否需要动态选择 Source？
3. 是否真的需要多步？
4. 增加的效果值得成本吗？

---


---

## RAG-15【P1】百万级甚至千万级 Chunk 怎么做系统设计？

这题不要一上来报数据库名字。

### 先分层

```text
             API / Auth
                 │
                 ▼
             Query Layer
                 │
        ┌────────┴────────┐
        ▼                 ▼
    Metadata          Retrieval
        │          Vector / BM25
        └────────┬────────┘
                 ▼
              Rerank
                 ▼
               LLM

Offline:
Upload → Storage → MQ → Parse → Chunk → Embed → Index
```

### 数据层

可以分：

- Original Document：OSS/S3/MinIO；
- Metadata：MySQL/PostgreSQL；
- Full Text：ES/OpenSearch；
- Vector：Milvus/Qdrant/pgvector；
- State/Cache：Redis。

但不是说必须“五个数据库”。

规模和团队决定。

### 百万级重点

- metadata filter；
- index type；
- partition / sharding；
- hot/cold data；
- incremental update；
- backfill；
- permission；
- rebuild strategy。

### 千万级更关心

- ingestion throughput；
- re-embedding migration；
- storage cost；
- indexing time；
- multi-tenant noisy neighbor；
- online/offline resource isolation。

### 面试加分点

> “百万 Chunk 不是一个神奇分界线，架构升级应该由延迟、吞吐、索引构建时间、成本和运维瓶颈触发，而不是数据一到某个整数就换技术。”

---


---

---

## 附：V1 RAG 工程实现补充保留区

### A. 复杂 Metadata Filter 的性能不能只看“能不能过滤”

当权限、租户、项目、时间、文档状态等过滤条件越来越复杂时，需要同时关注：

- Filter 是否在向量召回前生效；
- 标量字段是否有合适索引；
- 高选择性字段和低选择性字段差异；
- Partition / Sharding 是否真的匹配查询模式；
- Filter + ANN 组合后的召回和延迟；
- 多租户是否出现热点分区；
- 数据更新后索引维护成本。

不要把“建 Partition 就一定更快”写成标准答案。不同 Vector DB 的执行计划、索引和版本差异很大，必须用真实 Query Pattern 做 benchmark。

### B. Reranker 的生产降级路径

Reranker 不是“加了必然更准”。生产设计需要考虑：

```text
Retrieve candidates
   ↓
Reranker available?
   ├─ Yes → rerank → final context
   └─ No  → retrieval ranking → final context
```

需要明确：

- candidate 数量；
- timeout；
- fallback；
- batch；
- 模型升级回归；
- 专有词/编号类 Bad Case。

业务规则可以作为 feature 或补充信号，但不要用“发现专有词就强制 Top3”这种硬编码当通用方案。

### C. 多语言、Embedding 升级和重建要放进同一套版本治理

如果系统既支持多语言，又升级 Embedding Model，要特别关注：

- 旧向量和新向量不能直接混用；
- 多语言能力是否退化；
- 新旧索引双写/双读；
- Golden Dataset 分语言评测；
- 切换和回滚；
- 文档版本与 Embedding Version 绑定。

这一点与 `RAG-10` 的双索引迁移是同一工程问题。

### D. 多轮检索去重：排除历史命中过的段落只是一个策略

多轮问答中可能出现同一 Chunk 被反复召回。可以考虑：

- 记录上一轮/最近几轮的 `chunkId`；
- 对重复 Chunk 降权；
- 在“继续补充新信息”的意图下排除部分已展示证据。

但不能无条件排除历史命中过的段落，因为用户可能就是在追问同一个证据。

正确做法是把“是否需要新证据”作为 Query Intent 的一部分，而不是写死排除规则。

### E. Java RAG 常见代码坏味道

旧题库这类内容继续保留：

1. Controller 里直接把上传文件解析、Embedding、入库全部同步做完；
2. 把大文件字节直接塞 MQ；
3. Chunk ID 只用递增序号，文档更新后全变；
4. Filter 用字符串拼接；
5. Vector Search、BM25、Rerank 全串行，且没有 Deadline；
6. `catch (Exception)` 后吞掉错误继续标记任务成功；
7. Prompt、Embedding、Knowledge Base Version 不进 Trace；
8. 把固定 TopK、Threshold 写死在业务代码；
9. 文档删除只删 DB，不处理索引；
10. 把检索分数直接当“答案置信度”。

这些坏味道分别对应 `RAG-02/03/05/06/09/10/11/13` 中的生产治理问题。
