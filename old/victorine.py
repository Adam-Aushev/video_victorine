import os
import platform
from gtts import gTTS
# from playsound import playsound 
import subprocess
from textwrap import wrap
from colorama import init, Fore, Back, Style

def colorize(numb, text):
    colors = [Fore.BLUE, Fore.GREEN, Fore.MAGENTA, Fore.RED, Fore.YELLOW, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX]
    return f'{colors[numb]}{text}{Fore.RESET}'

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


def text_slice(text, width=20):
    end_text  = ''
    for line in wrap(text, width):
        end_text += '{0:^{1}}'.format(line, width) + '\n'
        
    return end_text



def draw_text(text, x_pos, y_pos, fontsize, fade_in, fade_out):
    if platform.system() == "Windows":
        font_path = "'C\\:/Windows/fonts/consola.ttf'"
    else:
        font_path =  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        
    if '.txt' in text:
        text = f"textfile='{text}'"
    else:
        text = f"text='{text}'"


    fade = f"alpha='if(lt(t,{fade_in}),0,if(lt(t,{fade_in+1}),(t-{fade_in})/1,if(lt(t,{fade_out+fade_in-1}),1,if(lt(t,{fade_out+fade_in}),(1-(t-{fade_out+fade_in-1}))/1,0))))'"
    code = f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:{text}: x={x_pos}:y={y_pos}:line_spacing=10: fontsize={fontsize}:{fade},"
    return code



def made_victorine(block, delims='.'):
    if platform.system() == "Windows":
        font_path = "'C\\:/Windows/fonts/consola.ttf'"
    else:
        font_path =  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

    durations = {}
    input_file = "victorine/background.mp4"
    path = 'victorine/'
    QA_name_list = [path + 'quest.mp3', path + 'answer_1.mp3', path + 'answer_2.mp3', path + 'answer_3.mp3', path + 'answer_4.mp3',  path + 'explain.mp3']
    textfile = 'victorine/qwest_file.txt'
    explain_file = 'victorine/explain_file.txt'
    audio_times = []
    block = block.strip().upper()
    block = block.split(delims)
    explain = block[-1].strip()
    print(block[0])
    right_answer = int(block[-2].strip())
    right_answer_time = get_dur(path+'countdown.mp3')
    right_answer_y = f'((main_h/10.4  * {right_answer})+(main_h/8*4.54)) - (overlay_h/2)'

    inputs_list = []
    
    with open (f'{path}qwest_file.txt', 'w+', encoding='utf-8') as quest_file, open (f'{path}explain_file.txt', 'w+', encoding='utf-8') as explain_text_file:
        quest_file.write(text_slice(block[0]))   
        explain_text_file.write(text_slice(explain))   
    aud_times = [get_dur(path + 'quest.mp3'), get_dur(path + 'answer_1.mp3'), get_dur(path + 'answer_2.mp3'), get_dur(path + 'answer_3.mp3'), get_dur(path + 'answer_4.mp3'), get_dur(path + 'explain.mp3')]
    first_stage_time = sum(aud_times[:5]) + right_answer_time + aud_times[right_answer]
    
    inputs_list.append({'text':'qwest_file.txt', 'link':'quest.mp3', 'dur':aud_times[0], 'time_in':1, 'time_out':                     first_stage_time, 'pos_y':'((h/10.4  * 1 +(h/8*4.54)) - (text_h/2)' })
    inputs_list.append({'text':block[1],         'link':'answer_1.mp3', 'dur':aud_times[1], 'time_in':sum(aud_times[0:1]), 'time_out':first_stage_time, 'pos_y':'((h/10.4  * 1 +(h/8*4.54)) - (text_h/2)' })
    inputs_list.append({'text':block[2],         'link':'answer_2.mp3', 'dur':aud_times[2], 'time_in':sum(aud_times[0:2]), 'time_out':first_stage_time, 'pos_y':'((h/10.4  * 1 +(h/8*4.54)) - (text_h/2)' })
    inputs_list.append({'text':block[3],         'link':'answer_3.mp3', 'dur':aud_times[3], 'time_in':sum(aud_times[0:3]), 'time_out':first_stage_time, 'pos_y':'((h/10.4  * 1 +(h/8*4.54)) - (text_h/2)' })
    inputs_list.append({'text':block[4],         'link':'answer_4.mp3', 'dur':aud_times[4], 'time_in':sum(aud_times[0:4]), 'time_out':first_stage_time, 'pos_y':'((h/10.4  * 1 +(h/8*4.54)) - (text_h/2)' })
    inputs_list.append({'text':'explain_file.txt', 'link':'explain.mp3', 'dur':aud_times[5], 'time_in':first_stage_time,   'time_out':aud_times[5],      'pos_y':'((h/10.4  * 1 +(h/8*4.54)) - (text_h/2)' })

    for i in inputs_list:
        print(i)
    print(right_answer_time)
    input()    

    for made_aud in QA_name_list:
        get_aud(block[QA_name_list.index(made_aud)], made_aud)
        durations[made_aud[made_aud.rfind('/')+1:made_aud.rfind('.')]] = get_dur(made_aud)


    print(text_slice(block[0]))
    scale = [540, 960]
    fontsize = scale[1]/25
    quest_x = 'w/2-(text_w/2)'
    quest_y = f'h/3.3 - (text_h/2)' 
    explain_x = 'w/2-(text_w/2)'
    explain_y = f'h/2 - (text_h/2)' 
    print(block)
    
    name = ''.join(names for names in block[0] if names.isalpha())
    drawtext = ''
    #question = f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:text='{block[0]}':y={quest_y}: x={quest_x}: fontsize={fontsize}:{fade_quest}, "
    ''' if(lt(t,5),0,if(lt(t,6),(t-5)/1,if(lt(t,13),1,if(lt(t,14),(1-(t-13))/1,0)))) '''
          #f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:textfile='{textfile}':y={quest_y}: x={quest_x}:line_spacing=10: fontsize={fontsize}:{fade_quest}, "

    for each_input in inputs_list:
        print(each_input)
        drawtext += draw_text(each_input['text'], 'w/2-text_w/2', each_input['pos_y'], fontsize, each_input['time_in'], each_input['time_out'])       #f"drawtext=fontfile={font_path}:fontcolor=#FFFFFF:text='{line}':y={answer_y}: x={quest_x}: fontsize={fontsize}:{fade_answer},"

    input_links = ''
    for inp in inputs_list:
        input_links += f' -i {inp["link"]}'
    
    print(input_links)
    input()
    
    concat = f'[aud_0][aud_1][aud_2][aud_3][aud_4]concat=n=5:a=1:v=0[cat]'
    overlay = f"[6:0]scale=540:-2[tube],[quest][tube]overlay=x={right_answer_x}:y={right_answer_y}:enable='gte=(t,{intro_time+5})'[final]"
    background = f"[8:0][9:0]concat=n=2:v=1:a=0[interface], [0:0][interface]overlay,"
    filter_complex = f'-filter_complex "{background}scale={scale[0]}:{scale[1]},{question}{drawtext}{explain_draw.strip(",")}[quest],{overlay}, {adelay} {concat}, {timer}, {amix}"'
    code = f'fflite -hide_banner -v error  -t {intro_time + 20} -i {input_file} {input_audio_files} -i victorine/tube.png   -i victorine/countdown.mp3 -t {answer_time_in + 6.22 + get_dur(answer_aud[right_answer-1])} -i victorine/inteface.mov -ss 39 -i victorine/inteface.mov {filter_complex} -map "[final]" -map "[audio]" -y "victorine\\{name}.mp4"'
    os.system(code)
#    for a in code.split(','):
#        print(colorize(code.split(',').index(a),a))
    return f'victorine/{name}.mp4'

if __name__ == "__main__": 
    with open ('victorine/questions.txt', 'r', encoding='utf-8') as text_file:
        text_file = text_file.read()
    for block in text_file.split(';'):
        if block.strip():
            made_victorine(block, delims='\n')

#print(code)
    
# ffmpeg -i victorine/background.mp4 -vf "drawtext=textfile=victorine/qwest_file.txt:x=0:y=t*5" -y victorine/test.mp4 
