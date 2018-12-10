from socket import *
import sys 
import time 

#实现各种功能请求
class TftpClient(object):
    def __init__(self,sockfd):
        self.sockfd = sockfd 

    def do_list(self):
        self.sockfd.send(b'L') #发送请求类型
        #接收服务器回应
        data = self.sockfd.recv(1024).decode()
        if data == "OK":
            data = self.sockfd.recv(4096).decode()
            files = data.split('#')
            for file in files:
                print(file)
            print("文件展示完毕")
        else:
            #请求失败原因
            print(data)


    def do_get(self,filename):
        self.sockfd.send(('G ' + filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            fd = open(filename,'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
            print("%s 下载完成\n"%filename)
        else:
            print(data)

    def do_put(self,filename):
        try:
            fd = open(filename,'rb')
        except:
            print("上传文件不存在")
            return 
        self.sockfd.send(("P "+filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            while True:
                data = fd.read(1024)
                if not data:
                    break
                self.sockfd.send(data)
            fd.close()
            time.sleep(0.1)
            self.sockfd.send(b'##')
            print("%s 上传完毕"%filename)
        else:
            print(data)

#创建套接字建立连接
def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST,PORT)

    sockfd = socket()
    sockfd.connect(ADDR)

    tftp = TftpClient(sockfd)   #__init__是否需要传参

    while True:
        print("")
        print("==========命令选项===========")
        print("**********  list  *********")
        print("********** get file  ******")
        print("********** put file  ******")
        print("**********  quit  *********")
        print("=============================")

        cmd = input("输入命令>>")

        if cmd.strip() == "list":
            tftp.do_list()
        elif cmd[:3] == "get":
            filename = cmd.split(' ')[-1]
            tftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.split(' ')[-1]
            tftp.do_put(filename)
        elif cmd.strip() == "quit":
            sockfd.send(b'Q')
            sockfd.close()
            sys.exit("欢迎使用")
        else:
            print("请输入正确命令！")

if __name__ == "__main__":
    main()