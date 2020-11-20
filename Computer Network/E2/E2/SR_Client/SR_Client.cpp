#include <stdlib.h>
#include <WinSock2.h>
#include <time.h>
#include<iostream>
#include <Ws2tcpip.h>

#pragma comment(lib,"ws2_32.lib")

using namespace std;

//#define _WINSOCK_DEPRECATED_NO_WARNINGS 
#define SERVER_PORT 12340 //�������ݵĶ˿ں�
#define SERVER_IP "127.0.0.1" // �������� IP ��ַ

const int BUFFER_LENGTH = 1027;
const int seqSize = 20;//���кŸ���
const int windowSize = 8;//�������ڴ�С
int rec[seqSize];//���յ����ĵ������1�����յ���-1����û�յ�
int base;

SOCKET clientSocket;//�ͻ����׽���
SOCKADDR_IN serverAddr;

int InitClientSocket();
int ifLoss(float lossRatio);
void sendDataUp(int start, int base, int buffer_1[windowSize]);

int main(int argc, char* argv[]) {
	if (InitClientSocket() == 0) {
		cout << "��ʼ���ͻ��˵��׽���ʧ��" << endl;
		return -1;
	}
	char buffer[BUFFER_LENGTH];
	ZeroMemory(buffer, sizeof(buffer));
	int length = sizeof(SOCKADDR);
	float packetLossRatio = 0.2; //����ʧ�� 
	float ackLossRatio = 0.2; //ACK ��ʧ�� 
	int a;
	int buffer_1[windowSize];//���յ��Ļ��������ݶ�Ӧ�������к�
	ZeroMemory(buffer_1, windowSize);

	while (1) {
		cout << endl;
		cout << "-------------------" << endl;
		cout << "����1����-time" << endl;
		cout << "����2����-quit" << endl;
		cout << "����3����-testgbn" << endl;
		cout << "-------------------" << endl;
		cout << "�����룺";
		cin >> a;
		cout << endl;
		if (a == 1) {
			sendto(clientSocket, "-time", strlen("-time") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
			cout << "ʱ��Ϊ��" << buffer << endl;
		}
		else if (a == 2) {
			sendto(clientSocket, "-quit", strlen("-quit") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
			cout << buffer << endl;
			break;
		}
		else if (a == 3) {
			cout << "�����붪���ʣ�";
			cin >> packetLossRatio;
			cout << "������ack��ʧ�ʣ�";
			cin >> ackLossRatio;
			sendto(clientSocket, "-testgbn", strlen("-testgbn") + 1, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
			int state = 0;
			//int waitSeq = -1;
			ZeroMemory(rec, seqSize);

			while (1) {
				int a = recvfrom(clientSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&serverAddr, &length);
				//cout << "�ͻ����յ����Ĵ�С��" << a << endl;
				if (state == 0) {//��������
					if ((unsigned char)buffer[0] == 205) {
						buffer[0] = (unsigned short)200;
						buffer[1] = '\0';
						cout << "���յ��������󣬿��Կ�ʼ����" << endl;
						sendto(clientSocket, buffer, 2, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
						state = 1;
						base = 0;
						for (int i = 0; i < windowSize; i++) {
							rec[i] = 1;
						}
					}
				}
				else if (state == 1) {//�ȴ��������ݷ���ACK

					int recvSeq = buffer[1];
					if (ifLoss(packetLossRatio) == 1) {//�жϰ��Ƿ�ʧ
						cout << "���к�Ϊ" << recvSeq << "�Ĵ��䱨�Ķ�ʧ" << endl;
						continue;
					}
					cout << "���յ����к�Ϊ" << recvSeq << "�İ�" << endl;
					int step;
					if ((base + windowSize) >= seqSize) {
						if (((recvSeq >= base) && (recvSeq < seqSize)) || ((recvSeq >= 0) && (recvSeq < (windowSize + base - seqSize)))) {
							//�ڴ�����
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
							
							if ((start - base) != 0) {//���ڻ���
								sendDataUp(start, base, buffer_1);
							}


						}
					}
					else {

						if ((recvSeq >= base) && (recvSeq < base + windowSize)) {

							//�ڴ�����
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
							if ((start - base) != 0) {//���ڻ���
								sendDataUp(start, base, buffer_1);
							}


						}
					}
					buffer[0] = '1';
					buffer[1] = (unsigned short)recvSeq;
					buffer[2] = '\0';
					if (ifLoss(ackLossRatio) == 1) {//�ж�ack�Ƿ�ʧ
						cout << "ACK" << recvSeq << "��ʧ" << endl;
						continue;
					}
					sendto(clientSocket, buffer, 3, 0, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));//����ACK����
					cout << "����ACK" << recvSeq << endl;
					
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
	//�����׽��ֿ⣨���룩
	WORD wVersionRequested;
	WSADATA wsaData;
	//�׽��ּ���ʱ������ʾ
	int err;
	//�汾 2.2
	wVersionRequested = MAKEWORD(2, 2);
	//���� dll �ļ� Scoket ��
	err = WSAStartup(wVersionRequested, &wsaData);
	if (err != 0) {
		//�Ҳ��� winsock.dll
		cout << "����winsockʧ�ܣ��������Ϊ��" << WSAGetLastError() << endl;
		return 0;
	}
	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2) {
		cout << "�����ҵ���ȷ�� winsock �汾\n" << endl;
		WSACleanup();
		return 0;
	}
	clientSocket = socket(AF_INET, SOCK_DGRAM, 0);
	InetPton(AF_INET, TEXT(SERVER_IP), &serverAddr.sin_addr.S_un.S_addr);
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(SERVER_PORT);
	return 1;
}

//���ݶ�ʧ��ģ���Ƿ�ʧ
int ifLoss(float lossRatio) {
	int RanddomNumber = rand() % 101;
	if (RanddomNumber < (int)(lossRatio * 100)) {//��ʧ
		return 1;
	}
	return -1;//����ʧ
}


//���ϲ㰴��˳�򽻸�����
void sendDataUp(int start, int base, int buffer_1[windowSize]) {
	cout << "���ϲ㽻������(��������кţ���" ;
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

