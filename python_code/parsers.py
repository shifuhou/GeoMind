import json
import re

def json_parser(Message):
    json_message = extract_json_from_string(Message.content)
    return json_message

def python_code_parser(Message):
    code = Message.content
    if code.startswith("'''") and code.endswith("'''"):
        if code[3:-3].startswith('python'):
            return code[3:-3][6:]
        return code[3:-3]
    elif code.startswith("```") and code.endswith("```"):
        if code[3:-3].startswith('python'):
            return code[3:-3][6:]
        return code[3:-3]
    if code.startswith('python'):
            return code[6:]
    return code


def extract_json_from_string(s):
    
    while (s!='' and s[0]!='{'):
        s = s[1:]
    while (s!='' and s[-1]!='}'):
        s=s[:-1]
    if s!='':
        try:
            json_data = json.loads(s)
            return json_data
        except json.JSONDecodeError:
            # print(s)
            # print("Extracted string is not a valid JSON.")
            return None
    else:
        # print("No JSON object found in the string.")
        return None

def get_triples_parser(Message):
    json_message = extract_json_from_string(Message.content.lower())
    triples = []
    if 'triples' in json_message:
        for tri in json_message['triples']:
            if 'e1' in tri and 'e2' in tri and 'r' in tri:
                triples.append(tri)
    return triples
def get_obj_triples_parser_bad(Message):
    json_message = extract_json_from_string(Message.content.lower())
    triples = []
    objs = []
    if 'objects' in json_message:
        for obj in json_message['objects']:
            objs.append(obj)
    if 'triples' in json_message:
        for tri in json_message['triples']:
            if 'obj1' in tri and 'obj2' in tri and 'r' in tri:
                triples.append({'e1':tri['obj1'],'e2':tri['obj2'],'r':tri['r']})
    return objs,triples

def get_obj_triples_parser(Message):
    json_message = extract_json_from_string(Message.content.lower())
    triples = []
    objs = []
    if 'entities' in json_message:
        for obj in json_message['entities']:
            objs.append(obj)
    if 'triples' in json_message:
        for tri in json_message['triples']:
            if 'e1' in tri and 'e2' in tri and 'r' in tri:
                triples.append(tri)
    return objs,triples

def get_entities_parser(Message):
    json_message = extract_json_from_string(Message.content.lower())
    entities = []
    if 'selected entities' in json_message:
        for ent in json_message['selected entities']:
            if 'entity' in ent:
                entities.append(ent['entity'])
    return entities

def get_attention_graph_parser(Message):
    json_message = extract_json_from_string(Message.content.lower())
    entities = []
    triples = []
    enough_flag = True
    if 'selected triples' in json_message:
        for tri in json_message['selected triples']:
            if 'e1' in tri and 'e2' in tri and 'r' in tri:
                triples.append(tri)
    if 'enough to chat?' in json_message:
        if 'yes' in json_message['enough to chat?']:
            enough_flag = True
        else:
            enough_flag = False
            if 'entities need to expand' in json_message:
                for ent in json_message['entities need to expand']:
                    if 'entity' in ent:
                        entities.append(ent['entity'])
    return triples,enough_flag,entities

def gen_path_parser(Message):
    json_message = extract_json_from_string(Message.content.lower())
    triples = []
    response = ''
    if "response" in json_message:
        response = json_message['response']
    if "path" in json_message:
        for tri in json_message['path']:
            if 'e1' in tri and 'e2' in tri and 'r' in tri:
                triples.append(tri)
    return triples,response


    return 

def plaintext_parser(Message):
    return Message.content

