# Instructions for advisor Codex / contributors

这是可复算的TEV历史工程与天然进化证据仓库。先读README、docs/Methods.md、docs/Results.md、docs/Limitations.md和data/provenance/curation_corrections.json。

- 当前仅整理证据和方法框架。不得生成新突变序列、候选库，运行主动学习搜索或声称已训练模型。
- 人工工程实体在variants/mutations；天然同源在natural_homologs。通过成熟TEV 1–242映射关联，不能把天然差异当作人工突变记录。
- 1505是候选，35是成熟域分析，23是代表树。天然冷活性UNKNOWN；宿主或地理来源不是冷适应证据。
- 缺失条件用NULL，CSV编码为`\N`。ND、下界和区间保留限定语。不能以厂家说明填论文的未知条件。
- 不跨论文平均效率、不从不同实验fold-change建立绝对排名。双拟合不是双重复；kapp不是kcat。
- 任何争议更正必须同时保留旧值、原始定位、拟议解释、严重程度和review_status。原始数据不静默修改。
- 序列重建仅限参考与完整突变定义都核实的构建；商业酶身份不映射到专利SEQ ID。
- 公开发布须负责人审核。不要配置/推送远端，除非明确指定了私有仓库。不得输出令牌或加入PDF、论文原图、字体、依赖和未公开商业序列。

入口：`python3 scripts/rebuild.py`重建SQLite，`python3 scripts/recurate_natural.py`从冻结UniProt源重新筛选35成熟域，`python3 scripts/recompute_conservation.py`从MSA重算242位约束，`python3 scripts/recompute_structure.py`重算PDB坐标与映射，`python3 scripts/recheck_overlap.py`复算ProSSpeC的标签交集，`python3 scripts/review_natural.py`复核归档树，`python3 scripts/make_figures.py`生成五图，`python3 -m unittest discover -s tests -v`检查。全部结果在results/；受限原文并不随仓库提供，sources.local_path是历史溯源标识，核实用sources.uri与references。

数据调整后更新data/tables、审计记录、table_counts及SHA256SUMS，再重跑重建、图和测试。哈希清单只是完整性依据，不是原始抽取已独立验证的证据。说明实际测过的环境；未知版本不宣称兼容。
