import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wonplat", # 包的名称
    version="0.0.1", # 版本号
    author="Xianghe Wang", # 作者名
    author_email="3200104190@zju.edu.cn", # 作者邮箱
    description="A short description of your package", # 包的简短描述
    long_description=long_description, # 包的详细描述，可以从README.md中读取
    long_description_content_type="text/markdown", # 包的详细描述的格式
    url="https://github.com/WonderLari/Clifford-Sampling", # 包的主页，一般是Github仓库的地址
    packages=setuptools.find_packages(), # 包含的子模块或子包，一般使用find_packages()来查找所有的子模块和子包
    classifiers=[ # 包的分类标签，用于搜索和分类
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6", # 指定Python的最低版本
    install_requires=[ # 指定依赖的其他Python包
        "numpy>=1.15.0",
        "scipy>=1.3.0",
        "matplotlib>=3.0.0",
        "stim>=1.9.0",
        "qiskit>=0.39.0"
    ],
)
