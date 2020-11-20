#include<stdlib.h>
#include<time.h>
#include<iostream>
#include<WS2tcpip.h>
#include<fstream>
#include <WinSock2.h>
#include<Windows.h>
 

#pragma comment(lib,"ws2_32.lib")

using namespace std;

#define _WINSOCK_DEPRECATED_NO_WARNINGS 
#define SERVER_PORT 12340 //接收数据的端口号
#define SERVER_IP "127.0.0.1" // 服务器的 IP 地址

const int BUFFER_LENGTH = 1027;
const int seqSize = 20;//序列号个数
int curSeq=0;//当前伴随ack传输的seq

SOCKET clientSocket;//客户端套接字
SOCKADDR_IN serverAddr;

int InitClientSocket();
int ifLoss(float lossRatio);


int main(int argc, char* argv[]) {
	if (InitClientSocket() == 0) {
		cout << "初始化客户端的套接字失败" << endl;
		return -1;
	}
	char buffer[BUFFER_LENGTH];
	ZeroMemory(buffer, sizeof(buffer));
	int length = sizeof(SOCKADDR);
	float packetLossRatio = 0.2; //包丢失率 
	float ackLossRatio = 0.2; //ACK 丢失率 
	int a;
	
	while (1) {
		cout << endl;
		cout << "-------------------" << endl;
		cout << "输入1代表-time" << endl;
		cout << "输入2代表-quit" << endl;
		cout << "输入3代表-testgbn" << endl;
		cout << "-------------------" << endl;
		cout << "请输入：";
		cin >> a;
		cout << endl;
		if (a == 1) {
			sendto(clientSocket, "-time", strlen("-time") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
			cout << "时间为：" << buffer << endl;
		}
		else if (a == 2) {
			sendto(clientSocket, "-quit", strlen("-quit") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
			cout << buffer << endl;
			break;
		}
		else if (a == 3) {
			cout << "请输入丢包率:";
			cin >> packetLossRatio;
			cout << "请输入ack丢失率:";
			cin >> ackLossRatio;
			sendto(clientSocket, "-testgbn", strlen("-testgbn") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			int state = 0;
			int waitSeq = -1;
			int waitTime = 0;
			ofstream os;     //创建一个文件输出流对象
			os.open("newdata.txt");//将对象与文件关联
			while (1) {
				recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
				int ifRecieve = -1;
				if (state == 0) {//建立连接
					if ((unsigned char)buffer[0] == 205) {
						buffer[0] = (unsigned short)200;
						buffer[1] = '\0';
                        cout << "接收到连接请求,可以开始传输." << endl;
						sendto(clientSocket, buffer, 2, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
						state = 1;
						waitSeq = 0;
						//Sleep(50000);
					}
				}
				else if (state == 1) {//等待接收数据发送ACK
					//int recvSeq = (unsigned short)buffer[1];
					int recvSeq = buffer[1];
					if (ifLoss(packetLossRatio) == 1) {//判断包是否丢失
						cout << "序列号为" << recvSeq << " 的传输报文丢失了" << endl;
						continue;
					}
					if (recvSeq == waitSeq) {//收到的就是想要的
						cout << "接收序列号为" << recvSeq << "的包" << endl;
						ifRecieve = 1;
						waitSeq = (waitSeq + 1) % seqSize;
						//cout << "数据为：" << endl;
						for (int i = 3; i < 1024; i++) {
							//cout << buffer[i];
							os << buffer[i];//将data写入文件
						}
						cout << endl;
						buffer[0] = '1';
						buffer[1] = (unsigned short)recvSeq;
						buffer[2] = (curSeq + 1) % seqSize;
						buffer[3] = '\0';
						curSeq=(curSeq+1) % seqSize;
						if (ifLoss(ackLossRatio) == 1) {//判断ack是否丢失
							cout << "ACK" << recvSeq << "丢失" << endl;
							continue;
						}
						sendto(clientSocket, buffer, 4, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));//发送ACK报文
						cout << "发送ACK" << recvSeq <<",发送包的序列号为:"<<curSeq<< endl;
					}
					else {//收到的不是想要的，丢弃
						cout << "接收到的包序列号为:" << recvSeq << ",想要的包序列号为:" << waitSeq  <<endl;
						buffer[0] = '1';
						buffer[1] = (unsigned short)(waitSeq - 1);
						buffer[2] = (curSeq + 1) % seqSize;
						buffer[3] = '\0';
						curSeq = (curSeq + 1) % seqSize;
						if (ifLoss(ackLossRatio) == 1) {//判断ack是否丢失
							cout << "ACK" << waitSeq - 1 << "丢失" << endl;
							continue;
						}
						sendto(clientSocket, buffer, 4, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));//发送ACK报文
						cout << "发送ACK" << waitSeq - 1 << ",发送包序列号为"<< curSeq << endl;
						

					}

				}
				Sleep(500);
			}
			os.close();
		}
		
	}
	
	closesocket(clientSocket);
	WSACleanup();
	return 0;
}

int InitClientSocket() {
	//加载套接字库（必须）
	WORD wVersionRequested;
	WSADATA wsaData;
	//套接字加载时错误提示
	int err;
	//版本 2.2
	wVersionRequested = MAKEWORD(2, 2);
	//加载 dll 文件 Scoket 库
	err = WSAStartup(wVersionRequested, &wsaData);
	if (err != 0) {
		//找不到 winsock.dll
		cout << "加载winsock失败,错误代码为：" << WSAGetLastError() << endl;
		return 0;
	}
	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2) {
		cout << "不能找到正确的 winsock 版本\n" << endl;
		WSACleanup();
		return 0;
	}
	clientSocket = socket(AF_INET, SOCK_DGRAM, 0);
	// InetPton(AF_INET, TEXT(SERVER_IP), &serverAddr.sin_addr.S_un.S_addr);
	serverAddr.sin_addr.S_un.S_addr = inet_pton(AF_INET, SERVER_IP, &serverAddr.sin_addr);
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(SERVER_PORT);
	return 1;
}

//根据丢失率模拟是否丢失
int ifLoss(float lossRatio) {
	int RanddomNumber = rand() % 101;
	if (RanddomNumber < (int)(lossRatio * 100)) {//丢失
		return 1;
	}
	return -1;//不丢失
}



