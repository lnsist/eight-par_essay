import os
import shutil

SUMMARY_PATH = r'D:\#个人\workspace\git_total\summary'


def _clear_file():
    if os.path.exists(SUMMARY_PATH):
        shutil.rmtree(SUMMARY_PATH)
    os.makedirs(SUMMARY_PATH)

    for file in ('gitstats.css', 'sortable.js', 'arrow-up.gif', 'arrow-down.gif', 'arrow-none.gif'):
        base = r'D:\#个人\workspace\eight-par_essay\core\gitstats-master'
        src = '{}/{}'.format(base, file)
        if os.path.exists(src):
            shutil.copyfile(src, '{}/{}'.format(SUMMARY_PATH, file))


def print_header(f):
    f.write("""
    <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>GitStats</title>
            <link rel="stylesheet" href="gitstats.css" type="text/css">
            <meta name="generator" content="GitStats">
            <script type="text/javascript" src="sortable.js"></script>
        </head>
        <body>
    """)


def print_nav(f):
    f.write(""" 
    <div class="nav"> 
        <ul> 
            <li> <a href="index.html">General</a> </li>
            <li> <a href="activity.html">Activity</a> </li> 
            <li> <a href="authors.html">Authors</a> </li>
            <li> <a href="files.html">Files</a> </li> 
            <li> <a href="lines.html">Lines</a> </li>
            <li> <a href="tags.html">Tags</a> </li> 
        </ul> 
    </div> 
    """)


def generate_summary_html():
    with open('{}/index.html', 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>GitStats</h1>')
        print_nav(_f)

        with open(r'{}/index_html.txt'.format(SUMMARY_PATH), 'a+', encoding='utf-8') as _h:
            _f.write(_h.read())

        _f.write('</body>\n</html>')

    with open('{}/activity.html', 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Activity</h1>')
        print_nav(_f)

        # todo

        _f.write('</body>\n</html>')

    with open('{}/authors.html', 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Authors</h1>')
        print_nav(_f)

        # todo

        _f.write('</body>\n</html>')

    with open('{}/files.html', 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Files</h1>')
        print_nav(_f)

        # todo

        _f.write('</body>\n</html>')

    with open('{}/lines.html', 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Lines</h1>')
        print_nav(_f)

        # todo

        _f.write('</body>\n</html>')

    with open('{}/tags.html', 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Tags</h1>')
        print_nav(_f)

        # todo

        _f.write('</body>\n</html>')


def _run():
    this_input = input('是否清空文件(y/n)')
    if this_input in ['y', 'Y']:
        _clear_file()
    html_url = []
    command_list = []
    command_list2 = []
    print('打开 C:\Program Files\PortableGit\git-bash.exe')
    print('执行下面生成的命令')
    for project_name in [
        'SMAIServ',
        'SMAIDataSearch',
        'SMAIToolBoxPY3',
        'SMAIExport',
        'SMAIDataServ',
        'SMAIFormDc',
        'SMAIImage',
        'SMAIModelPre',
        'SMAIModels',
        'SMAIALog',
        'SMAIFiles',
        'SMAI4Annet',
        'SMAIFormManage',
        'SMAIUAC',
        'SMAIFdef',
        'SMAIFollow',
        'SMAINotify',
        'SMAIRDMgmt',
        'SMAIGcpServ',
        'SMAIMultiCenter',
        'SMAISurvey',
        'SMAITriaManage',
        'SZSYInterfaceApi',
    ]:
        command_str = rf'D:/#个人/workspace/eight-par_essay/venv/Scripts/python.exe ' \
                      rf'D:/#个人/workspace/eight-par_essay/core/gitstats-master/gitstats ' \
                      rf'D:/code/{project_name} ' \
                      rf'D:/#个人/workspace/git_total/{project_name}'
        command_list.append(command_str + ' 0')
        command_list2.append(command_str + '_me 1')
        html_url.append(rf'D:\#个人\workspace\git_total\{project_name}\index.html')

    print('\n'.join(command_list))
    print('\n'.join(command_list2))
    # print('\n'.join(html_url))

    # while True:
    #     this_input = input('执行完命令后输入(y)')
    #     if this_input in ['y', 'Y']:
    #         generate_summary_html()
    #         break


if __name__ == '__main__':
    _run()
