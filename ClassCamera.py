import os, time, sys, json, platform
import subprocess
import ClassUtils
from PIL import Image, ImageDraw, ImageFont

basepath = os.path.dirname(os.path.realpath(__file__))
with open(basepath + '/Config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


def takePicture(personGroupId, delay, size='small'):
    cameras = config['camera'].split(',')
    for camera in cameras:
        if camera[0] == '*' and camera == '*webcam':
            return takePicture_webcam(personGroupId, delay)
        elif camera[0] == '*' and camera == '*CSIcamera':
            return takePicture_CSI(personGroupId, delay, size)
    return takePicture_CSI(personGroupId, delay, size)


def takePicture_CSI(personGroupId, delay, size='small'):
    # delay in ms 3000ms = 3s
    # jpgimagepath = os.path.join(basepath, 'takepictures', personGroupId + "_" + time.strftime(
    #     "%Y%m%d_%H%M%S", time.localtime()) + ".jpg")
    jpgimagepath = ClassUtils.getTakePicturePath(personGroupId)
    if not os.path.exists(os.path.dirname(jpgimagepath)):
        os.makedirs(os.path.dirname(jpgimagepath))
    try:
        # small for 辨識，加快速度。
        if size == 'small':
            subprocess.call([
                'raspistill', '-hf', '-w', '800', '-h', '450', '-t',
                str(delay), '-o', jpgimagepath
            ])
        else:  # for 訓練。訓練用圖片可以比較大
            subprocess.call([
                'raspistill', '-hf', '-w', '1600', '-h', '900', '-t',
                str(delay), '-o', jpgimagepath
            ])

    except OSError:
        # ClassMessageBox.FaceAPIErrorGUI('def takePicture_CSI', 'CSI 攝影機無法啟動！',
        #                                 'OSError: raspistill 無法執行或不存在！！')
        print('def takePicture_CSI', 'CSI 攝影機無法啟動！',
              'OSError: raspistill 無法執行或不存在！！')
        return None

    #os.system("raspistill -t " + str(delay) + " -o " + imagepath)
    return jpgimagepath


def show_webcam(imagepath, mirror=False):
    import cv2
    import numpy as np

    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)

        # font                   = cv2.FONT_HERSHEY_SIMPLEX
        # bottomLeftCornerOfText = (10,10)
        # fontScale              = 5
        # fontColor              = (255,255,255)
        # lineType               = 2
        # cv2.putText(img,'Hello World!',
        # bottomLeftCornerOfText,
        # font,
        # fontScale,
        # fontColor,
        # lineType)

        #W, H = (1024, 1024 // 16 * 9)
        H, W = img.shape[:2]
        #imS = cv2.resize(img, (W, H))

        cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # cv2和PIL中颜色的hex码的储存顺序不同
        pil_im = Image.fromarray(cv2_im)
        draw = ImageDraw.Draw(pil_im)  # 括号中为需要打印的canvas，这里就是在图片上直接打印

        # macos: /Library/Fonts/Microsoft Sans Serif.ttf
        sysstr = platform.system()
        if sysstr == 'Darwin':
            #ttf = '/Library/Fonts/Microsoft\\ Sans\\ Serif.ttf'
            #ttf = "/Library/Fonts/AppleMyungjo.ttf"
            #ttf = "/Library/Fonts/AppleGothic.ttf"
            ttf = "/Library/Fonts/Arial Unicode.ttf"
            font = ImageFont.truetype(
                ttf, 40, encoding="utf-8")  # 第一个参数为字体文件路径，第二个为字体大小
            hintfont = ImageFont.truetype(
                ttf, 24, encoding="utf-8")  # 第一个参数为字体文件路径，第二个为字体大小

        elif sysstr == 'Windows':
            ttf = "simhei.ttf"
            font = ImageFont.truetype(
                ttf, 40, encoding="utf-8")  # 第一个参数为字体文件路径，第二个为字体大小
            hintfont = ImageFont.truetype(
                ttf, 24, encoding="utf-8")  # 第一个参数为字体文件路径，第二个为字体大小
        else:
            ttf = "simhei.ttf"
            font = ImageFont.truetype(
                ttf, 40, encoding="utf-8")  # 第一个参数为字体文件路径，第二个为字体大小
            hintfont = ImageFont.truetype(
                ttf, 24, encoding="utf-8")  # 第一个参数为字体文件路径，第二个为字体大小

        title = config['title'] + ""
        w, h = draw.textsize(title, font=font)
        draw.rectangle(
            ((W / 2 - w / 2 - 5, 0), (W / 2 + w / 2 + 5, h + 20)),
            fill="black")
        titlelocation = (W / 2 - w / 2, 5)
        #textlocation = (0,0)
        draw.text(
            titlelocation, title, (0, 255, 255),
            font=font)  # 第一个参数为打印的坐标，第二个为打印的文本，第三个为字体颜色，第四个为字体

        hint = "請按「空白鍵」拍照"
        w, h = draw.textsize(hint, font=hintfont)
        draw.rectangle(
            ((W / 2 - w / 2 - 5, H - h), (W / 2 + w / 2 + 5, H)), fill="red")
        hintlocation = (W / 2 - w / 2, H - h)
        #textlocation = (0,0)
        draw.text(
            hintlocation, hint, (0, 255, 255),
            font=hintfont)  # 第一个参数为打印的坐标，第二个为打印的文本，第三个为字体颜色，第四个为字体

        cv2_text_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
        cv2.imshow(config['title'], cv2_text_im)

        key = cv2.waitKey(1)
        if key == ord(' '):
            cv2.imwrite(imagepath, img)
            break
        elif key == 27:  # esc to quit
            break
    cv2.destroyAllWindows()
    cv2.VideoCapture(0).release()


def takePicture_webcam(personGroupId, delay):
    sysstr = platform.system()
    print('os=', sysstr)
    if (sysstr == "Windows" or sysstr == "Darwin"):
        # jpgimagepath = os.path.join(basepath, 'takepictures', personGroupId + "_" + time.strftime(
        #     "%Y%m%d_%H%M%S", time.localtime()) + ".jpg")
        jpgimagepath = ClassUtils.getTakePicturePath(personGroupId)

        show_webcam(jpgimagepath, mirror=True)
        return jpgimagepath
    else:
        # jpgimagepath = os.path.join(basepath, 'takepictures', personGroupId + "_" + time.strftime(
        #     "%Y%m%d_%H%M%S", time.localtime()) + ".jpg")
        jpgimagepath = ClassUtils.getTakePicturePath(personGroupId)

        if not os.path.exists(os.path.dirname(jpgimagepath)):
            os.makedirs(os.path.dirname(jpgimagepath))
        try:
            subprocess.call(['fswebcam', "--no-banner", jpgimagepath])
        except OSError:
            # ClassMessageBox.FaceAPIErrorGUI('def takePicture_fswebcam',
            #                                 'web cam 無法啟動！',
            #                                 'OSError: fswebcam 無法執行或不存在！！')
            print('EXCEPTION: fswebcam 無法執行或不存在！！', file=sys.stderr)
            return None
        return jpgimagepath


'''
def takePicture_Picamera(personGroupId, delay):
    # 安裝 sudo apt-get install python3-picamera
    # 預設解析度1280x800
    imagepath = basepath + "/takepictures/Identity_" + personGroupId + "_" + time.strftime(
        "%Y-%m-%d_%H:%M:%S", time.localtime()) + ".jpg"
    if not os.path.exists(os.path.dirname(imagepath)):
        os.makedirs(os.path.dirname(imagepath))
    
    with picamera.PiCamera() as camera:
        camera.start_preview()
        sleep(delay)
        camera.capture(imagepath)
        return imagepath
'''