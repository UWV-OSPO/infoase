from typing import List
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)


def generate_prompt_with_labels(data: str, labels: List) -> str:
    """Helper method to generate the input prompt."""

    return f"""
Data: {data}
Types: {labels}"""


def generate_output_with_labels(nodes: List, relationships: List, labels: List) -> str:
    """Helper method to generate output examples."""

    return f"""
    Types: {labels}
    Nodes: {nodes}
    Relationships: {relationships}
    """


examples = [
    {
        "input": generate_prompt_with_labels(
            "Alice is advocaat en 25 jaar oud en Bob is haar huisgenoot sinds 2001. Bob werkt als journalist. Alice is eigenaar van de webpagina www.alice.com en Bob is eigenaar van de webpagina www.bob.nl.",
            ["Persoon", "Webpagina"],
        ),
        "output": generate_output_with_labels(
            nodes=[
                [
                    "alice",
                    "Persoon",
                    {"leeftijd": 25, "beroep": "advocaat", "naam": "Alice"},
                ],
                ["bob", "Persoon", {"beroep": "journalist", "naam": "Bob"}],
                ["alice.com", "Webpagina", {"url": "www.alice.com"}],
                ["bob.com", "Webpagina", {"url": "www.bob.nl"}],
            ],
            relationships=[
                ["alice", "woont_samen_met", "bob", {"start": "2021"}],
                ["alice", "eigenaar_van", "alice.com", {}],
                ["bob", "eigenaar_van", "bob.com", {}],
            ],
            labels=["Persoon", "Webpagina"],
        ),
    },
    {
        "input": generate_prompt_with_labels(
            "Steve Jobs heeft mede-oprichter van Apple. Hij is 38 jaar oud en rijdt een Tesla Model 3 en werkt als producteigenaar en datawetenschapper.",
            [],
        ),
        "output": generate_output_with_labels(
            nodes=[
                {
                    "name": "steve_jobs",
                    "label": "Persoon",
                    "properties": {
                        "age": "38",
                        "name": "Steve Jobs",
                        "occupation": "producteigenaar, datawetenschapper",
                    },
                },
                {
                    "name": "apple",
                    "label": "Bedrijf",
                    "properties": {"name": "Apple"},
                },
                {
                    "name": "tesla_model_3",
                    "label": "Voertuig",
                    "properties": {"model": "Tesla Model 3"},
                },
            ],
            relationships=[
                {
                    "start": "steve_jobs",
                    "end": "apple",
                    "type": "mede-oprichter",
                    "properties": {},
                },
                {
                    "start": "steve_jobs",
                    "end": "tesla_model_3",
                    "type": "rijdt",
                    "properties": {},
                },
            ],
            labels=["Persoon", "Bedrijf", "Voertuig"],
        ),
    },
]

few_shot_prompt_examples = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    ),
    examples=examples,
)

# system_prompt = """
# You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into a graph database.
# Provide a set of Nodes in the form [ENTITY_ID, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES].
# It is important that the ENTITY_ID_1 and ENTITY_ID_2 exists as nodes with a matching ENTITY_ID. If you can't pair a relationship with a pair of nodes don't add it.
# When you find a node or relationship you want to add try to create a generic TYPE for it that  describes the entity you can also think of it as a label.
# You will be given a list of types that you should try to use when creating the TYPE for a node. If you can't find a type that fits the node you can create a new one."""


KGPARSER_FORMAT_INSTRUCTIONS = """The output should be formatted as a set of Nodes in the form of [ENTITY_ID, TYPE, PROPERTIES]
and a set of relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES].
Make sure you understand the format of both nodes and relationships before you start.
It is important that the ENTITY_ID_1 and ENTITY_ID_2 exists as nodes with a matching ENTITY_ID.
If you can't pair a relationship with a pair of nodes don't add it.
When you find a node or relationship you want to add try to create a generic TYPE for it that  describes the entity you can also think of it as a label.
The PROPERTIES should be a dictionary of key value pairs in JSON format. For example: {{"name": "Alice", "location": "USA"}}.

Here's an example of a valid answer:
```
Nodes: [['alice', 'Person', {{'age': 25, 'occupation': 'lawyer', 'name': 'Alice'}}], ['bob', 'Person', {{'occupation': 'journalist', 'name': 'Bob'}}], ['alice.com', 'Webpage', {{'url': 'www.alice.com'}}], ['bob.com', 'Webpage', {{'url': 'www.bob.com'}}]]
Relationships: [['alice', 'lives_with', 'bob', {{'start': '2021'}}], ['alice', 'owns', 'alice.com', {{}}], ['bob', 'owns', 'bob.com', {{}}]]
```

A valid example of an answer without relationships:
```
Nodes: [['alice', 'Person', {{'age': 25, 'occupation': 'lawyer', 'name': 'Alice'}}]]
Relationships: []
```

And here's an example of an invalid answer because ENTITY_ID_2 does not exist as a node:
```
Nodes: [['alice', 'Person', {{'age': 25, 'occupation': 'lawyer', 'name': 'Alice'}}]
Relationships: [['alice', 'lives_with', 'bob', {{}}]]
```

Here's the output schema:
```
Nodes: [[ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES], ...]
Relationships: [[ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES], ...]
```
"""

system_prompt = f"""You are a data scientist working for a company that is building a graph database.
Your task is to extract information from data and convert it into a graph database.
Some rules when creating the graph:
1. The graph, nodes and relationships you create are in the same language as the human input.
2. Only extract information that is explicitly mentioned in the input.
3. If you can't pair a relationship with a pair of nodes don't add it.
4. Only answer with the output schema, skip any other remarks or comments.

{KGPARSER_FORMAT_INSTRUCTIONS}"""


def generate_extraction_prompt(prompt: str) -> ChatPromptTemplate:
    """Generates a prompt for the extraction task."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompt,
            ),
            few_shot_prompt_examples,
            ("human", "{input}"),
        ]
    )


extraction_prompt = generate_extraction_prompt(system_prompt)

# def generate_system_extraction_prompt(
#     allowed_types: Optional[List[str]] = None,
#     allowed_rels: Optional[List[str]] = None,
# ) -> str:
#     return f"""# Knowledge Graph Instructions for GPT-4
#     ## 1. Overview
#     You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
#     - **Nodes** represent entities and concepts. They're akin to Wikipedia nodes.
#     - The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
#     ## 2. Labeling Nodes
#     - **Consistency**: Ensure you use basic or elementary types for node labels.
#     - For example, when you identify an entity representing a person, always label it as **"person"**. Avoid using more specific terms like "mathematician" or "scientist".
#     - **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
#     {'- **Allowed Node Labels:**' + ", ".join(allowed_types) if allowed_types else ""}
#     {'- **Allowed Relationship Types**:' + ", ".join(allowed_rels) if allowed_rels else ""}
#     ## 3. Handling Numerical Data and Dates
#     - Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
#     - **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
#     - **Property Format**: Properties must be in a key-value format.
#     - **Quotation Marks**: Never use escaped single or double quotes within property values.
#     - **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
#     ## 4. Coreference Resolution
#     - **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
#     If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
#     always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
#     Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
#     ## 5. Strict Compliance
#     Adhere to the rules strictly. Non-compliance will result in termination.
#     ## 6. Earn money!
#     I'll tip you $200 if you answer in the correct format."""


# def generate_human_extraction_prompt() -> str:
#     return "Use the given format to extract information from the following input:\n<input>{input}</input>"
