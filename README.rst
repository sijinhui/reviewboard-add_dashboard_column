====================
add_dashboard_column
====================

Describe your extension.


进入虚拟环境后最好先安装一下`ez_setup.py`: `python ez_setup.py`

后续就能正常构建whl包就行：`python setup.py bdist_wheel sdist`，这个打包的比较简洁，不要用uv运行

添加到当前环境，用于开发：`python setup.py develop`, [参考文档](https://www.reviewboard.org/docs/manual/latest/extending/extensions/distribution/)