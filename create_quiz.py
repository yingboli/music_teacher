import json
import os
from typing import List, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
import pandas as pd

# from IPython.display import Markdown, Image, display
from pydantic import BaseModel, Field
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from typing_extensions import TypedDict

# from langgraph.checkpoint.memory import MemorySaver


def create_quiz(
    openai_model = "gpt-5.2", #"gpt-4o"
    topics = ['pitch', 'duration', 'time_signature'],
    num_questions = 200,
    message = """If pitch is among the syllabus topics, then about 50% of the time, the question is about the pitch of a note. Please spread out them randomly. 
    """,
):

    ## Set API Key
    for var in ["OPENAI_API_KEY"]: #"LANGSMITH_API_KEY"
        os.environ[var] = st.secrets[var]
    
    ## Use temperature 1 for generative tasks
    llm = ChatOpenAI(model=openai_model, temperature=1) 
    
    quiz_creator_instructions="""You are a helpful and creative music theory teacher.
    
    You are going to create a quize that contains {num_questions} multiple choice questions on the following syllabus:
    
    {syllabus_in_quiz}
    
    For each question, it contains the following part:
    
    1. Question
    
    The question consists a text and a music note generator Python code. 
    
    For example, the text can be "What's this name of this note?", and the python code uses musci21 libarary
    
        import music21
        from music21 import note, pitch, duration, stream, dynamics, tempo, expressions, articulations
        q = note.Note("G4")
        q.write('musicxml.png', fp='game.png') ## Keep this line in the exact format
    
    At the end of the code, the python code will output the music note out as a tmp.png file.
    
    Make sure the question text does not reveal too much info such that the answer is too easy.
    
    Also, please stick with the concept within the syllabus so the question is not out of the scope thus too difficult.

    Double check that the music21 code can run without errors.
    
    
    2. Choices
    
    Create four choices in the format of a python list of str.
    
    The choices are pure text. For the above example question, the chocies can be ["E", "F", "G", "B"]
    
    Double check that there exact a correct answer among the options.
    
    Double check that only there is only one correct answer among the choices.
    
    Please evenly spread out the correct answer among the four choices, i.e., the correct answer is not always the 2nd or 3rd choices.
    
    3. Correct answer in index
    
    Give the index of the correct answer among the four choices. 
    
    Only output the index as an int.
    
    It can only take value in the list [0, 1, 2, 3]
    
    Double check the answer is correct.
    
    
    These questions are for American students. So use the american version of the music theory terminologies 
    (e.g., use whole note instead of semibreve).

    Double check to make sure you created exact {num_questions} questions, no less and no more. In addition, these questions are all different from each other!

    """
    
    ################################################################
    ## LangGraph
    class Question(BaseModel):
        question_text: str = Field(
            description="Question text",
        )
        question_code: str = Field(
            description="Python music21 code to generate the question score",
        )
        choices: List[str] = Field(
            description="A list of four choices",
        )
        answer_index: Literal[0, 1, 2, 3] = Field(
            description="Index of the correct answer among the choices",
        )
    
    class Quiz(BaseModel):
        quiz: List[Question] = Field(
            description="A list of questions."
        )
    
    class GenerateQuizState(TypedDict):
        quiz: List[Question]
        num_questions: int
        syllabus_in_quiz: str
        message: str
    
    
    def create_quiz(state: GenerateQuizState):
        
        """Create quiz """
        # Enforce structured output
        structured_llm = llm.with_structured_output(Quiz)
    
        # System message
        system_message = quiz_creator_instructions.format(num_questions=state['num_questions'], 
                                                          syllabus_in_quiz=state['syllabus_in_quiz'])
    
        # Generate question 
        quiz = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(state['message'])])
        
        # Write the list of analysis to state
        return {"quiz": quiz.quiz}
    
    def save_quiz_to_dict(results):
        quiz = []
        for i in range(len(results['quiz'])):
            quiz.append({
                'question_text': results['quiz'][i].question_text,
                'question_code': results['quiz'][i].question_code,
                'choices': results['quiz'][i].choices,
                'answer_index': results['quiz'][i].answer_index,
            })
        return quiz

    def save_quiz_to_df(results):
        quiz = pd.DataFrame(columns = ["question_text", 
                                       "question_code", 
                                       "choices", 
                                       "answer_index"])
        for i in range(len(results['quiz'])):
            new_question = pd.Series({
                'question_text': results['quiz'][i].question_text,
                'question_code': results['quiz'][i].question_code,
                'choices': results['quiz'][i].choices,
                'answer_index': results['quiz'][i].answer_index,
            })
            quiz = pd.concat([quiz.T, new_question.T], axis=1).T
        return quiz

    # Add nodes and edges 
    quiz_builder = StateGraph(GenerateQuizState)
    quiz_builder.add_node("create_quiz", create_quiz)
    quiz_builder.add_edge(START, "create_quiz")
    quiz_builder.add_edge("create_quiz", END)
    
    # Compile
    quiz_graph = quiz_builder.compile()#checkpointer=memory)
    
    # View
    # display(Image(quiz_graph.get_graph(xray=1).draw_mermaid_png()))
    
    with open("data/syllabus/ABRSM_syllabus_grade1.json", "r") as f:
        syllabus = json.load(f)
    
    syllabus_in_quiz = []
    for topic in topics:
        syllabus_in_quiz += f"{topic}: {syllabus[topic]}\n\n" 
            
    results = quiz_graph.invoke({'num_questions': num_questions, 
                                 'syllabus_in_quiz': syllabus_in_quiz, 
                                 'message': message})
    
    # quiz = save_quiz_to_dict(results)
    # with open(output_json, "w") as f:
    #     json.dump(quiz, f)
    
    quiz = save_quiz_to_df(results)
    conn = st.connection("gsheets_game_inventory", type=GSheetsConnection)
    conn.update(data=quiz, worksheet="Sheet1")

    

