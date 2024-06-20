set terminal png transparent size 640,240
set size 1.0,1.0
set encoding utf8
set term png font "simsun,12"

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
            plot 'commits_by_project.dat' using 1:2 title "SMAIServ (患者数据服务)" w lines lw 2, 'commits_by_project.dat' using 1:3 title "SMAIDataSearch (数据快速搜索服务)" w lines lw 2, 'commits_by_project.dat' using 1:4 title "SMAIToolBoxPY3 (工具箱PY3服务)" w lines lw 2, 'commits_by_project.dat' using 1:5 title "SMAIExport (数据导出服务)" w lines lw 2, 'commits_by_project.dat' using 1:6 title "SMAIDataServ (新版本数据服务)" w lines lw 2, 'commits_by_project.dat' using 1:7 title "SMAIFormDc (表单数据服务)" w lines lw 2, 'commits_by_project.dat' using 1:8 title "SMAIImage (影像科研服务)" w lines lw 2, 'commits_by_project.dat' using 1:9 title "SMAIModelPre (模型管理与预测服务)" w lines lw 2, 'commits_by_project.dat' using 1:10 title "SMAIModels (新模型服务)" w lines lw 2, 'commits_by_project.dat' using 1:11 title "SMAIALog (审计日志服务)" w lines lw 2, 'commits_by_project.dat' using 1:12 title "SMAIFiles (文件管理服务)" w lines lw 2, 'commits_by_project.dat' using 1:13 title "SMAI4Annet (annet定制接口服务)" w lines lw 2, 'commits_by_project.dat' using 1:14 title "SMAIFormManage (表单管理(新)服务)" w lines lw 2, 'commits_by_project.dat' using 1:15 title "SMAIUAC (用户与权限控制服务)" w lines lw 2, 'commits_by_project.dat' using 1:16 title "SMAIFdef (字段模版管理服务)" w lines lw 2, 'commits_by_project.dat' using 1:17 title "SMAIFollow (患者随访服务)" w lines lw 2, 'commits_by_project.dat' using 1:18 title "SMAINotify (短信或其它通知服务)" w lines lw 2, 'commits_by_project.dat' using 1:19 title "SMAIRDMgmt (科研管理服务)" w lines lw 2, 'commits_by_project.dat' using 1:20 title "SMAIGcpServ (临床实验服务)" w lines lw 2, 'commits_by_project.dat' using 1:21 title "SMAIMultiCenter (多中心服务)" w lines lw 2, 'commits_by_project.dat' using 1:22 title "SMAISurvey (调查问卷(深圳三院))" w lines lw 2, 'commits_by_project.dat' using 1:23 title "SMAITriaManage (分诊管理后端接口服务)" w lines lw 2, 'commits_by_project.dat' using 1:24 title "SZSYInterfaceApi (开放接口(深圳三院))" w lines lw 2
