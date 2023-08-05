import time
from jnius import autoclass
import platform

context=autoclass("android.content.Context")
from  plyer.platforms.android import activity
Context = autoclass('android.content.Context')
window=autoclass ('android.view.WindowManager$LayoutParams')
from kivy.app import App
from jnius import autoclass ,cast
from android.runnable import run_on_ui_thread
def hide(package_name,package_name_activity):
    p= activity.getPackageManager()
    c=com(package_name,package_name_activity)
    p.setComponentEnabledSetting(c,pak.COMPONENT_ENABLED_STATE_DISABLED,pak.DONT_KILL_APP)
def isSecure():
    x=cast ("android.app.KeyguardManager",activity.getSystemService(Context.KEYGUARD_SERVICE)  )
    h=x.isKeyguardSecure()
    if(h):
        return True
    else:
        return False
def isMusicActive():
    x = cast("android.media.AudioManager", activity.getSystemService(Context.AUDIO_SERVICE))
    h = x.isMusicActive()
    if (h):
        return True
    else:
        return False
@run_on_ui_thread
def screen_Secure():
    z = activity.getWindow()
    z.setFlags(window.FLAG_SECURE, window.FLAG_SECURE)

def isWiredHeadsetOn():
    h = x.isWiredHeadsetOn()
    if (h):
        return True
    else:
        return False







    
            
