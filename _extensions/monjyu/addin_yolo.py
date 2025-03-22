#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

import json

import os
import codecs

from PIL import Image

import numpy as np
import cv2



class yolov8_class:
    def __init__(self, ):
        
        # yolov8 -> onnx
        self.yolov8_procSize        = 640
        #self.yolov8_model = YOLO('_datas/yolov8/yolov8n.pt')
        #self.yolov8_model.export(format='onnx', imgsz=self.yolov8_procSize, opset=12, )

        # yolov8
        self.yolov8_weights         = '_datas/yolov8/yolov8n.onnx'
        self.yolov8_model           = None
        self.yolov8_threshold_score = 0.8
        self.yolov8_threshold_nms   = 0.45
        self.yolov8_labels          = []
        self.yolov8_colors          = []
        res, _                      = self.txtsRead('_datas/yolov8/yolov8_labels.txt', )
        if (res != False):
            self.yolov8_labels      = res
        for n in range(len(self.yolov8_labels)):
            self.yolov8_colors.append(np.random.randint(low=0, high=255, size=3, dtype=np.uint8))

    # yolov8
    def cv2detect_yolov8(self, inp_image=None, base_image=None, ):
        res_detect = {}
        out_image  = None

        # 初回モデル構築
        if (self.yolov8_model is None):
            try:
                self.yolov8_model : cv2.dnn.Net = cv2.dnn.readNetFromONNX(self.yolov8_weights)
                print('cv2detect_yolov8 : "' + self.yolov8_weights + '" loading complite!')
            except Exception as e:
                print(e)
                self.yolov8_model = None

        # エラー？
        if (self.yolov8_model is None):
            return res_detect, out_image

        # 入出力画像
        inp_height, inp_width = inp_image.shape[:2]
        if (base_image is not None):
            out_image  = base_image.copy()
        else:
            # 彩度、明度変換
            hsv_image = cv2.cvtColor(inp_image, cv2.COLOR_BGR2HSV)  # 色空間をBGRからHSVに変換
            s_magnification = 1  # 彩度(Saturation)の倍率
            v_magnification = 0.5  # 明度(Value)の倍率
            hsv_image[:,:,(1)] = hsv_image[:,:,(1)]*s_magnification  # 彩度の計算
            hsv_image[:,:,(2)] = hsv_image[:,:,(2)]*v_magnification  # 明度の計算
            out_image = cv2.cvtColor(hsv_image,cv2.COLOR_HSV2BGR)  # 色空間をHSVからBGRに変換

        # 入力画像成形　四角形へ
        if (inp_width > inp_height):
            proc_size = inp_width
            proc_img  = np.zeros((proc_size,proc_size,3), np.uint8)
            offset    = int((inp_width-inp_height)/2)
            proc_img[offset:offset+inp_height, 0:inp_width] = inp_image.copy()
        elif (inp_height > inp_width):
            proc_size = inp_height
            proc_img  = np.zeros((proc_size,proc_size,3), np.uint8)
            offset    = int((inp_height-inp_width)/2)
            proc_img[0:inp_height, offset:offset+inp_width] = inp_image.copy()
        else:
            proc_size = inp_width
            proc_img  = inp_image.copy()
            offset    = 0
        proc_img = cv2.resize(proc_img, (self.yolov8_procSize, self.yolov8_procSize), )

        # 物体検出
        try:
            blob = cv2.dnn.blobFromImage(proc_img, scalefactor=1/255, size=(self.yolov8_procSize, self.yolov8_procSize), swapRB=True)
            self.yolov8_model.setInput(blob)
            output = self.yolov8_model.forward()
            output = np.array([cv2.transpose(output[0])])
        except Exception as e:
            print(e)
            return res_detect, out_image

        detections = output[0]

        classids = []
        scores   = []
        boxes    = []

        for detection in detections:
            classes_scores = detection[4:]
            (minScore, score, minClassLoc, (x, classid)) = cv2.minMaxLoc(classes_scores)
            if (score >= float(self.yolov8_threshold_score)):
                width  = detection[2]
                height = detection[3]
                left   = detection[0] - (width  / 2)
                top    = detection[1] - (height / 2)
                classids.append(int(classid))
                scores.append(float(score))
                boxes.append([int(left), int(top), int(width), int(height)])
                #print('rows', classid, score, [left, top, width, height], )

        # 重複した領域を排除した内容を利用する。
        indices = cv2.dnn.NMSBoxes(boxes, scores, float(self.yolov8_threshold_score), float(self.yolov8_threshold_nms), 0.5, )
        if (len(indices)<3):
            indices = cv2.dnn.NMSBoxes(boxes, scores, float(self.yolov8_threshold_score/2), float(self.yolov8_threshold_nms), 0.5, )
        #if (len(indices)<3):
        #    indices = cv2.dnn.NMSBoxes(boxes, scores, float(0.0), float(self.yolov8_threshold_nms), 0.5, )

        # ループ
        for i in indices:
            id    = classids[i]
            score = scores[i]
            box   = boxes[i][0:4]
            try:
                label  = self.yolov8_labels[id]
                label2 = label + '({:4.1f}%)'.format(score*100)
                color  = [ int(c) for c in self.yolov8_colors[id] ]
            except:
                label  = str(id)
                label2 = label + '({:4.1f}%)'.format(score*100)
                color  = (int(255),int(255),int(255))
            #print(label2, box)

            # 座標計算
            l, t, w, h = box
            if   (inp_width > inp_height):
                left   = int(l * (proc_size / self.yolov8_procSize))
                top    = int(t * (proc_size / self.yolov8_procSize)) - offset
                width  = int(w * (proc_size / self.yolov8_procSize))
                height = int(h * (proc_size / self.yolov8_procSize))
            elif (inp_height > inp_width):
                left   = int(l * (proc_size / self.yolov8_procSize)) - offset
                top    = int(t * (proc_size / self.yolov8_procSize))
                width  = int(w * (proc_size / self.yolov8_procSize))
                height = int(h * (proc_size / self.yolov8_procSize))
            else:
                left   = int(l * (proc_size / self.yolov8_procSize))
                top    = int(t * (proc_size / self.yolov8_procSize))
                width  = int(w * (proc_size / self.yolov8_procSize))
                height = int(h * (proc_size / self.yolov8_procSize))
            if (left < 0):
                left = 0
            if (top < 0):
                top = 0
            if ((left + width) > inp_width):
                width = inp_width - left
            if ((top + height) > inp_height):
                height = inp_height - top

            try:

                # 枠とラベル
                cv2.rectangle(out_image, (left, top), (left+width, top+height), color, 5)
                t_size = cv2.getTextSize(label2, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1 , 1)[0]
                x = left + t_size[0] + 3
                y = top  + t_size[1] + 4
                cv2.rectangle(out_image, (left, top), (x, y), color, -1)
                cv2.putText(out_image, label2, (left, top + t_size[1] + 1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 1)

                # 結果
                value = res_detect.get(label, 0)
                if (score > value):
                    res_detect[label] = score

            except:
                pass

        # 結果 (%変換)
        for key in res_detect.keys():
            res_detect[key] = f"{ res_detect[key] * 100 :4.1f}%"

        return res_detect, out_image

    def pil2cv(self, pil_image=None):
        try:
            cv2_image = np.array(pil_image, dtype=np.uint8)
            if (cv2_image.ndim == 2):  # モノクロ
                pass
            elif (cv2_image.shape[2] == 3):  # カラー
                cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)
            elif (cv2_image.shape[2] == 4):  # 透過
                cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGBA2BGRA)
            return cv2_image
        except:
            pass
        return None

    def txtsRead(self, filename, encoding='utf-8', exclusive=False, ):
        if (not os.path.exists(filename)):
            return False, ''

        encoding2 = encoding
        if (encoding2 == 'utf-8'):
            encoding2 =  'utf-8-sig'

        if (exclusive == False):
            try:
                txts = []
                txt  = ''
                r = codecs.open(filename, 'r', encoding2)
                for t in r:
                    t = t.replace('\n', '')
                    t = t.replace('\r', '')
                    txt  = (txt + ' ' + str(t)).strip()
                    txts.append(t)
                r.close
                r = None
                return txts, txt
            except Exception as e:
                r = None
                return False, ''
        else:
            f2 = filename[:-4] + '.txtsRead.tmp'
            res = self.remove(f2, )
            if (res == False):
                return False, ''
            else:
                try:
                    os.rename(filename, f2)
                    txts = []
                    txt  = ''
                    r = codecs.open(f2, 'r', encoding2)
                    for t in r:
                        t = t.replace('\n', '')
                        t = t.replace('\r', '')
                        txt = (txt + ' ' + str(t)).strip()
                        txts.append(t)
                    r.close
                    r = None
                    self.remove(f2, )
                    return txts, txt
                except Exception as e:
                    r = None
                    return False, ''



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "image_detect_to_text"
        self.func_ver  = "v0.20240630"
        self.func_auth = "KxO2p63bsxmsExB8YmKUQcUP/1VQy6z0gi5jdoTmtQggXful5uGSEV7PLy/yLlbw"
        self.function  = {
            "name": self.func_name,
            "description": "イメージファイルの物体認識(yolov8)",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "addin_yolo_test.jpg"
                    },
                },
                "required": ["runMode", "file_path"]
            }
        }

        # 初期設定
        self.runMode  = 'assistant'
        self.yolo     = yolov8_class()
        self.file_seq = 0
        self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        file_path = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            self.runMode   = args_dic.get('runMode', self.runMode)
            file_path      = args_dic.get('file_path')

        # 処理
        res_okng   = 'ng'
        res_text   = None
        image_path = None

        if (file_path is None) or (not os.path.isfile(file_path)):
            pass

        else:

            #inp_image = cv2.imread(file_path)
            image = Image.open(file_path)
            inp_image = self.yolo.pil2cv(pil_image=image, )
            res_dic, res_image = self.yolo.cv2detect_yolov8(inp_image=inp_image, )
            if (len(res_dic) > 0):
                res_text = json.dumps(res_dic, ensure_ascii=False, )

                # 検出画像
                if (res_image is not None):
                    filename = file_path.replace('.png', '')
                    filename = filename.replace('.sabun', '')
                    filename = filename + '.yolo.png'
                    if (filename != file_path):
                        cv2.imwrite(filename, res_image)

        # 戻り
        dic = {}
        if (res_text is not None) and (res_text != ''):
            dic['result']      = 'ok'
            dic['result_text'] = res_text
        else:
            dic['result']      = 'ng'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ "runMode" : "assistant" }'))

    print(ext.func_proc('{ ' \
                      + '"file_path" : "addin_yolo_test.jpg"' \
                      + ' }'))


