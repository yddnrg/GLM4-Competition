from zhipuai import ZhipuAI
from tokens_ import tokens
import json
sub_info="""
你是一个专精于帮助总结子公司信息的助手。请你根据提供给你的子公司名单，以及问题，对关键字，进行重新格式化总结
提示一：格式要求仅保留'上市公司参股比例'、'上市公司投资金额'、 '公司名称'，以完整列表返回。
提示二：根据问题决定是否按某些数值排序，返回完整列表
提示三：如果提问主要投资者、投资最多，只问哪一家、哪家，那么请找到"投资金额"最大的一家公司。
提示四：如果涉及总投资金额，你应该先列出所有完整列表，然后进行计算。
提示五：如果涉及根据条件（如参股比例，投资额）进行统计，为了避免过长的上下文，你可以只做统计，得出结果
你的返回格式：[\{\},\{\}]
"""
categories=f"""
你是一个帮助专精于将给定的“问题”进行“分类”的助手，请你对这个问题进行多分类，即可能包含1个或者多个类别
类别：1.母公司查找子公司，涉及投资信息 2.子公司查找母公司 3.根据公司的名称查找公司信息 4.法律文书判决相关 5. 给定了母公司，查询其子公司的控股、投资比例 6.开放性问题 7.先得知主体企业的行业类型，再根据行业的类型，查找属于该行业的所有企业\n
下面是3个问答的例子：
例1:你接收到的问题：想问问，浙江杰克成套智联科技有限公司、上海三菱电梯有限公司、潍坊西能宝泉天然气有限公司分别属于哪家公司旗下。分析：2.问题分类：子公司查找母公司。 主体：浙江杰克成套智联科技有限公司、上海三菱电梯有限公司、潍坊西能宝泉天然气有限公司
例2:你接收到的问题：劲拓股份拥有哪些子公司？分析：1.母公司查找子公司。主体：劲拓股份
例3:你接收到的问题：请问Beijing Comens New Materials Co., Ltd.全资控股的子公司有哪些？或 持股超过50%的子公司有哪些？分析：5.查询子公司的控股投资比例，主体：Beijing Comens New Materials Co., Ltd.
例4:你接收到的问题：广汇能源股份有限公司的主要投资者是哪一家企业？分析：5. 给定了母公司，查询其子公司的控股、投资比例。主体：广汇能源股份有限公司
例5:你接收到的问题：帮忙找下无锡上机数控股份有限公司的企业主承销商以及首次公开发行募集资金净额。分析：3.根据公司的名称查找公司信息。主体：无锡上机数控股份有限公司
例6:你接收到的问题：关于案号为(2019)鄂01民初4724号的案件，能否提供原告和被告的详细身份信息，并阐述该案件的具体诉讼理由？分析：4.法律文书判决相关。主体:(2019)鄂01民初4724号
例7:你接收到的问题：在新城控股集团股份有限公司面临诉讼担任被告时，其通常委托哪一家律师事务所提供法律服务？该合作关系的频次如何？分析：4.法律文书判决相关。主体:新城控股集团股份有限公司
例7:你接收到的问题：上市公司如何因违反公平披露原则受到处罚？ 分析：6.开放性问题 主体：无
请你严格按照例子的格式给出分类，不允许进行推测以及额外信息
"""
refiner="""
你是一个负责将答案进行优化的助手，接下来你会收到{"问题":问题,"答案":答案}这样的问题答案对，
你需要将根据问题的需要将答案的内容进行优化，使其精炼、保留关键信息，去除无用符号，使其更符合自然语言。
你的回答模板：{"答案":新答案}，
你的回答里的内容必须只能包含根据模板产生的答案，不能带有任何其他文字，因为我需要将其转换成python dict.
"""

def agent_question(question, model_type="glm-4-air"):
    agent_question = ZhipuAI(api_key=tokens["glm_token"])
    messages_q = [
        {"role": "system", "content": categories},
        {"role": "user", "content": f"你接收到的问题：{question}"},
    ]
    response = agent_question.chat.completions.create(
        model=model_type,
        messages=messages_q,
    )
    return response.choices[0].message.content


def agent_sub_info(question, sub_list, model_type="glm-4"):
    agent_sub_info = ZhipuAI(api_key=tokens["glm_token"])
    messages_sub = [
        {"role": "system", "content": sub_info},
        {"role": "user", "content": f"你接收到的问题：{question},子公司列表{json.dumps(sub_list, ensure_ascii=False)}"},
    ]
    response = agent_sub_info.chat.completions.create(
        model=model_type,
        messages=messages_sub,
    )
    return response.choices[0].message.content
def agent_answer_refiner(question,answer,model_type="glm-4"):
    agent_sub_info = ZhipuAI(api_key=tokens["glm_token"])
    qa_pair={"问题":question,"答案":answer}
    messages_sub = [
        {"role": "system", "content": refiner},
        {"role": "user", "content": f"{qa_pair}"},
    ]
    response = agent_sub_info.chat.completions.create(
        model=model_type,
        messages=messages_sub,
    )
    raw_response = response.choices[0].message.content

    # 使用 rstrip 和 lstrip 去除返回结果中 JSON 对象外的多余字符
    cleaned_response = raw_response.lstrip().rstrip()
    start_index = cleaned_response.find('{')
    end_index = cleaned_response.rfind('}') + 1
    if start_index != -1 and end_index != -1:
        json_content = cleaned_response[start_index:end_index]
        json_content = json_content.replace("'", '"')
    else:
        json_content = "{}"  # 默认值，以防无法匹配
    
    return json_content
if __name__=="__main__":
    import json
    with open("submit_example_new.json","r") as fp:
        with open("submit_example_new_refined.json","a") as refined_fp:
            for id,line in enumerate(fp):
                if id<225:
                    continue
                submit=json.loads(line.strip())
                message=agent_answer_refiner(submit["question"],submit["answer"])
                try:
                    answer = json.loads(message)
                except:
                    print(message)
                    raise BaseException
                new_line={"id": id, "question":submit["question"], "answer": answer["答案"]}
                print(f"line{id}:complete")
                refined_fp.write(json.dumps(submit, ensure_ascii=False) + "\n")
