# Methods

## 范围与抽取

冻结历史来源为7篇实验论文、1篇Sanchez–Ting勘误及US20260234592A1；专利、厂商规格、结构与UniProt来源独立计入sources。P8118的官方规格v1.0（2025-05-27生效）单列commercial_products，不把厂商端点声明并入论文测量；来源SHA256和逐字段摘录另见vendor_curation.json。2026两篇论文用作定位与方法比较，未直接扩充168条历史测量。逐测量保存source_id、source_figure_table、protocol_id、原值/单位/限定语、不确定性、重复数、构建与底物。未报告项保持NULL。来源及本地原始哈希在sources与data/provenance中；论文全文和原图不随仓库分发。

自动完整性检查不替代人工回原文。`data/provenance/assay_methods.json`包含原文短引、Methods定位与缺口；`curation_corrections.json`包含本轮7处DTT字段的原值→修订值；其余早期演示稿更正经与现有协议表核对，数据库已含相应正确表述，不重复更改。

## 编号和序列

成熟TEV坐标1–242。文献原始突变标记先保留，再以已确认参考序列、N端锚点和构建边界映射；序列不全不自动补齐。PDB坐标以entity序列与label_seq_id映射；`scripts/recompute_structure.py`从`data/source/structures/`中的公开1LVB/1LVM mmCIF重算868条Cα坐标及914条编号映射并与冻结数据核对；1LVB C151A是失活实验构建体。F1用真实Cα坐标SVD二维投影，不能按图上距离推断机制。专利的公开实验序列与未公开商业产品身份区分，P8118不映射专利SEQ ID。

## 天然序列、MSA与树

UniProt 2026_03冻结候选1505条，经明确成熟CHAIN、完整域、唯一成熟序列与催化锚点检查，35条进入分析。精确筛选不代表其余1470条一定不含有效蛋白酶。35域MAFFT L-INS-i：`--localpair --maxiterate 1000`，290列；23条代表独立比对272列，不能用35条MSA列号直接替换代表MSA列号。

归档IQ-TREE版本2.4.0，LG+I+G4，无根推断；SH-aLRT和UFB各1000次、BNNI。三项敏感性输入在build/publication_natural：repeat35、去除A0AUJ5/A4KZ49/Q65730的exclude3、保留占有率≥0.7列的occupancy70；固定种子20261029。共同taxa上的无根非平凡二分裂计算RF/两树split总数；本仓库入口重算RF，不宣称重新执行IQ-TREE。

在已安装MAFFT与IQ-TREE的环境，可在临时工作目录重推（不要覆盖归档树）：

```bash
mafft --localpair --maxiterate 1000 natural_nia_pro_sequences.fasta > /tmp/tev35_realign.fasta
iqtree2 -s build/publication_natural/repeat35.fasta -m LG+I+G4 -alrt 1000 -B 1000 -bnni -seed 20261029 -T 2 --prefix /tmp/tev_repeat35
iqtree2 -s build/publication_natural/exclude3.fasta -m LG+I+G4 -alrt 1000 -B 1000 -bnni -seed 20261029 -T 2 --prefix /tmp/tev_exclude3
iqtree2 -s build/publication_natural/occupancy70.fasta -m LG+I+G4 -alrt 1000 -B 1000 -bnni -seed 20261029 -T 2 --prefix /tmp/tev_occupancy70
```

原始命令的版本、线程与参数以归档log为准，以上是明示的复跑命令；不同版本/线程可能改变逐字节结果。重新推断和下载不是离线默认检查的一部分。

## 保守性和五图

以标准20氨基酸计算H=−Σp log2 p；保守性1−H/log2(20)，gap不作为氨基酸，另报占有率。三条曲线分别为35域、去长支32域、每属总权重相等；加权不是独立样本或置信区间。保守性反映所选数据，不能证明突变耐受或冷适应。

F1为来源位点/真实坐标；F2为168条测量的来源与结构化字段覆盖，分母不是论文质量评分；F3为23条代表基因树；F4为242个位点保守性与占有率；F5为专利端点与四组配对斜率比。所有图均从仓库数据重绘，输出精确CSV和输入哈希。专利斜率比不是独立测定的绝对kcat/Km，不跨组混合对照。绘图无随机采样；SVD坐标符号方向可能随数值库改变，含义不变。

## 执行层次

1. CSV→SQLite：保留NULL/空字符串、类型、约束、索引与视图；校验每表数量、外键和完整性。
2. 冻结UniProt TSV→1505候选→35成熟域：`scripts/recurate_natural.py`重新执行边界与去重筛选，验证输出FASTA逐字节一致；源数据与元数据在`data/source/`，CC BY 4.0。ProSSpeC的公开MSA仅提取3817行accession标签（保留重复），原始压缩包及member的SHA256、数据DOI和提取规则另存元数据；`scripts/recheck_overlap.py`重算3786个不同标签及29个标签交集，不推断序列相同。`scripts/recompute_conservation.py`从MSA重算242位三条曲线和两条覆盖度。
3. 公开PDB mmCIF→实验Cα坐标及编号映射：`scripts/recompute_structure.py`重算并核对，含工程构建的序列差异，绝不视为野生型序列一致。
4. 归档树→RF复核，冻结CSV/SQLite→五图：无需受限PDF、无需网络。
5. 原始论文下载→抽取及MAFFT/IQ-TREE：须独立原文审核与指定二进制。提供日志、参数与溯源，树重新推断和论文重新抽取不在默认离线检查内。
