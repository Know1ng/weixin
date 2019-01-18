# 微信文章


微信文章爬虫。


用于爬取搜狗微信文章https://weixin.sogou.com/


一、关于反爬：


1、需要登录才能访问更多文章页面。


2、访问频繁弹出验证码。


3、使用代理ip仍会弹出验证码（同一个账号，多个ip）。


4、访问过于频发（即被封号，大约24h），每次访问文章都需要微信扫码，只能在手机上看查看文章。


解决：代理池+cookie池+访问延时


二、关于代理：


这里使用的是别人维护好的代理池，效果比较好，具体使用和介绍可参照：https://github.com/jhao104/proxy_pool


这里不做赘述。


三、关于cookie：


使用单一cookie+代理仍然会出现弹出验证码的情况，解决办法：可以自建cookie池，每次访问随机挑选一个cookie。


四、延时：


对于类似这种反爬机制比较健全的网站，爬取数据需要牺牲一下速度来换取成功率，不然被检测出封24h，得不偿失。


所以这里建议每次访问文章链接延时2-3s。


五、运行：


运行程序之前先运行代理，然后在config.py添加你需要使用的cookie池，设置最大页数MAX_PAGE和关键词KEYWORD即可。
这里以搜索最近比较火热的话题为例，MAX_PAGE = 3，
KEYWORD = '无印良品饼干致癌'。



六、结果：


运行结果
![Image text](https://github.com/Know1ng/weixin/blob/master/weixin/run.png)


保存结果
![Image text](https://github.com/Know1ng/weixin/blob/master/weixin/result.png)


七、不足：


该爬虫只能爬取文章的文本内容，无法爬取文章的图片和视频。

八、其他：


该爬虫仅用于学习
