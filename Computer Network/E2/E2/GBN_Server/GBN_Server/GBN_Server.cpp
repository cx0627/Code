#include <stdlib.h>
#include <time.h>
#include <WinSock2.h>
#include <fstream>
#include<iostream>
#include<Windows.h>

#pragma comment(lib,"ws2_32.lib")

using namespace std;

#define SERVER_PORT 12340 //�˿ں�
#define SERVER_IP "0.0.0.0" //IP ��ַ

const int BUFFER_LENGTH = 1027; //��������С������̫���� UDP ������֡�а�����ӦС�� 1480 �ֽڣ�
//|1 ��1���ֽڣ�|nextSendSeq ��1���ֽڣ�|ackȷ��seq ��1���ֽڣ�|data ��1024���ֽڣ�
int windowSize;//���ʹ��ڴ�С,ͣ��Э��Ϊ1��GBNЭ��Ϊ8
const int seqSize = 20;//���кŸ���

int ack[seqSize];//���յ�ack�������1�����յ���-1����û�յ�
int nextSendSeq;//��һ��Ҫ���͵� seq
int base;//��ǰ�ȴ�ȷ�ϵ� ack
int totalSeq;//�յ��İ�������
int totalPacket;//��Ҫ���͵İ�����

SOCKET serverSocket;//���������׽���
SOCKADDR_IN serverAddr;

int InitServerConnectSocket();
BOOL seqIsAvailable();


int main(int argc, char* argv[]) {
	if (InitServerConnectSocket() == 0) {
		cout << "��ʼ�����������׽���ʧ��" << endl;
		return -1;
	}
	int recvSize;
	for (int i = 0; i < seqSize; i++) {
		ack[i] = 1;
	}
	SOCKADDR_IN clientAddr; //�ͻ��˵�ַ
	int length = sizeof(SOCKADDR);
	char buffer[BUFFER_LENGTH]; //�������ݵĻ�����
	ZeroMemory(buffer, sizeof(buffer));
	char data[1024 * 100];
	ZeroMemory(data, sizeof(data));
	int datalen = 0;
	ifstream file("data.txt");
	while (!file.eof()) {
		file >> data[datalen++];
	}
	//cout << "data:" << data << endl;
	totalPacket = sizeof(data) / 1024;
	int choose;
	cout << "����1����ͣ��Э��" << endl;
	cout << "����2����GBNЭ�飬���ڴ�СΪ8" << endl;
	cout << "�����룺";
	cin >> choose;
	if (choose == 1) {
		windowSize = 1;
	}
	else {
		windowSize = 8;
	}
	while (1) {
		recvSize = recvfrom(serverSocket, buffer, BUFFER_LENGTH, 0, ((SOCKADDR*)&clientAddr), &length);
		if (recvSize < 0) {
			Sleep(200);
			continue;
		}
		cout << "-----�������ӿͻ��˽��յı���------" << endl;
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
			int r_seq=-1;
			while (flag) {//����205
				if (state == 0) {
					buffer[0] = (unsigned short)205;
					sendto(serverSocket, buffer, strlen(buffer) + 1, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
					Sleep(100);
					state = 1;

				}
				else if (state == 1) {//�ȴ�����200
					recvSize = recvfrom(serverSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&clientAddr, &length);
					if (recvSize < 0) {
						waitTime++;
						if (waitTime > 15) {
							flag = 0;
							cout << "û����Ӧ����ʱ��ֹͣ����" << endl;
						}
						else {
							Sleep(500);
						}
					}
					else {
						if ((unsigned char)buffer[0] == 200) {
							cout << "�ļ���ʼ׼������...." << endl;
							base = 0;
							nextSendSeq = 0;
							totalSeq = 0;
							waitTime = 0;
							state = 2;
						}
					}
				}
				else if (state == 2) {//��������
					if (seqIsAvailable() && (totalSeq + 1 <= totalPacket)) {
						totalSeq++;
						buffer[0] = '1';
						buffer[1] = (unsigned short)nextSendSeq;
						buffer[2] = (unsigned short)r_seq;
						ack[nextSendSeq] = -1;
						memcpy(&buffer[3], &data[totalSeq * 1024], 1024);
						sendto(serverSocket, buffer, BUFFER_LENGTH, 0, (SOCKADDR*)&clientAddr, sizeof(SOCKADDR));
						cout << "�ɹ��������к�Ϊ:" << nextSendSeq << "�ķ��鷢��ACK."<<r_seq << endl;
						nextSendSeq = (nextSendSeq + 1) % seqSize;
						Sleep(500);
					}
					recvSize = recvfrom(serverSocket, buffer, BUFFER_LENGTH, 0, ((SOCKADDR*)&clientAddr), &length);
					if (recvSize < 0) {//û�յ�ack
						//cout << "û���յ�ack" << endl;
						waitTime++;
						if (waitTime > 15) {
							waitTime = 0;//������ʱ��
							cout << "���к�" << base << "�ȴ���ʱ���ش�" << endl;
							for (int i = 0; i < windowSize; i++) {
								int index = (i + base) % seqSize;
								ack[index] = 1;
							}
							totalSeq = totalSeq - (nextSendSeq - base);
							nextSendSeq = base;
						}
					}
					else {//�յ�ack
						int r = buffer[1];
						r_seq = buffer[2];
						if (r != -1) {
							cout << "�յ�ack" << r  <<",�յ����к�"<<r_seq<<"�ķ���"<< endl;
							if (r < base) {
								for (int i = base; i < seqSize; i++) {
									ack[i] = 1;
								}
							}
							for (int i = base; i <= r; i++) {
								ack[i] = 1;
							}
							base = (r + 1) % seqSize;
							waitTime = 0;//��ʼ��һ�ֵļ�ʱ
							if (buffer[2] == totalPacket) {
								flag = 0;
								cout << "����ȫ��������" << endl;
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
					cout << endl;
					cout << endl;
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

//��ʼ�����������׽���
int InitServerConnectSocket() {
	//�����׽��ֿ�
	WORD wVersionRequested;
	WSADATA wsaData;
	int error;
	wVersionRequested = MAKEWORD(2, 2);
	error = WSAStartup(wVersionRequested, &wsaData);
	if (error != 0) {
		cout << "����winsockʧ��,�������Ϊ:" << WSAGetLastError() << endl;
		return 0;
	}
	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2)
	{
		cout << "�����ҵ���ȷ�� winsock �汾\n" << endl;
		WSACleanup();
		return 0;
	}
	serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);//����UDP�׽���
	if (serverSocket == INVALID_SOCKET) {
		cout << "�����׽���ʧ�ܣ�����Ϊ��" << WSAGetLastError() << endl;
		return 0;
	}
	int iMode = 1;
	ioctlsocket(serverSocket, FIONBIO, (u_long FAR*)&iMode);//����Ϊ������
	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(SERVER_PORT);
	serverAddr.sin_addr.S_un.S_addr = htonl(INADDR_ANY);
	int bind_return = bind(serverSocket, (SOCKADDR*)&serverAddr, sizeof(SOCKADDR));
	if (bind_return == -1) {
		cout << "���׽��ֶ˿�δ�ɹ�" << endl;
		WSACleanup();
		return 0;
	}
	return 1;

}

//�ж���һ��ʹ�õ����к��Ƿ����
BOOL seqIsAvailable() {
	int step = nextSendSeq - base;
	if (step < 0) {
		step = step + seqSize;
	}
	if (step >= windowSize) {
		return FALSE;
	}
	if (ack[nextSendSeq] == 1) {
		return TRUE;
	}
	return FALSE;
}


