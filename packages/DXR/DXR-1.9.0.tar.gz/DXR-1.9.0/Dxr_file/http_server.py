import os
from flask import Flask, request,render_template,url_for,redirect,send_file

import http.client
import json
from flask import abort

path = "/root/DXR_Project/DXR_FaceRec/face/database"


# 生成一个Flask对象
app = Flask(__name__)

# 路由
@app.route('/get_users', methods=['GET'])
def get_user():
    # 获取path目录下的所有文件名称进行返回
    file_list = os.listdir(path)
    # dit = {"users":file_list}
    # 遍历file_list，如果是文件夹，则添加到data中
    data = []
    for i in range(len(file_list)):
        if os.path.isdir(path+"/"+file_list[i]):
            print(file_list[i])
            # 过滤掉nohup.out,001,002,003
            if file_list[i] == "nohup.out" or file_list[i] == "001" or file_list[i] == "002" or file_list[i] == "003":
                continue
            data.append(file_list[i])
    print(data)
    return json.dumps(data)

@app.route('/get_user_list/<user_name>', methods=['GET'])
def get_user_list(user_name):
    # 获取path目录下的所有文件名称进行返回
    file_list = os.listdir(path+"/"+user_name)
    # 如果user_name是中文，则需要进行编码
    if user_name != user_name.encode('utf-8').decode('utf-8'):
        print("user_name is chinese")
        user_name = user_name.encode('utf-8').decode('utf-8')
    data = []
   # 存成一个数组，有两个字段，一个是name,一个是url
    for i in range(len(file_list)):
        data.append({"name":file_list[i],"url":f"/{user_name}/{file_list[i]}", "file_create_time":os.path.getctime(path+"/"+user_name+"/"+file_list[i])})
    return json.dumps(data)

# 添加用户
@app.route('/add_user', methods=['POST'])
def add_user():
    # 获取用户名称
    user_name = request.form['user_name']
    # user_name 是要创建的文件夹的绝对路径
    return_dit = {
        'code': 200,
        'msg': '添加成功'
    }
    print(user_name)
    # 判断user_name文件夹是否存在
    if os.path.exists(user_name):
        print("user_name is exists")
        return_dit['code'] = 400
        return_dit['msg'] = '用户已存在'
    else:
        os.mkdir(user_name)
    return json.dumps(return_dit)

# 删除用户
@app.route('/delete_user', methods=['POST'])
def delete_user():
    # 获取用户名称
    user_name = request.form['user_name']
    # user_name 是要创建的文件夹的绝对路径
    return_dit = {
        'code': 200,
        'msg': '删除成功'
    }
    # 判断user_name文件夹是否存在
    if os.path.exists(user_name):
        # 如果文件夹里面有文件，也要删除
        file_list = os.listdir(user_name)
        for i in range(len(file_list)):
            os.remove(user_name+"/"+file_list[i])
        os.rmdir(user_name)
    else:
        return_dit['code'] = 400
        return_dit['msg'] = '用户不存在'
    return json.dumps(return_dit)

# 上传图片
@app.route('/upload_image', methods=['POST'])
def upload_image():
    # 将图片存在/root/face_tmp下，并且返回上传图片的名称
    return_dit = {
        'code': 200,
        'msg': '上传成功',
        'data':{
            'image_name':''
        }
    }
    # 获取上传的文件
    file = request.files['file']
    # 获取上传的文件名
    file_name = file.filename
    print(file_name)
    # 获取上传的文件类型
    file_type = file_name.split('.')[-1]
    # 存储的文件,用原来的文件名
    file_path = '/root/face_tmp/'+file_name
    # 判断file_path是否存在,如果存在则把原来的文件备份
    if os.path.exists(file_path):
        os.rename(file_path,file_path+'.bak')
    # 保存文件
    file.save(file_path)
    # 返回文件名
    return_dit['data']['image_name'] = file_name
    return json.dumps(return_dit)

# 删除图片
@app.route('/delete_image', methods=['POST'])
def delete_image():
    # 删除图片,获取user_name,是要删除的文件的绝对路径
    user_name = request.form['user_name']
    print(user_name)
    return_dit = {
        'code': 200,
        'msg': '删除成功'
    }
    # 判断user_name文件夹是否存在
    if os.path.exists(user_name):
        os.remove(user_name)
    else:
        return_dit['code'] = 400
        return_dit['msg'] = '文件不存在'
    return json.dumps(return_dit)


@app.route('/download_file', methods=['GET'])
def download_file():
    # 获取文件的绝对路径
    file_path = request.args.get('remote_path')
    # 判断文件是否存在，如果存在则返回文件
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        # 如果文件不存在，则返回404
        return abort(404)
    

# 定义一个下载文件夹的方法
@app.route('/download_dir', methods=['GET'])
def download_dir():
    try:
        os.chdir('/root/nav_ws/src/lidar_localization/Localization/data')
        file_name = "latest"
        print(file_name)
        if os.path.exists(file_name + '.zip'):
            os.remove(file_name + '.zip')
        print(f'pwd: {os.getcwd()}')
        os.system('zip -r ' + file_name + '.zip ' + file_name)
        print('zip -r ' + file_name + '.zip ' + file_name)
        # 返回压缩后的文件
        return send_file(os.getcwd() + '/' + file_name + '.zip', as_attachment=True)
    except Exception as e:
        print(e)
        return abort(404)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        remote_path = '/root/nav_ws/src/lidar_localization/Localization/data'
        os.chdir(remote_path)
        # 上传文件
        return_dit = {
            'code': 200,
            'msg': '上传成功'
        }
        # 获取上传的文件
        file = request.files['file']
        # 获取上传的文件名
        file_name = file.filename
        # 获取上传的文件类型
        file_type = file_name.split('.')[-1]
        # 保存文件
        # 判断文件是否存在，如果存在则删除
        if os.path.exists('./'+file_name):
            os.remove('./'+file_name)
        # 创建空文件
        os.system('touch '+'./'+file_name)
        file.save('./'+file_name)
        if file_type == 'zip':
            # 删掉原来的备份文件
            os.system('rm -rf '+file_name.split('.')[0]+'.bak')
            print(f'rm -rf {file_name.split(".")[0]}.bak')
            os.system('mv '+file_name.split('.')[0]+' '+file_name.split('.')[0]+'.bak')
            print(f'mv {file_name.split(".")[0]} {file_name.split(".")[0]}.bak')
            os.system('rm -rf '+file_name.split('.')[0])
            print(f'rm -rf {file_name.split(".")[0]}')
            # 查看当前目录
            print(f'pwd: {os.getcwd()}')
            # 查看当前目录下的文件
            print(f'ls: {os.listdir(os.getcwd())}')
            
            os.system('unzip '+file_name)
            print(f'unzip {file_name}')
            # 777权限
            os.system('chmod -R 777 '+file_name.split('.')[0])
            print(f'chmod -R 777 {file_name.split(".")[0]}')
        return json.dumps(return_dit)
    except Exception as e:
        print(e)
        return abort(404)
    
    

@app.route('/upload_single_file', methods=['POST'])
def upload_single_file():
    print('upload_single_file')
    try:
        remote_path = '/root/nav_ws/src/lidar_localization/Localization/data/latest'
        # 上传文件
        return_dit = {
            'code': 200,
            'msg': '上传成功'
        }
        # 获取上传的文件
        file = request.files['file']
        # 获取上传的文件名
        file_name = file.filename
        # 获取上传的文件类型
        file_type = file_name.split('.')[-1]
        print(f'file_name: {file_name} file_type: {file_type}')
        # 保存文件
        # 判断文件是否存在，如果存在，就把原来的文件备份
        if os.path.exists(remote_path+'/'+file_name):
            os.rename(remote_path+'/'+file_name,remote_path+'/'+file_name+'.bak')
        # 创建空文件
        os.system('touch '+remote_path+'/'+file_name)
        file.save(remote_path+'/'+file_name)
        # 777权限
        os.system('chmod -R 777 '+remote_path+'/'+file_name)
        return json.dumps(return_dit)
    except Exception as e:
        print(e)
        return abort(404)
            


if __name__ == '__main__':
    # 运行Flask
    app.run(host='0.0.0.0', port=5000)

