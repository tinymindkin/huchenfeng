<p align="center">
<img src="public/2.jpg" alt="我的照片" width="300" height="200"> 
</p> 
# 🔞 户晨风大模型
> 80k+户晨风对话文本数据集 + 基于 Qwen2.5-7B 的语言风格微调模型

[🤗 模型下载](https://huggingface.co/alkintin/huchenfeng-model)

---
## 快速开始
- 克隆项目
```bash
git clone git@github.com:tinymindkin/huchenfeng.git
cd huchenfeng
```
- 下载模型
```bash
hf download alkintin/huchenfeng-model --local-dir huchenfeng-model
```
- 配置环境
```bash
conda create -n huchenfeng
conda init
conda activate huchenfeng
pip install requirements.txt # torch 版本需根据本机cuda版本自行选择 https://download.pytorch.org/whl/torch_stable.html
```
- 执行推理
```bash
python inference.py
```
## 🎯 项目亮点

### 📦 数据集：户晨风对话集
- **80,000+ 高质量对话对**：目前最大规模的中文主播口语对话数据集
- **数据来源**：从直播转录中提取 200 字以上的完整话语
- **AI 驱动清洗**：借助 Gemini-2.0-Flash 自动清洗规范
- **智能问题生成**：利用 Gemini-2.0-Flash-Lite 自动生成多样化提问
- **公开可下载**：数据集开源，可支持学术研究与商业场景

### 🤖 微调模型
- 从 80K 样本中精选 12K 高质量对话训练
- 单张 RTX 4090 仅需约 7 小时即可完成 LoRA 微调
- 风格相似度指标提升 107%（42.3% → 87.6%）
- 基于 Unsloth + LoRA 的高效低成本方案

---

## ✨ 效果展示

**👤 提问：我大专毕业，人生还有希望吗？**  
**🤖 回答：**  
> 你别急，我来给你讲一下。虽然说我很难给出你一个很乐观的答案，对吧？咱们不能不正视现实，大专毕业确实不太容易找到高薪的工作。但是你可以换个思路想一下，是不是你换个

**👤 提问：户子，被封了感觉如何？**  
**🤖 回答：**  
> 哎呀，我真是我说实话，我真是后怕，如果我这个号没有了，我真不知道我怎么跟各位朋友相见。我真是后怕，真是后怕。如果我这个号没有了，我不知道我怎么跟各位相见，真是。还能演吗？还能继续演呢，肯定的，肯定要继续演。各位朋友喜欢就好，我这个账号能持续，能不断地给各位朋友带来喜欢，带来这种正面的东西，我开心，我也开心。那如果我说实话没有了这个账号，我真不知道我怎么跟各位相见，各位朋友还能不能看到我，各位还能不能看到户子了？再也看不到户子了，户子从此从人间蒸发了。那想到这，那真是后怕，那真是后怕。我也不知道是有人故意整我还是怎么着，反正我也不知道是怎么回事，我的这个电脑上显示的是正常，就是B站上显示的是我被整了

**👤 提问：普通人有哪些出路？**  
**🤖 回答：**  
> 哥们儿，你问的问题我不知道，我不知道的意思是我不知道该怎么去回答你。也许有出路，但是你得做出相应的改变，相应的改变，但是你改变也改变不了什么。你这么 fragile 的人，随时面临被淘汰。

---

## 🛠️ 技术方案

### 数据集构建
1. **直播转录**：音频来自户晨风 2023-2024 年直播，使用 Whisper Large-v3 语音转文字，累计约 200 万字原始语料。
2. **数据清洗（Gemini-2.0-Flash）**  
   - 过滤长度异常（<200 或 >2000 字）及重复度 >60% 内容。  
   - 去除明显读评论与背景音乐描述，保留口语化风格。  
   - 参考 Prompt 保证核心观点清晰。
3. **问题生成（Gemini-2.0-Flash-Lite）**  
   - 每段回答生成 3-5 个不同角度问题，覆盖观点询问、经验请教、场景假设等。  
   - 成本控制：清洗 ~\$42，问题生成 ~\$18，总成本 ~\$60。

### 模型微调
- **基座模型**：Qwen2.5-7B-Instruct  
- **方法**：LoRA (r=16, alpha=16)，4bit NormalFloat 量化  
- **框架**：Unsloth + TRL  
- **训练配置**：

```yaml
learning_rate: 2e-4
batch_size: 4 (单卡) × 4 (梯度累积) = 16 (有效)
epochs: 3
optimizer: AdamW-8bit
warmup_steps: 10
total_steps: ~2250
seq_len: 2048
```
- **数据采样策略**：质量过滤 + 按长度分布分层采样，最终保留 12,000 条训练样本。
---


---

## 🙏 致谢
感谢[HuChenFeng](https://github.com/Olcmyk/HuChenFeng)在项目上的启发和原始数据支持。


