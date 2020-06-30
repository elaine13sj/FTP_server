"""
FTP文件服务器
并发网络功能训练
"""
from socket import  *
from threading import Thread
import sys,os
from time import sleep

#全局变量（很多函数都要用/变量本身有意义）
HOST='0.0.0.0'
PORT=8080
ADDR=(HOST,PORT)
FTP="/home/summer/FTP/"   #文件库路径

#将客户端请求功能封装为类
class FtpServer:
    def __init__(self,confd,path):
        self.confd=confd
        self.path=path

    def do_list(self):
        #获取文件列表
        files=os.listdir(self.path)    #文件包含了隐藏文件
        if not files:
            self.confd.send("该文件夹为空")
        else:
            self.confd.send(b"OK")
            sleep(0.1)

        fs=''  #将读取的文件加入到fs中，然后只须将fs发送给客户端
        for file in files:
            # 不是隐藏文件且为普通文件
            if file[0]!='.' and os.path.isfile(self.path+file):
                fs +=file +'\n'
        self.confd.send(fs.encode())

    def do_get(self,filename):
        try:
            fd = open(self.path+filename,'rb')
        except Exception:
            self.confd.send("文件不存在".encode())
        else:
            self.confd.send(b'OK')
            sleep(0.1)
            #发送文件内容
            while True:
                data=fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.confd.send(b'##')
                    break
                self.confd.send(data)

    def do_put(self,filename):
        if  os.path.exists(self.path+filename):
            self.confd.send("文件已经存在".encode())
            return
        self.confd.send(b'OK')
        fd=open(self.path+filename,'wb')
        while True:
            data=self.confd.recv(1024)
            if data==b'##':
                break
            fd.write(data)
        fd.close()




#客户端请求处理函数
def handle(confd):

    """先接收客户端选择的文件夹种类
    再接收操作的类型（显示文件列表，上传文件，下载文件，退出）"""

    #选择文件夹
    cls= confd.recv(1024).decode()
    FTP_PATH= FTP + cls + '/'
    ftp = FtpServer(confd,FTP_PATH)   #服务器文件处理类的对象
    while True:
        #接收客户端请求
        data=confd.recv(1024).decode()
        # 客户端断开返回data为空
        if not data or data[0]=='Q':
            return
        elif data[0]=='L':
            ftp.do_list()
        elif data[0]=='G':
            filename=data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0]=='P':
            filename=data.split(' ')[-1]
            ftp.do_put(filename)




#网络搭建通过函数完成
def main():
    sockfd=socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(3)
    print("Listen the port 8080...")
    while True:
        try:
            connfd,addr=sockfd.accept()
        except KeyboardInterrupt:
            sys.exit("服务端退出")
        except Exception as e:
            continue
        print("连接的客户端：",addr)

        #创建线程处理请求
        client=Thread(target=handle,args=(connfd,))
        client.setDaemon(True)
        client.start()

if __name__=="__main__":
    main()
