from pathlib import Path
from langchain_core.prompts import PromptTemplate


def build_prompt(text: str) -> str:
    """Render the prompt template with the given text."""

    template_str = Path(__file__).with_name("prompt.md").read_text(encoding="utf-8")
    prompt = PromptTemplate.from_template(template_str)
    return prompt.format(text=text)

def build_custom_prompt(text: str,prompt_file : str = "generate_question.md" ) -> str:
    """Render the prompt template with the given text."""

    template_str = Path(__file__).with_name(prompt_file).read_text(encoding="utf-8")
    prompt = PromptTemplate.from_template(template_str)
    return prompt.format(text=text)


if __name__ == "__main__":
    print(build_prompt('''聊呗，你老管弹幕干嘛？弹幕都是一群很可爱的笔友们在开玩笑，网络世界不就是这样吗？我相信我从你的面相上来看，也是个经历过大风大浪的人，怎么这两把刷子就把你给唬住了呢？是不是？你是螺丝数码是码拉出来溜溜是吧？也是在社会上摸爬滚打这么多年了是吧？我们重新开始好吗？好不好？好不好？我重新问，你重新答，就像一切没有发生过一样，OK。'''))
    print(build_custom_prompt('''聊呗，你老管弹幕干嘛？弹幕都是一群很可爱的笔友们在开玩笑，网络世界不就是这样吗？我相信我从你的面相上来看，也是个经历过大风大浪的人，怎么这两把刷子就把你给唬住了呢？是不是？你是螺丝数码是码拉出来溜溜是吧？也是在社会上摸爬滚打这么多年了是吧？我们重新开始好吗？好不好？好不好？我重新问，你重新答，就像一切没有发生过一样，OK。''','generate_question.md'))
