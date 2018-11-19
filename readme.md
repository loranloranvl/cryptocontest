## 姿势 
```sh
$ python encrypt.py [file_path]
$ python analyze.py [file_path].enc
$ python decrypt.py [file_path].enc
$ python chain.py [file_path].enc
```
## 说明
#### 主要源码
(server side) encrypt.py 加密一个文档，生成以enc为后缀的新文件  
(helper) analyze.py 用于向程序狗分析enc文件的结构，不是加密必须流程  
(client side) decrypt.py 获取用户基本信息，将其与用户签名一起发送给服务器  
(server side) chain.py 获取来自客户端的信息，更新enc文件  

#### 其他源码
(helper) ecckeygen.py 用于生成sm2的公私钥对，随机产生6字节的用户id存到数据库  
(test file) test_sm2.py test_sm3.py test_sm4.py 加密函数测试文件  
(lib) gmssl 国密sm2/sm3/sm4加密函数  
#### 数据库文件（伪）
database/keypairs.csv 存放用户id和公私钥对，实际应用中私钥不应该存于数据库  
database/info.csv 临时文件 模拟从decrypt.py到chain.py的浏览者信息的信道-.-  