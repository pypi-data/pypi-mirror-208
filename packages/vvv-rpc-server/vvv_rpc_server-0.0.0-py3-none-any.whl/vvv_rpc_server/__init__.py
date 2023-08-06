import shutil
import os
import sys
import time
import tempfile
def extractall(self, path=None, members=None, pwd=None):
    if members is None: members = self.namelist()
    path = os.getcwd() if path is None else os.fspath(path)
    for zipinfo in members:
        try:    _zipinfo = zipinfo.encode('cp437').decode('gbk')
        except: _zipinfo = zipinfo.encode('utf-8').decode('utf-8')
        print('[*] unpack...', _zipinfo)
        if _zipinfo.endswith('/') or _zipinfo.endswith('\\'):
            myp = os.path.join(path, _zipinfo)
            if not os.path.isdir(myp):
                os.makedirs(myp)
        else:
            myp = os.path.join(path, _zipinfo)
            youp = os.path.join(path, zipinfo)
            self.extract(zipinfo, path)
            if myp != youp:
                os.rename(youp, myp)
import zipfile
zipfile.ZipFile.extractall = extractall

def creat_windows_shortcut(exe_path):
    vbsscript = '\n'.join([
        'set WshShell = WScript.CreateObject("WScript.Shell" )',
        'set oShellLink = WshShell.CreateShortcut(Wscript.Arguments.Named("shortcut") & ".lnk")',
        'oShellLink.TargetPath = Wscript.Arguments.Named("target")',
        'oShellLink.WindowStyle = 1',
        'oShellLink.Save',
    ])

    s = tempfile.mkdtemp()
    try:
        vbs = os.path.join(s, 'temp.vbs')
        with open(vbs, 'w', encoding='utf-8') as f:
            f.write(vbsscript)
        exe  = exe_path
        link = os.path.join(os.path.expanduser("~"),'Desktop','v_chrome')
        if os.path.isfile(link + '.lnk'):
            os.remove(link + '.lnk')
        cmd = r'''
        {} /target:"{}" /shortcut:"{}"
        '''.format(vbs, exe, link).strip()
        print('[*] make shortcut in Desktop:', cmd)
        v = os.popen(cmd)
        v.read()
        v.close()
    finally:
        import traceback;
        if traceback.format_exc().strip() != 'NoneType: None':
            print('create shortcut failed.')
            traceback.print_exc()
        shutil.rmtree(s)

def get_v_path_info():
    localpath = os.path.dirname(__file__)
    v_chrome_file = os.path.join(localpath, 'chrome-win32-x64.zip')
    v_chrome_main_file = os.path.join(localpath, 'chrome-exe.zip')
    # v_chrome_target = os.path.join(localpath, 'chrome-win32-x64')
    v_chrome_target = os.path.join(os.path.split(sys.executable)[0], 'Scripts', 'chrome-win32-x64')
    v_chrome_exec_path = os.path.join(v_chrome_target, 'chrome-win32-x64')
    v_chrome_exec = os.path.join(v_chrome_target, 'chrome-win32-x64', 'v_chrome.exe')
    v_chrome_update = os.path.join(v_chrome_target, 'chrome-win32-x64', 'resources', 'app')
    return localpath, v_chrome_file, v_chrome_main_file, v_chrome_exec_path, v_chrome_target, v_chrome_exec, v_chrome_update

def install():
    localpath, v_chrome_file, v_chrome_main_file, v_chrome_exec_path, v_chrome_target, v_chrome_exec, v_chrome_update = get_v_path_info()
    print('[*] zip file path ===>', v_chrome_file)
    print('[*] exe file path ===>', v_chrome_exec)
    if not os.path.isdir(v_chrome_target):
        print('[*] unpack...')
        f = zipfile.ZipFile(v_chrome_file, 'r')
        f.extractall(v_chrome_target)
        f.close()
        f = zipfile.ZipFile(v_chrome_main_file, 'r')
        f.extractall(v_chrome_exec_path)
        f.close()
        print('[*] unpacked path ===>', v_chrome_target)
    main1, main2 = get_update()
    shutil.copy(main1, v_chrome_update)
    shutil.copy(main2, v_chrome_update)
    creat_windows_shortcut(v_chrome_exec)

def remove():
    localpath, v_chrome_file, v_chrome_main_file, v_chrome_exec_path, v_chrome_target, v_chrome_exec, v_chrome_update = get_v_path_info()
    if os.path.isdir(v_chrome_target):
        os.popen('taskkill /f /im v_chrome.exe /t').read()
        print('[*] remove...', v_chrome_target)
        for i in range(10):
            try:
                shutil.rmtree(v_chrome_target)
                break
            except:
                print('[*] wait...')
                time.sleep(0.2)

def get_update():
    import vvv_rpc_server_update
    path = os.path.split(vvv_rpc_server_update.__file__)[0]
    main1 = os.path.join(path, 'main.js')
    main2 = os.path.join(path, 'main.kfcvme50')
    return main1, main2

def execute():
    argv = sys.argv
    print('v_server :::: [ {} ]'.format(' '.join(argv)))
    if len(argv) == 1:
        print('[install]:  v_server install')
        print('[remove]:   v_server remove')
        return
    if len(argv) > 1:
        if argv[1] == 'install':
            install()
        if argv[1] == 'remove':
            remove()

if __name__ == '__main__':
    # execute()
    install()
    # remove()
    pass
