from langchain_core.prompts.prompt import PromptTemplate


CONTEXTUALIZE_QUESTION_SYSTEM_TEMPLATE = """ \
Given a chat history and the latest user question which might reference context in the chat history, 
formulate a standalone question which can be understood without the chat history. 

## Rules
- Do NOT answer the question, just reformulate it if needed and otherwise return it as is. \
- Do NOT reformulate the question if not needed.
- Translate the question to English.

I'll tip you $200 if you follow these rules correctly.

## Chat history
{chat_history}

## Examples
```
Chat history:
Human: Wie is Bob?
AI: Bob is een man die in Amsterdam woont.

Question to reformulate to a standalone question:
Heeft hij familie?

Your answer:
Does Bob have any family?
```

```
Chat history:


Question to reformulate to a standalone question:
Wie is Bob?

Your answer:
Who is Bob?
```


```
Chat history:
Human: Alice en Bob zijn vrienden.
AI: Fijn voor ze.

Question to reformulate to a standalone question:
Weet je of Carol ook vrienden is met Alice en Bob?

Your answer:
Do you know if Carol is friends with Alice and Bob?
```

## Question to reformulate
Question to reformulate to a standalone question:
{question}
"""

CONTEXTUALIZE_QUESTION_GENERATION_PROMPT = PromptTemplate(
    input_variables=["chat_history", "question"],
    template=CONTEXTUALIZE_QUESTION_SYSTEM_TEMPLATE,
)

# CONTEXTUALIZE_QUESTION_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("human", "{question}"),
#     ]
# )

# CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
# Instructions:
# Use only the provided relationship types and properties in the schema.
# Do not use any other relationship types or properties that are not provided.
# Schema:
# {schema}
# Note:
# - Do NOT include any explanations or apologies in your responses.
# - Do NOT respond to any questions that might ask anything else than for you to construct a Cypher statement.
# - Do NOT include any text except the generated Cypher statement.
# - If the question is not related to the schema, respond with nothing.

# The question is:
# {question}"""

# CYPHER_GENERATION_PROMPT = PromptTemplate(
#     input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
# )
