import os
import pandas as pd
import time
import sys,os
import cloudpss
import time
import numpy as np
import pandas as pd

while True:
    try:
        os.environ['CLOUDPSS_API_URL'] = 'https://cloudpss.net/'
        print('CLOUDPSS connected')
        cloudpss.setToken(
            'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjgyNCwidXNlcm5hbWUiOiJ6Y3l5eWRzIiwic2NvcGVzIjpbXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNjk2MjUwMzk5LCJpYXQiOjE2ODA2OTgzOTl9.AULfiouwQsPSQ0ZKRnNaanFqtPM_V33v5PJvufADX3po1S4B1VIf21mtAbru7PZTH-12qRfxpeshHiaWTCkfbA')
        print('Token done')
        project = cloudpss.Model.fetch('model/zcyyyds/39e')
        print('model load successfully')
        output_block = []
        # 不填默认用model的第一个job
        job = project.jobs[1]  # 计算方案
        # 不填默认用model的第一个config
        config = project.configs[0]  # 参数方案
        # latest_file = os.listdir('./output/')
        # sorted_list = sorted(latest_file, key=lambda x: os.path.getctime(os.path.join('./output', x)))[-1]
        # latest_fault = int(sorted_list.split('_')[0].strip('Fault'))
        # latest_gain = int(sorted_list.split('_')[1].strip('.csv').strip('GAIN'))
        latest_fault = 9
        latest_gain = 5000
        print(latest_fault)
        print(latest_gain)
        output_block = []
        for fault in range(latest_fault, 10):
            config['args']['fault'] = "#bus" + str(fault)
            for gain in range(latest_gain, 6450, 50):
                config['args']['gain'] = gain
                t1 = time.time()
                runner = project.run(job, config)
                # while not runner.status():
                #     print('running time: {}s'.format(time.time()))
                #     time.sleep(10)
                time_flag = 1
                plotChannelNames = runner.result.getPlotChannelNames(0)
                lenchannel = len(plotChannelNames)
                for i in range(lenchannel):
                    result = runner.result.getPlotChannelData(0, plotChannelNames[i])
                    output_list = result['y']
                    if time_flag == 1:
                        output_block.append(result['x'])
                        print('Time is appended in the output block.')
                        output_block.append(output_list)
                        time_flag = 0
                    else:
                        output_block.append(output_list)
                    print('get channel result: {} .'.format(plotChannelNames[i]))
                writerCSV = pd.DataFrame(data=output_block)
                writerCSV.to_csv('./test/Fault{}_GAIN{}.csv'.format(fault, gain), index=False, header=False,
                                 encoding='utf-8')
                output_block = []
                print('Fault{} and GAIN{} is finished'.format(fault, gain))

        print('All tasks finished')

    except Exception as e:
        # 记录异常日志
        with open('error.log', 'a') as f:
            f.write('[{}] {}: {}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), type(e).__name__, str(e)))

        # 等待一段时间后重启程序
        time.sleep(10)
        print("程序出错，重启中")
        continue

print('All tasks finished')
