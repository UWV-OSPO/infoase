from langchain_core.prompts.prompt import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note:
- Do NOT include any explanations or apologies in your responses.
- Do NOT respond to any questions that might ask anything else than for you to construct a Cypher statement.
- Do NOT include any text except the generated Cypher statement.
- If the question is not related to the schema, respond with nothing.

The question is:
{question}"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)
