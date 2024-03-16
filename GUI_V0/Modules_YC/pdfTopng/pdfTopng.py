# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：pdfTopng.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2022/2/21 22:33 
'''
import os
import sys
import fitz
def pyMuPDF_fitz(pdfPath, imagePath, zoomFactor=1.33333333):
    if pdfPath:
        head, tail = os.path.split(pdfPath)
        FilNam, FilFormat = os.path.splitext(tail)
    else:
        print("IOError:No such file or directory")

    pdfDoc = fitz.open(pdfPath)
    if pdfDoc.pageCount>1:
        for pg in range(pdfDoc.pageCount):
            page = pdfDoc[pg]
            rotate = int(0)
            # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
            # 此处若是不做设置，默认图片大小为：792X612, dpi=96
            zoom_x = zoomFactor  # (1.33333333-->1056x816)   (2-->1584x1224)
            zoom_y = zoomFactor
            mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pix = page.getPixmap(matrix=mat, alpha=False)
            if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
                os.makedirs(imagePath)  # 若图片文件夹不存在就创建
                # newfilename = pdfPath[:-4] + str(pg) + '.jpeg'
            # pix.writePNG(imagePath + '/' + 'images_%s.png' % pg)  # 将图片写入指定的文件夹内
            pix.writePNG(imagePath + '/' + FilNam + '_%s.png' % pg)  # 将图片写入指定的文件夹内
    else:
        page = pdfDoc[0]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = zoomFactor  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = zoomFactor
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
            os.makedirs(imagePath)  # 若图片文件夹不存在就创建
            # newfilename = pdfPath[:-4] + str(pg) + '.jpeg'
        # pix.writePNG(imagePath + '/' + 'images_%s.png' % pg)  # 将图片写入指定的文件夹内
        pix.writePNG(imagePath + '/' + FilNam + '.png')  # 将图片写入指定的文件夹内
    pdfDoc.close()

if __name__ == "__main__":
    # pdfPath = r"E:\tst\cleanup_labelmap96_src.pdf"
    pdfPath = sys.argv[1]
    # imagePath = r"E:\tst"
    imagePath = sys.argv[2]
    if len(sys.argv)>3:
        zoomFactor = sys.argv[3]
        pyMuPDF_fitz(pdfPath, imagePath, zoomFactor)
    else:
        pyMuPDF_fitz(pdfPath, imagePath)



