import os
import stat
import threading
import time
import requests


def ssh_download_file(remote_path, local_path, ip, user_name, password, port=22, callback=None):
    # 使用requests下载文件,并调用callback函数,持续返回进度
    url = f'http://{ip}:{port}/download_file?remote_path={remote_path}'
    print(url)
    # 获取文件的大小
    response = requests.get(url=url, auth=(user_name, password), stream=True)
    response.raise_for_status()
    file_size = int(response.headers['Content-Length'])
    # 获取文件的名字
    file_name = os.path.basename(remote_path)
    local_file_path = os.path.join(local_path, file_name)
    # 判断文件是否存在
    if os.path.isfile(local_file_path):
        # 如果本地文件已经存在，则删除
        os.remove(local_file_path)
        time.sleep(1)
    # 下载文件
    response = requests.get(url=url, auth=(user_name, password), stream=True)
    response.raise_for_status()
    # 保存文件
    with open(local_file_path, 'wb') as f:
        # 记录下载的大小
        count = 0
        # 记录下载的时间
        start_time = time.time()
        # 以流的形式下载文件
        process = 0
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                count += len(chunk)
                # 每下载1M,调用一次callback函数
                if count / file_size > 0.01:
                    # 调用callback函数
                    if callback:
                        process += count / file_size
                        # threading.Thread(target=callback, args=(round(process * 100, 2), file_name)).start()
                        callback(round(process * 100, 2), file_name)
                    count = 0
        # threading.Thread(target=callback, args=(100, file_name)).start()
        callback(100, file_name)
                    
    print('下载完成')
    return True

def ssh_upload_file(local_path, remote_path, ip=None, user_name=None, password=None, port=22, callback=None):
    # 使用requests上传文件,并调用callback函数,持续返回进度
    url = f'http://{ip}:{port}/upload_single_file'
    print(url)
    # 获取文件的大小
    file_size = os.path.getsize(local_path)
    # 获取文件的名字
    file_name = os.path.basename(local_path)
    # 上传文件
    with open(local_path, 'rb') as f:
        response = requests.post(url, files={'file': (file_name, f)})
        response.raise_for_status()
    
    print('上传完成')
    return True
    
def callback(process, filename):
    # 使用锁来确保线程安全
    with threading.Lock():
        print(process, filename)
    
    
if __name__ == '__main__':
    remote_path = '/root/nav_ws/src/lidar_localization/Localization/data/latest/finalCloud.pcd'
    local_path = './'
    ip = '10.10.9.254'
    user_name = 'root'
    password = '0'
    port = 5000
    # res = ssh_download_file(remote_path, local_path, ip, user_name, password, port, callback)
    # print(res)
    
    res = ssh_upload_file("./test.pcd", remote_path, ip, user_name, password, port)
    print(res)
