from zhipuai import ZhipuAI
from tokens_ import tokens
from data_query import url as origin_url, headers
from tools import tools,use_the_tool
from agents import *
client = ZhipuAI(api_key=tokens["glm_token"])
question='广汇能源股份有限公司的主要投资者是哪一家企业？'
agent_content = agent_question(question=question)
print(agent_content)
messages = [
    {
        "role":"system",
        "content": "你是一个通过调用企业信息或者法律文书信息的tools给用户提供信息的助手，注意工具提供给你的信息已经足够完整，可以足够回答问题。对于一些非查询的开放性问题，你也可以根据你的知识自己回答,不需要使用tools"
    },
    { 
        "role": "user",
        "content": f"{question}{agent_content}"+"。请注意的标点符号格式要和主体保持一致，要与提问对齐，但如果多次查询无果，可以尝试将中英文括号进行替换，如（）和()之间进行互换，提示：对于主体中的公司名，一般是全称，但也可能是非全称的简称或英文名称，请尝试用tools将其转换为“全称”；对于案件号，请捕捉更正确的格式。稍后，才会提供tools的选择,请充分运用tools解决问题”"
    }
]
"请你先将问题先进行拆分，便于你自己的理解，思考一下完成任务的顺序，以短语操作和箭头表示，简短，不做任何模拟，以避免污染数据，"
'''response = client.chat.completions.create(
    model="glm-4", # 填写需要调用的模型名称
    messages=messages,
    )
print(response.choices[0].message)
messages.append(response.choices[0].message.model_dump())
messages.append({ 
        "role": "user",
        "content": f"{question}，{response.choices[0].message.content}"+"。请不要显式包含换行符号，以自然的文本段回答就可以"
    })'''
for i in range(20):
    response = client.chat.completions.create(
    model="glm-4", # 填写需要调用的模型名称
    messages=messages,
    tools=tools,
    )
    print(response.choices[0].message)
    if 'Complete' in response.choices[0].message.content:
        break
    messages.append(response.choices[0].message.model_dump())# 后文补全
    while(True):
        rsp = use_the_tool(tool_calls=response.choices[0].message.tool_calls,origin_url=origin_url,headers=headers,question=question)
        if rsp is None:
            print("找不到tools")
            break
        print("------------------------------------------")
        print(rsp)
        print("------------------------------------------")
        messages.append({
                    "role": "tool",
                    "content": f"{rsp}",
                    "tool_call_id": response.choices[0].message.tool_calls[0].id
                })
        response = client.chat.completions.create(
                model="glm-4",  
                messages=messages,
                tools=tools
            )
        print(response.choices[0].message)
        messages.append(response.choices[0].message.model_dump())
    messages.append({
    "role": "user",
    "content": "如果你认为你的回答足以回答这个问题：,\'"+f"{question}"+"。那就回复一个'Complete',但如果没有任何信息，是你错误调用了工具，不能令人满意。请根据该问题，以及你得到的信息，以及你的回答，试想如何使用工具完成任务"
    })