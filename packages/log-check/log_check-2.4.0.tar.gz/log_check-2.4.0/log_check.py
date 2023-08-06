# -*- coding: UTF-8 -*-

import sys, re, os
from colorama import Fore
from colorama import Style
from rich.progress import Progress

help = """
Usage:
    logc [option] [paths|files]

Option:
    -S, -show_ok                show ok file.
    -H, -hide_ok                hide ok file, progress bar instead.
    -h, -help                   just show this.

Example:
    logc                        check all .cpp, .h, .hpp, .mm in `./`
    logc ../crcp                check all .cpp, .h, .hpp, .mm in `../crcp`
    logc main.cpp               check main.cpp
"""

g_unknow_logs = []

def getfiles(current_dir, types, files = []):
    try:
        dir_list = os.listdir(current_dir)
    except PermissionError:
        return None
    for dir in dir_list:
        path = os.path.join(current_dir, dir)
        if os.path.isdir(path):
            getfiles(path, types, files)
        else:
            obs_path = current_dir + '/' + dir
            for type in types:
                if obs_path.endswith(type):
                    files.append(obs_path.replace('\\', '/'))
    return files


def parse(text, start_pos):
    first_quote_idx = text.find('\"', start_pos)
    in_dou_quote = False
    fmt_end_pos = None
    for i in range(first_quote_idx, len(text)):
        c = text[i] 
        if c == '\"':
            in_dou_quote = not in_dou_quote
        if not in_dou_quote and (c==',' or c==')'):
            fmt_end_pos = i
            break
    if fmt_end_pos == None:
        raise Exception('fmt_end_pos is None')
    place_hoder_num = len( re.findall(r'({.*?})', text[start_pos:fmt_end_pos]) )

    i = fmt_end_pos
    arg_num = 0
    left_braces = {'(', '[', '{'}
    right_braces = {')', ']', '}'}
    in_dou_quote = False
    in_sin_quote = False
    deep = 1
    while deep!=0 and i<len(text):
        c = text[i]
        if c == '"':
            in_dou_quote = not in_dou_quote
        if c == "'":
            in_sin_quote = not in_sin_quote
        if not in_dou_quote and not in_sin_quote:
            if c in left_braces:
                deep = deep+1
            if c in right_braces:
                deep = deep-1
        if c == ',' and deep == 1 and not in_dou_quote and not in_sin_quote:
            arg_num = arg_num+1
        i = i+1
    end_pos = i
    if deep != 0:
        raise Exception('deep({}) error'.format(deep))

    statement = text[start_pos:end_pos]
    return ((place_hoder_num, arg_num, statement))

bad_log_fmt = """
{} [line {}] : {{}} = {}, argc = {}
"""+Fore.RED+"""{}
"""+Style.RESET_ALL

def check(files, show_ok):
    if len(files) == 0:
        return
    max_file_name_len = max([len(file_name) for file_name in files])

    bad_files = []

    if show_ok == None:
        show_ok = len(files) <= 128

    with Progress() as progress:
        task = progress.add_task("[red]checking...", total=len(files))

        for source_file in files:
            try:
                text = open(source_file, encoding='utf-8').read().replace('\\\"', '').replace('\\\'', '')
            except UnicodeDecodeError:
                print('\n can not read file `{}`'.format(source_file))
                continue
            iter = re.finditer('(LOG[T|D|I|W|E|C]\(|fmt::format\()', text, re.MULTILINE)

            bad_fmt = []
            log_len = 0
            for item in iter:
                log_len = log_len+1
                key_word = item.group()
                location = len(re.findall('\n', text[:item.start()])) + 1
                try:
                    place_hoder_num, arg_num, statement = parse(text, item.start())
                except Exception as e:
                    g_unknow_logs.append({'file':source_file, 'line':location, 'exception': e, 'key_word':key_word})
                    continue
                    
                if place_hoder_num != arg_num:
                    print(bad_log_fmt.format(source_file, location, place_hoder_num, arg_num, statement))
                    bad_fmt.append((key_word, place_hoder_num, arg_num))
                
            space_num = max_file_name_len-len(source_file)
            if len(bad_fmt) == 0:
                if show_ok:
                    space_num = max_file_name_len-len(source_file)
                    print((Fore.GREEN+'{}{} all {:2} `Fmt` ok'+Style.RESET_ALL).format(source_file, ' '*space_num, log_len))
            else:
                print('{}{} {:2} bad `Fmt` total in {} `Fmt`\n'.format(source_file, ' '*space_num, len(bad_fmt), log_len))
                bad_files.append({'source_file':source_file, 'bad_fmt': bad_fmt})
            
            if not show_ok:
                progress.advance(task)

    print()
    print()
    print('({}/{})(badfile/total) {:3} bad `Fmt` total'.format(len(bad_files), len(files), sum([len(bad_file['bad_fmt']) for bad_file in bad_files])))
    print()
    print()
    print()
    print('{} unknown `Fmt`:'.format(len(g_unknow_logs)))
    for log in g_unknow_logs:
        print(log)

def main():
    if '-help' in sys.argv or '-h' in sys.argv:
        print(help)
        exit()

    default_types = ['.cpp', '.h', '.hpp', '.mm']
    show_ok = None
    show_ok_res = {
       '-S'       : True,
       '-show_ok' : True,
       '-H'       : False,
       '-hide_ok' : False,
    }
    for arg in show_ok_res:
        if arg in sys.argv:
            sys.argv.remove(arg)
            show_ok = show_ok_res[arg]
        
    if len(sys.argv) > 1:
        files = []
        for arg in sys.argv[1:]:
            if os.path.isdir(arg):
                files = files + getfiles(arg, default_types)
            elif os.path.isfile(arg):
                files.append(arg)
                print('{} is file'.format(arg))
            else:
                print('`{}` is not file or dir!!!'.format(arg))
        check(files, show_ok)
    else:
        check(getfiles('./', default_types), show_ok)

if __name__ == "__main__":
    main()
