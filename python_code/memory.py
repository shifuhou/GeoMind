import networkx as nx
import pickle
import os
import shutil
import time
from flask_socketio import emit
from python_code.parsers import *
from python_code.prompts import *
from python_code.keys import *
from python_code.test import *


class function_agent:
    def __init__(self,prompt,model,parser):
        self.agent = prompt|model|parser
    def get_result(self,*args, **kwargs):
        agent_response = self.agent.invoke(kwargs)
        print('==================================')
        print(agent_response)
        print('==================================')
        return agent_response
class get_objects_agent:
    def __init__(self,prompt,model,parser):
        self.agent = prompt|model|parser
    def get_result(self,*args, **kwargs):
        objects,triples = self.agent.invoke(kwargs)
        return objects,triples
    
class thinking_on_graph_agent:
    def __init__(self,prompt,model,parser):
        self.agent = prompt|model|parser
    def get_result(self,*args, **kwargs):
        triples,enough_flag,entities = self.agent.invoke(kwargs)
        print('thinking_on_graph==================================')
        print(triples,enough_flag,entities)
        print('==================================================')
        return triples,enough_flag,entities
class gen_path_agent:
    def __init__(self,prompt,model,parser):
        self.agent = prompt|model|parser
    def get_result(self,*args, **kwargs):
        path,respone = self.agent.invoke(kwargs)
        print('genpath_on_graph==================================')
        print(path,respone)
        return path,respone


def convert_rela(relas):
    s = ''
    for r in relas:
        s+=str(r)+'\n'
    return s


class memory:
    def __init__(self,name) -> None:
        self.name = name
        # if os.path.exists(name):
        #     shutil.rmtree(name)
        if os.path.exists(name):
            with open(os.path.join(name,'memory.pkl'),'rb') as f:
                self.G = pickle.load(f)
            with open(os.path.join(name,'history.pkl'),'rb') as f:
                self.history = pickle.load(f)
            with open(os.path.join(name,'info.pkl'),'rb') as f:
                self.info = pickle.load(f)
            with open(os.path.join(name,'parameters.pkl'),'rb') as f:
                self.parameters = pickle.load(f)
        else:
            os.mkdir(name)
            self.G = nx.DiGraph()
            self.history = []
            self.info = {}
            self.info['time'] = 0
            self.info['attention_graph'] = nx.DiGraph()
            self.info['attention_entities'] = []
            self.info['current_triples'] = []
            self.info['attention_graph_updata_time'] = str(time.time())
            self.info['full_graph_updata_time'] = str(time.time())
            self.info['objects'] = {}
            self.parameters = {}
            self.parameters['max_history'] = 50
            self.parameters['max_expand_times'] = 2  
            
            self.save()
        self.sid =0       
        # self.to_triples_agent = function_agent(sentence2triples_prompt,llm_model('gpt4o'),get_triples_parser)
        self.to_triples_agent = get_objects_agent(sentence2triples_prompt,llm_model('gpt4o'),get_obj_triples_parser)
        self.get_attention_entities_agent = function_agent(attention_entities_prompt,llm_model('gpt4o'),get_entities_parser)
        self.get_attention_memory_graph_agent = thinking_on_graph_agent(attention_graph_prompt,llm_model('gpt4o'),get_attention_graph_parser)
        self.get_path_agent = gen_path_agent(gen_path_prompt,llm_model('gpt4o'),gen_path_parser)

    def save(self):
        with open(os.path.join(self.name,'memory.pkl'),'wb') as f:
            pickle.dump(self.G,f)
        with open(os.path.join(self.name,'history.pkl'),'wb') as f:
            pickle.dump(self.history,f)
        with open(os.path.join(self.name,'info.pkl'),'wb') as f:
            pickle.dump(self.info,f)
        with open(os.path.join(self.name,'parameters.pkl'),'wb') as f:
            pickle.dump(self.parameters,f)
        return
    
    
    def convert_graph_to_visjs(self,G,att_ents,path):
        nodes = []
        edges = []
        e_dict = {}
        n_dict = {}
        for tri in path:
            u = tri['e1']
            v = tri['e2']
            r = tri['r']
            e_dict [u+'-'+v] = r 
            n_dict [u] = 1
            n_dict [v] = 1
            
        for n in G.nodes():
            if str(n) in n_dict:
                try:
                    nodes.append({"id": str(n), "label": str(n), "info": self.info['objects'][str(n)], 'color': 'red' })
                except:
                    pass
            elif str(n) in att_ents:
                try:
                    nodes.append({"id": str(n), "label": str(n), "info": self.info['objects'][str(n)],'color': 'green' })
                except:
                    pass
            else:
                try:
                    nodes.append({"id": str(n), "label": str(n), "info": self.info['objects'][str(n)],'color': 'blue' })
                except:
                    pass
        # nodes = [{"id": str(n), "label": str(n)} for n in G.nodes()]

        for u, v in G.edges():
            if u+'-'+v in e_dict:
                try:
                    edges.append({"from": str(u), "to": str(v), "label": convert_rela(G[u][v].get("relation", {})), "arrows": "to",'color':'red'})
                except:
                    pass
            else:
                try:
                    edges.append({"from": str(u), "to": str(v), "label": convert_rela(G[u][v].get("relation", {})), "arrows": "to",'color':'gray'})
                except:
                    pass


        # edges = [{"from": str(u), "to": str(v), "label": convert_rela(G[u][v].get("relation", {})), "arrows": "to"} for u, v in G.edges()]
        return {"nodes": nodes, "edges": edges}

    def get_history_str(self):
        return '\n'.join(self.history)
    
    def get_entities_str(self,entities):
        return '\n'.join(entities)
    
    def get_triples_str(self,triples):
        triples_str = '' 
        for tri in triples:
            u = tri['e1']
            v = tri['e2']
            r = tri['r']
            triples_str += u+'-'+r+'-'+v+'\n'
        return triples_str


        
    
    
    def updata_edge(self,G,u,v,key,value):
        if not G.has_node(u):
            self.updata_node(G,u)
        if not G.has_node(v):
            self.updata_node(G,v)
        if G.has_edge(u,v):
            G[u][v]['relation'][key] = value
        else:
            G.add_edge(u,v,relation = {key:value})

        return
    def updata_node(self,G,node):
        if not G.has_node(node):
            if node in self.info['objects']:
                G.add_node(node, attributes = self.info['objects'][node])
            else:
                G.add_node(node, attributes = {'name':node,'type':'','concept?':'concept','attributes':[]})
        return 

    def renew_attention_entities(self):
        attention_entities = self.info['attention_entities']
        for tri in self.info['current_triples']:
            u = tri['e1']
            v = tri['e2']
            if u not in attention_entities:
                attention_entities.append(u)
            if v not in attention_entities:
                attention_entities.append(v)
        entities_str = '\n'.join(attention_entities)
        self.info['attention_entities'] = self.get_attention_entities_agent.get_result(history = self.get_history_str(), attention_entities = entities_str)
        return 
    
    def get_triples(self, message):
        objs,triples = self.to_triples_agent.get_result(sentence = message)
        for obj in objs:
            if obj['name'] not in self.info['objects']:
                self.info['objects'][obj['name']] = obj
        self.info['current_triples'] = triples
        return triples
    
    def get_related_triples(self,entities,not_entities):
        related_triples = []
        n_entities = not_entities
        for u in entities:
            if u in self.G and u not in n_entities:
                for node in list(self.G.successors(u)):
                    if node not in n_entities:
                        for rela in self.G[u][node]['relation']:
                            related_triples.append({'e1':u,'e2':node,'r':rela})
                for node in list(self.G.predecessors(u)):
                    if node not in n_entities:
                        for rela in self.G[node][u]['relation']:
                            related_triples.append({'e1':node,'e2':u,'r':rela})
            n_entities.append(u)
        return related_triples     
    
    
    
    def renew_attention_graph(self):
        k = 0
        related_triples = []
        self.info['attention_graph'] = nx.DiGraph()
        for ent in self.info['attention_entities']:
            self.updata_node(self.info['attention_graph'],ent)
        self.socketio.emit('partial_graph_data', self.convert_graph_to_visjs(self.info['attention_graph'],self.info['attention_entities'],[]))#,to = self.sid)

        while k<self.parameters['max_expand_times']:
            if k!= 0:
                related_triples = attention_triples + self.get_related_triples(entities_need_expand,self.info['attention_entities'])
                new_entities_flag = False
                for ent in entities_need_expand:
                    if ent not in self.info['attention_entities']:
                        self.info['attention_entities'].append(ent)
                        new_entities_flag =True
                if not new_entities_flag:
                    break
            else:
                related_triples = self.get_related_triples(self.info['attention_entities'],[])

            related_triples_str = self.get_triples_str(related_triples)
            attention_triples,enough_flag,entities_need_expand  = self.get_attention_memory_graph_agent.get_result(memory = related_triples_str,attention_entities =self.get_entities_str(self.info['attention_entities']),history = self.get_history_str())
            if enough_flag or len(entities_need_expand) == 0:
                break
            else:
                k+=1

                self.info['attention_graph'] = nx.DiGraph()
                for tri in attention_triples:
                    u = tri['e1']
                    v = tri['e2']
                    r = tri['r']
                    self.updata_edge(self.info['attention_graph'],u,v,r,self.info['time'])
                self.info['attention_graph_updata_time'] = str(time.time())
                self.socketio.emit('partial_graph_data', self.convert_graph_to_visjs(self.info['attention_graph'],self.info['attention_entities'],[]))#,to = self.sid)
                
        return attention_triples
    
    def get_attention_graph(self):
        return self.info['attention_graph']
    def get_full_graph(self):
        return self.G

        
    def gen_path(self,message):
        triples = self.get_triples(message)
        self.remember_triples(message,triples)
        self.renew_attention_entities()
        
        attention_triples= self.renew_attention_graph()

        path, response = self.get_path_agent.get_result(memory = self.get_triples_str(attention_triples),history = self.get_history_str())

        for tri in path:
            u = tri['e1']
            v = tri['e2']
            r = tri['r']
            self.updata_edge(self.info['attention_graph'],u,v,r,self.info['time'])

        self.socketio.emit('partial_graph_data', self.convert_graph_to_visjs(self.info['attention_graph'],self.info['attention_entities'],path))#,to = self.sid)

        self.remember(response,path)

        return response
    
    def gen_path_2(self,message,result):
        triples = self.get_triples(message)
        self.remember_triples(message,triples)
        self.renew_attention_entities()
        
        attention_triples= self.renew_attention_graph()
        self.socketio.emit('partial_graph_data', self.convert_graph_to_visjs(self.info['attention_graph'],self.info['attention_entities'],[]))
        return result



    def remember_triples(self,message,triples):
        for tri in triples:
            u = tri['e1']
            v = tri['e2']
            r = tri['r']
            self.updata_edge(self.G,u,v,r,self.info['time'])
        self.info['full_graph_updata_time'] = str(time.time())
        self.history.append(message)
        if len(self.history)>self.parameters['max_history']:
            self.history = self.history[len(self.history)-self.parameters['max_history']:]
        self.info['time'] +=1
        self.save()
        return
    

    def remember(self,message,path):
        self.remember_triples(message,path)
        # self.renew_attention_entities()
        return

    # def remember(self,message):
    #     triples = self.get_triples(message)
    #     self.remember_triples(message,triples)
    #     self.renew_attention_entities()
    #     return




