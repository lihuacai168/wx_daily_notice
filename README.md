# 效果预览
![](https://s2.loli.net/2022/09/15/TUqGFJmdPNS8lCk.png)
# 使用步骤
## 1、申请微信公众号测试账号
[点击这里](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)  
**注意** 登录完成后，需要刷新一次，这样得到的`app_secret`才是正确的

## 2、Fork本项目
点击右上角的Fork按钮，将本项目Fork到自己的仓库中
![](https://s2.loli.net/2022/09/15/6VJYRFtsjieuaE7.png)


## 3、配置Actions密钥
![](https://s2.loli.net/2022/09/15/fsoHYp5cziLVqyN.png)

### 3.1微信公众号相关的配置
`APP_ID`和`APP_SECRET`  
![](https://s2.loli.net/2022/09/15/XizmvNBlZeGqQoW.png)  
`TEMPLATE_ID` 作用指定发送的消息模板，我使用的是  
```
今天天气: {{weather.DATA}} 
当前温度: {{temperature.DATA}} 
恋爱の第: {{love_days.DATA}} 天 
距离她的生日还有: {{birthday_left.DATA}} 天 
每日一句: {{sentence.DATA}} 
```
![](https://s2.loli.net/2022/09/15/PjWvUgl6TcQhO2y.png)

### 3.2推送内容相关配置
`BIRTHDAY` 必填，生日，格式是`07-01`  
`CITY` 必填，天气使用的城市，格式是`广州`  
`IS_LUNAR_BIRTHDAY` 非必填，默认是否；是否为农历生日，是就写1；不是就写`"`或者不配置  
`START_DATE` 必填，恋爱纪念日，格式是`2022-09-15`  
`USER_ID` 必填，接收推送消息用户id  
![](https://s2.loli.net/2022/09/15/jrERVkZv5PiKYpG.png)

## 4、定时推送配置
> 这里crontab的时区是UTC，和中国时区相差8小时
> 也就说说这里配置0时0点，就是中国时间早上08:00
![](https://s2.loli.net/2022/09/15/oltPeQXIzgr7vOc.png)