## Sequoia选股系统
### 简介
本程序使用[AKShare接口](https://github.com/akfamily/akshare)，从东方财富获取数据。

本程序实现了若干种选股策略，大家可以自行选择其中的一到多种策略组合使用，参见[work_flow.py](https://github.com/sngyai/Sequoia/blob/master/work_flow.py#L28-L38)，也可以实现自己的策略。

各策略中的`end_date`参数主要用于回测。

## 准备工作:
###  环境&依赖管理
推荐使用 Miniconda来进行 Python 环境管理 [Miniconda — conda documentation](https://docs.conda.io/en/latest/miniconda.html)

安装 conda 后，切换到项目专属环境进行配置，例如：
```
# 在包含 dependencies.yml 文件的目录下运行
conda env create -f dependencies.yml
conda activate sequoia
```

###  验证依赖安装

```
conda activate sequoia
python test_sequoia_installation.py
```

###  format源码

```
conda activate sequoia
./format_code.sh
```
 
 ### 更新akshare数据接口
 本项目已切换至akshare数据接口，该项目更新频率较高，使用前建议检查接口更新
``` 
pip install akshare --upgrade
```
 ### 生成配置文件

```
cp config.yaml.example config.yaml
```
## 运行
### 本地运行
```
$ python main.py
```
运行结果查看 logs 目录下生成的日志文件 格式为 `logs/sequoia-$YEAR-$MONTH-$DAY-$HOUR-$MINUTE-$SECOND.log`
如：`logs/sequoia-2023-03-03-20-47-56.log`

### 服务器端运行
#### 定时任务
服务器端运行需要改为定时任务，共有两种方式：
1. 使用Python schedule定时任务
   * 将[config.yaml](config.yaml.example)中的`cron`配置改为`true`，`push`.`enable`改为`true`

2. 使用crontab定时任务
   * 保持[config.yaml](config.yaml.example)中的`cron`配置为***false***，`push`.`enable`为`true`
   * [安装crontab](https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804)
   * `crontab -e` 添加如下内容(服务器端安装了miniconda3)：
   ```bash
    SHELL=/bin/bash
    PATH=/usr/bin:/bin:/home/ubuntu/miniconda3/bin/
    # m h  dom mon dow   command
    0 3 * * 1-5 source /home/ubuntu/miniconda3/bin/activate python3.10; python3 /home/ubuntu/Sequoia/main.py >> /home/ubuntu/Sequoia/sequoia.log; source /home/ubuntu/miniconda3/bin/deactivate
   ```

程序中的时间是服务器的本地时间，在部署的时候留意设置服务器时区为目标市场时区。

#### 微信推送
使用[WxPusher](https://wxpusher.zjiecode.com/docs/#/)实现了微信推送，用户需要自行获取wxpusher_token和topic_id，并配置到`config.yaml`中去。


## 如何回测
修改[config.yaml](config.yaml.example)中`end_date`为指定日期，格式为`'YYYY-MM-DD'`，如：
```
end = '2019-06-17'
```

