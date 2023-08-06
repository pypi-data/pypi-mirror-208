from simplechain.pipeline.module import module


@module("Chat Output Prompt")
def output_prompt(questions: str, answers: str, chat_history: str):
    prompt = f"""
    I am a professional car salesman and I am having a conversation with a customer.
    """

    if questions:
        prompt += f"""
        I have some questions that I would like to ask the customer:
        {questions}
        """

    if answers:
        prompt += f"""
        I have some answers in response to the customer's questions:
        {answers} 
        """

    # TODO how do i write a response that includes the answers and questions
    prompt += f"""
    How do I write a response that fits the conversation history:
    {chat_history}
    Me:"""
    return prompt

@module("Formulate Questions Prompt")
def formulate_questions_prompt(questions: str, answer: str, knowledge: str):
    prompt = f"""
    I am a professional car salesman and I am having a conversation with a customer.
    
    I have the following knowledge about the customer:
    {knowledge}
    
    The customer asked me the following question:
    {questions}
    
    And my response for it:
    {answer}
    
    What questions can I ask the customer to be able to improve my answer or narrow down the results? Please write out a list:
    """
    return prompt



@module("Verify Answer")
def information_extraction_template(question: str, answer: str):
    BASE_PROMPT = """
    You are a 
    
    """

    pass


@module("Question Template")
def question_template(role: str, chat_history: str, knowledge: str, questions: str) -> str:
    """question template"""
    """
    knowledge 
    chat history - last 5 lines
    questions to ask
    """

    """
    questions {what does customer want?}
    wants: {to buy, information}
    
    to_buy: {what?}
    information: {about what}
    wants: {}
    wants to buy: car part category 
    """

    BASE_PROMPT = """I am a {role} professional car parts salesman. I can find and explain any car part. 
    
    In addition, I can assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. 
    
    I am talking with a customer.
    
    Here are some things I know about the customer:
    {knowledge}
    
    Here is the most recent chat history:
    {chat_history}
    
    They may have 
    I need to decide whether I need a tool to respond to the customer. If I need access to one of the following tools:
    {tools}
    
    Then I should say 
    

    
    
    
    
    I am 
     
    I am not a mechanic, so I can't tell you how to install the part. I can only tell you what part you need. 
    I can also tell you where to buy the part. I can also tell you how much the part costs. I can also tell you how much the part weighs. 
    I can also tell you how much the part costs to ship. I can also tell y
    
    
    I'm talking with a customer. I have access to the following tools:
    {tools}
    
    
        prompt =

    

    You have access to the following chat history:
    

    You have to find out about the following information:
    {questions_to_ask}
    
    """

    return ""


@module("MRKL Template")
def mrkl_template() -> str:
    """MRKL template for prompt templates."""
    PREFIX = """Answer the following questions as best you can. You have access to the following tools:"""
    FORMAT_INSTRUCTIONS = """Use the following format:
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question"""
    SUFFIX = """Begin!
    Question: {input}
    Thought:{agent_scratchpad}"""

    return FORMAT_INSTRUCTIONS
