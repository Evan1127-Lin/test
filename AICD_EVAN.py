import sys
import os

import PyQt5
import imageio
import numpy as np
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *

import cva
import irmad
import isfa
import dcva_UnequalRowColumn
import dsfa_main
import kpcamnet_train
import acc_ass
import compare
import overlay

# 导入UI代码文件
import CDGUI
import AssessGUI
import instructionGUI
import aboutGUI
# from CDGUI import Ui_MainWindow
# from AssessGUI import Ui_dialog
# from instructionGUI import Ui_Form
# from aboutGUI import Ui_Form

def CVA(image_path1, image_path2, threshold_algorithm):
    cva.main(image_path1, image_path2, threshold_algorithm)

def IRMAD(image_path1, image_path2, threshold_algorithm):
    irmad.main(image_path1, image_path2, threshold_algorithm)

def SFA(image_path1, image_path2, threshold_algorithm):
    isfa.main(image_path1, image_path2, threshold_algorithm)

def DCVA(image_path1, image_path2, threshold_algorithm):
    dcva_UnequalRowColumn.main(image_path1, image_path2, threshold_algorithm)
    # print('method:%s,%s,%s,%s' % ('DCVA',image_path1, image_path2, threshold_algorithm))

def DSFA(image_path1, image_path2, threshold_algorithm):
    dsfa_main.main(image_path1, image_path2, threshold_algorithm)
    # print('method:%s,%s,%s,%s' % ('DSFA',image_path1, image_path2, threshold_algorithm))

def KPCA_MNet(image_path1, image_path2, threshold_algorithm):
    kpcamnet_train.train_net(image_path1, image_path2, threshold_algorithm)
    # print('method:%s,%s,%s,%s' % ('KPCA_MNet',image_path1, image_path2, threshold_algorithm))


def openimage(graphicsview, lineedit):
    imagepath, imagetype = QtWidgets.QFileDialog.getOpenFileName(None, "打开图像", "", '影像文件 (*.png *.bmp '
                                                                                   '*.tif *.tiff *.jpg *.jpeg)')
    img = QtGui.QPixmap(imagepath).scaled(graphicsview.width(), graphicsview.height())
    # item = QtWidgets.QGraphicsPixmapItem(img)  # 把pixmap转成item
    scene = QtWidgets.QGraphicsScene()  # 新建一个用于graphicview的scene
    # scene.addItem(item)  # 将图片item添加到scene中
    scene.addPixmap(img)
    graphicsview.setScene(scene)  # 在graphicview中设置
    lineedit.setText(imagepath)

def saveimgresult(lineedit):
    filename = QtWidgets.QFileDialog.getSaveFileName(None, "保存图像", "", 'Image files (*.png *.bmp '
                                                                                   '*.tiff *.jpg *.jpeg)')
    if filename[0] != '':
        img_path = lineedit.text()
        img = imageio.imread(img_path)
        imageio.imsave(filename[0], img)
        showinformationmsgbox('提示', '图像结果已保存为：%s！' % filename[0])
    else:
        pass

def savetxtresult(tablewidget):
    filename = QtWidgets.QFileDialog.getSaveFileName(None, "保存结果", "")
    if filename[0] != '':
        with open(filename[0], 'w') as f:
            for row in range(5):
                result = tablewidget.item(row, 0).text() + ':' + tablewidget.item(row, 1).text() + '\n'
                f.write(result)
        showinformationmsgbox('提示', '计算结果已保存为：%s！' % filename[0])
    else:
        pass

def showinformationmsgbox(title, message):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, title, message)
    msg_box_icon = QtGui.QIcon('./logo.png')
    msg_box.setWindowIcon(msg_box_icon)
    msg_box.exec_()


# 多线程
class MyCDThread(QtCore.QThread):
    # 创建信号，发送str类型数据
    trigger = QtCore.pyqtSignal(str)
    def __init__(self):
        super(MyCDThread, self).__init__()

    def run(self, lineedit_path1, lineedit_path2, lineedit_cd, combox_method, combobox_threshold_algorithm,
           graphicsview_cd, graphicsview_t1masked, graphicsview_t2masked, lineedit_t1masked, lineedit_t2masked):

        image_path1 = lineedit_path1.text()
        image_path2 = lineedit_path2.text()
        threshold_algorithm = combobox_threshold_algorithm.currentText()
        cd_method = combox_method.currentText()
        lineedit_cd.setText('变化检测中...请稍后')
        QtWidgets.QApplication.processEvents()  # 在耗时的程序中保持UI刷新
        if cd_method == 'CVA':
            self.CVA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'IR-MAD':
            self.IRMAD(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'SFA':
            self.SFA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'DCVA':
            self.DCVA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'DSFA':
            self.DSFA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'KPCA-MNet':
            self.KPCA_MNet(image_path1, image_path2, threshold_algorithm)
        # print(image_path1, image_path2, cd_method, threshold_algorithm)
        self.showresult(graphicsview_cd, cd_method, lineedit_cd)
        self.showoverlay(graphicsview_t1masked, lineedit_path1, lineedit_cd, 'mask1.png', lineedit_t1masked)
        self.showoverlay(graphicsview_t2masked, lineedit_path2, lineedit_cd, 'mask2.png', lineedit_t2masked)
        self.trigger.emit("success")

# 重写主窗口类
class CDmainWindow(QtWidgets.QMainWindow, CDGUI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def closeEvent(self, event):  # 关闭窗口触发以下事件
        QuitMessageBox = QtWidgets.QMessageBox()
        msg_box_icon = QtGui.QIcon('./logo.png')
        QuitMessageBox.setWindowIcon(msg_box_icon)
        QuitMessageBox.setWindowTitle('退出确认')
        QuitMessageBox.setText('确定要退出程序吗？')
        QuitMessageBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        button_yes = QuitMessageBox.button(QtWidgets.QMessageBox.Yes)
        button_yes.setText('是')
        button_no = QuitMessageBox.button(QtWidgets.QMessageBox.No)
        button_no.setText('否')
        QuitMessageBox.exec_()
        if QuitMessageBox.clickedButton() == button_yes:
            event.accept()
        else:
            event.ignore()

    def showthreshold(self):
        method = self.comboBox_method.currentText()
        if method == 'DCVA':
            self.comboBox_threshold.setItemText(0, "k-means")
            self.comboBox_threshold.setItemText(1, "otsu")
            self.comboBox_threshold.removeItem(2)

        else:
            self.comboBox_threshold.setItemText(0, "k-means")
            self.comboBox_threshold.setItemText(1, "otsu")
            self.comboBox_threshold.removeItem(2)

    def showresult(self, graphicsview, method, lineedit_cd):
        working_path = os.path.dirname(os.path.abspath(__file__))
        if method == 'CVA':
            result_path = os.path.join(working_path, 'CVA_result', 'CVA_result.png')
        elif method == 'IR-MAD':
            result_path = os.path.join(working_path, 'IR-MAD_result', 'IR-MAD_result.png')
        elif method == 'SFA':
            result_path = os.path.join(working_path, 'SFA_result', 'SFA_result.png')
        elif method == 'DCVA':
            result_path = os.path.join(working_path, 'DCVA_result', 'DCVA_result.png')
        elif method == 'DSFA':
            result_path = os.path.join(working_path, 'DSFA_result', 'DSFA_result.png')
        elif method == 'KPCA-MNet':
            result_path = os.path.join(working_path, 'KPCA-MNet_Result', 'KPCA-MNet_Result.png')
        lineedit_cd.setText(result_path)
        result_img = QtGui.QPixmap(result_path).scaled(graphicsview.width(), graphicsview.height())
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(result_img)
        graphicsview.setScene(scene)

    def showoverlay(self, graphicsview_mask, lineedit_raw, lineedit_cd, result_name, lineedit_masked):
        raw_img = lineedit_raw.text()
        cd_img = (lineedit_cd.text()).replace('\\', '/')
        overlay.overlay(raw_img, cd_img, result_name)
        working_path = os.path.dirname(os.path.abspath(__file__))
        result_path = os.path.join(working_path, 'overlay_result', result_name)
        result_img = QtGui.QPixmap(result_path).scaled(graphicsview_mask.width(),graphicsview_mask.height())
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(result_img)
        graphicsview_mask.setScene(scene)
        lineedit_masked.setText(result_path)


    def CD(self, lineedit_path1, lineedit_path2, lineedit_cd, combox_method, combobox_threshold_algorithm,
           graphicsview_cd, graphicsview_t1masked, graphicsview_t2masked, lineedit_t1masked, lineedit_t2masked):
        # self.thread = MyCDThread()
        # self.thread.trigger.connect(self.finish)
        # self.thread.start()

        # img = QtGui.QPixmap("F:\\Evan\\Tongji\\14\\毕业设计\\code\\CD_GUI\\detecting.jpg").scaled(graphicsview_cd.width(),
        #                                                                                   graphicsview_cd.height())
        # scene = QtWidgets.QGraphicsScene()
        # scene.addPixmap(img)
        # graphicsview_cd.setScene(scene)
        lineedit_cd.setText('变化检测中...')
        QtWidgets.QApplication.processEvents()  # 在耗时的程序中保持UI刷新

        image_path1 = lineedit_path1.text()
        image_path2 = lineedit_path2.text()
        threshold_algorithm = combobox_threshold_algorithm.currentText()
        cd_method = combox_method.currentText()
        if cd_method == 'CVA':
            CVA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'IR-MAD':
            IRMAD(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'SFA':
            SFA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'DCVA':
            DCVA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'DSFA':
            DSFA(image_path1, image_path2, threshold_algorithm)
        elif cd_method == 'KPCA-MNet':
            KPCA_MNet(image_path1, image_path2, threshold_algorithm)
        # print(image_path1, image_path2, cd_method, threshold_algorithm)
        self.showresult(graphicsview_cd, cd_method, lineedit_cd)
        self.showoverlay(graphicsview_t1masked, lineedit_path1, lineedit_cd, 'mask1.png', lineedit_t1masked)
        self.showoverlay(graphicsview_t2masked, lineedit_path2, lineedit_cd, 'mask2.png', lineedit_t2masked)
        showinformationmsgbox('提示', '变化检测已完成！')

    # 多线程备用
    # def finish(self, msg):
    #     print('msg: {}'.format(msg))

    def reset(self):
        img = QtGui.QPixmap()
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img)
        self.graphicsView_T1.setScene(scene)
        self.graphicsView_T2.setScene(scene)
        self.graphicsView_CD.setScene(scene)
        self.graphicsView_T1mask.setScene(scene)
        self.graphicsView_T2mask.setScene(scene)
        self.lineEdit_T1PATH.setText('')
        self.lineEdit_T2PATH.setText('')
        self.lineEdit_CDPATH.setText('')
        self.lineEdit_T1maskPATH.setText('')
        self.lineEdit_T2maskPATH.setText('')
        showinformationmsgbox('提示', '数据已重置，可重新进行变化检测！')


# 重写子窗口类
class AssessDialog(QtWidgets.QDialog, AssessGUI.Ui_dialog):
    def __init__(self):
        super(AssessDialog, self).__init__()
        self.setupUi(self)
    def openassess(self, lineedit_CD):
        self.show()
        CD_PATH = lineedit_CD.text()
        cd_img = QtGui.QPixmap(CD_PATH).scaled(self.graphicsView_CD.width(), self.graphicsView_CD.height())
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(cd_img)
        self.graphicsView_CD.setScene(scene)
        self.lineEdit_CDPATH.setText(CD_PATH)
    def assess(self):
        self.lineEdit_COMPARE.setText('精度评估中...')
        QtWidgets.QApplication.processEvents()  # 在耗时的程序中保持UI刷新
        gt_path = self.lineEdit_GTPATH.text()
        gt_map = imageio.imread(gt_path)
        cd_path = self.lineEdit_CDPATH.text()
        cd_map = np.array(Image.open(cd_path).convert('L')).astype('uint8')
        test_metrics = acc_ass.initialize_metrics()
        conf_mat, oa, kappa_co, precision, recall, F1 = acc_ass.assess_accuracy(gt_map, cd_map)
        test_metrics = acc_ass.set_test_metrics(test_metrics, oa, kappa_co, precision, recall, F1)
        row = 0
        for key in test_metrics:
            tableitem_key = QtWidgets.QTableWidgetItem('%s' % key)
            tableitem_value = QtWidgets.QTableWidgetItem('%.4f' % test_metrics[key][0])
            tableitem_key.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            tableitem_value.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, tableitem_key)
            self.tableWidget.setItem(row, 1, tableitem_value)
            row += 1
            # self.textBrowser.append('%s: %.4f\n' % (key, test_metrics[key][0]))
            # f.write('%s: %.4f\n' % (key, test_metrics[key][0]))
        # f.write(20 * '--' + '\n')
        compare.compare(gt_map, cd_map)
        working_dir = os.path.dirname(os.path.abspath(__file__))
        compare_img_path = os.path.join(working_dir, 'compare_result/compare_result.png')
        compare_img = QtGui.QPixmap(compare_img_path).scaled(self.graphicsView_DI.width(), self.graphicsView_DI.height())
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(compare_img)
        self.graphicsView_DI.setScene(scene)
        self.lineEdit_COMPARE.setText(compare_img_path)
        showinformationmsgbox('提示', '精度评估已完成！')


    def reset(self):
        img = QtGui.QPixmap()
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(img)
        self.graphicsView_CD.setScene(scene)
        self.graphicsView_GT.setScene(scene)
        self.graphicsView_DI.setScene(scene)
        self.lineEdit_CDPATH.setText('')
        self.lineEdit_GTPATH.setText('')
        self.lineEdit_COMPARE.setText('')
        self.tableWidget.clearContents()
        showinformationmsgbox('提示', '数据已重置，可重新进行精度评估！')


class InstructionDialog(QtWidgets.QDialog, instructionGUI.Ui_Form):
    def __init__(self):
        super(InstructionDialog, self).__init__()
        self.setupUi(self)

    def openinstruction(self):
        self.show()

class AboutDialog(QtWidgets.QDialog, aboutGUI.Ui_Form):
    def __init__(self):
        super(AboutDialog, self).__init__()
        self.setupUi(self)

    def openabout(self):
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = CDmainWindow()
    assessdialog = AssessDialog()
    instructiondialog = InstructionDialog()
    aboutdialog = AboutDialog()
    mainWindow.show()
    mainWindow.action_loadT1.triggered.connect(
        lambda: openimage(mainWindow.graphicsView_T1, mainWindow.lineEdit_T1PATH))  # 无参数时不可以写成self.openimage()。要加lambda才可以传参数
    mainWindow.action_loadT2.triggered.connect(
        lambda: openimage(mainWindow.graphicsView_T2, mainWindow.lineEdit_T2PATH))

    # cdthread = MyCDThread()
    # cdthread.start()
    mainWindow.pushButton_CD.clicked.connect(
        lambda: mainWindow.CD(mainWindow.lineEdit_T1PATH, mainWindow.lineEdit_T2PATH, mainWindow.lineEdit_CDPATH,
                              mainWindow.comboBox_method, mainWindow.comboBox_threshold, mainWindow.graphicsView_CD,
                              mainWindow.graphicsView_T1mask, mainWindow.graphicsView_T2mask, mainWindow.lineEdit_T1maskPATH, mainWindow.lineEdit_T2maskPATH))
    mainWindow.action_assess.triggered.connect(
        lambda: assessdialog.openassess(mainWindow.lineEdit_CDPATH))
    mainWindow.action_cdmap.triggered.connect(
        lambda: saveimgresult(mainWindow.lineEdit_CDPATH))
    mainWindow.action_augT1.triggered.connect(
        lambda: saveimgresult(mainWindow.lineEdit_T1maskPATH))
    mainWindow.action_augT2.triggered.connect(
        lambda: saveimgresult(mainWindow.lineEdit_T2maskPATH))
    mainWindow.comboBox_method.activated.connect(mainWindow.showthreshold)
    mainWindow.pushButton_reset.clicked.connect(mainWindow.reset)
    mainWindow.action_instruction.triggered.connect(instructiondialog.openinstruction)
    mainWindow.action_about.triggered.connect(aboutdialog.openabout)


    assessdialog.pushButton_changeCD.clicked.connect(
        lambda: openimage(assessdialog.graphicsView_CD, assessdialog.lineEdit_CDPATH))
    assessdialog.pushButton_importGT.clicked.connect(
        lambda: openimage(assessdialog.graphicsView_GT, assessdialog.lineEdit_GTPATH))
    assessdialog.pushButton_assess.clicked.connect(assessdialog.assess)
    assessdialog.pushButton_export_compare.clicked.connect(
        lambda: saveimgresult(assessdialog.lineEdit_COMPARE))
    assessdialog.pushButton_export_accuracy.clicked.connect(
        lambda: savetxtresult(assessdialog.tableWidget))
    assessdialog.pushButton_reset.clicked.connect(assessdialog.reset)
    sys.exit(app.exec_())
