# COS Uploader

跨平台的腾讯云对象存储上传工具

 - 支持 Windows、Linux、MacOS
 - 可以用于图片上传（图床）、文件分享等
 - 带有日志记录功能，可以查看上传历史
 - 支持通过系统自带的工具快速上传文件（Windows：「发送到」；MacOS：「快捷指令」）


## 安装
我们推荐使用 [pipx](https://pypa.github.io/pipx/) 安装 COS Uploader，请参见其官网来安装 pipx。

```bash
# 安装方法 1：使用 pipx 安装 (推荐)
pipx install cos-uploader

# 安装方法 2：使用 pip 安装
pip3 install cos-uploader

# 安装方法 3：手动创建虚拟环境安装 (可能会出现未经测试的问题)
mkdir -p ~/.cos-uploader/bin
python3 -m venv ~/.cos-uploader/venv
source ~/.cos-uploader/venv/bin/activate
pip install cos-uploader
ln -s ~/.cos-uploader/venv/bin/cos-uploader* ~/.cos-uploader/bin
echo 'export PATH="$PATH:$HOME/.cos-uploader/bin"' >> ~/.profile
```

## 使用
安装完成后，请运行 `cos-uploader-install` 来初始化配置，然后编辑 `~/.cos-uploader/config.toml` 来配置 COS Uploader。

请确保 `secret-id`、`secret-key`、`bucket`、`region` 配置正确，否则无法上传文件。

如果输入 `cos-uploader-install` 后提示找不到命令，可能是 PATH 环境变量没有生效或没有配置，请依次检查：
 - 重新启动当前 shell，如 `exec zsh` 或 `exec bash`
 - 重新启动当前终端，在 GUI 下应退出终端应用（iTerm2 下按 <kbd>Command ⌘</kbd> + <kbd>Q</kbd>、Windows Terminal 下关闭窗口）
 - 查看 PATH 变量
    - 使用 pipx，需要根据 pipx 的提示将 `~/.local/bin` 添加到 PATH
    - Windows 版的 Python 默认不会将 `Scripts` 添加到 PATH，需要手动添加。打开 [设置——系统——关于](ms-settings:about) 点击右侧「高级系统设置」，添加 `C:\Users\<用户名>\AppData\Roaming\Python\<Python版本>\Scripts` 到 PATH
    - 如果使用了手动创建虚拟环境安装（安装方法 3），请将 `~/.cos-uploader/bin` 添加到 PATH

配置完成后，可以使用 `cos-uploader` 命令来上传文件。

```bash
# 上传文件试试，测试配置是否正确
echo "Hello World" > hello.txt
cos-uploader hello.txt
```

### Windows 平台功能
在运行 `cos-uploader-install` 时，会自动创建「发送到」菜单项。

配置完成 `config.toml`后，在「资源管理器」中右键想要上传的文件，在菜单中选择「发送到」，然后选择「COS Uploader」即可上传该文件。

### MacOS 平台功能

请导入 [COS Uploader 快捷指令](https://www.icloud.com/shortcuts/76e95603ee464cddb0a7af9afe89c719)

导入完成后，请打开「快捷指令」App，选择左上角菜单中的「快捷指令——设置——高级」，勾选「允许运行脚本」。

配置完成 `config.toml` 后，在 Finder 中右键想要上传的文件，在菜单中选择「快速操作」，然后选择「COS Uploader」即可上传该文件。

## 查看历史
COS Uploader 会记录上传历史，可以通过 `cos-uploader-history` 命令来查看。输出记录按照时间戳降序排列。

`cos-uploader-history` 默认会输出全部记录，可以通过 `-n` 参数来限制输出的记录数量。

```bash
cos-uploader-history -n 10
```

COS Uploader 按月分割文件，文件日志格式为 `~/cos-uploader/history-yyyy-MM.ndjson`，其中 `yyyy-MM` 为年月。`cos-uploader-history` 仅输出当前月份的记录，可以通过 `-y`、`-m` 参数来指定时间。

```bash
cos-uploader-history -y 2023 -m 1
```

COS Uploader 使用 NDJSON 格式来记录上传历史，可以通过 `cos-uploader-history -r` 来查看原始记录。

```bash
cos-uploader-history -n 10 -r
```

### 优化海外使用体验
如果您上传文件的设备位于中国大陆境外，请修改 `config.toml` 如下：
```toml
oversea-upload = true
```

如果您的文件使用者位于中国大陆境外，请修改 `config.toml` 如下，并使用输出的 `Acc URL` 来访问文件。注意：需要在腾讯云控制台开启该 bucket 的「加速域名」功能。
```toml
[domains]
enabled = ["accelerate"]  # 在此处添加 accelerate，原来的可以删掉也可以保留
```

COS Uploader 默认在 URL 格式化的时候，使用 UTC 时间。如果需要使用本地时间（使用上传设备的系统时间），请修改 `config.toml` 如下：
```toml
utc-time = false
```

## 构建
COS Uploader 使用 Poetry 构建。请先安装 Poetry，然后执行以下命令：

```bash
git clone https://github.com/baobao1270/cos-uploader.git
cd cos-uploader
poetry install
```

要发布到 PyPI，请执行以下命令：

```bash
poetry publish --build
```

## 许可
COS Uploader 使用 MIT 协议
