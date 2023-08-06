# Usage

```bash
pipx install publish-to-zhihu

# convert latex math formula to zhihu format
zhihu_convert_latex to_be_convert.md

# upload a list of images to azure storage container
zhihu_upload_images azure_storage_container_name azure_storage_account_connection_string file_root file_rel_path_0 file_rel_path_1

# Convert standard Markdown file to Zhihu Format and upload all local images
zhihu_prepare_md --container container_name image_link_root output_folder md_file0 md_file1


```

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

# Acknowledgement

- [搭建图床与自动上传 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/258230175)
- [markdown公式转为知乎格式 - 知乎](https://zhuanlan.zhihu.com/p/87153002)
