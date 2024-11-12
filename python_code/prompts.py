from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate


cad_code_prompt = PromptTemplate.from_template(
    '''
    {code}
    The code above is for your reference. It is FreeCAD code used to generate {description}.
    My requirement is: {problem}
    Please help me write the corresponding FreeCAD code.
    Please reply me only with FreeCAD python code. Do not reply with anything else.
    Note that the name of output file must be "output"
    '''
)





sentence2triples_prompt_old = PromptTemplate.from_template(
    # Task: convert the sentence above into multiple triples.
    
    '''
    {sentence}
    Task: Please convert the main idea of this sentence into multiple triples. 
    That is, entity-relation-entity. I need to add these triplets to the Knowledge graph.
    Please note that entities need to be as concise as possible. An object is best.
    Using JSON format to answer. Do not output anything else except json.
    Output Format:
    {{
    "triples":[{{
        "e1":"<fill>",
        "r":"<fill>",
        "e2":"<fill>",
        }},
    ...
    ]
    }}
    '''
)
sentence2triples_prompt = PromptTemplate.from_template(
    
    '''
    {sentence}
    Task: Please convert the main idea of this sentence into multiple triples. 
    That is, entity-relation-entity. I need to add these triplets to the Knowledge graph.
    Please note that entities need to be as concise as possible. An object is best.
    after that, for each entity, tell me it is a concept or instance, it type, and all attributes of this entity in this sentence.
    Using JSON format to answer. Do not output anything else except json.
    Output Format:
    {{
    "triples":[{{
        "e1":"<fill>",
        "r":"<fill>",
        "e2":"<fill>",
        }},
    ...
    ],
    "entities":[{{
        "name":"<fill>",
        "type":"<fill>",
        "isconcept":"<concept/instance>"
        "attributes":["<fill>",...]
    }},
    ...
    ]
    }}
    '''
)
sentence2triples_prompt_bad = PromptTemplate.from_template(
    # Task: convert the sentence above into multiple triples.
    '''
    {sentence}
    Please extract the objects and the relations between objects in the above sentence.
    First, list the objects in the sentence.
    For each object,  list all attributes of this object in this sentence.
    Then list the relations between objects as triples. That is object-relation-object.
    Note that the object in triples must be the object listed above in the first step.

    Using JSON format to answer. Do not output anything else except json.
    Output Format:
    {{
    "objects":[{{
        "name":"<fill>",
        "type":"<fill>",
        "concept?":"<concept/instance>"
        "attributes":["<fill>",...]
    }},
    ...
    ],
    "triples":[{{
        "obj1":"<fill>",
        "r":"<fill>",
        "obj2":"<fill>",
        }},
    ...
    ]
    }}
    '''
)
attention_graph_prompt = PromptTemplate.from_template(
    '''
    These triples are the relevant information in ai-agent memory based on knowledge graph:
    {memory}
    These triples are expanded by following attention entities:
    {attention_entities}
    Task 1: Which of the triples above will be helpful for the chat below?
    {history}
    Task 2: do you think the triplets you selected are enough to continue the chat?
    If not, which entities not in attention entities do you think can be expanded to obtain valuable information?
    Using JSON format to answer. Do not output anything else except json.
    Output Format:
    {{
    "selected triples":[{{
        "e1":"<fill>",
        "r":"<fill>",
        "e2":"<fill>,
        }},
    ...
    ],
    "enough to chat?":<Yes/No>,
    "entities need to expand":[{{
        "entity":<fill>
    }},
    ...
    ]
    }}
    Note: "entities need to expand" must in the triples you selected and can not in attention entities i gave you.
    '''
)
attention_entities_prompt = PromptTemplate.from_template(
    '''
    {history}
    Based on the above chat history, which of the following entities do you think are the focus of the conversation and are likely to be involved in the next conversation.
    {attention_entities}
    Using JSON format to answer. Do not output anything else except json.
    Output Format:
    {{
    "selected entities":[{{
        "entity":<fill>
    }},
    ...
    ]
    }}
    '''
)
speak_prompt = PromptTemplate.from_template(
    '''
    This is the relevant information in ai-agent memory:
    {memory}
    This is ai-agent latest chat history:
    {history}
    Please output what ai-agent should say next. Don't make it too long, 1-3 sentences is enough.
    '''
)
gen_path_prompt = PromptTemplate.from_template(
    '''
    This is the relevant information in ai-agent memory based on knowdege graph:
    {memory}
    This is latest chat history:
    {history}
    Please provide the response the AI agent should give. And base on what you said generate a path on the Knowdege graph i give you.
    Note:
    If the entity has appeared in the Knowledge graph I gave you, please use the same entity. 
    If you must add a new entity, that entity need to be as concise as possible. An object is best.
    Using JSON format to answer. Do not output anything else except json.
    {{
    "Response":<1-2 sentences>,
    "Path":[{{
        "e1":"<fill>",
        "r":"<fill>",
        "e2":"<fill>,
        }},
    ...
    ]
    }}
    '''
)

def customize_prompt(prompt_str):
    return PromptTemplate.from_template(prompt_str)

def vision_prompt(prompt_str):
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        template=[
            {"type": "text", "text": prompt_str},
            {"type": "image_url", "image_url": "{encoded_image}"},
        ]
    )
    return human_message_prompt