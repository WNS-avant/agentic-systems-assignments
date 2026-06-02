from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


def build_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a beginner-friendly programming instructor. "
                "Explain concepts in simple language using the analogy provided by the user.",
            ),
            (
                "human",
                "Explain {topic} using an analogy from {analogy_domain}. "
                "Keep the explanation simple and easy for beginners.",
            ),
        ]
    )

    llm = ChatOllama(
        model="qwen:1.8b",
        base_url="http://localhost:11434",
        temperature=1,
        num_predict=100,
    )

    parser = StrOutputParser()

    chain = prompt | llm | parser

    return chain