sipiiiii是一款面向小微企业和个人开发者的应用托管平台。其主要目的是满足chatgpt插件系统的托管需求。
## 产品定位
sipiiiii定位为简单易用的云应用托管平台:
- 小微企业:可以便捷部署业务应用,降低 IT 成本
- 个人开发者:可以快速部署个人开发的应用,实现想法
- chatgpt插件开发者:专为chatgpt插件系统提供托管服务,降低开发难度
## 产品优势
- 简单易用:通过命令行工具,可以极简操作完成应用的部署、管理等
- 低成本:积分制度,可以零成本体验所有功能
- 应用生成:支持根据模版一键生成应用框架
- chatgpt插件专属:深度整合chatgpt插件系统,提供专属托管解决方案
## 主要功能
- 应用部署:支持本地部署与远程部署,可一键部署应用 
- 应用管理:可启动、停止、重启应用等
- 应用生成:可根据yaml模版或者AI自动生成应用框架
- 账号管理:支持注册、登录、邮件激活等
- 积分系统:通过各功能消耗积分,可零成本使用
- chatgpt插件支持:提供chatgpt插件托管解决方案
## 未来计划
- 增加更多语言支持:如Ruby、Rust、Go等
- 添加更多应用模版
- 添加应用监控和报警功能
- 支持应用自动部署与回滚
## 
sipiiiii是一款专注于应用托管的产品,通过简单易用的命令行工具,为小微企业和个人开发者提供低成本的云应用托管服务。同时,也深度整合了chatgpt插件系统,专门为其提供托管解决方案。
未来,sipiiiii会不断丰富功能,增强产品性能与稳定性,为用户提供更加稳定可靠与高性能的应用托管服务

# sipiiiii 命令行工具
## 账号管理
### 登录账号

sipiiiii -L 或 --login  
登录后,token有效期为3天
### 注册账号

sipiiiii -R 或 --register
 
### 邮箱激活账号

sipiiiii -A 或 --activate
激活后的账号赠送10积分
### 查看积分余额

sipiiiii -t 或 --tally
## 应用部署
### 运行应用(非部署)
在应用目录下直接运行:
 
sipiiiii -d 或 --dev
### 本地化部署应用
消耗5积分,同一个应用只扣一次:

sipiiiii -LD 或 --localdepl
根据当前目录名获取应用名

### 部署应用
消耗20积分,同一个应用只扣一次:

sipiiiii -D 或 --deployed 
根据当前目录名获取应用名

## 应用生成
根据 yaml 模版和选项创建一个应用框架,目前有三种方式创建应用
1. 根据自己提供的yaml文件创建应用
2. 使用aiapi的模版创建应用
3. 使用向导模式创建应用
 
sipiiiii -n <test.yaml> 或 --new <test.yaml>
如果没有 <test.yaml> 参数则根据模板或者向导创建应用

## 应用管理
### 列出应用列表

sipiiiii -l 或 --list
### 查看应用详情

sipiiiii -i <app name> 或 --info <app name> 
如果没有 <app name> 参数则根据当前目录名获取应用名

### 停止应用(非本地部署)

sipiiiii -s <app name> 或 --stop <app name>
如果没有 <app name> 参数则根据当前目录名获取应用名

### 重启应用(非本地部署)

sipiiiii -r <app name> 或 --restart <app name>  
如果没有 <app name> 参数则根据当前目录名获取应用名

## 示例

sipiiiii -L
sipiiiii -n 
sipiiiii -D
sipiiiii -l
sipiiiii -i your-app-name