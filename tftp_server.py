from socket import *
import os 
import signal 
import sys 
import time 

#文件库
FILE_PATH = "/home/tarena/"

#实现功能模块
class TftpServer(object):
    def __init__(self,connfd):
        self.connfd = connfd 

    def do_list(self):
        #获取列表
        file_list = os.listdir(FILE_PATH)
        if not file_list:
            self.connfd.send("文件库为空".encode())
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)

        files = ""
        for file in file_list:
            if os.path.isfile(FILE_PATH+file) and \
            file[0] != '.':
                files = files + file + '#'

        self.connfd.send(files.encode())


    def do_get(self,filename):
        try:
            fd = open(FILE_PATH + filename,'rb')
        except:
            self.connfd.send("文件不存在".encode())
            return
        self.connfd.send(b'OK')
        time.sleep(0.1)
        #发送文件
        try:
            while True:
                data = fd.read(1024)
                if not data:
                    break
                self.connfd.send(data)
        except Exception as e:
            print(e)
        time.sleep(0.1)
        self.connfd.send(b'##') #表示文件发送完成
        print("文件发送完毕")

    def do_put(self,filename):
        try:
            fd = open(FILE_PATH+filename,'wb')
        except:
            self.connfd.send("无法上传".encode())
            return 
        self.connfd.send(b'OK')
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()
        print("文件上传完毕")

#流程控制，创建套接字，创建并发，方法调用
def main():
    HOST = '0.0.0.0'
    PORT = 8888
    ADDR = (HOST,PORT)

    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try: 
            connfd,addr = sockfd.accept()
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue
        print("客户端登录:",addr)

        #创建父子进程
        pid = os.fork()

        if pid == 0:
            sockfd.close()
            tftp = TftpServer(connfd)  # __init__传参
            while True:
                data = connfd.recv(1024).decode()
                if (not data) or data[0] == 'Q':
                    print("客户端退出")
                    sys.exit(0)
                elif data[0] == "L":
                    tftp.do_list()
                elif data[0] == 'G':
                    filename = data.split(' ')[-1]
                    tftp.do_get(filename)
                elif data[0] == 'P':
                    filename = data.split(' ')[-1]
                    tftp.do_put(filename)       
                else:
                    print("客户端发送错误指令")
        else:
            connfd.close()
            continue

if __name__ == "__main__":
    main()
