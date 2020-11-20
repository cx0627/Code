#include <stdlib.h>
#include <WinSock2.h>
#include <time.h>
#include<iostream>
#include <Ws2tcpip.h>

#pragma comment(lib,"ws2_32.lib")

using namespace std;

//#define _WINSOCK_DEPRECATED_NO_WARNINGS 
#define SERVER_PORT 12340 //接收数据的端口号
#define SERVER_IP "127.0.0.1" // 服务器的 IP 地址

const int BUFFER_LENGTH = 1027;
const int seqSize = 20;//序列号个数
const int windowSize = 8;//滑动窗口大小
int rec[seqSize];//接收到报文的情况，1代表收到，-1代表没收到
int base;

SOCKET clientSocket;//客户端套接字
SOCKADDR_IN serverAddr;

int InitClientSocket();
int ifLoss(float lossRatio);
void sendDataUp(int start, int base, int buffer_1[windowSize]);

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
	int buffer_1[windowSize];//接收到的缓冲区数据对应包的序列号
	ZeroMemory(buffer_1, windowSize);

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
			cout << "请输入丢包率：";
			cin >> packetLossRatio;
			cout << "请输入ack丢失率：";
			cin >> ackLossRatio;
			sendto(clientSocket, "-testgbn", strlen("-testgbn") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			int state = 0;
			//int waitSeq = -1;
			ZeroMemory(rec, seqSize);

			while (1) {
				int a = recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
				//cout << "客户端收到报文大小：" << a << endl;
				if (state == 0) {//建立连接
					if ((unsigned char)buffer[0] == 205) {
						buffer[0] = (unsigned short)200;
						buffer[1] = '\0';
						cout << "接收到连接请求，可以开始传输" << endl;
						sendto(clientSocket, buffer, 2, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
						state = 1;
						base = 0;
						for (int i = 0; i < windowSize; i++) {
							rec[i] = 1;
						}
					}
				}
				else if (state == 1) {//等待接收数据发送ACK

					int recvSeq = buffer[1];
					if (ifLoss(packetLossRatio) == 1) {//判断包是否丢失
						cout << "序列号为" << recvSeq << "的传输报文丢失" << endl;
						continue;
					}
					cout << "接收到序列号为" << recvSeq << "的包" << endl;
					int step;
					if ((base + windowSize) >= seqSize) {
						if (((recvSeq >= base) && (recvSeq < seqSize)) || ((recvSeq >= 0) && (recvSeq < (windowSize + base - seqSize)))) {
							//在窗口内
							buffer_1[recvSeq] = recvSeq;
							rec[recvSeq] = 0;
							bool flag = false;
							int start = base;
							for (int i = base; i < seqSize; i++) {
								if (rec[i] == 1) {
									step = i - base;
									base = i;
									flag = true;
									break;
								}
							}
							//cout << flag << endl;
							if (!flag) {
								for (int i = 0; i < (windowSize + base - seqSize); i++) {
									if (rec[i] == 1) {
										step = seqSize - base + i;
										base = i;
										flag = true;
										break;
									}
								}
							}
							if (!flag) {
								base = (base + windowSize) % windowSize;
								step = windowSize;
							}
							int index;
							for (int i = 0; i < step; i++) {
								index = (base + windowSize - step + i) % seqSize;
								rec[index] = 1;

							}
							
							if ((start - base) != 0) {//窗口滑动
								sendDataUp(start, base, buffer_1);
							}


						}
					}
					else {

						if ((recvSeq >= base) && (recvSeq < base + windowSize)) {

							//在窗口内
							rec[recvSeq] = 0;
							buffer_1[recvSeq] = recvSeq;
							bool flag = false;
							int start = base;
							for (int i = base; i < (base + windowSize); i++) {
								if (rec[i] == 1) {
									step = i - base;
									base = i;
									flag = true;
									break;
								}
							}
							if (!flag) {
								base = base + windowSize;
								step = windowSize;
							}
							int index;
							//cout << "step=" << step << endl;
							for (int i = 0; i < step; i++) {
								index = (base + windowSize - step + i) % seqSize;
								rec[index] = 1;
								//cout << "index=" << index << endl;
							}
							if ((start - base) != 0) {//窗口滑动
								sendDataUp(start, base, buffer_1);
							}


						}
					}
					buffer[0] = '1';
					buffer[1] = (unsigned short)recvSeq;
					buffer[2] = '\0';
					if (ifLoss(ackLossRatio) == 1) {//判断ack是否丢失
						cout << "ACK" << recvSeq << "丢失" << endl;
						continue;
					}
					sendto(clientSocket, buffer, 3, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));//发送ACK报文
					cout << "发送ACK" << recvSeq << endl;
					
				}
				Sleep(500);

			}
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
		cout << "加载winsock失败，错误代码为：" << WSAGetLastError() << endl;
		return 0;
	}
	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2) {
		cout << "不能找到正确的 winsock 版本\n" << endl;
		WSACleanup();
		return 0;
	}
	clientSocket = socket(AF_INET, SOCK_DGRAM, 0);
	InetPton(AF_INET, TEXT(SERVER_IP), &serverAddr.sin_addr.S_un.S_addr);
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


//向上层按照顺序交付数据
void sendDataUp(int start, int base, int buffer_1[windowSize]) {
	cout << "向上层交付数据(分组的序列号）：" ;
	cout << "start=" << start << ",base=" << base << endl;
	if (start < base) {
		for (int i = start; i < base; i++) {
			cout << buffer_1[i] <<"--";
		}
		cout << endl;
	}
	else {
		for (int i = start; i < seqSize; i++) {
			cout << buffer_1[i] << "--";
		}
		for (int i = 0; i < base; i++) {
			cout << buffer_1[i] << "--";
		}
		cout << endl;
	}
	Sleep(1000);
}

