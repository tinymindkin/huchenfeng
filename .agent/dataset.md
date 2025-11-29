


## 我的标注界面
```xml
<View>
  <!-- 1. 使用 Text 标签来显示原始数据（它是对象，不需要 toName） -->
  <Text name="source" value="$huchenfeng" />
  
  <!-- 2. 使用 TextArea 进行编辑/输入（它是控件，toName 指向上面的 source） -->
  <TextArea name="edited" toName="source" label="修改后的文本" rows="15"/>

</View>
```
## 我的数据结构
- id
- huchenfeng (这个是需要被标注的数据)
- source

## 标注结果
IMPORTANT: 标注结果是一个列表，也就是一个$huchenfeng可以被处理为多个文本
```json
[
  {
    "id": 2,
    "data": {
      "id": "custom-2",
      "text": "第二条文本"
    },
    "annotations": [
      {
        "id": 1001,
        "result": [...]
        "model_version": ""
        
      }
    ]
  }
]
```