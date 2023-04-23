# Auto CloudWatch Alarm

## 方案介绍
AWS CloudWatch Alarm 是 AWS CloudWatch 的一项功能，用于监控 AWS 资源和应用程序，并在达到特定阈值时发送通知或执行自动操作。一旦 CloudWatch Alarm 触发警报，可以使用多种方式通知用户，例如发送电子邮件、短信或推送通知到 SNS 主题。此外，还可以设置自动响应，例如执行 AWS Lambda 函数、停止或重新启动 EC2 实例等。

利用CloudWatch Alarm 可以帮助用户及时发现和解决系统问题，提高系统的可用性和可靠性，保障业务的正常运行。

然而，CloudWatch Alarm 只能针对单台的 EC2 实例创建，如果用户有数以千计的 EC2 实例需要监控，手动为每个实例创建 CloudWatch Alarm 将会是一项耗时耗力，同时也极容易出现错误的工作。

为了解决这个问题，这里介绍了一个利用EventBridge去监听EC2 创建/销毁 时间的通知，并触发Lambda函数去自动创建/删除CloudWatch Alarm的方案。

## 如何安装
本方案使用SAM CLI来进行构建。

#### 环境准备


- SAM CLI， 参考 https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
  
- Python3， 参考 https://www.python.org/downloads/
  
- Docker， 参考 https://hub.docker.com/
  

#### 使用SAM CLI 部署方案

```shell
git clone https://github.com/readybuilderone/auto-cloudwatch-alarm.git
cd auto-cloudwatch-alarm


sam build --use-container
sam deploy --guided
```
