from python_code.parsers import *
from python_code.prompts import *
from python_code.memory import *
from python_code.utils import *
from python_code.keys import *
from python_code.test import *
from flask_socketio import emit
from langchain_openai import ChatOpenAI,OpenAI
import faiss
from pathlib import Path
import subprocess
import time



class function_agent:
    def __init__(self,prompt,model,parser):
        self.agent = prompt|model|parser
    def get_result(self,*args, **kwargs):
        agent_response = self.agent.invoke(kwargs)
        # print('==================================')
        # print(agent_response)
        # print('==================================')
        return agent_response
    
class aiagent:
    def __init__(self,name):
        self.history = []
        self.gen_code_agent = function_agent(cad_code_prompt,llm_model('gpt4o'),python_code_parser)
        self.ebs = np.zeros((0, 256), dtype='float32')
        self.infos = []
        directory = Path('data') 
        for pkl_file in directory.rglob('*.pkl'):
            with open(pkl_file, 'rb') as file:
                info = pickle.load(file)
                print(info['path'])
                print(type(info['embedding']))
                self.ebs = np.concatenate((self.ebs,info['embedding'].reshape(1, -1)),axis=0)
                self.infos.append(info)
        
        self.faissindex = faiss.IndexFlatL2(256)    
        self.faissindex .add(self.ebs)
            # print(pkl_file)

    
    def chat(self,message):
        # relevant_memory,history = self.memory.get_memory('User: '+message)
        # print(relevant_memory,history)
        # response = self.get_result(memory = relevant_memory,history = history)

        # new_message = {"type": "info", "content": 'Change to weld_sim_agent'}
        # self.socketio.emit('new_message',new_message)
        eb = get_embedding(texts = message)
        distances, indices = self.faissindex.search(eb, 1)
        print(distances, indices[0][0])

        info = self.infos[indices[0][0]]
        print(info['path'])
        # new_message = {"type": "response", "content": message}
        # self.socketio.emit('new_message',new_message)
        try:
            message_plan = {"type":"plan","content":info['plan']}
            self.socketio.emit('plan_message',message_plan)

            new_message = {"type": "info", "content": 'Plan Retrieved'}
            self.socketio.emit('new_message',new_message)

            new_code = self.gen_code_agent.get_result(code = info['code'],description = info['description'], problem = message)
            message_code = {"type":"code","content":new_code}
            self.socketio.emit('code_message',message_code)

            new_message = {"type": "info", "content": 'Code genrated'}
            self.socketio.emit('new_message',new_message)

            with open('code.py','w') as fout:
                fout.write(new_code)
            if os.path.exists('output.stl'):
                os.remove('output.stl')
            if os.path.exists('output.dxf'):
                os.remove('output.dxf')
            if os.path.exists('output.FCStd'):
                os.remove('output.FCStd')

            result = subprocess.run(["freecadcmd", f'code.py'], capture_output=True, text=True)
            time.sleep(1)
            print(result)


            time_str = time.strftime("%Y%m%d%H%M%S")
            save_sketch_fig('output.dxf',f'static/imgs/sketch{time_str}.png')


            self.socketio.emit('sketch_message', {'url': f'static/imgs/sketch{time_str}.png'})

            new_message = {"type": "info", "content": 'sketch genrated'}
            self.socketio.emit('new_message',new_message)

            save_stl_fig('output.stl',f'static/imgs/multiview{time_str}.png')


            self.socketio.emit('multiview_message', {'url': f'static/imgs/multiview{time_str}.png'})

            imgs_message = {"type": "imgs", "content": 'multi view imgs genrated'}
            self.socketio.emit('imgs_message',imgs_message)

            

            new_message = {"type": "info", "content": 'multi view imgs genrated'}
            self.socketio.emit('new_message',new_message)
        except Exception as e:
            new_message = {"type": "info", "content": 'generation failed.'+str(e)}
            self.socketio.emit('new_message',new_message)




        # if not self.cheat_flag:
        #     try:
        #         response = self.memory.gen_path('User: '+message)
        #     except:
        #         response = self.memory.gen_path('User: '+message)
        #     return response
        # else:
        #     try:
        #         response =self.memory.gen_path_2('User: '+message, weld_get_result(message))
        #     except:
        #         response = weld_get_result(message)

        #     print('1111')
        #     new_message = {"type": "response", "content": response['content'] , "file_url": response['file_url'] , "file_name": response['file_name'] , "image": response['image']}
        #     print('222')
        #     self.socketio.emit('new_message',new_message)
        #     print('333')
        #     if response['content'] == 'Begin simulate. This will take a few minutes.':
        #         time.sleep(10)
        #         new_message = {"type": "response", "content": 'Simulation Result' ,'image':'/static/imgs/deformed_shape_animation.gif','file_url':'/static/files/Job-1.odb','file_name':'Job-1.odb'}
        #         self.socketio.emit('new_message',new_message)
        #         self.cheat_flag = False
        #         new_message = {"type": "info", "content": 'Change to general agent'}
        #         self.socketio.emit('new_message',new_message)
                    


        #     return None
    


        




        