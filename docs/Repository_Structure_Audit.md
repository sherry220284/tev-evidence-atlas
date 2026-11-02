# 第二轮仓库结构与复现审计

本审计在重制PPT与独立仓库实作前形成。现有项目为本地工作目录，尚非Git仓库。旧版数据库、五图、演示文稿和依赖混放，不能直接整体发布。

| 项目 | 核实结果 | 本轮处理 |
|---|---|---|
| 数据范围 | 36个来源限定变体、168条测量；1505条天然候选、35条分析、23条代表展示 | 所有Results和图表从数据库/文件计数，维持三个天然分母 |
| 基线 | 57项测试通过；21项原始下载、MSA和树哈希一致 | 交付前重复核验，记录实际结果 |
| Methods一致性 | 核对演示稿的7类更正；多数已在协议表。本轮仅Nam标准液DTT曾被误写为反应液条件 | 将Nam 7处冗余字段更正为未报告，逐处保留原值；不把7处字段说成7类新错误 |
| 天然复核入口 | `scripts/review_natural_publication.py`缺失，已有计算结果、树与日志仍在 | 补齐读入既有结果的复核入口，另给出重推树的参数和命令，明确重算层次 |
| 原始来源依赖 | 旧构建需论文PDF/HTML、原图与本地绝对路径 | 独立仓库从经审计CSV与公开序列/坐标派生数据重建，来源下载另列清单 |
| 五图代码 | 有真实绘图脚本与精确CSV，但路径绑定旧目录 | 独立仓库提供相对路径入口，重建SQLite后再绘图 |
| 运行环境 | 本机Python 3.6.8及本地科学依赖；LibreOffice本地安装 | 发布依赖清单、实际版本记录与新环境命令；不打包依赖或字体 |
| 公开范围 | 受限PDF、论文原图、字体、商业未公开序列不得入Git | 仅独立白名单复制，检查全部Git待跟踪文件；PPT证据图仅在导师交付包 |
| 授权与发布 | 用户要求公开前审核；尚未指定私有远端 | 仅本地初始化可审阅仓库，不创建公开仓库或推送 |

## 目标结构

```
tev-evidence-atlas/
  README.md, AGENTS.md, CITATION.cff, LICENSE, DATA_LICENSE.md
  requirements.txt, Makefile, .gitignore
  data/tables/                 # 审计后的CSV，NULL编码有定义
  data/sequences/              # 公共/已核验序列、MSA
  data/phylogeny/              # 原始Newick、敏感性树与参数
  data/structure/              # 实验坐标派生表
  data/provenance/             # 来源/哈希/更正记录，不含受限原图
  docs/Methods.md, Results.md, Limitations.md, data_dictionary.md
  docs/2026_Novelty_Comparison.md, Assay_Methods.md, Active_Learning_Plan.md
  scripts/                    # CSV重建SQLite、五图、天然复核、完整性验证
  tests/                      # 外键、计数、哈希、限定语与序列检查
  results/                    # SQLite、五图与QC，均可重新生成
```

## 可复现程度的边界

离线重建数据库、五幅计算图和既有树的诊断，应能只依赖仓库内容执行。重新下载UniProt可能因版本变化不同，必须使用冻结输入；树推断须有MAFFT/IQ-TREE并运行记录参数，随机种子不保证跨版本逐字节一致。论文数据抽取的正确性仍须人工回原文检查，不将通过完整性测试表述为全部测量已独立复现实验。数据集不是跨论文活性排行榜，不提供训练完成或4℃天然增强结论。
