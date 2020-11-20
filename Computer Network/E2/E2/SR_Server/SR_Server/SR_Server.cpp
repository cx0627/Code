#include <stdlib.h>
#include <time.h>
#include <WinSock2.h>
#include <fstream>
#include<iostream>
#include<Windows.h>

#pragma comment(lib,"ws2_32.lib")

using namespace std;

#define SERVER_PORT 12340 //端口号
#define SERVER_IP "0.0.0.0" //IP 地址

const int BUFFER_LENGTH = 1027; //缓冲区大小，（以太网中 UDP 的数据帧中包长度应小于 1480 字节）
//|1 （1个字节）|nextSendSeq （1个字节）|base （1个字节）|data （1024个字节）
const int windowSize = 8;//发送窗口大小为8
const int seqSize = 20;//序列号个数

int ack[seqSize];//接收到ack的情况，1代表收到，-1代表没收到
int counts[seqSize];//每个分组的计时器
int nextSendSeq;//下一个要发送的 seq
int base;//当前等待确认的 ack
int totalSeq;//收到的包的总数
int totalPacket;//需要发送的包总数

SOCKET serverSocket;//服务器的套接字
SOCKADDR_IN serverAddr;

int InitServerConnectSocket();
BOOL seqIsAvailable();


int main(int argc, char* argv[]) {
	if (InitServerConnectSocket() == 0) {
		cout << "初始化服务器的套接字失败" << endl;
		return -1;
	}
	int recvSize;
	for (int i = 0; i < seqSize; i++) {
		ack[i] = 1;
	}
	SOCKADDR_IN clientAddr; //客户端地址
	int length = sizeof(SOCKADDR);
	char buffer[BUFFER_LENGTH]; //接收数据的缓冲区
	ZeroMemory(buffer, sizeof(buffer));
	char data[1024 * 100];
	ZeroMemory(data, sizeof(data));
	int datalen = 0;
	ifstream file("data.txt");
	while (!file.eof()) {
		file >> data[datalen++];
	}
	cout << "data:" << data << endl;
	totalPacket = sizeof(data) / 1024;
	while (1) {
		recvSize = recvfrom(serverSocket, buffer, BUFFER_LENGTH, 0, ((SOCKADDR*)&clientAddr), &length);
		if (recvSize < 0) {
			Sleep(200);
			continue;
		}
		cout << "-----服务器从客户端接收的报文------" << endl;
		cout << buffer << endl;
		cout << endl;
		if (strcmp(buffer, "-quit") == 0) {
			strcpy_s(buffer, strlen("Good bye!") + 1, "Good bye!");
			cout << buffer << endl;
			sendto(serverSocket, buffer, strlen(buffer) + 1, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
			break;
		}
		else if ((strcmp(buffer, "-time") == 0)) {
			SYSTEMTIME sys;
			GetLocalTime(&sys);
			sprintf_s(buffer, "%4d/%02d/%02d %02d:%02d:%02d", sys.wYear, sys.wMonth, sys.wDay, sys.wHour, sys.wMinute, sys.wSecond, sys.wMilliseconds);
			cout << "time:" << buffer << endl;
			sendto(serverSocket, buffer, strlen(buffer) + 1, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
		}
		else if (strcmp(buffer, "-testgbn") == 0) {
			ZeroMemory(buffer, sizeof(buffer));
			int waitTime = 0;
			int state = 0;
			int flag = 1;
			while (flag) {//发送205
				if (state == 0) {
					buffer[0] = (unsigned short)205;
					sendto(serverSocket, buffer, strlen(buffer) + 1, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
					Sleep(100);
					state = 1;

				}
				else if (state == 1) {//等待接收200
					recvSize = recvfrom(serverSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&clientAddr, &length);
					if (recvSize < 0) {
						waitTime++;
						if (waitTime > 15) {
							flag = 0;
							cout << "没有响应，超时，停止测试" << endl;
						}
						else {
							Sleep(500);
						}
					}
					else {
						if ((unsigned char)buffer[0] == 200) {
							cout << "文件开始准备传输...." << endl;
							base = 0;
							nextSendSeq = 0;
							totalSeq = 0;
							ZeroMemory(counts, 0);
							state = 2;
						}
					}
				}
				else if (state == 2) {//传输数据
					if (seqIsAvailable() && (totalSeq + 1 <= totalPacket)) {
						totalSeq++;
						buffer[0] = '1';
						buffer[1] = (unsigned short)nextSendSeq;
						buffer[2] = (unsigned short)totalSeq;
						ack[nextSendSeq] = -1;
						memcpy(&buffer[3], &data[totalSeq * 1024], 1024);
						sendto(serverSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
						cout << "成功发送序列号为" << nextSendSeq << "的分组" << endl;
						nextSendSeq = (nextSendSeq + 1) % seqSize;
						Sleep(500);
					}
					recvSize = recvfrom(serverSocket, buffer, BUFFER_LENGTH, 0, ((SOCKADDR*)&clientAddr), &length);
					cout << "ACK打印" << endl;
					for (int i = 0; i < seqSize; i++) {
						cout << ack[i];
					}
					cout << endl;
					if (recvSize < 0) {//没收到ack
						//cout << "没有收到ack" << endl;
						for (int i = 0; i < seqSize; i++) {
							if (ack[i] == -1) {//发送了，还没收到ack
								counts[i] = counts[i] + 1;
								if (counts[i] > 20) {
									counts[i] = 0;//重启计时器
									cout << "序列号" << i << "等待超时，重传" << endl;
									buffer[0] = '1';
									buffer[1] = (unsigned short)i;
									buffer[2] = (unsigned short)totalSeq;
									sendto(serverSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
									cout << "成功发送序列号为" << i << "的分组" << endl;
								}
							}
						}
					}
					else {//收到ack
						int r = buffer[1];
						if (r != -1) {
							cout << "收到ack" << r << endl;
							ack[r] = 1;
							for (int i = 0; i < seqSize; i++) {
								if (ack[i] == -1) {//发送了，还没收到ack
									counts[i] = counts[i] + 1;
									if (counts[i] > 20) {
										counts[i] = 0;//重启计时器
										cout << "序列号" << i << "等待超时，重传" << endl;
										buffer[0] = '1';
										buffer[1] = (unsigned short)i;
										buffer[2] = (unsigned short)totalSeq;
										sendto(serverSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
										cout << "成功发送序列号为" << i << "的分组" << endl;
									}
								}
							}
							bool flag = false;
							if ((r + windowSize) > seqSize) {
								for (int i = base; i < seqSize; i++) {
									if (ack[i] == -1) {
										base = i;
										flag = true;
										break;
									}
								}
								if (!flag) {
									for (int i = 0; i < (windowSize + base - seqSize); i++) {
										if (ack[i] == -1) {
											base = i;
											flag = true;
											break;
										}
									}
								}
								if (!flag) {
									base = nextSendSeq;
								}

							}
							else {
								for (int i = base; i < (base + windowSize); i++) {
									if (ack[i] == -1) {
										base = i;
										flag = true;
										break;
									}
								}
								if (!flag) {
									base = nextSendSeq;
								}
							}
							if (buffer[2] == totalPacket) {
								flag = 0;
								cout << "数据全部发送完" << endl;
							}
						}
						else {
							for (int i = 0; i < seqSize; i++) {
								ack[i] = 1;
							}
							base = 0;
							nextSendSeq = 0;
							totalSeq = 0;
							waitTime = 0;
						}

					}
					Sleep(500);
				}
			}
		}
		sendto(serverSocket, buffer, strlen(buffer) + 1, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
		Sleep(500);
	}
	closesocket(serverSocket);
	WSACleanup();
	return 0;

}

//初始化服务器的套接字
int InitServerConnectSocket() {
	//加载套接字库
	WORD wVersionRequested;
	WSADATA wsaData;
	int error;
	wVersionRequested = MAKEWORD(2, 2);
	error = WSAStartup(wVersionRequested, &wsaData);
	if (error != 0) {
		cout << "加载winsock失败，错误代码为：" << WSAGetLastError() << endl;
		return 0;
	}
	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2)
	{
		cout << "不能找到正确的 winsock 版本\n" << endl;
		WSACleanup();
		return 0;
	}
	serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);//创建UDP套接字
	if (serverSocket == INVALID_SOCKET) {
		cout << "创建套接字失败，代码为：" << WSAGetLastError() << endl;
		return 0;
	}
	int iMode = 1;
	ioctlsocket(serverSocket, FIONBIO, (u_long FAR*)&iMode);//设置为非阻塞
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(SERVER_PORT);
	serverAddr.sin_addr.S_un.S_addr = htonl(INADDR_ANY);
	int bind_return = bind(serverSocket, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
	if (bind_return == -1) {
		cout << "绑定套接字端口失败" << endl;
		WSACleanup();
		return 0;
	}
	return 1;

}

//判断下一个使用的序列号是否可用
BOOL seqIsAvailable() {
	int step = nextSendSeq - base;
	if (step < 0) {
		step = step + seqSize;
	}
	//cout << "step=" << step << ",base=" << base << ",next=" << nextSendSeq << endl;
	if (step >= windowSize) {
		return FALSE;
	}
	if (ack[nextSendSeq] == 1) {
		return TRUE;
	}
	return FALSE;
}




