# 导入easyocr
import easyocr
# 创建reader对象
reader = easyocr.Reader(['de']) 
# 读取图像
result = reader.readtext('pictures/IMG_5230.jpeg')
# 结果
for i in result:
    word = i[1]
    print(word)