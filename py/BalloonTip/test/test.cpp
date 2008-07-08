// test.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <windows.h>
extern "C"  void LaunchBalloon(LPCTSTR strTitle, LPCTSTR strContent,
               POINT& ptAnchor,
               LPCTSTR szIcon,
               unsigned int unOptions,
               HWND hParentWnd,
               LPCTSTR strURL,
               unsigned int unTimeout);


int main(int argc, char* argv[])
{
	printf("Hello World!\n");
	POINT pt = {100,100};
	LaunchBalloon("Test Title", "Test Text\nTest Text2", pt, IDI_EXCLAMATION, 0x438, NULL, "", 10000);
	// Start the message loop.

	BOOL bRet;
	MSG msg;

   while((bRet = GetMessage( &msg, NULL, 0, 0 )) != 0)
   {
      if (bRet == -1)
      {
          // handle the error and possibly exit
      }
      else
      {
          TranslateMessage(&msg);
          DispatchMessage(&msg);
      }
    }

	return 0;
}

