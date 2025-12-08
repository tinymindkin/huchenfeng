---
language:
  - zh
license: other
pretty_name: HuChenFeng Dialogue Dataset
size_categories:
  - 50K<n<100K
task_categories:
  - text-generation
task_ids:
  - dialogue-generation
source_datasets:
  - original
---

# Dataset Card: HuChenFeng Dialogue Dataset

## Dataset Summary
HuChenFeng Dialogue Dataset 收录了 81,060 条高质量的中文单轮对话，每条样本由一个「用户」提问与一段长篇的「主播」回答组成，完整保留了知名主播 **户晨风** 的口语化表达、情绪变化与节奏。原始素材来自 2023–2025 年的直播转录，先经 Whisper Large-v3 语音识别，再由 Gemini-2.5-Flash 清洗去噪，最终使用 Gemini-2.5-Flash-Lite 为每段回答生成 3–5 个不同角度的问题。生成的问题与对应原回答经人工与规则联动过滤，最后导出为 `question_answer.jsonl`（ChatML 风格 `messages` 列表），可直接用于监督微调（SFT）、LoRA/QLoRA、角色扮演代理构建等任务。

* **规模**：81,060 条问答对（≈2.8B tokens，Qwen 分词），平均问题 18.3 个中文字，回答 342.7 个中文字。
* **格式**：JSON Lines，每行一个样本，字段同 `transformers` ChatML（`user` → `assistant`）。
* **来源**：户晨风 2023–2025 年[直播转录](https://github.com/Olcmyk/HuChenFeng)。
* **用途**：适合训练中文风格迁移、长篇回答、直播带货口吻或人格化聊天的模型，也可作为 prompt 工程与数据合成案例。

## Supported Tasks and Leaderboards
- **Dialogue / Instruction Tuning**：训练中文问答、角色扮演、对话安全或记忆模块。
- **Data Augmentation**：可为其他中文会话系统提供长篇回答示例。

## Languages
- **Input language**：Simplified Chinese (zh-Hans)，包含大量口语、俚语、幽默用法以及中文夹杂口头禅。

## Dataset Structure
### Data Instances
```json
{
  "messages": [
    {"role": "user", "content": "你觉得现在的大学还有含金量吗？"},
    {"role": "assistant", "content": "你读大学，你有点含金量也行，说白了水个学历..."}
  ]
}
```
回答通常是 1–3 段长文本，保持主播原始口吻；不同问题可能指向相同回答，以保留多问法效果。

### Data Fields
- `messages` *(List[Dict])*：标准 ChatML 对话列表，长度固定 2。
  - `role` *(str)*：`"user"` 或 `"assistant"`。
  - `content` *(str)*：UTF-8 中文文本，已去除 Markdown/表情符号，仅保留原生口语。

## Data Collection
### Curation Rationale
- 通过公开直播内容构建能体现主播人格、语速、逻辑跳跃等特征的风格化语料，填补中文口语 LoRA/SFT 数据缺口。

### Source Data
#### Initial Data Collection and Normalization
1. **语音转文字**：户晨风 2023–2025 直播音频 → Whisper Large-v3（≈200 万字）。
2. **转录切分**：仅保留 ≥200 字的完整段落，分月归档 (`dataset/2024年05月/*.md` 等)。
3. **语料清洗**：Gemini-2.5-Flash 删除噪声（读评论、重复口癖、背景音乐描述、ASR 错误）。
4. **问法生成**：Gemini-2.5-Flash-Lite 按段生成 3–5 个不同视角、语气提问。
5. **数据库存储**：写入 `raw_dialogues.db` → `train_dialogues`（长回答列表） → `question_answer_table`（问题、回答、模型版本、状态）。
6. **导出**：`train/generate_dataset.py` 过滤 `status=1` 且 `LEN(question)>2` 的行，输出 ChatML JSONL。

#### Who are the source language producers?
- 主体为主播户晨风在直播中的即兴独白，问题由 Gemini-2.5-Flash-Lite 自动生成，再由开发者审核。

## Annotations
### Annotation Process
- 由自动问法生成 + 规则过滤 + 人工抽检。`status` 字段记录是否通过审核，只有通过记录会进入导出的 JSONL。

### Who are the annotators?
- 项目维护者（HuChenFeng 团队）负责审查脚本日志、抽样评估以及剔除不合格的问答对。



## Citation
如果本数据集对你的工作有帮助，请引用本仓库：

```bibtex
@misc{huchenfeng_dialogue_2024,
  title        = {HuChenFeng Dialogue Dataset},
  author       = {tinymindkin and contributors},
  howpublished = {GitHub repository},
  url          = {https://github.com/tinymindkin/huchenfeng},
  year         = {2024}
}
```

## Contributions
- Dataset curators & maintainers: [@tinymindkin](https://github.com/tinymindkin) and HuChenFeng project collaborators.
- 感谢 [Olcmyk/HuChenFeng](https://github.com/Olcmyk/HuChenFeng) 提供完整直播文字稿参考。
