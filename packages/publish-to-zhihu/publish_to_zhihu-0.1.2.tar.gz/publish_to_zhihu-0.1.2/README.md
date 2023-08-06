# 功能
这个工具帮助将Obsidian风格的Markdown文件转化为mdnice的格式，主要有以下功能
- 自动上传本地图片到Azure blob storage
- 保证每个image link都在每行的最开始，没有额外的空格


想要转化为知乎格式，其实还需要下面几个工作，不过我们依赖mdnice来做下面的转换。
- 自动为每个list item前面增加额外的回车，不然知乎不识别
- 转换Obsidian的图片链接`![[attachments/Pasted image 20230511181810.png]]`到知乎格式
- 自动转换latex公式
# 安装
首先自行创造Azure storage account和blob container

设置环境变量IMAGEHOST_CONN_STR，这个变量要求包含形如`AccountName=(.*?);.*EndpointSuffix=(.*?)($|;)")`的信息

安装工具

```bash
pipx install publish-to-zhihu
```

如果过去安装过，可以用下面的命令升级
```
pipx upgrade publish-to-zhihu
```

# 日常使用

## 生成知乎格式的md文件并上传所有图片
假设你有多个md文件需要发布，下面是命令
```
# Convert standard Markdown file to Zhihu Format and upload all local images
zhihu_prepare_md --container container_name image_link_root output_folder md_file0 md_file1
```

其中
- container_name是Azure blob container的名字，假设为publishpic
- 本工具假设图像是相对路径，如`![[attachments/Pasted image 20230511181810.png]]`。假设在你硬盘上的真实路径是`C:\Cloud\OneDrive\note\attachments\Pasted image 20230511181810.png`，那么image_link_root就是`C:\Cloud\OneDrive\note`。
- output_folder是知乎格式md文件存放的目录。

所以，我自己发布`《曼昆经济学》成本笔记.md`时用的命令就是
```
zhihu_prepare_md --container publishpic c:\Cloud\OneDrive\note\ c:\Cloud\OneDrive\published_to_zhihu\  C:\Cloud\OneDrive\note\经济学\《曼昆经济学》成本笔记.md 
```
## 发布到知乎

发布
- 访问`c:\Cloud\OneDrive\published_to_zhihu\ `找到刚刚生成的文件
- 打开mdnice，把md文件拷贝进去。然后从mdnice拷贝出渲染好的适合知乎的内容
- 打开知乎，发表新文章，粘贴从mdnice得到的内容
- 保证知乎成功导入图片：知乎会从图床中导入图片，有的时候图片上传不成功，需要手工点击图片重试一次
- 手工填写标题
- 对于长文章，点击“目录”按钮来生成目录
- 如果需要投稿到问题，手工操作
- 手工选择标签
- 预览
- 发表

修改已发表的文章
- 点击文章的修改按钮或链接
- 清空文章的所有内容
- 粘贴从mdnice得到的内容
- 重新导入本地生成的md文件
- 保证知乎成功导入图片
- 预览
- 发表

# 进一步简化从Obisidan中发布文件的流程

安装Obsidian `Shell Commands`插件，增加一个下面的命令
```
zhihu_prepare_md --container publishpic c:\Cloud\OneDrive\note\ c:\Cloud\OneDrive\published_to_zhihu\  {{file_path:absolute}}
```

这样，在Obisidian中打开需要发布的文件，然后打开command palette，搜索"zhihu"命令运行就能够生成知乎格式的md文件了。


# Setup Dev Environment

First clone this repo then change to the repo directory.

Then run following command:
```sh
pip install poetry
poetry install   # Create virtual environement, install all dependencies for the project
poetry shell     # activate the virtual environment
pre-commit install    # to ensure automatically formatting, linting, type checking and testing before every commit
```

If you want to run unit test manually, just activate virtual environment and run:
```sh
pytest
```

# 本地开发流程

测试脚本是否正确
```bash
python -m publish_to_zhihu.prepare_md --container publishpic c:\Cloud\OneDrive\note\ c:\Cloud\OneDrive\published_to_zhihu\ C:\Cloud\OneDrive\note\经济学\《曼昆经济学》成本笔记.md 
```

发布到pipx
- bump version
- 发布
```
poetry publish --build --username %PYPI_USERNAME% --password %PYPI_PASSWORD%
```
- 本地升级最新版
```
pipx upgrade publish-to-zhihu
```



# Acknowledgement

- [搭建图床与自动上传 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/258230175)
- [markdown公式转为知乎格式 - 知乎](https://zhuanlan.zhihu.com/p/87153002)
