def get_build_envd_template():
    return (
        """# template
def build():
    base(os="ubuntu20.04", language="python3.10")
    install.vscode_extensions([
        "ms-python.python",
        "ms-toolsai.jupyter",
    ])
    # Mirror
    configure_apt_huawei()
    configure_conda()
    configure_pypi()
    # Configure Packages
    install.apt_packages([
        "build-essential"
    ])
    install.python_packages([
        "numpy",
        "pandas",
        "opencv-python",
        "plotly",
        "ray[default]",
        "lightning"
    ])
    # Configure jupyter notebooks.
    config.jupyter(
        token="hello",
        port=8090
    )

def configure_apt_huawei():
    run(commands=[
        "sudo cp -a /etc/apt/sources.list /etc/apt/sources.list.bak",
        "sudo sed -i 's@http://.*archive.ubuntu.com@http://repo.huaweicloud.com@g' /etc/apt/sources.list",
        "sudo sed -i 's@http://.*security.ubuntu.com@http://repo.huaweicloud.com@g' /etc/apt/sources.list",
        "sudo apt-get update"
    ])

def configure_pypi():
    config.pip_index(url = "https://pypi.tuna.tsinghua.edu.cn/simple")

def configure_conda():
    config.conda_channel(channel=\"\"\"
    channels:
    - defaults
    show_channel_urls: true
    default_channels:
    - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
    - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
    - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
    - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
    custom_channels:
    conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    pytorch-lts: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
    \"\"\")
    """)
