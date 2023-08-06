import time
from jnius import autoclass
import platform
from  plyer.platforms.android import activity
from kivy.app import App
from jnius import autoclass ,cast
from android.runnable import run_on_ui_thread
packagemanager = autoclass("android.content.pm.PackageManager")
context=autoclass("android.content.Context")
Context = autoclass('android.content.Context')
window=autoclass ('android.view.WindowManager$LayoutParams')
getL=autoclass("java.util.Locale")

def get_permissions(package_name):
    f=""
    a = activity.getPackageManager().getPackageInfo(package_name, packagemanager.GET_PERMISSIONS)
    if a!=None:
        for i in a.requestedPermissions:
            f+=i+"\n"
    else:
        return "None"
    return f
def getLanguage():
    return  getL.getDefault().getDisplayLanguage()
def unhide(package_name,package_name_activity):
    p= activity.getPackageManager()
    c=com(package_name,package_name_activity)
    p.setComponentEnabledSetting(c,pak.COMPONENT_ENABLED_STATE_ENABLED,pak.DONT_KILL_APP)
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







    
            
