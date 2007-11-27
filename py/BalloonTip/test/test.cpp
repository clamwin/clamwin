// test.cpp : Defines the entry point for the console application.
//

#include <windows.h>
#include <stdio.h>

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
	POINT pt = {500,500};
	LaunchBalloon("Test Title", "Test Text\nTest Text2\nTest nen hele langen tekst want zo kunnen we natuurlijk wel te weten komen waar het probleem nu eigenlijk just zit. AddressInfo blablabla of zo iets. Nu is da hier pertang nog ni lang genoeg om zeker te zijn dus ik moet nog maar wa babbelen he. misschien nu nog is compileren en proberen en hopen da ik het probleem kan repliceren he. Maar da lukt hier precies ni goe dus het zal misschien toch een probleem in Python zijn dus dan moet ik terug daar gaan zoeken. In alle geval zou ik nu toch wel bena genoeg zever moeten hebben he.", pt, IDI_EXCLAMATION, 0x438, NULL, "", 10000);
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

