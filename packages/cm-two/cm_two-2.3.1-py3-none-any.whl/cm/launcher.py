""" Лаунчер Gravity interface """
import threading

from cm.configs.settings import Settings
from cm import functions
from cm.main_operator import *
from cm.wlistener import WListener
from traceback import format_exc
import screeninfo
import os

functions.del_logs()
# functions.log_events()

monitors = screeninfo.get_monitors()
width = monitors[0].width
height = monitors[0].height
deffaultScreenSize = (width, height)
dirpath = os.path.dirname(os.path.realpath(__file__))
img_dir = os.path.join(dirpath, 'imgs')
loadingWin = os.path.join(img_dir, 'loadingWin.png')

root = Tk()
# root.grab_set()
# root.focus_set()
# root.attributes('-fullscreen', True)

loadingcan = Canvas(root, highlightthickness=0)
loadingcan.pack(fill=BOTH, expand=YES)
photoimg = PhotoImage(file=loadingWin)
loadingcan.create_image(width / 2, height / 2, image=photoimg)
loadingcan.create_text(width / 2, height / 2 * 1.24, text='Добро пожаловать',
                       font=fonts.loading_welcome_font,
                       fill='white', tag='loadingtext')


def check_double():
    """ Проверить, запущена ли уже программа """
    from cm_adb import client, server
    ip, port, msg = 'localhost', 1333, 'MSG'
    try:
        client.client(ip, port, msg)
        # loadingcan.delete('loadingtext')
        # loadingcan.create_text(
        #    width / 2, height / 2 * 1.24,
        #    text='Программа уже запущена, вы пытаетесь запустить ее повторно!'
        #         '\nЕсли это не так, позвоните в тех. поддержку.',
        #    font=fonts.loading_status_font, fill='white',
        #    justify='center')
        # sleep(5)
        # zoom_another_copy()11111
        # os._exit(0)
        return True
    except ConnectionRefusedError:
        server.CMADBServer(ip, port)._start()


def zoom_another_copy():
    """ Выполняется, если попытаться запустить дубль. Разворачивает
    первоначальную копию"""
    from cm_qdk.main import CMQDK
    cm_qdk = CMQDK('localhost', 50505)
    cm_qdk.make_connection()
    cm_qdk.zoom_app()
    cm_qdk.get_data()


from cm.styles.styles import *


def startLoading():
    '''Инициализация проекта, выполняется параллельно с окном загрузки'''
    # root.grab_set()
    # root.focus_set()

    threading.Thread(target=functions.install_fonts,).start()
    arg_parser = functions.create_parser()
    namespace = arg_parser.parse_args()
    cams_info = {'cad_gross': {
        'enable': namespace.gross_cam,
        'ip': namespace.gross_cam_ip,
        'port': namespace.gross_cam_port},
        'auto_exit': {
            'enable': namespace.auto_exit_cam,
            'ip': namespace.auto_exit_cam_ip,
            'port': namespace.auto_exit_cam_port},
        'main': {
            'enable': namespace.main_cam,
            'ip': namespace.main_cam_ip,
            'port': namespace.main_cam_port}}
    wlistener = WListener('Въезд', 'COM1', 9600, ar_ip=namespace.ar_ip)
    can = Canvas(root, highlightthickness=0, bg=cs.main_background_color)
    scale_server_port = get_scale_server_port(namespace)
    ar_qdk = ARQDK(namespace.ar_ip, int(namespace.ar_port))
    while True:
        try:
            ar_qdk.make_connection()
            ar_qdk.subscribe()
            ar_qdk.get_data()
            loadingcan.delete('no_connection_info')
            break
        except ConnectionRefusedError:
            no_ar_connection(loadingcan)
            sleep(3)
    launch_info = (
        ar_qdk.execute_method('get_cm_info', get_response=True)[
            'info'])
    settings = Settings(root, dirpath, mirrored=launch_info['mirrored'])
    if not check_double():
        root.grab_set()
        root.focus_set()
        root.attributes('-fullscreen', True)
    for canvas in [loadingcan, can]:
        functions.draw_version_on_screen(canvas=canvas,
                                         xpos=settings.screenwidth - 30,
                                         ypos=settings.screenheight - 30,
                                         version_text=settings.version + ' v.',
                                         font=fonts.version_font)
    Operator(
        root, settings, wlistener, can, deffaultScreenSize,
        loadingcan, ar_qdk=ar_qdk,
        scale_server_ip=namespace.scale_server_ip,
        scale_server_port=scale_server_port, fgsm=launch_info['FGSM'],
        cm_cams_info=cams_info)
    loadingcan.destroy()
    # root.overrideredirect(False)

    can.pack(fill=BOTH, expand=YES)
    root.geometry("1920x1080+400+400")


def get_scale_server_port(namespace):
    if not namespace.scale_server_port:
        return 2297
    else:
        return namespace.scale_server_port


def startLoadingThread():
    """ Запуск инициализации загрузки параллельным потоком """
    threading.Thread(target=startLoading, args=()).start()


def launch_mainloop():
    """ Запустить оснвной цикл работы """
    root.after(100, startLoadingThread)
    try:

        root.mainloop()
    except:
        # При выходе из программы - трассировать текст исключения и выполнить
        # необходимые завершающие работы
        print(format_exc())
        os._exit(0)


def no_ar_connection(loadingcan):
    """ Если нет подключения к AR """
    loadingcan.delete('no_connection_info')
    loadingcan.create_text(root.winfo_screenwidth() / 2,
                           root.winfo_screenheight() / 2,
                           text='Не удалось подключиться к ядру...'
                                '\nПерезапуск...',
                           font=fonts.loading_status_font,
                           fill='white',
                           anchor='s',
                           justify='center',
                           tags=('no_connection_info',))


launch_mainloop()

# Нули не совпадают и оборудование неправильно.
# Поговорить с Рафой. 0 о тшлагбаума, другой 0 от БП