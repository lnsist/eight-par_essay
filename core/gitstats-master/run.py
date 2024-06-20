import glob
import json
import logging
import os
import shutil
import subprocess

import arrow

logging.basicConfig(
    level=logging.DEBUG,  # 控制台打印的日志级别
    filename='new.log',
    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    # a是追加模式，默认如果不写的话，就是追加模式
    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    # 日志格式
)
TZ = 'Asia/Shanghai'
TIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'
START_TIME = arrow.now(tz=TZ)
AUTHOR = 'XieZhenHeng'
SUMMARY_PATH = r'D:\#个人\workspace\eight-par_essay\files\git_total\summary'
GNUPLOT_COMMON = 'set terminal png transparent size 640,240\n' \
                 'set size 1.0,1.0\n' \
                 'set encoding utf8\n' \
                 'set term png font "simsun,12"\n'  # Gnuplot是一个命令行的交互式绘图工具
WEEKDAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
PROJECT_LIST = [
    {'en_name': 'SMAIServ', 'cn_name': '患者数据服务'},
    {'en_name': 'SMAIDataSearch', 'cn_name': '数据快速搜索服务'},
    {'en_name': 'SMAIToolBoxPY3', 'cn_name': '工具箱PY3服务'},
    {'en_name': 'SMAIExport', 'cn_name': '数据导出服务'},
    {'en_name': 'SMAIDataServ', 'cn_name': '新版本数据服务'},
    {'en_name': 'SMAIFormDc', 'cn_name': '表单数据服务'},
    {'en_name': 'SMAIImage', 'cn_name': '影像科研服务'},
    {'en_name': 'SMAIModelPre', 'cn_name': '模型管理与预测服务'},
    {'en_name': 'SMAIModels', 'cn_name': '新模型服务'},
    {'en_name': 'SMAIALog', 'cn_name': '审计日志服务'},
    {'en_name': 'SMAIFiles', 'cn_name': '文件管理服务'},
    {'en_name': 'SMAI4Annet', 'cn_name': 'annet定制接口服务'},
    {'en_name': 'SMAIFormManage', 'cn_name': '表单管理(新)服务'},
    {'en_name': 'SMAIUAC', 'cn_name': '用户与权限控制服务'},
    {'en_name': 'SMAIFdef', 'cn_name': '字段模版管理服务'},
    {'en_name': 'SMAIFollow', 'cn_name': '患者随访服务'},
    {'en_name': 'SMAINotify', 'cn_name': '短信或其它通知服务'},
    {'en_name': 'SMAIRDMgmt', 'cn_name': '科研管理服务'},
    {'en_name': 'SMAIGcpServ', 'cn_name': '临床实验服务'},
    {'en_name': 'SMAIMultiCenter', 'cn_name': '多中心服务'},
    {'en_name': 'SMAISurvey', 'cn_name': '调查问卷(深圳三院)'},
    {'en_name': 'SMAITriaManage', 'cn_name': '分诊管理后端接口服务'},
    {'en_name': 'SZSYInterfaceApi', 'cn_name': '开放接口(深圳三院)'},
]


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
            <li> <a href="projects.html">Projects</a> </li>
            <!-- <li> <a href="files.html">Files</a> </li> --> 
            <!-- <li> <a href="lines.html">Lines</a> </li> --> 
            <!-- <li> <a href="tags.html">Tags</a> </li> -->
        </ul> 
    </div> 
    """)


def html_header(level, text):
    name = text.lower().replace(' ', '_')
    return '\n<h{l} id="{n}"><a href="#{n}">{t}</a></h{l}>\n\n'.format(l=level, n=name, t=text)


def generate_summary_html():
    json_data = _get_json()
    _generate_index_html(json_data)
    _generate_activity_html(json_data)
    _generate_projects_html(json_data)
    _run_plot()


def _get_json():
    file_path = r'{}\{}.json'.format(SUMMARY_PATH, 'test_json')
    with open(file_path, 'r', encoding='utf-8') as _f:
        json_load = json.load(_f)

    return_list = [
        {
            'key': 'total_commits', 'type': int, 'value': 0
        },
        {
            'key': 'activity_by_year_week', 'type': dict, 'value': {},
            'max_key': 'activity_by_year_week_peak', 'max_type': int, 'max_value': 0,
        },
        {
            'key': 'day_of_week', 'type': dict, 'value': {},
        },
        {
            'key': 'hour_of_day', 'type': dict, 'value': {},
            'max_key': 'hour_of_day_busiest', 'max_type': int, 'max_value': 0,
        },
        {
            'key': 'activity_by_hour_of_week', 'type': dict, 'value': {}, 'is_sub': True,
            'max_key': 'activity_by_hour_of_week_busiest', 'max_type': dict, 'max_value': {},
        },
        {
            'key': 'activity_by_month_of_year', 'type': dict, 'value': {},
        },
        {
            'key': 'commits_by_month', 'type': dict, 'value': {},
        },
        {
            'key': 'lines_added_by_month', 'type': dict, 'value': {},
        },
        {
            'key': 'lines_removed_by_month', 'type': dict, 'value': {},
        },
        {
            'key': 'commits_by_year', 'type': dict, 'value': {},
        },
        {
            'key': 'lines_added_by_year', 'type': dict, 'value': {},
        },
        {
            'key': 'lines_removed_by_year', 'type': dict, 'value': {},
        },
    ]
    author_info = {
        'first_commit_stamp': 0,
        'last_commit_stamp': 0,
        'active_days': [],
        'commits': 0,
        'lines_added': 0,
        'lines_removed': 0,
    }
    changes_by_date_by_commits = []
    changes_by_date_by_lines_added = []
    author_of_month = {}
    author_of_year = {}
    project_dict = {'ALL': {
        'author_info': author_info,
        'changes_by_date_by_commits': changes_by_date_by_commits,
        'changes_by_date_by_lines_added': changes_by_date_by_lines_added,
        'author_of_month': author_of_month,
        'author_of_year': author_of_year,
    }}

    changes_dict = {}
    by_commits_sort = []

    for pl_index, pl_element in enumerate(PROJECT_LIST):
        pl_en_name = pl_element['en_name']
        pl_cn_name = pl_element['cn_name']
        pl_json = json_load[pl_en_name]

        for rl_element in return_list:
            rl_key = rl_element['key']
            rl_type = rl_element['type']
            rl_is_sub = rl_element.get('is_sub', False)
            rl_max_key = rl_element.get('max_key')
            if rl_type == int:
                rl_element['value'] += pl_json[rl_key]
            elif rl_type == dict:
                rl_value = rl_element['value']
                for _key, _value in pl_json[rl_key].items():
                    if rl_is_sub is False:
                        if not rl_value.get(_key):
                            rl_value[_key] = 0
                        rl_value[_key] += _value
                        if rl_max_key:
                            if not rl_element.get('max_value'):
                                rl_element['max_value'] = 0
                            rl_element['max_value'] = _value if _value > rl_element['max_value'] else rl_element['max_value']
                    else:
                        if not rl_value.get(_key):
                            rl_value[_key] = {}
                        for _i_key, _i_value in _value.items():
                            if not rl_value[_key].get(_i_key, 0):
                                rl_value[_key][_i_key] = 0
                            rl_value[_key][_i_key] += _i_value
                            if rl_max_key:
                                if not rl_element.get('max_value'):
                                    rl_element['max_value'] = 0
                                rl_element['max_value'] = _i_value if _i_value > rl_element['max_value'] else rl_element['max_value']

        pl_author_info = pl_json['author_info'][AUTHOR]
        pl_changes_by_date_by_author = pl_json['changes_by_date_by_author']
        pl_author_of_month = pl_json['author_of_month']
        pl_author_of_year = pl_json['author_of_year']

        pl_ai_commits = pl_author_info['commits']
        pl_ai_active_days = pl_author_info['active_days']
        pl_ai_lines_added = pl_author_info['lines_added']
        pl_ai_lines_removed = pl_author_info['lines_removed']
        pl_ai_first_commit_stamp = pl_author_info['first_commit_stamp']
        pl_ai_last_commit_stamp = pl_author_info['last_commit_stamp']

        project_dict[pl_en_name] = {
            'en_name': pl_en_name,
            'cn_name': pl_cn_name,
            'author_info': pl_author_info,
            'commits': pl_ai_commits,
            'active_days': pl_ai_active_days,
            'lines_added': pl_ai_lines_added,
            'lines_removed': pl_ai_lines_removed,
            'first_commit_stamp': pl_ai_first_commit_stamp,
            'last_commit_stamp': pl_ai_last_commit_stamp,
        }
        if author_info['first_commit_stamp'] == 0 \
                or pl_ai_first_commit_stamp < author_info['first_commit_stamp']:
            author_info['first_commit_stamp'] = pl_ai_first_commit_stamp
        if author_info['last_commit_stamp'] == 0 \
                or pl_ai_last_commit_stamp > author_info['last_commit_stamp']:
            author_info['last_commit_stamp'] = pl_ai_last_commit_stamp
        author_info['active_days'] = list(set(pl_author_info['active_days'] + author_info['active_days']))
        author_info['commits'] += pl_ai_commits
        author_info['lines_added'] += pl_ai_lines_added
        author_info['lines_removed'] += pl_ai_lines_removed

        by_commits_sort.append({'en_name': pl_en_name, 'commits': pl_ai_commits})

        for _key, _value in pl_changes_by_date_by_author.items():
            _value = _value[AUTHOR]
            if not changes_dict.get(_key):
                changes_dict[_key] = {}
            changes_dict[_key][pl_en_name] = {
                'commits': _value['commits'],
                'lines_added': _value['lines_added'],
            }

        for _element in [
            {'pl_obj': pl_author_of_month, 'obj': author_of_month},
            {'pl_obj': pl_author_of_year, 'obj': author_of_year},
        ]:
            for _key, _value in _element['pl_obj'].items():
                if not _element['obj'].get(_key):
                    _element['obj'][_key] = {AUTHOR: 0, 'other': 0}
                for _i_key, _i_value in _value.items():
                    if _i_key == AUTHOR:
                        _element['obj'][_key][AUTHOR] += _i_value
                    else:
                        _element['obj'][_key]['other'] += _i_value

    by_commits_sort = [x['en_name'] for x in sorted(by_commits_sort, key=lambda s: s['commits'], reverse=True)]

    for pl_element in PROJECT_LIST:
        pl_en_name = pl_element['en_name']
        project_dict[pl_en_name]['by_commits'] = by_commits_sort.index(pl_en_name) + 1

    commits_list = [0 for _ in range(len(PROJECT_LIST))]
    lines_added_list = [0 for _ in range(len(PROJECT_LIST))]
    for _key in sorted(list(changes_dict.keys())):
        for pl_index, pl_element in enumerate(PROJECT_LIST):
            commits_value = changes_dict[_key].get(pl_element['en_name'], {}).get('commits')
            lines_added_value = changes_dict[_key].get(pl_element['en_name'], {}).get('lines_added')
            if commits_value:
                commits_list[pl_index] = commits_value
            if lines_added_value:
                lines_added_list[pl_index] = lines_added_value
        changes_by_date_by_commits.append([_key] + commits_list)
        changes_by_date_by_lines_added.append([_key] + lines_added_list)

    return_dict = {'project_dict': project_dict}
    return_dict.update({x['key']: x['value'] for x in return_list})
    return_dict.update({x['max_key']: x['max_value'] for x in return_list if x.get('max_key')})

    return return_dict


def _generate_index_html(json_data):
    def _write_html(**kwargs):
        project_en_name = kwargs.get('project_en_name')
        project_cn_name = kwargs.get('project_cn_name')
        author_info = kwargs['author_info']
        first_commit_stamp = author_info['first_commit_stamp']
        first_commit_stamp = arrow.get(first_commit_stamp).to(TZ)
        last_commit_stamp = author_info['last_commit_stamp']
        last_commit_stamp = arrow.get(last_commit_stamp).to(TZ)
        commits = author_info['commits']
        active_days = author_info['active_days']
        lines_added = author_info['lines_added']
        lines_removed = author_info['lines_removed']

        write_str = '<dl>'
        if project_en_name and project_cn_name:
            write_str += '<dt>Link</dt>' \
                         '<dd><a href="../{en_name}_self/index.html">Project Of Self</a></dd>' \
                         '<dd><a href="../{en_name}/index.html">Project Of All Author</a></dd>'.format(
                en_name=project_en_name,
            )
        write_str += '<dt>Generated</dt><dd>{} (in {} seconds)</dd>'.format(
            arrow.now(TZ).format(TIME_FORMAT),
            (arrow.now(TZ) - START_TIME).seconds,
        )
        if not project_en_name and not project_cn_name:
            write_str += '<dt>Generator</dt><dd><a href="http://gitstats.sourceforge.net/">GitStats</a> (version ), {}, {}</dd>'.format(
                'git version 2.33.1.windows.1', 'gnuplot 6.0 patchlevel 1'
            )
        write_str += '<dt>Report Period</dt><dd>{} to {}</dd>'.format(
            first_commit_stamp.format(TIME_FORMAT),
            last_commit_stamp.format(TIME_FORMAT),
        )
        commit_delta_days = int((last_commit_stamp.timestamp / 86400 - first_commit_stamp.timestamp / 86400) + 1)
        commit_delta_years = round(commit_delta_days / 365.0, 2)
        working_days = commit_delta_years * 250
        write_str += '<dt>Age</dt><dd>{} days, {} years, {} working days, {} active days ({}%)</dd>'.format(
            format(commit_delta_days, ','),
            format(commit_delta_years, ','),
            format(working_days, ','),
            len(active_days),
            round(100.0 * len(active_days) / working_days, 2),
        )
        # write_str += '<dt>Total Files</dt><dd>%s</dd>' % data.getTotalFiles()
        write_str += '<dt>Total Lines of Code</dt><dd>{} ({} added, {} removed)</dd>'.format(
            format(lines_added - lines_removed, ','),
            format(lines_added, ','),
            format(lines_removed, ','),
        )
        write_str += '<dt>Total Commits</dt><dd>{} (average {} commits per active day, {} per all working days)</dd>'.format(
            format(commits, ','),
            format(round(commits / len(active_days), 1), ','),
            format(round(commits / working_days, 1), ','),
        )
        # write_str += '<dt>Authors</dt><dd>1 (average {} commits per author)</dd>'.format(commits)
        write_str += '</dl>'
        return write_str

    project_dict = json_data['project_dict']
    with open('{}/index.html'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>GitStats</h1>')
        print_nav(_f)

        content_list = []
        for pl_element in PROJECT_LIST:
            pl_en_name = pl_element['en_name']
            pl_cn_name = pl_element['cn_name']
            p_json = project_dict[pl_en_name]
            p_author_info = p_json['author_info']
            content = _write_html(
                project_en_name=pl_en_name,
                project_cn_name=pl_cn_name,
                author_info=p_author_info
            )

            html_str = r'<details><summary>{en_name} ({cn_name})</summary><div style="text-indent:2em">{content}</div></details>'.format(
                en_name=pl_en_name,
                cn_name=pl_cn_name,
                content=content,
            )
            content_list.append(html_str)
        content_list.insert(0, _write_html(author_info=project_dict['ALL']['author_info']))
        for x in content_list:
            _f.write(x)
        _f.write('</body>\n</html>')


def _generate_activity_html(json_data):
    project_dict = json_data['project_dict']
    total_commits = json_data['total_commits']
    hour_of_day = json_data['hour_of_day']
    hour_of_day_busiest = json_data['hour_of_day_busiest']
    activity_by_year_week = json_data['activity_by_year_week']
    activity_by_year_week_peak = json_data['activity_by_year_week_peak']
    day_of_week = json_data['day_of_week']
    activity_by_hour_of_week = json_data['activity_by_hour_of_week']
    activity_by_hour_of_week_busiest = json_data['activity_by_hour_of_week_busiest']
    activity_by_month_of_year = json_data['activity_by_month_of_year']
    commits_by_month = json_data['commits_by_month']
    lines_added_by_month = json_data['lines_added_by_month']
    lines_removed_by_month = json_data['lines_removed_by_month']
    commits_by_year = json_data['commits_by_year']
    lines_added_by_year = json_data['lines_added_by_year']
    lines_removed_by_year = json_data['lines_removed_by_year']
    author_of_month = project_dict['ALL']['author_of_month']
    author_of_year = project_dict['ALL']['author_of_year']

    with open('{}/activity.html'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Activity</h1>')
        print_nav(_f)

        _f.write(html_header(2, 'Weekly activity'))
        weeks = 32
        _f.write('<p>Last {} weeks</p>'.format(weeks))

        now = arrow.now()
        weeks_list = []
        temp_time = now
        for i in range(0, weeks):
            temp_week = temp_time.week
            weeks_list.insert(0, '{}-{}{}'.format(temp_time.format('YYYY'), '' if temp_week > 10 else '0', temp_week))
            temp_time = temp_time.shift(weeks=-1)

        _f.write('<table class="noborders"><tr>')
        for i in range(0, weeks):
            commits = activity_by_year_week.get(weeks_list[i], 0)
            _f.write(
                '<td style="text-align: center; vertical-align: bottom">'
                '{}<div style="margin:0 auto; display: block; background-color: red; width: 20px; height: {}px"></div>'
                '</td>'.format(commits, max(1, int(200 * (commits / activity_by_year_week_peak))))
            )

        # bottom row: year/week
        _f.write('</tr><tr>')
        for i in range(0, weeks):
            _f.write('<td>{}</td>'.format(weeks_list[i]))
        _f.write('</tr></table>')

        _f.write(html_header(2, 'Hour of Day'))
        _f.write('<table><tr><th>Hour</th>')
        for i in range(0, 24):
            _f.write('<th>{}</th>'.format(i))
        _f.write('</tr>\n<tr><th>Commits</th>')
        with open('{}/hour_of_day.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for i in range(0, 24):
                _value = hour_of_day.get(str(i), 0)
                _f.write('<td{}>{}</td>'.format(
                    '' if _value == 0 else ' style="background-color: rgb({}, 0, 0)"'.format(
                        100 + int((float(_value) / hour_of_day_busiest) * 128)
                    ),
                    _value,
                ))
                _fp.write('%d %d\n' % (i + 1, _value))

        _f.write('</tr>\n<tr><th>%</th>')
        for i in range(0, 24):
            _value = hour_of_day.get(str(i), 0)
            _temp_percent = format(round((100.0 * _value) / total_commits, 2), '.2f')
            _f.write('<td{}>{}</td>'.format(
                '' if _value == 0 else ' style="background-color: rgb({}, 0, 0)"'.format(
                    100 + int((float(_value) / hour_of_day_busiest) * 128)
                ),
                _temp_percent + ('&ensp;' * (5 - len(_temp_percent))),
            ))
        _f.write('</tr></table>')
        _f.write('<img src="hour_of_day.png" alt="Hour of Day">')

        _f.write(html_header(2, 'Day of Week'))
        _f.write('<div class="vtable"><table>')
        _f.write('<tr><th>Day&ensp;</th><th>Total&ensp;</th><th>percent of self (%)</th></tr>')
        with open('{}/day_of_week.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for d in range(0, 7):
                commits = day_of_week.get(str(d), 0)
                _fp.write('{} {} {}\n'.format(d + 1, WEEKDAYS[d], commits))
                _f.write('<tr>')
                _f.write('<th>{}</th>'.format(WEEKDAYS[d]))
                _f.write('<td>{}</td><td>{}%</td>'.format(
                    str(commits) + ('&ensp;' * (4 - len(str(commits)))),
                    format(round(100.0 * commits / total_commits, 2), '.2f'))
                )
                _f.write('</tr>')
            _f.write('</table></div>')
            _f.write('<img src="day_of_week.png" alt="Day of Week">')

        # Hour of Week
        _f.write(html_header(2, 'Hour of Week'))
        _f.write('<table>')

        _f.write(r'<tr><th>Week\Hour&ensp;</th>')
        for hour in range(0, 24):
            _f.write('<th>{}</th>'.format(hour))
        _f.write('</tr>')

        for weekday in range(0, 7):
            _f.write('<tr><th>{}</th>'.format(WEEKDAYS[weekday]))
            for hour in range(0, 24):
                commits = activity_by_hour_of_week.get(str(weekday), {}).get(str(hour), 0)
                _f.write('<td{}>{}</td>'.format(
                    '' if commits == 0 else ' style="background-color: rgb({}, 0, 0)"'.format(
                        127 + int((float(commits) / activity_by_hour_of_week_busiest) * 128)
                    ),
                    str(commits if commits else '&ensp;') + ('&ensp;' * (3 - len(str(commits)))),
                ))
            _f.write('</tr>')
        _f.write('</table>')

        # Month of Year
        _f.write(html_header(2, 'Month of Year'))
        _f.write('<div class="vtable"><table>')
        _f.write('<tr><th>Month&ensp;</th><th>Commits&ensp;</th><th>percent of self (%)</th></tr>')
        with open('{}/month_of_year.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for mm in range(1, 13):
                commits = activity_by_month_of_year.get(str(mm), 0)
                _f.write('<tr><td>{}</td><td>{}</td><td>{}%</td></tr>'.format(
                    mm, commits, format(round(100.0 * commits / total_commits, 2), '.2f'))
                )
                _fp.write('%d %d\n' % (mm, commits))
        _f.write('</table></div>')
        _f.write('<img src="month_of_year.png" alt="Month of Year">')

        # Commits by year/month
        _f.write(html_header(2, 'Commits by year/month'))
        _f.write('<div class="vtable"><table><tr>'
                 '<th>Month&ensp;</th>'
                 '<th>Commits&ensp;</th>'
                 '<th>percent of all authors (%)&ensp;</th>'
                 '<th>Lines added&ensp;</th>'
                 '<th>Lines removed&ensp;</th>'
                 '<th>Commit ranking</th>'
                 '</tr>')
        for yymm in reversed(sorted(commits_by_month.keys())):
            s_data = author_of_month[yymm]
            s_d_self_commits = s_data[AUTHOR]
            if s_d_self_commits == 0:
                continue
            s_d_other_commits = s_data['other']
            s_d_total_commits = s_d_self_commits + s_d_other_commits
            s_d_percent_commits = format(round(100 * s_d_self_commits / s_d_total_commits, 2), '.2f')
            temp_commits = commits_by_month.get(yymm, 0)
            _f.write('<tr><td>{}</td><td>{}</td><td>{}%&ensp;of&ensp;{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                yymm,
                temp_commits,
                s_d_percent_commits,
                s_d_total_commits,
                format(lines_added_by_month.get(yymm, 0), ','),
                format(lines_removed_by_month.get(yymm, 0), ','),
                '1' if s_d_self_commits >= s_d_other_commits else '2',
            ))
        _f.write('</table></div>')
        _f.write('<img src="commits_by_year_month.png" alt="Commits by year/month">')
        with open('{}/commits_by_year_month.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for yymm in sorted(commits_by_month.keys()):
                _fp.write('%s %s\n' % (yymm, commits_by_month[yymm]))

        # Commits by year
        _f.write(html_header(2, 'Commits by Year'))
        _f.write('<div class="vtable"><table><tr>'
                 '<th>Year&ensp;</th>'
                 '<th>Commits&ensp;</th>'
                 '<th>percent of self&ensp;</th>'
                 '<th>percent of all authors&ensp;</th>'
                 '<th>Lines added&ensp;</th>'
                 '<th>Lines removed&ensp;</th>'
                 '<th>Commit ranking&ensp;</th>'
                 '</tr>')
        for yy in reversed(sorted(commits_by_year.keys())):
            yy_data = commits_by_year.get(yy, 0)
            s_data = author_of_year[yy]
            s_d_self_commits = s_data[AUTHOR]
            if s_d_self_commits == 0:
                continue
            s_d_other_commits = s_data['other']
            s_d_total_commits = s_d_self_commits + s_d_other_commits
            s_d_percent_commits = format(round(100 * s_d_self_commits / s_d_total_commits, 2), '.2f')

            _f.write('<tr><td>{}</td><td>{}</td><td>{}%<td>{}%&ensp;of&ensp;{}</td></td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                yy,
                str(yy_data) + ('&ensp;' * (4 - len(str(yy_data)))),
                format(round(100.0 * yy_data / total_commits, 2), '.2f'),
                s_d_percent_commits,
                s_d_total_commits,
                format(lines_added_by_year.get(yy, 0), ','),
                format(lines_removed_by_year.get(yy, 0), ','),
                '1' if s_d_self_commits >= s_d_other_commits else '2',
            ))
        _f.write('</table></div>')
        _f.write('<img src="commits_by_year.png" alt="Commits by Year">')
        with open('{}/commits_by_year.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for yy in sorted(commits_by_year.keys()):
                _fp.write('{} {}\n'.format(yy, commits_by_year[yy]))

        _f.write('</body>\n</html>')


def _generate_projects_html(json_data):
    project_dict = json_data['project_dict']
    changes_by_date_by_commits = project_dict['ALL']['changes_by_date_by_commits']
    changes_by_date_by_lines_added = project_dict['ALL']['changes_by_date_by_lines_added']
    total_commits = json_data['total_commits']
    author_of_month = project_dict['ALL']['author_of_month']
    author_of_year = project_dict['ALL']['author_of_year']
    with open('{}/projects.html'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        print_header(_f)
        _f.write('<h1>Projects</h1>')
        print_nav(_f)

        # Projects :: List of projects
        _f.write(html_header(2, 'List of Projects'))
        _f.write('<table class="authors sortable" id="authors">')
        _f.write('<tr>'
                 '<th>Project</th>'
                 '<th>Commits (%)</th>'
                 '<th>+ lines</th>'
                 '<th>- lines</th>'
                 '<th>First commit</th>'
                 '<th>Last commit</th>'
                 '<th class="unsortable">Age</th>'
                 '<th>Active days</th>'
                 '<th># by commits</th>'
                 '</tr>')
        for pl_element in PROJECT_LIST:
            pl_en_name = pl_element['en_name']
            pl_cn_name = pl_element['cn_name']
            project_data = project_dict[pl_en_name]
            pd_first_commit_stamp = arrow.get(project_data['first_commit_stamp']).to(TZ)
            pd_last_commit_stamp = arrow.get(project_data['last_commit_stamp']).to(TZ)
            pd_percent_commits = round(100 * project_data['commits'] / total_commits, 2)
            pd_commits = str(project_data['commits'])
            _f.write('<tr><td>{}</td><td>{}&ensp;({}%)</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                '{} ({})'.format(pl_en_name, pl_cn_name),
                pd_commits + ('&ensp;' * (4 - len(pd_commits))),
                ('' if pd_percent_commits > 10 else '&ensp;') + format(pd_percent_commits, '.2f'),
                format(project_data['lines_added'], ','),
                format(project_data['lines_removed'], ','),
                pd_first_commit_stamp.format(TIME_FORMAT),
                pd_last_commit_stamp.format(TIME_FORMAT),
                pd_last_commit_stamp - pd_first_commit_stamp,
                len(project_data['active_days']),
                project_data['by_commits'],
            ))
        _f.write('</table>')

        _f.write(html_header(2, 'Cumulated Added Lines of Code per Project'))
        _f.write('<img src="lines_of_code_by_project.png" alt="Lines of code per Project">')

        _f.write(html_header(2, 'Commits per Project'))
        _f.write('<img src="commits_by_project.png" alt="Commits per Project">')

        with open('{}/commits_by_project.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for _v in changes_by_date_by_commits:
                _fp.write(' '.join([str(x) for x in _v]))
                _fp.write('\n')
        with open('{}/lines_of_code_by_project.dat'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _fp:
            for _v in changes_by_date_by_lines_added:
                _fp.write(' '.join([str(x) for x in _v]))
                _fp.write('\n')

        # temp_month_html = ''
        # temp_year_html = ''
        # for _element in [
        #     {'type': 'month', 'obj': author_of_month},
        #     {'type': 'year', 'obj': author_of_year},
        # ]:
        #     for s_element in reversed(sorted(_element['obj'].keys())):
        #         s_data = _element['obj'][s_element]
        #         s_d_self_commits = s_data[AUTHOR]
        #         if s_d_self_commits == 0:
        #             continue
        #         s_d_other_commits = s_data['other']
        #         s_d_total_commits = s_d_self_commits + s_d_other_commits
        #         s_d_percent_commits = round(100 * s_d_self_commits / s_d_total_commits, 2)
        #         temp_content = '<tr><td>{}</td><td>{}</td><td>{}&ensp;({}%&ensp;of&ensp;{})</td><td>{}</td></tr>'.format(
        #             str(s_element) + ('' if _element['type'] == 'month' else '&nbsp;&ensp;&ensp;&ensp;&ensp;'), AUTHOR,
        #             str(s_d_self_commits) + ('&ensp;' * (4 - len(str(s_d_self_commits)))),
        #             format(s_d_percent_commits, '.2f'),
        #             str(s_d_total_commits),
        #             '1' if s_d_self_commits >= s_d_other_commits else '2',
        #         )
        #         if _element['type'] == 'month':
        #             temp_month_html += temp_content
        #         else:
        #             temp_year_html += temp_content
        # # Projects :: Author of Month
        # _f.write(html_header(2, 'Author of Month'))
        # _f.write('<table class="sortable" id="aom"><tr><th>Month</th><th>Author</th><th>Commits (%)</th><th>Commit ranking</th></tr>{}</table>'.format(temp_month_html))
        #
        # # Projects :: Author of Year
        # _f.write(html_header(2, 'Author of Year'))
        # _f.write('<table class="sortable" id="aoy"><tr><th>Year</th><th>Author</th><th>Commits (%)</th><th>Commit ranking</th></tr>{}</table>'.format(temp_year_html))

        _f.write('</body>\n</html>')


def _run_plot():
    # hour of day
    with open('{}/hour_of_day.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write("""
            set output 'hour_of_day.png'
            unset key
            set xrange [0.5:24.5]
            set yrange [0:]
            set xtics 4
            set grid y
            set ylabel "Commits"
            plot 'hour_of_day.dat' using 1:2:(0.5) w boxes fs solid
            """)

    # day of week
    with open('{}/day_of_week.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write(
            """
            set output 'day_of_week.png'
            unset key
            set xrange [0.5:7.5]
            set yrange [0:]
            set xtics 1
            set grid y
            set ylabel "Commits"
            plot 'day_of_week.dat' using 1:3:(0.5):xtic(2) w boxes fs solid
            """)

    # Domains
    with open('{}/domains.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write(
            """
            set output 'domains.png'
            unset key
            unset xtics
            set yrange [0:]
            set grid y
            set ylabel "Commits"
            plot 'domains.dat' using 2:3:(0.5) with boxes fs solid, '' using 2:3:1 with labels rotate by 45 offset 0,1
            """)

    # Month of Year
    with open('{}/month_of_year.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write(
            """
            set output 'month_of_year.png'
            unset key
            set xrange [0.5:12.5]
            set yrange [0:]
            set xtics 1
            set grid y
            set ylabel "Commits"
            plot 'month_of_year.dat' using 1:2:(0.5) w boxes fs solid
            """)

    # commits_by_year_month
    with open('{}/commits_by_year_month.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write("""
            set output 'commits_by_year_month.png'
            unset key
            set yrange [0:]
            set xdata time
            set timefmt "%Y-%m"
            set format x "%Y-%m"
            set xtics rotate
            set bmargin 6
            set grid y
            set ylabel "Commits"
            plot 'commits_by_year_month.dat' using 1:2:(0.5) w boxes fs solid lw 2
            """)

    # commits_by_year
    with open('{}/commits_by_year.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write("""
            set output 'commits_by_year.png'
            unset key
            set yrange [0:]
            set xtics 1 rotate
            set grid y
            set ylabel "Commits"
            set yrange [0:]
            set bmargin 6
            plot 'commits_by_year.dat' using 1:2:(0.5) w boxes fs solid
            """)

    # Files by date
    with open('{}/files_by_date.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write(
            """
            set output 'files_by_date.png'
            unset key
            set yrange [0:]
            set xdata time
            set timefmt "%Y-%m-%d"
            set format x "%Y-%m-%d"
            set grid y
            set ylabel "Files"
            set xtics rotate
            set ytics autofreq
            set bmargin 6
            plot 'files_by_date.dat' using 1:2 w steps lw 2
            """)

    # Lines of Code
    with open('{}/lines_of_code.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write(
            """
            set output 'lines_of_code.png'
            unset key
            set yrange [0:]
            set xdata time
            set timefmt "%s"
            set format x "%Y-%m-%d"
            set grid y
            set ylabel "Lines"
            set xtics rotate
            set bmargin 6
            plot 'lines_of_code.dat' using 1:2 w lines lw 2
            """)

    # Lines of Code Added per author
    with open('{}/lines_of_code_by_project.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write("""
            set terminal png transparent size 1340,870
            set output 'lines_of_code_by_project.png'
            unset key
            # set key left top
            set yrange [2000:320000]
            set xdata time
            set timefmt "%s"
            set format x "%Y-%m-%d"
            set logscale y
            set ylabel "Lines"
            set xtics rotate
            set bmargin 6
            plot """
                 )
        plots = []
        for pl_index, pl_element in enumerate(PROJECT_LIST):
            pl_en_name = pl_element['en_name']
            pl_cn_name = pl_element['cn_name']
            plots.append("'lines_of_code_by_project.dat' using 1:{} title \"{}\" w lines lw 2".format(
                pl_index + 2,
                '{} ({})'.format(pl_en_name, pl_cn_name)
            ))
        _f.write(", ".join(plots))
        _f.write('\n')

    # Commits per author
    with open('{}/commits_by_project.plot'.format(SUMMARY_PATH), 'w', encoding='utf-8') as _f:
        _f.write(GNUPLOT_COMMON)
        _f.write(
            """
            set terminal png transparent size 1340,870
            set output 'commits_by_project.png'
            unset key
            # set key left top
            set yrange [10:1500]
            set xdata time
            set timefmt "%s"
            set format x "%Y-%m-%d"
            set logscale y
            set ylabel "Commits"
            set xtics rotate
            set bmargin 6
            plot """
        )
        plots = []
        for pl_index, pl_element in enumerate(PROJECT_LIST):
            pl_en_name = pl_element['en_name']
            pl_cn_name = pl_element['cn_name']
            plots.append("'commits_by_project.dat' using 1:{} title \"{}\" w lines lw 2".format(
                pl_index + 2,
                '{} ({})'.format(pl_en_name, pl_cn_name)
            ))
        _f.write(", ".join(plots))
        _f.write('\n')

    files = glob.glob('{}/*.plot'.format(SUMMARY_PATH))
    for f in files:
        temp_cmd = 'gnuplot "{}"'.format(f)
        subprocess.Popen(
            temp_cmd,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=SUMMARY_PATH,
        )


def _run():
    this_input = input('是否重新生成文件(y/n)')
    if this_input in ['y', 'Y']:
        _clear_file()
        git_bash_cmd = r'C:\Program Files\PortableGit\git-bash.exe'
        for project_name in [x['en_name'] for x in PROJECT_LIST]:
            command_str = rf'D:/#个人/workspace/eight-par_essay/venv/Scripts/python.exe ' \
                          rf'D:/#个人/workspace/eight-par_essay/core/gitstats-master/gitstats ' \
                          rf'D:/code/{project_name} ' \
                          rf'D:/#个人/workspace/eight-par_essay/files/git_total/{project_name}'
            p = subprocess.Popen(
                '{} -c "{}"'.format(git_bash_cmd, command_str + ' 0'),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            p.wait()
            p = subprocess.Popen(
                '{} -c "{}"'.format(git_bash_cmd, command_str + '_self 1'),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=SUMMARY_PATH,
            )
            p.wait()

    generate_summary_html()


if __name__ == '__main__':
    # 合并一行测试用
    # D:/#个人/workspace/eight-par_essay/venv/Scripts/python.exe
    # D:/#个人/workspace/eight-par_essay/core/gitstats-master/gitstats
    # D:/code/SMAIServ
    # D:/#个人/workspace/eight-par_essay/files/git_total/SMAIServ_self 1
    _run()
