# fetchman
一个简单、好用的网络爬虫框架

基础组件

```
redis
mongodb
```

ubuntu安装
```
sudo apt-get install -y redis-server
sudo apt-get install -y mongodb
```

关键数据结构

```
{'task':
    {'id': str,
     'url': str,
     'status': int,
     'schedule':
        {'priority': int,  # 优先级
         'retries': int,  # 重试次数
         'retried': int,
         'exetime': int,  # 执行时间
         'age': int,  # 生命周期
         },
     'fetch':
        {'method': str,
         'headers': dict,
         'data': str,  # HTTP 请求信息 body
         'timeout': int
         },
     'process':
        {'callback': str,
         'save': dict},
     'updatetime': int,
     },
 }

{'result':
    {'url': str,
    'original_url': str,
    'status_code': int,
    'headers': dict,
    'content': str,
    'time': int,
    'save': str,
    }
}
```
