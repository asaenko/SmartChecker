{{checklist.name}}检查列表模块信息
====================================

--------------------------------------------------

### 检查列表包含以下模块：


{% for m in modules %}
####Module  #{{loop.index}}

#### 1.模块名称: {{m.name}}

#### 2.判断条件:
```
{{m.criteria}}
```
 
#### 3.说明:

  {{m.desc}}

---------------
{% endfor %}


### 请运行以下命令收集检查所需的信息

**注意：**

> 以下有部分命令仍缺部分参数，请根据实际网元情况填写相关的网元名称。 

-------------------------------------------------------------------------
```
{%- for cmd,desc in cmdlist %}
#{{desc}}
{{cmd}}
{% endfor %}
```

