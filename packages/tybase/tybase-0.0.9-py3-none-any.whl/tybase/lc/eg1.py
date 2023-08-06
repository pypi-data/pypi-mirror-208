from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
# 这就是我们依次运行这两条链的整体链。
from langchain.chains import SequentialChain
import json


class GetPrompt():
    def __init__(self, openai_api_key, role_temperature: float = 0.3):
        self.openai_api_key = openai_api_key
        self.role_temperature = role_temperature

    def chain_role(self):
        prompt_base = """
            [机器人信息]:
            ```
            {prompt_info}\n
            {desc}
            ```
        
            通过以上的[角色信息],我应该用什么样的格式向这个机器人输入内容? 可以把输入的内容举{num}个例子,每个例子的长度不要超过中文20个汉字,示例如下:
        
            输入示例: xxx
        
            不用返回机器人回复,只需要输出[输入示例]的内容即可
        
            """

        human_message_prompt = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=prompt_base,
                input_variables=["prompt_info", "desc", "num"],
            )
        )

        chat_prompt_template = ChatPromptTemplate.from_messages([human_message_prompt])
        return LLMChain(llm=ChatOpenAI(temperature=self.role_temperature, openai_api_key=self.openai_api_key),
                        prompt=chat_prompt_template, output_key="example")

    def chain_json(self):
        prompt_json = """
        请提取下面文本中的所有"输入示例"里面的**内容**,返回成一个list,可以直接用json解析
    
        ```
        {example}
        ```
    
        """

        human_message_prompt = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=prompt_json,
                input_variables=["example"],
            )
        )

        chat_prompt_template = ChatPromptTemplate.from_messages([human_message_prompt])
        return LLMChain(llm=ChatOpenAI(temperature=0, openai_api_key=self.openai_api_key),
                        prompt=chat_prompt_template, output_key="example_json")

    def main(self, prompt, desc, num=4):
        """

        :param prompt: 系统设定的指令
        :param desc:   系统设定的描述语
        :param num:    需要生成的指令数量
        :return:       ( json )的str,需要自己再解析一下
        """
        overall_chain = SequentialChain(
            chains=[self.chain_role(), self.chain_json()],
            input_variables=["prompt_info", "desc", "num"],
            # Here we return multiple variables
            output_variables=["example", "example_json"],
            verbose=True)

        inputs = {"prompt_info": prompt, "desc": desc, "num": num}  # 参数传递就这样传递
        return json.loads(overall_chain(inputs)["example_json"])


if __name__ == '__main__':
    pass
