# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/6/28 0028
__author__ = 'huohuo'
import datetime
import os
import fitz
import glob
import PythonMagick
from PythonMagick import Image
bgcolor = '#FFFFFF'


def pdf2img(input_pdf, postfix='.png', **kwargs):
    # print os.path.exists(input_pdf)
    img = Image(input_pdf)
    img.density('300')
    size = "%sx%s" % (img.columns(), img.rows())
    output_img = Image(size, bgcolor)
    output_img.type = img.type
    output_img.composite(img, 0, 0, PythonMagick.CompositeOperator.SrcOverCompositeOp)
    output_img.resize(str(img.rows()))
    output_img.magick('JPG')
    output_img.quality(75)
    if 'out_path' in kwargs:
        output_jpg = kwargs['out_path']
    else:
        output_jpg = input_pdf + postfix
    if os.path.exists(output_jpg):
        os.remove(output_jpg)
    output_img.write(output_jpg)


if __name__ == "__main__":
    pdffilename = '/tumor/facets_cval_50.pdf'
    img_path = '/tumor/image'
    # pdf2img(pdf_path)
    import PyPDF2
    pdf_im = PyPDF2.PdfFileReader(file(pdffilename, "rb"))
    npage = pdf_im.getNumPages()
    print(npage)
    for p in range(npage):
        p1 = '%s[%s]' % (pdffilename, p)
        print p1
        p_path = os.path.join(img_path), 'tumor_balanced_vafs%s.png' % p
        im = PythonMagick.Image(p1)
        im.density('3000')
        im.write(p_path)
        # try:
        #
        # # try:
        # #     pdf2img('%s[%s]' % (pdffilename, p))
        # except:
        #
        #     continue

    # for p in range(npage):
    #     im = PythonMagick.Image()
    #     im.density('300')
    #     im.read(pdffilename + '[' + str(p) +']')
    #     im.write('file_out-' + str(p)+ '.png')
    #     #im.read(pdffilename + '[' + str(p) +']')


# pyMuPDF_fitz(pdf_path, img_path)
    pass

    

