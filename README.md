# Douyin_spider
抖音视频下载

SSL的问题：

 

    最近iPhone系统更新到ios 10.3后,用Charles抓包竟然出现了一些问题,https的请求都会失败,提示错误信息为Failure SSLHandshake: Received fatal alert: unknown_ca 和You may need to configure your browser or application to trust the Charles Root Certificate. 然而之前任何问题都没有,并且相关设置都正确:电脑上安装了Charles的根证书,并且设置了始终信任,然后手机上也登录了http://chls.pro/ssl安装了描述文件,一切都按正常程序走的,但是错误始终无法解决.

 

原因：

    虽然charles的根证书已经在安装列表中显示,但它是被关闭的。在iOS 10.3之前,当你将安装一个自定义证书,iOS会默认信任,不需要进一步的设置。而iOS 10.3之后,安装新的自定义证书默认是不受信任的。如果要信任已安装的自定义证书,需要手动打开开关以信任证书。

 

解决：

设置->通用->关于本机->证书信任设置-> 找到charles proxy custom root certificate然后信任该证书即可.

https://blog.csdn.net/mxw2552261/article/details/78645118