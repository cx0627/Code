#include <iostream>
#include <stdio.h>
#include <string.h>
#include <locale>
#include <wchar.h>
using namespace std;

wchar_t str[5005];

int main(){
    freopen("test.in","r",stdin);
    // setlocale(LC_ALL,"zh_CN.GBK");
    printf("yes");
    wscanf(L"%ls",str);
    int len = wcslen(str);
    printf("yes");
    cout << len << endl;
    // for(int i=0;i<len;i++)
        // wcout << sizeof(str[0]) << endl;
    printf("%d\n",str[0]);
    printf("%lc\n",str[1]*256+str[0]);
    return 0;
}