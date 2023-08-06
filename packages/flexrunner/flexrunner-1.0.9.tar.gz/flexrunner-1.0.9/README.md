# test-runner-flex
测试执行引擎/框架，python

## 快速开始
```
(venv) D:\workspace\src\test-runner-flex>python run_main.py --help
Usage: run_main.py [OPTIONS]

  FlexRunner 命令行 CLI

Options:
  -f, --test_conf_path TEXT       配置文件路径，对应目录：./{$project}/conf/{$test_conf}
                                  [default: ./demo/conf/demo.xml]
  --loglevel [TRACE|DEBUG|INFO|SUCCESS|WARNING]
                                  日志等级  [default: LogLevelEnum.INFO]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

```

## 测试demo环境搭建
```
.\minio.exe server D:\minio\data\ --console-address 127.0.0.1:9001
```