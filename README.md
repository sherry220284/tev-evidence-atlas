# TEV Evidence Atlas — review release 0.2.0

历史工程证据与天然NIa-Pro成熟域的可追溯数据包。用于导师讨论、检查原始证据和复算五幅计算图。当前为私有导师审核仓库：[sherry220284/tev-evidence-atlas](https://github.com/sherry220284/tev-evidence-atlas)。公开发布须项目负责人审核。

数据范围：7篇实验论文、1篇勘误、1件专利；36个来源限定变体、115条突变记录、168条测量。天然候选1505条，成熟域分析35条，代表展示23条。没有新设计序列、没有已训练的主动学习模型；当前`training_ready`视图为0条。

## 快速复现

建议新建Python 3.10或以上环境：

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
make all
```

也可依次运行：

```bash
python3 scripts/rebuild.py
python3 scripts/recurate_natural.py
python3 scripts/recompute_conservation.py
python3 scripts/recompute_structure.py
python3 scripts/recheck_overlap.py
python3 scripts/review_natural.py
python3 scripts/make_figures.py
python3 -m unittest discover -s tests -v
```

`rebuild.py`仅使用仓库中的schema与CSV生成根目录`tev_history.sqlite`；空值以CSV中的`\N`表示，空字符串仍为空字符串。`recurate_natural.py`从冻结UniProt TSV重新筛得35条成熟域并验证FASTA逐字节相同；`recompute_conservation.py`从MSA重新计算242位三条保守性曲线和两条覆盖度；`recompute_structure.py`从公开1LVB/1LVM mmCIF重算868条Cα坐标并核对914条编号映射；`recheck_overlap.py`从派生公开accession标签重算3817配对/3786标签与35域的29个标签交集；`review_natural.py`从归档树重新计算三项RF距离；`make_figures.py`输出`results/figures/`中的五幅SVG/PNG/PDF和`results/figure_data/`的逐图输入。根目录数据库和results为派生输出，不加入Git。使用本机旧版依赖的实测环境与结果见[QC报告](docs/QC_Report.md)，Python 3.10或以上环境用于推荐配置；离线全流程的实测版本为Python 3.6.8，见[QC报告](docs/QC_Report.md)。推荐新环境依赖范围不等同于已测试所有版本。

## 数据导航

| 路径 | 内容 |
|---|---|
| `data/source/` | UniProt 2026_03冻结候选TSV（CC BY 4.0）；公开PDB mmCIF及来源元数据 |
| `data/tables/` | 22张SQLite表的完整CSV导出，带来源、协议与审计字段 |
| `data/schema.sql` | 表、约束、索引及追溯/训练视图 |
| `data/provenance/` | 哈希、原始来源下载记录、原值→更正值、方法和数据交集 |
| 根目录FASTA/CSV/Newick | 冻结公共序列、成熟域MSA、位置映射与天然元数据 |
| `build/phylogeny/` | 23域代表MSA/树及MAFFT参数日志 |
| `build/publication_natural/` | 三项敏感性输入、真实推断树和原始日志 |
| `build/structure_ca_coordinates.csv` | PDB实验Cα坐标派生表，不含预测结构 |
| `scripts/`、`tests/` | 数据重建、五图、天然复核与完整性测试 |

[Methods](docs/Methods.md)解释抽取、编号、树/保守性、复算层次；[Results](docs/Results.md)列出真实数量与结论；[Limitations](docs/Limitations.md)列出不能支持的推断；[数据字典](docs/data_dictionary.md)解释每一实体；[2026差异分析](docs/2026_Novelty_Comparison.md)比较两篇新论文；[方法参数](docs/Assay_Methods.md)和[五轮规划](docs/Active_Learning_Plan.md)供导师决策。

原论文、专利PDF、论文原图、字体、依赖安装、秘密及商业未公开序列不在仓库。`sources.local_path`和来源记录中的旧路径是冻结来源标识，并不表示受限文件随仓库提供；回原文需使用来源URI。本仓库能复算数据和图表，不能自动独立核验全部论文抽取。没有跨论文绝对活性排行。许可证边界见[DATA_LICENSE.md](DATA_LICENSE.md)。引用时使用`CITATION.cff`并同时引用相关原始论文/UniProt/PDB。
