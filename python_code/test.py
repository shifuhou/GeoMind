
def weld_get_result(message):
    dic={'I want to simulate the welding of two iron plates. The sizes of the two iron plates are both 20*10*2':
         {'content':'Step 0: Please tell me your arc welding voltage, current and welding speed.','image':None,'file_url':None,'file_name':None},
         'arc welding voltage 15. current 80. speed 5.0':
         {'content':'Step 1: Could you provide the shapes and sizes of the parts you need for welding simulation?','image':None,'file_url':None,'file_name':None},
         'The two iron plates i metioned before':
         {'content':'Step 2: Can you tell me the materials used for the parts you welded?','image':None,'file_url':None,'file_name':None},
         'SUS301 Stainless steel':
         {'content':'{ "Name": "SUS301 Stainless Steel", "Specific heat": "500 J/kg\u00b7K", "Density": "7900 kg/m\u00b3", "Conductivity": "16 W/m\u00b7K" } Is this a thermal property of the material you are using? ','image':None,'file_url':None,'file_name':None},
         'yes':
         {'content':'Step 3: This step involves the Assembly Instance; please describe how to arrange the parts.','image':None,'file_url':None,'file_name':None},
         'I want the two iron plates to be horizontal and have their sides joined together to form a 40*10*2 iron plate. The stitching seam is on the x-axis':
         {'content':'Does the one shown in the figure meet your assembly requirements?','image':'/static/imgs/model_screenshot.png','file_url':None,'file_name':None},
         'Yes':
         {'content':'Begin simulate. This will take a few minutes.','image':None,'file_url':None,'file_name':None}

         }
    return dic[message] 