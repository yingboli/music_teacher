import os
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import streamlit as st


def create_chat(
    topic: str,
    profile: Optional[str] = None,
    openai_model: str = "gpt-5.2", #"gpt-4o"
    message: Optional[str] = None,
):

    ## Set API Key
    for var in ["OPENAI_API_KEY"]: #, "LANGSMITH_API_KEY"
        os.environ[var] = st.secrets[var]
    
    ## Use temperature 0 for facts and logics
    llm = ChatOpenAI(model=openai_model, temperature=0) 
    
    chat_instructions="""You are a rigorous and friendly music theory teacher. 
    You are going to explain the follow topic to a student. 

    Topic: {topic}
    Student profile: {profile}
    
    Based on specific student profile, determine the most appropriate and effective way to structure your answer.
    
    Double check the correctness of your answer.
    
    Keep you answer concise. Most of the time, one or two paragraphs should be sufficient.

    At the end, no need to ask what else you can do for the student.
    """

    system_message = chat_instructions.format(topic=topic, 
                                              profile=profile or '')
    with st.spinner("AI music teacher is thinking..."):                                            
        results = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(message or '')])

    return results
