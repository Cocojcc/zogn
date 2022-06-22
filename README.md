# ZOGN

静态博客生成器

### 创建项目

```python
zogn init[项目名]
```

### 新建博客

```python
zogn new[文件路径]
```

### 项目打包

```python
zogn build
```

### 预览

```python
zogn server
```

## 配置文件

### 主题相关配置

```python
STATIC_FOLDER = "default/static"  # 主题名/静态文件文件夹
TEMPLATES_FOLDER = "default/templates"  # 主题名/模板文件夹
```

### 友链

```editorconfig
LINKS = 

[
    ['zhanghaoran', 'http://blog.zhanghaoran.ren/']
]
```

### 站点配置

```editorconfig
# 网站名
SITE_NAME = "zo9n"
# 网站关键词
SITE_KEYWORDS = "Python, Django, backend, blog, web, MySQL optimization, website optimization, random thoughts, coding"
# 网站描述
SITE_DESCRIPTION = "This is a salted fish coder developed website which mainly records and shares coding notes, random thoughts."
# 网站地址
SITE_URL = "https://zo9n.com"
# 统计代码
ANALYTICS_CODE = ""
```
