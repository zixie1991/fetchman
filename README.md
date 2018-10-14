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
sudo apt-get  install phantomjs
```

启动phantomjs
```
phantomjs phantomjs_server.js --disk-cache=true
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
         'save': dict
         },
     'updatetime': int,
     'track':
        {'fetch':
            {'ok': True,
             'status_code': 200,
             'headers': dict,
             'encoding': str,
             'time': int
            },
         'process': 
            {'follows': int,
             'time': int
            }
        },
     },
 }

{'result':
    {'url': str,
    'original_url': str,
    'status_code': int,
    'headers': dict,
    'cookies': dict,
    'content': str,
    'time': int,
    'save': dict,
    }
}
```
