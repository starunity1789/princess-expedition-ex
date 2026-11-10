"""通过 Steam 客户端更新创意工坊物品 3821602893（只换内容 + 更新说明，不动标题/简介/预览图/可见性）

用法：python tools/upload_workshop.py 2.9
- 需要 Steam 客户端开着并已登录（用游戏目录里的 steam_api64.dll，不需要密码）
- 内容取仓库的 mod/（含不进 git 的 PD 贴图），所以上传前先跑过合并工具与 check_mod.py
- 上传期间 Steam 会显示「正在玩 Stellaris」
- 最后一行 eResult=1 表示成功
"""
import ctypes
import os
import pathlib
import sys
import time
from ctypes import c_bool, c_char_p, c_int, c_uint32, c_uint64, c_void_p, byref

sys.stdout.reconfigure(encoding="utf-8")
if len(sys.argv) < 2:
    sys.exit("用法：python tools/upload_workshop.py <更新说明，例如 2.9>")
APPID = 281990
ITEM = 3821602893
CONTENT = str(pathlib.Path(__file__).resolve().parent.parent / "mod")
NOTE = sys.argv[1]
DLL = r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris\steam_api64.dll"

os.environ["SteamAppId"] = str(APPID)
os.environ["SteamGameId"] = str(APPID)
d = ctypes.WinDLL(DLL)
d.SteamAPI_Init.restype = c_bool
if not d.SteamAPI_Init():
    sys.exit("FAIL SteamAPI_Init（Steam 没开或没登录）")

d.SteamAPI_SteamUGC_v016.restype = c_void_p
d.SteamAPI_SteamUtils_v010.restype = c_void_p
ugc = d.SteamAPI_SteamUGC_v016()
utils = d.SteamAPI_SteamUtils_v010()

d.SteamAPI_ISteamUGC_StartItemUpdate.argtypes = [c_void_p, c_uint32, c_uint64]
d.SteamAPI_ISteamUGC_StartItemUpdate.restype = c_uint64
d.SteamAPI_ISteamUGC_SetItemContent.argtypes = [c_void_p, c_uint64, c_char_p]
d.SteamAPI_ISteamUGC_SetItemContent.restype = c_bool
d.SteamAPI_ISteamUGC_SubmitItemUpdate.argtypes = [c_void_p, c_uint64, c_char_p]
d.SteamAPI_ISteamUGC_SubmitItemUpdate.restype = c_uint64
d.SteamAPI_ISteamUGC_GetItemUpdateProgress.argtypes = [c_void_p, c_uint64, ctypes.POINTER(c_uint64), ctypes.POINTER(c_uint64)]
d.SteamAPI_ISteamUGC_GetItemUpdateProgress.restype = c_int
d.SteamAPI_ISteamUtils_IsAPICallCompleted.argtypes = [c_void_p, c_uint64, ctypes.POINTER(c_bool)]
d.SteamAPI_ISteamUtils_IsAPICallCompleted.restype = c_bool
d.SteamAPI_ISteamUtils_GetAPICallResult.argtypes = [c_void_p, c_uint64, c_void_p, c_int, c_int, ctypes.POINTER(c_bool)]
d.SteamAPI_ISteamUtils_GetAPICallResult.restype = c_bool


class SubmitItemUpdateResult(ctypes.Structure):
    _pack_ = 8
    _fields_ = [("eResult", c_int), ("needsLegal", c_bool), ("fileId", c_uint64)]


h = d.SteamAPI_ISteamUGC_StartItemUpdate(ugc, APPID, ITEM)
if not d.SteamAPI_ISteamUGC_SetItemContent(ugc, h, CONTENT.encode("utf-8")):
    sys.exit("FAIL SetItemContent")
call = d.SteamAPI_ISteamUGC_SubmitItemUpdate(ugc, h, NOTE.encode("utf-8"))
STATUS = {0: "无效", 1: "准备配置", 2: "准备内容", 3: "上传内容", 4: "上传预览图", 5: "提交更改"}
last = None
t0 = time.time()
while True:
    d.SteamAPI_RunCallbacks()
    failed = c_bool(False)
    if d.SteamAPI_ISteamUtils_IsAPICallCompleted(utils, call, byref(failed)):
        r = SubmitItemUpdateResult()
        ok = d.SteamAPI_ISteamUtils_GetAPICallResult(utils, call, byref(r), ctypes.sizeof(r), 3404, byref(failed))
        print(f"DONE ok={ok} failed={failed.value} eResult={r.eResult} needsLegal={r.needsLegal} "
              f"fileId={r.fileId} 用时{int(time.time()-t0)}s", flush=True)
        break
    a, b = c_uint64(0), c_uint64(0)
    st = d.SteamAPI_ISteamUGC_GetItemUpdateProgress(ugc, h, byref(a), byref(b))
    cur = (st, b.value and int(a.value * 10 / b.value))
    if cur != last:
        print(f"{int(time.time()-t0)}s {STATUS.get(st, st)} {a.value/2**20:.0f}/{b.value/2**20:.0f} MB", flush=True)
        last = cur
    time.sleep(0.5)
d.SteamAPI_Shutdown()
