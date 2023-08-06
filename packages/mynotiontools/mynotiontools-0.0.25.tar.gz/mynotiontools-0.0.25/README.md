# My Notion Tools

随手写的Notion小工具，只是个小玩意，暂时没有按照标准的开发规范对代码和流程进行约束。
只作为自己使用，为方便在各平台之间快速同步，协作使用，所以发布了出来。

> 这个工具重要是封装了一些简单的Notion接口，方便使用Python操作Notion时过程。

## Usage

Do this first.
需要在当前的操作系统环境变量中添加`NOTION_SECRETS`，Mac, Linux，Unix如下：

```bash
export NOTION_SECRETS='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### 引入使用

```python
from mynotiontools import *

```
