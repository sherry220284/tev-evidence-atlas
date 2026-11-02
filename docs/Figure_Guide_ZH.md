# TEV Evidence Atlas v0.1｜五幅图的汇报说明

版本：0.1.0。使用顺序建议：F1 → F2 → F3 → F4 → F5。图形均由现有数据库、真实实验坐标或已完成的天然序列分析生成；SVG 可缩放，PNG 为 4000×2250、300 dpi，另附 PDF。每张图的精确作图表和输入文件 SHA-256 见 [figure_manifest.json](figure_manifest.json)。图中英文标签便于后续编辑；以下中文段落可直接用于讲稿。

## F1｜TEV 历史工程化突变与结构位置

[SVG](figures/F1_history_structure.svg) · [PNG](figures/F1_history_structure.png) · [PDF](figures/F1_history_structure.pdf)

**中文讲解（5 句）：**本图把已整理的历史突变放到统一的成熟 TEV 1–242 位点编号下，并按研究来源展开。左侧使用真实晶体结构 PDB 1LVB 的 A 链 Cα 坐标作二维主成分投影，不是预测结构或生成式图片。蓝色方块标记催化位点 46、81 和 151，但该晶体构建体在 151 位实际为失活替换 Ala。橙色实心点表示已有完整序列核验支撑的映射，空心点表示保留了来源记法但完整序列尚未确认。历史记录同时包含背景突变、负结果和不同性状的改造，因此位点被标记不等于它已被证明有益，也不能从二维邻近直接推导作用机制。

**原始数据与来源：**[突变记录](figure_data/F1_mutations.csv)、[实验坐标](figure_data/F1_experimental_coordinates.csv)；数据库 `mutations` / `residue_maps`；[1LVB 原始 CIF](../raw-data/structures/1LVB.cif)，RCSB https://www.rcsb.org/structure/1LVB；七篇实验论文和专利的逐条引用见 [Evidence_Index.csv](Evidence_Index.csv)。未跨越缺失坐标连接主链。

**关键限制：**这是所选来源的历史位置图，不是全面的有益突变图谱；投影失去三维距离信息；C151A 构建体不能代表活性酶的完整催化状态。原始 1LVB/1LVM 数据与预测模型证据分开保存。

## F2｜历史实验测量与条件字段覆盖

[SVG](figures/F2_measurement_coverage.svg) · [PNG](figures/F2_measurement_coverage.png) · [PDF](figures/F2_measurement_coverage.pdf)

**中文讲解（4 句）：**左侧统计冻结范围内七篇论文和一件专利贡献的 168 条测量记录，计数单位是测量行。右侧检查温度、反应时间、浓度、缓冲液、pH、重复数和不确定性等字段是否已有结构化值。来源覆盖与条件完整性共同决定数据能否进入后续统一比较；存在原始定位并不意味着条件已经齐全。同一实验的不同端点、同一数据的两种拟合以及并非所有测量都适用的字段，会影响这些比例，所以不能把图中比例解释为文献全集覆盖率或研究质量评分。

**原始数据与来源：**[168 条测量](figure_data/F2_measurements.csv)、[来源计数](figure_data/F2_source_counts.csv)、[字段统计](figure_data/F2_metadata_availability.csv)；SQLite `measurements`，逐条 `source_figure_table` 和 `protocol_id` 保留。Messing 的来源 ID 延续 `src_messing2024`，正式发表年为 2025，DOI 含 2024。

**关键限制：**非 NULL 只表示字段可用，不表示所有适用条件已验证；部分条件仅保存在协议或备注中，未转为数值字段；本版全部测量保持 `PARTIAL`，没有自动升级为训练就绪。论文内重复拟合不增加独立样本数。

## F3｜天然 NIa-Pro 代表系统发育树

[SVG](figures/F3_natural_phylogeny.svg) · [PNG](figures/F3_natural_phylogeny.png) · [PDF](figures/F3_natural_phylogeny.pdf)

**中文讲解（5 句）：**本图显示通过边界检查的 35 条成熟域中选出的 23 条代表序列，树与其自身的 23 条、272 列 MSA 对应。树由 IQ-TREE 2.4.0 在 LG+I+G4 模型下推断，枝长表示每位点替换数，展示根不代表祖先方向。实心节点同时满足 SH-aLRT≥80 和 ultrafast bootstrap≥95，空心节点至少一项未达阈值。三条经核查后保留的长分支用橙色标注；既有敏感性分析中，去除它们或过滤高缺口列未改变共享序列的拓扑，换随机种子有一个分裂变化。35 条分析序列有 27 条来自 Potyvirus，因此该树不能被解释为均衡的科级多样性调查，任何天然序列也没有据此获得低温活性标签。

**原始数据与来源：**[树](../build/phylogeny/nia_pro_representative_phylogeny.nwk)、[对应 MSA](../build/phylogeny/nia_pro_representative_alignment.fasta)、[末端元数据](figure_data/F3_tip_metadata.csv)、[节点支持](figure_data/F3_node_support.csv)；`src_uniprot`，原始 UniProt 导出及 `homolog_metadata.csv`；[自然模块审核](../build/publication_natural/natural_review_summary.json)。MAFFT 版本按原始日志为 7.526。

**关键限制：**短蛋白域的无根基因树，不是有根物种演化史；重组未评估。三项敏感性分析作用于 35 条全分析集及其子集，不等同于对 23 条代表树另做三次重复。所有天然候选低温活性为 `UNKNOWN`。

## F4｜天然位点保守性与覆盖

[SVG](figures/F4_natural_conservation.svg) · [PNG](figures/F4_natural_conservation.png) · [PDF](figures/F4_natural_conservation.pdf)

**中文讲解（4 句）：**上图在成熟 TEV 的 242 个标准位置展示按氨基酸熵计算的保守性，指标为 1−H/log₂20。三条曲线分别使用 35 条原始序列、移除三条长分支后的 32 条序列，以及每属总权重相等的描述性方案。下图同时展示位点覆盖，防止把缺口多、实际观察较少的位置误读为高度可靠的保守位点。这些曲线表达当前取样的描述性差异，既不是置信区间，也不能证明某个位点不可突变或与冷适应存在因果关系。

**原始数据与来源：**[逐位点数据](figure_data/F4_conservation_and_coverage.csv)、[35 条 MSA](../nia_pro_alignment.fasta)、[映射](../msa_positions.csv)；`src_uniprot`；原始全分析集 290 列，≥70%占有率敏感性集 243 列。催化位点锚定检查 35/35 通过。

**关键限制：**Potyvirus 过量取样、属内相关性、缺口和域长度都会影响结果；按属加权不是独立样本增加。没有使用这些曲线生成新突变设计。

## F5｜NEB 专利低温实验结果

[SVG](figures/F5_patent_low_temperature.svg) · [PNG](figures/F5_patent_low_temperature.png) · [PDF](figures/F5_patent_low_temperature.pdf)

**中文讲解（5 句）：**左图重绘专利 US20260234592A1 Example 12 的蛋白底物切割端点：18 小时、4℃ 时对照、追加 L76P 和追加 R49F/L76P 分别为 77%、87% 和 97%，并同时展示 0℃ 数据。所有构建体都含 L56V/S135G/S219V 背景且成熟域截至 237 位，图上的名称只表示追加替换。右图的 2.0、1.7、1.5、2.6 倍来自 Example 13 四组分别配对的 4℃ 端点拟合，代表 ln(1−切割比例) 对酶浓度的斜率之比。这不是独立测得的绝对 kcat/Km，也不支持把四个对照斜率混成一个对照。原文未报告的重复数和误差没有补造，专利构建体也没有被强行等同于商业 NEB P8118。

**原始数据与来源：**[10 条测量](figure_data/F5_patent_measurements.csv)、[USPTO 原始 PDF](../raw-data/patents/US20260234592A1.pdf)，Example 12–13、Figure 12/14、Tables 2–5，PDF 第 29–30 页；`pat_*` 测量和 `src_patent2026`。Example 12 配方推算的终浓度为酶 0.4 µM、底物 37 µM，属于由配方计算而非原文另行报告的数值。

**关键限制：**专利证据类别；长时间端点接近饱和，不是初速比较。该图只概括此专利，不能被称为所有 TEV 4℃ 证据全集；Messing Figure 2D 和 Cabrita 未展示数据的文字陈述另见导师摘要第 4 页。
