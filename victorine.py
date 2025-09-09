import os
import platform
from gtts import gTTS
import subprocess
from textwrap import wrap



def get_dur(link):
    cmd = ["ffprobe", "-i", link, "-show_entries", "format=duration", "-v", "quiet",  "-of", "csv=p=0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    for line in process.stdout:
        digit = line.strip()
    return float(digit)

def get_aud(text, name):
    language = 'ru' 
    obj = gTTS(text=text, lang=language, slow=False) 
    obj.save(name)


def text_slice(text, width=20, max_line=7):
    end_text  = ''
    line_sise = 0
    for line in wrap(text, width):
        end_text += '{0:^{1}}'.format(line, width) + '\n'
    line_count = end_text.count('\n')
    if line_count > max_line:
        line_sise = (line_count - max_line) * 2
        width = width + ((line_count - max_line) * 1)
        end_text  = ''
        for line in wrap(text, width):
            end_text += '{0:^{1}}'.format(line, width) + '\n'   
    return {'end_text':end_text, 'line_sise':line_sise}

def get_fade(fadein, fadeout, fadetime=1):
    fade = f'if(lt(t,{fadein}),0,if(lt(t,{fadein+1}),(t-{fadein})/1,if(lt(t,{fadeout+fadein-1}),1,if(lt(t,{fadeout+fadein}),(1-(t-{fadeout+fadein-1}))/1,0))))'
    return fade

def draw_text(text, x_pos, y_pos, fontsize, fade_in, fade_out):
    text = text
    if platform.system() == "Windows":
        font_path = "'C\\:/Windows/fonts/consola.ttf'"
    else:
        font_path =  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    if '.txt' in text:
        text = f"textfile='{text}'"
    else:
        text = f"text='{text}'"
    fade = f"alpha='{get_fade(fade_in, fade_out)}'"
    code = f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:{text}: x={x_pos}:y={y_pos}:line_spacing=3: fontsize={fontsize}:{fade},"
    return code

def made_textfile(link, text, line_max):
    text_and_slice = text_slice(text, max_line=line_max)
    text = text_and_slice['end_text']
    line_sise = text_and_slice['line_sise']
    with open (link, 'w+', encoding='utf-8') as quest_file: 
        quest_file.write(text.rstrip())   
    return line_sise


def made_victorine(block, delims='.'):
    block = block.strip()#.upper()
    block = block.split(delims)
    for bl in block:
        block[block.index(bl)] = block[block.index(bl)].replace('%','\\%')
    name = ''.join(names for names in block[0] if names.isalpha())[:10]


    path = 'sources/'
    QA_name_list = [path + 'quest.mp3', path + 'answer_1.mp3', path + 'answer_2.mp3', path + 'answer_3.mp3', path + 'answer_4.mp3',  path + 'explain.mp3']
    aud_times = []
    explain = block[-1].strip()
    drawtext = ''
    right_answer = int(block[-2].strip())
    block.pop(-2)
    scale = [540, 960]
    fontsize = scale[1]/25

    inputs_list = []
    

    quest_size = scale[1] / (25 + made_textfile(f'sources/qwest_file.txt', block[0], line_max = 7))
    explain_size = scale[1] / (25 +made_textfile(f'sources/explain_file.txt', explain, line_max=20))
    answer_size = scale[1] / 25
    for made_aud in QA_name_list:
        get_aud(block[QA_name_list.index(made_aud)], made_aud)
        aud_times.append(get_dur(made_aud))
    aud_times[0] = aud_times[0]+1    
    aud_times[5] = aud_times[5]+2  

    
    first_stage_time = sum(aud_times[:5]) + 6.22 + aud_times[right_answer] 
    
    inputs_list.append({'text':'sources/qwest_file.txt',   'link':path + 'quest.mp3',    'dur':aud_times[0], 'time_in':1,                   'time_out':first_stage_time - 1, 'pos_y':'h/3.4 - (text_h/2)' , 'size':quest_size})
    inputs_list.append({'text':block[1],           'link':path + 'answer_1.mp3', 'dur':aud_times[1], 'time_in':sum(aud_times[0:1]), 'time_out':first_stage_time - sum(aud_times[0:1]), 'pos_y':'(h/10.4  * 0 + (h/8*4.54)) - (text_h/2)', 'size':answer_size })
    inputs_list.append({'text':block[2],           'link':path + 'answer_2.mp3', 'dur':aud_times[2], 'time_in':sum(aud_times[0:2]), 'time_out':first_stage_time - sum(aud_times[0:2]), 'pos_y':'(h/10.4  * 1 + (h/8*4.54)) - (text_h/2)', 'size':answer_size })
    inputs_list.append({'text':block[3],           'link':path + 'answer_3.mp3', 'dur':aud_times[3], 'time_in':sum(aud_times[0:3]), 'time_out':first_stage_time - sum(aud_times[0:3]), 'pos_y':'(h/10.4  * 2 + (h/8*4.54)) - (text_h/2)', 'size':answer_size })
    inputs_list.append({'text':block[4],           'link':path + 'answer_4.mp3', 'dur':aud_times[4], 'time_in':sum(aud_times[0:4]), 'time_out':first_stage_time - sum(aud_times[0:4]), 'pos_y':'(h/10.4  * 3 + (h/8*4.54)) - (text_h/2)', 'size':answer_size })
    inputs_list.append({'text':'sources/explain_file.txt', 'link':path + 'explain.mp3',  'dur':aud_times[5], 'time_in':first_stage_time+1,  'time_out':aud_times[5],                      'pos_y':'(h/2) - (text_h/2)',                      'size':explain_size })

    input_links = ''
    for inp in inputs_list:
        input_links += f' -i {inp["link"]}'
    input_links +=  ' -i sources/countdown.mp3 '
    input_links +=  ' -i sources/tube.png '
    input_links += f' -t {first_stage_time} -i sources/inteface.mov '
    input_links += f' -ss 39 -t {inputs_list[-1]["dur"]} -i sources/inteface.mov '
    input_links += f' -t  {first_stage_time + inputs_list[-1]["dur"]} -i sources/background.mp4 '
    



    pos_x = 'w/2-(text_w/2)'
    quest_y = f'h/3.3 - (text_h/2)' 
    explain_x = 'w/2-(text_w/2)'
    explain_y = f'h/2 - (text_h/2)' 
    

    for each_input in inputs_list:
        drawtext += draw_text(each_input['text'], pos_x, each_input['pos_y'], each_input['size'], each_input['time_in'], each_input['time_out'])     

    
    background = f"[8:0][9:0]concat=n=2:v=1:a=0[interface], [10:0][interface]overlay, scale={scale[0]}:{scale[1]},"
    overlay = f"[7:0]scale=540:-2[tube],[quest][tube]overlay=x=main_w/2-(overlay_w/2):y=(main_h/10.4*{right_answer-1}+ (main_h/8*4.54)) - (overlay_h/2):enable='if(lt(t,{first_stage_time-aud_times[right_answer]-1}),0,if(lt(t,{first_stage_time}),1,0))'[final]"
    concat = f'[0:a]adelay=1000|1000[quest],[5:a]adelay=2000|2000[exp],[quest][1:a][2:a][3:a][4:a][6:a][{right_answer}:a][exp]concat=n=8:a=1:v=0[audio]'
    filter_complex = f'-filter_complex "{background}{drawtext[:-1]}[quest],{overlay}, {concat}"'
    code = f'fflite -hide_banner -v error   {input_links}   {filter_complex} -map "[final]" -map "[audio]" -y "{name}.mp4"'
    os.system(code)
    return f'sources/{name}.mp4'



if __name__ == "__main__": 
    with open ('questions.txt', 'r', encoding='utf-8') as text_file:
        text_file = text_file.read()
    for block in text_file.split(';'):
        if block.strip():
            made_victorine(block, delims='\n')
# ffmpeg -i sources/background.mp4 -vf "drawtext=textfile=sources/qwest_file.txt:x=0:y=t*5" -y sources/test.mp4 
    #question = f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:text='{block[0]}':y={quest_y}: x={quest_x}: fontsize={fontsize}:{fade_quest}, "
    ''' if(lt(t,5),0,if(lt(t,6),(t-5)/1,if(lt(t,13),1,if(lt(t,14),(1-(t-13))/1,0)))) '''
          #f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:textfile='{textfile}':y={quest_y}: x={quest_x}:line_spacing=10: fontsize={fontsize}:{fade_quest}, "
