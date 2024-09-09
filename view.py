from aqt.qt import QMessageBox
from aqt import gui_hooks
from aqt import mw

# 初始化全局变量以存储弹窗对象
sync_popup = None

def start_sync_popup():
    """
    显示一个正在同步的提示窗口。
    """
    global sync_popup
    # 创建并显示消息框
    sync_popup = QMessageBox(mw)
    sync_popup.setWindowTitle("Syncing with Notion")
    sync_popup.setText("Anki is syncing, please wait...")
    sync_popup.setStandardButtons(QMessageBox.StandardButton.NoButton)
    sync_popup.setModal(True)
    sync_popup.show()
    print("syncing popup shown")

def close_sync_popup():
    """
    在同步完成时关闭弹窗。
    """
    global sync_popup
    if sync_popup:
        sync_popup.close()
        print("syncing popup closed")
        sync_popup = None  # 释放弹窗对象
