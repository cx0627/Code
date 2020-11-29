#include <iostream>
#include <clocale>//c->ctype,cmath;locale->local environment
using std::cout;
using std::endl;
using std::wcin;
using std::wcout;
wchar_t s[50045];
int main()
{   
    freopen("test.in", "r", stdin);
    freopen("test1.out", "w", stdout);
	setlocale(LC_ALL, "chs");//输出wchar_t类型的必要条件
	wcin >> s;
    cout << "yes" << endl;
    wcout << s[0] << endl;
    cout << wcslen(s) << endl;
    cout << "yes" << endl;

    return 0;
}
