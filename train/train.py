from unsloth import FastLanguageModel
from datasets import load_dataset
import torch

# ============ 配置参数 ============
max_seq_length = 2048  # 根据你的对话长度调整
dtype = None  # 自动检测。Tesla T4, V100 用 Float16，Ampere+ 用 Bfloat16
load_in_4bit = True  # 使用 4bit 量化节省显存

# ============ 1. 加载模型 ============
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/qwen2.5-7b-bnb-4bit",  # 支持 Qwen, Llama, Mistral 等
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# ============ 2. 添加 LoRA 适配器 ============
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank，越大参数越多
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_alpha=16,
    lora_dropout=0,  # 优化支持 0
    bias="none",
    use_gradient_checkpointing="unsloth",  # 长上下文必备
    random_state=3407,
)

# ============ 3. 准备数据集 ============
# 方式A：从数据库加载（结合你的 SFT 数据表）
def load_from_mysql():
    """从你的 sft_training_data 表加载"""
    import mysql.connector
    
    conn = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT instruction, input, output FROM sft_training_data")
    
    data = []
    for instruction, input_text, output in cursor.fetchall():
        messages = [
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": output}
        ]
        data.append({"messages": messages})
    
    return data

# 方式B：直接使用 ChatML 格式的 JSON
dataset = load_dataset("json", data_files="your_sft_data.jsonl")

# ============ 4. 格式化数据 ============
# Unsloth 提供自动格式化
def formatting_prompts_func(examples):
    """将数据转换为 Qwen 的 chat template"""
    convos = examples["messages"]
    texts = [
        tokenizer.apply_chat_template(
            convo, 
            tokenize=False, 
            add_generation_prompt=False
        ) 
        for convo in convos
    ]
    return {"text": texts}

dataset = dataset.map(
    formatting_prompts_func, 
    batched=True,
)

# ============ 5. 训练配置 ============
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,  # 多轮对话建议关闭 packing
    
    args=TrainingArguments(
        # 基础配置
        output_dir="./outputs",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,  # 有效 batch_size = 2*4 = 8
        
        # 训练步数
        num_train_epochs=3,
        max_steps=-1,  # -1 表示使用 num_train_epochs
        
        # 学习率
        learning_rate=2e-4,
        warmup_steps=10,
        lr_scheduler_type="linear",
        
        # 优化器（Unsloth 优化过的 AdamW）
        optim="adamw_8bit",
        weight_decay=0.01,
        
        # 日志和保存
        logging_steps=10,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=3,
        
        # 显存优化
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        gradient_checkpointing=True,
        
        # 性能
        dataloader_num_workers=2,
        group_by_length=True,  # 按长度分组减少 padding
        
        # 其他
        seed=3407,
        report_to="tensorboard",  # 或 "wandb"
    ),
)

# ============ 6. 开始训练 ============
trainer_stats = trainer.train()

# ============ 7. 保存模型 ============
# 保存 LoRA 适配器
model.save_pretrained("./lora_model")
tokenizer.save_pretrained("./lora_model")

# 保存合并后的完整模型（推理用）
model.save_pretrained_merged(
    "./merged_model", 
    tokenizer,
    save_method="merged_16bit",  # 或 "lora", "merged_4bit"
)

# ============ 8. 推理测试 ============
FastLanguageModel.for_inference(model)  # 启用推理模式（快2倍）

messages = [
    {"role": "user", "content": "你对创业怎么看？"}
]

inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
).to("cuda")

outputs = model.generate(
    input_ids=inputs,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))