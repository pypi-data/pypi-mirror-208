import subprocess
import click

import requests
from .ChatGPT import Chatbot
import os
import sys
from rich.live import Live
from rich.markdown import Markdown
from .code_execution import *

sys.stdin.reconfigure(encoding='utf-8')

@click.command()
def hello():
    """Say hello"""
    click.echo('Hello, world!')

@click.group()
def dxr():
    """Figlu command line tool"""
    # 默认调用bash函数
    pass

def get_bash_scripts():
    url = 'http://39.101.69.111:4000/bash'
    r = requests.get(url)
    scripts = r.json()
    return scripts

def get_bash_script_dir(script):
    url = f'http://39.101.69.111:4000/bash/{script}'
    r = requests.get(url)
    scripts = r.json()
    return scripts

def get_bash_script(script, sub_script):
    url = f'http://39.101.69.111:4000/bash/{script}/{sub_script}'
    r = requests.get(url)
    script = r.text
    return script

def chatgpt_explanation(language, error_message, model, maxtoken):
    query = construct_query(language, error_message)
    base_url, api_key = get_api_key()
    chatbot = Chatbot(api_key=api_key, base_url=base_url, engine=model, max_tokens=maxtoken)
    res = chatbot.ask_stream(query)
    return res

def choose_script(scripts, step=1):
    script_index = 0
    while True:
        click.clear()
        click.echo('Select a script:')
        for i, script in enumerate(scripts):
            if i == script_index:
                click.echo(f'> {script}')
            else:
                click.echo(f'  {script}')
        key = click.getchar()
        # 上下键选择，左键返回，右键进入
        if key == '\r':
            return scripts[script_index], step + 1
        elif key == '\x1b[A':
            script_index = (script_index - 1) % len(scripts)
        elif key == '\x1b[B':
            script_index = (script_index + 1) % len(scripts)
        elif key == '\x1b[D':
            return None, step - 1
        elif key == '\x1b[C':
            return scripts[script_index], step + 1
            

@dxr.command()
def bash():
    """执行云端上的脚本"""
    import os
    # scripts = get_bash_scripts()
    # script = choose_script(scripts)
    # sub_scripts = get_bash_script_dir(script)
    # sub_script = choose_script(sub_scripts)
    # bash_script = get_bash_script(script, sub_script)
    # print("=" * 80)
    # click.echo(bash_script)
    # print("=" * 80)
    # click.echo('Run this script?')
    # if click.confirm('Continue?'):
    #     os.system(bash_script)
    step = 1
    while True:
        if step == 0:
            break
        if step == 1:
            scripts = get_bash_scripts()
            script, step = choose_script(scripts, step)
        elif step == 2:
            sub_scripts = get_bash_script_dir(script)
            sub_script, step = choose_script(sub_scripts, step)
        elif step == 3:
            bash_script = get_bash_script(script, sub_script)
            print("=" * 80)
            click.echo(bash_script)
            print("=" * 80)
            click.echo('Run this script?')
            if click.confirm('Continue?'):
                os.system(bash_script)
                break
            step = 2
    
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY", '')
    if api_key == '':
        url = f'http://39.101.69.111:4000/chat/get_api_key'
        r = requests.get(url)
        base_url_and_api_key = r.text
        base_url, api_key = base_url_and_api_key.split(',')
    return base_url, api_key  

@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
def chat(model, maxtoken):
    """Chat with GPT-3 or GPT-4"""
    base_url, api_key = get_api_key()
    bot = Chatbot(api_key=api_key, base_url=base_url, engine=model, max_tokens=maxtoken)
    while True:
        text = input("You: ")
        if text.strip() == "exit":
            break
        response = bot.ask_stream(text)
        md = Markdown("")
        with Live(md, auto_refresh=False) as live:
            tmp = ""
            for r in response:
                tmp += r
                md = Markdown(tmp)
                live.update(md, refresh=True)
                

@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
def git(model, maxtoken):
    """问问关于git的问题"""
    print("这是一个git命令行助手,你可以通过这个助手来学习git命令")
    # use openai to generate git scripts
    base_url, api_key = get_api_key()
    bot = Chatbot(api_key=api_key, base_url=base_url, system_prompt="""
    你是一个很好的git命令行助手，你可以帮助我更好的使用git, 
    根据我的问题,你可以给我提供一些git命令
    """, engine=model, max_tokens=maxtoken)
    while True:
        text = input("请输入你的问题: ")
        if text.strip() == "exit":
            break
        response = bot.ask_stream(text)
        print("=" * 80)
        tmp = ""
        for r in response:
            tmp += r
            print(r, end='', flush=True)
        print()
        print("=" * 80)
    
# dxr python test.py --model gpt-3.5-turbo --maxtoken 4096 
# 用来直接运行python脚本，并且获取运行时的错误输出，
# 将错误输出 发送给openai，让openai来帮助我们解决这个问题  
@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
@click.option("--binary", default="python", help="Specify which binary to use")
@click.argument('script', type=click.Path(exists=True))
def python(model, maxtoken, binary,  script):
    args = [binary, script]
    language = binary
    if not language:
        print_invalid_language_message()
        return
    error_message = execute_code(args, language)
    if not error_message:
        return
    with LoadingMessage():
        res = chatgpt_explanation(language, error_message, model, maxtoken)
    md = Markdown("")
    with Live(md, auto_refresh=True) as live:
        tmp = ""
        for r in res:
            tmp += r
            md = Markdown(tmp)
            live.update(md, refresh=True)
            
            
@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
@click.argument('script', type=click.Path(exists=True))
def python3(model, maxtoken, script):
    args = ['python3', script]
    language = get_language(args)
    print(language)
    if not language:
        print_invalid_language_message()
        return
    error_message = execute_code(args, language)
    if not error_message:
        return
    with LoadingMessage():
        res = chatgpt_explanation(language, error_message, model, maxtoken)
    md = Markdown("")
    with Live(md, auto_refresh=True) as live:
        tmp = ""
        for r in res:
            tmp += r
            md = Markdown(tmp)
            live.update(md, refresh=True)
            
            
            
@click.command()
@click.argument('args', nargs=-1)
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
@click.option("--lines", default=100, help="Number of lines before and after the error to capture as context")
def run(args, model, maxtoken, lines):
    """
    接收不固定参数的命令，并执行它们。如果发生错误，将捕获并显示错误输出及其上下文。
    """
    try:
        language = get_language(args)
        # 将参数元组转换为列表，并将其传递给subprocess.run函数
        result = subprocess.run(
            list(args), stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        # 找出可能涉及的文件
        source_files = [arg for arg in args if os.path.isfile(arg)]
        file_contents = []

        for file in source_files:
            # 检查文件字数是否超过2000
            num_chars = os.stat(file).st_size
            if num_chars <= 2000:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # 取前后各100行的代码
                # with open(file, 'r', encoding='utf-8') as f:
                #     head_lines = [next(f) for _ in range(lines)]
                # with open(file, 'r', encoding='utf-8') as f:
                #     tail_lines = f.readlines()[-lines:]
                with open(file, 'r', encoding='utf-8') as f:
                    head_lines = [next(f, '') for _ in range(lines)]
                with open(file, 'r', encoding='utf-8') as f:
                    tail_lines = [line for _, line in zip(range(lines), f.readlines())]
                    

                content = "".join(head_lines) + "\n...\n" + "".join(tail_lines)

            file_contents.append(content)

        # 获取错误输出
        error_output = e.stderr
        
        # 打印错误输出
        click.echo(error_output)

        # 将文件内容与错误输出合并
        total_input = f"Error Output:\n{error_output}\n\n"
        for i, content in enumerate(file_contents):
            total_input += f"File Content ({source_files[i]}):\n{content}\n\n"

        # 使用GPT模型处理整个输入
        with LoadingMessage():
            response = chatgpt_explanation(language, total_input, model, maxtoken)

        # 使用Rich库将结果显示为Markdown
        md = Markdown("")
        with Live(md, auto_refresh=True) as live:
            tmp = ""
            for r in response:
                tmp += r
                md = Markdown(tmp)
                live.update(md, refresh=True)
    else:
        click.echo(result.stdout)
    
        
    
    

     
    


def main():
    print("Hello world!")

dxr.add_command(hello)
dxr.add_command(bash)
dxr.add_command(chat)
dxr.add_command(git)
dxr.add_command(python)
dxr.add_command(python3)
dxr.add_command(run)

if __name__ == '__main__':
    dxr()
