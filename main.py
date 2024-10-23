from tkinter import *
from tkinter import ttk
import pandas as pd
import datetime as dt
import schedule , time
from win11toast import toast
import threading

# 画面切り替えを制御するクラス
class Application(Tk):
    def __init__(self):
        super().__init__()
        self.geometry('480x800+20+20')
        self.resizable(0,0)
        self.title('ナ二ゴミ')
        self.logo = PhotoImage(file='img/LogoScreen/logo_yellowfishbone.png')
        self.iconphoto(True, self.logo)

        # 変数の初期化
        self.ward = None  
        self.index = None 
        self.ku_part = None 
        self.gomisep_selection = None
        self.gomisep_selection_detail = None
        self.frames = {}  # 各フレームを格納する辞書

        # フレームクラスのマッピング
        self.frame_classes = {
            'LogoScreen': LogoScreen,
            'SelectAreaScreen': SelectAreaScreen,
            'SelectArea_by_postcode': SelectArea_by_postcode,
            'SelectArea_by_area': SelectArea_by_area,
            'MenuScreen': MenuScreen,
            'Gomi_Cal': Gomi_Cal,
            'Gomi_separate': Gomi_separate,
            'Gomi_dict': Gomi_dict,
            'Gomi_type_search': Gomi_type_search,
            'SelectArea_by_chome': SelectArea_by_chome,
            'Gomi_separate_choose': Gomi_separate_choose,
            'Gomi_separate_detail': Gomi_separate_detail,
            'Reminder': Reminder
        }

        self.show_frame('LogoScreen') # 初期画面を表示
        
    def show_frame(self, page_name):
        # 指定されたページ名が存在しない場合
        if page_name not in self.frame_classes:
            raise ValueError(f"Unknown page: {page_name}")
       
        # リマインダーページを保存し、フレーム辞書をクリア
        reminder_frame = self.frames.get('Reminder', None)
        self.frames.clear()


        # リマインダーページの再追加
        if reminder_frame is not None:
            self.frames['Reminder'] = reminder_frame

        # フレームが存在しない場合は新しく作成
        if page_name not in self.frames:
            frame_class = self.frame_classes[page_name]
            frame = frame_class(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[page_name] # 指定されたフレームを取得

        if page_name == "MenuScreen" and self.ward:
             # タイトルに表示するための詳細設定
            if not self.ward.find('丁') == -1: 
                stop_index = self.ward.find('（')
                self.ward = self.ward[:stop_index]
            elif not self.ward.find('番') == -1:
                stop_index = self.ward.find('（')
                self.ward = self.ward[:stop_index] 
            frame.city_label.config(text=self.ward) # 区のラベルを更新

        elif page_name == "Gomi_type_search" and self.index:
            frame.index.config(text=self.index) # インデックスラベルを更新
        frame.tkraise() # フレームを前面に表示


# ロゴ画面を表示
class LogoScreen(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')
        self.logo = PhotoImage(file='img/LogoScreen/logo_yellowfishbone.png')
        self.nanigomi = PhotoImage(file='img/LogoScreen/nanigomi_logo.png')

        # キャンバスを作成し、画像を配置
        cv = Canvas(self, width=480, height=800, bg='#FFFFFF')
        cv.pack()
        cv.create_image(250, 350, image=self.nanigomi)
        cv.create_image(250, 200, image=self.logo)

        # 保存された住所データを読み込み
        with open('saved_address/ku_part.txt','r') as f:
            ku_part = f.readline() # 区の部分を読み込む
            address = f.readline() # 住所を読み込む
        if ku_part and address:
            self.controller.ku_part = ku_part.replace('\n', '')
            self.controller.ward = address.replace('\n', '')
            self.after(1000, lambda: controller.show_frame("MenuScreen")) # 1秒後にメニュー画面を表示
        else:
            self.after(1000, lambda: controller.show_frame("SelectAreaScreen")) # 1秒後に地域選択画面を表示


# 位置選択画面を表示
class SelectAreaScreen(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像を読み込む
        self.logo = PhotoImage(file='img/SelectAreaScreen/fishboneS.png')
        self.welcome = PhotoImage(file='img/SelectAreaScreen/welcome_text.png')
        self.welcome2 = PhotoImage(file='img/SelectAreaScreen/welcome_text2.png')
        self.fromarea = PhotoImage(file='img/SelectAreaScreen/fromarea.png')
        self.frompostcode = PhotoImage(file='img/SelectAreaScreen/frompostcode.png')

        # タイトル
        Label(self, image=self.welcome, bd=0).place(x=30, y=45)
        Label(self, image=self.welcome2, bd=0).place(x=35, y=110)
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=40)

        # 住所検索方法のボタン
        Button(self, bg='#FFFFFF', bd=0, activebackground='#FFFFFF', activeforeground='#FFFFFF', image=self.frompostcode, compound='center', font=("Arial", 14, 'bold'), command= lambda: self.controller.show_frame("SelectArea_by_postcode")).place(x=80,y=340)
        Button(self, bg='#FFFFFF', bd=0, activebackground='#FFFFFF', activeforeground='#FFFFFF', image=self.fromarea, compound='center', font=("Arial", 14, 'bold'), command= lambda: self.controller.show_frame("SelectArea_by_area")).place(x=80,y=570)

# 郵便番号によるエリア選択画面を表示
class SelectArea_by_postcode(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像を読み込む
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/by_postcode/mailbox.png')
        self.postcode = PhotoImage(file='img/by_postcode/postcode_text.png')
        self.searchingbar = PhotoImage(file='img/by_postcode/searchingbar.png')
        self.location_ui = PhotoImage(file='img/by_postcode/location_icon.png')

        # データフレームを読み込む
        self.df_postcode = pd.read_csv('csv/sapporo_ken.csv')

        # タイトル
        Label(self, bg='#FFFFFF', image=self.postcode).place(x=90, y=50)
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=30)
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= self.back_to_SelectArea).place(x=40,y=65)

        # 位置アイコンを表示
        Label(self, image=self.location_ui, bd=0).place(x=86, y=250)

        # 郵便番号検索ラベル
        self.address = Label(self, bg='#FFFFFF', bd=0, font=("Arial", 30, 'bold'))
        self.address.place(x=55, y=670)
        Label(self, image=self.searchingbar, compound='center', bg='#FFFFFF').place(x=45,y=730)

        # 郵便番号入力用のエントリー
        vcmd = (self.register(self.validate_input),'%S')
        self.postcode_ety = Entry(self, font=("Arial", 14, 'bold'), width=13, bd=0, validate='key', validatecommand=vcmd)
        self.postcode_ety.place(x=265,y=747)
        
        # エンターキーで郵便番号を取得
        self.postcode_ety.bind("<Return>", lambda event: self.get_ku_part(self.postcode_ety.get(), self.df_postcode))
        
    # 入力検証関数
    def validate_input(self,val):
        return val.isdigit() or val == "" # 数字または空文字のみ許可


    # エリア選択画面に戻る
    def back_to_SelectArea(self):
        self.controller.frames.clear()
        self.controller.show_frame("SelectAreaScreen")  # エリア選択画面を表示


    # 郵便番号から区号を取得する
    def get_ku_part(self, postcode, df_postcode):

        # 対象郵便番号をフィルタリング
        filtered_df = df_postcode[df_postcode['post_code'] == int(postcode)]
        
        # 地区と部品データを表示
        if not filtered_df.empty:
            # 表示する住所を取得
            address = filtered_df.iloc[0]['kanji_district'] + filtered_df.iloc[0]['kanji_chome']
            self.address.config(text=address) # アドレスラベルを更新
            self.controller.ward = address # コントローラーのwardを更新
            self.after(1000,lambda : self.controller.show_frame("MenuScreen")) # 1秒後にメニュー画面を表示
                
            # 区号を取得
            ku_part = filtered_df.iloc[0]['kanji_district'] + str(int(filtered_df.iloc[0]['part']))

            # 区号をファイルに書き込む
            with open('saved_address/ku_part.txt','w') as f:
                f.write(f'{ku_part}\n{address}\n') # 区号と住所を保存
            self.controller.ku_part = ku_part  # コントローラーのku_partを更新
        else:
            self.address.config(text='無効な郵便番号')


# 地域を選択する画面
class SelectArea_by_area(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像を読み込む
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/by_area/areamap.png')
        self.area = PhotoImage(file='img/by_area/area_text.png')
        self.chuoku = PhotoImage(file='img/by_area/中.png')
        self.kita = PhotoImage(file='img/by_area/北.png')
        self.higashi = PhotoImage(file='img/by_area/東.png')
        self.shiro = PhotoImage(file='img/by_area/白.png')
        self.atsu = PhotoImage(file='img/by_area/厚.png')
        self.toyo = PhotoImage(file='img/by_area/豊.png')
        self.kiyo = PhotoImage(file='img/by_area/清.png')
        self.minami = PhotoImage(file='img/by_area/南.png')
        self.nishi = PhotoImage(file='img/by_area/西.png')
        self.teine = PhotoImage(file='img/by_area/手.png')


        # タイトル
        Label(self, bg='#FFFFFF', image=self.area).place(x=90, y=50)
        # ロゴ
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=40)
        # 戻るアイコン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("SelectAreaScreen")).place(x=40,y=65)
        
        # 地域ボタン
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.chuoku, compound='center', bd=0, command=lambda :self.get_area('中央区')).place(x=55,y=200)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.kita, compound='center', bd=0, command=lambda :self.get_area('北区')).place(x=255,y=200)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.higashi, compound='center', bd=0, command=lambda :self.get_area('東区')).place(x=55,y=310)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.shiro, compound='center', bd=0, command=lambda :self.get_area('白石区')).place(x=255,y=310)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.atsu, compound='center', bd=0, command=lambda :self.get_area('厚別区')).place(x=55,y=420)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.toyo, compound='center', bd=0, command=lambda :self.get_area('豊平区')).place(x=255,y=420)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.kiyo, compound='center', bd=0, command=lambda :self.get_area('清田区')).place(x=55,y=530)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.minami, compound='center', bd=0, command=lambda :self.get_area('南区')).place(x=255,y=530)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.nishi, compound='center', bd=0, command=lambda :self.get_area('西区')).place(x=55,y=640)
        Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.teine, compound='center', bd=0, command=lambda :self.get_area('手稲区')).place(x=255,y=640)

    # 選択した地域を保存し、次の画面に移動する
    def get_area(self,area):
        self.controller.ward = area
        self.controller.show_frame("SelectArea_by_chome")

# 地区を選択する画面
class SelectArea_by_chome(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像を読み込む
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/by_area/areamap.png')
        self.chome = PhotoImage(file='img/by_area/chome_text.png')
        self.searchingbar = PhotoImage(file='img/by_area/chome_searchingbar.png')

        # データフレームを読み込む
        self.df_ward = pd.read_csv('csv/sapporo_ken.csv')

        # タイトル
        Label(self, bg='#FFFFFF', image=self.chome).place(x=90, y=50)
        # ロゴ
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=40)
        # 戻るアイコン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("SelectArea_by_area")).place(x=40,y=65)
        
        # 検索バー
        Label(self, image=self.searchingbar, bg='#FFFFFF').place(x=25, y=150)
        self.search_term_ety = Entry(self, font=("Arial", 17), width=15, bd=0)
        self.search_term_ety.place(x=230,y=167)

        # あいまい検索用データリストボックス
        self.chome_listbox = Listbox(self, activestyle='none',relief='flat', highlightthickness=4,font=("Arial", 18), width=28, height=19, fg='#333333', selectbackground='black', selectforeground='#ffde59',highlightbackground='black')
        self.chome_listbox.place(x=53,y=210)

        # イベント
        self.chome_listbox.bind("<ButtonRelease-1>", lambda e:self.get_ku_part())
        self.search_term_ety.bind("<KeyRelease>",lambda e: self.fuzzy_search())

        # ごみ名のリストボックスを表示
        self.show_related_index()

    def get_ku_part(self):
        # 選択されたリストボックスの項目を取得
        selected_chome = self.chome_listbox.get(self.chome_listbox.curselection()[0]).replace('・', '')

        # データフレームから一致する行を取得
        target_row = self.df_ward[self.df_ward['kanji_chome'] == selected_chome]

        if not target_row.empty:
            address = target_row.iloc[0]['kanji_district'] + target_row.iloc[0]['kanji_chome']
            self.controller.ward = address

            #  区の情報を取得
            ku_part = target_row.iloc[0]['kanji_district'] + str(target_row.iloc[0]['part'])

            # 区の情報をファイルに書き込む
            with open('saved_address/ku_part.txt','w') as f:
                f.write(f'{ku_part}\n{address}\n')
            self.controller.ku_part = ku_part
            self.controller.show_frame("MenuScreen")



    def show_related_index(self):
        # リストボックスをクリア
        self.chome_listbox.delete(0, END)

        # 選択された地区を取得
        ward = self.controller.ward

        # ユーザーが選択したインデックスから
        result = self.df_ward[self.df_ward['kanji_district'] == ward]
        chomes = result['kanji_chome']

        if not chomes.empty:
            # リストボックスに追加
            for i in list(chomes):
                self.chome_listbox.insert(END,f"・{i}")
        else:
            return "結果はありません"


    def fuzzy_search(self):
        # エントリーの検索内容を取得
        search_term = self.search_term_ety.get().replace('・', '')

        if search_term:
            # データフレームからあいまい検索の内容を取得
            result = self.df_ward[self.df_ward['kanji_chome'].str.contains(search_term, na=False)]

            if not result.empty:
                # '丁目'列のみを抽出
                chomes = result['kanji_chome']
                self.chome_listbox.delete(0,END)

                # リストボックスに追加
                for i in list(chomes):
                    self.chome_listbox.insert(END,f"・{i}")
            else:
                self.chome_listbox.delete(0,END)
                self.chome_listbox.insert(0,'結果はありません')



# ごみメニュー（地域取得後）
class MenuScreen(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像を読み込む
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.gomi_sep_icon = PhotoImage(file='img/MenuScreen/gomi_sep.png')
        self.gomi_dict_icon = PhotoImage(file='img/MenuScreen/gomi_dict.png')
        self.gomi_cal_icon = PhotoImage(file='img/MenuScreen/gomi_cal.png')
        self.home_icon = PhotoImage(file='img/MenuScreen/home.png')
        self.gomi_reminder_icon = PhotoImage(file='img/MenuScreen/gomi_reminder1.png')
        self.locate_icon = PhotoImage(file='img/MenuScreen/location.png')
        
        # タイトル
        self.city_label = Label(self, bg='#FFFFFF', font=("Arial", 30, 'bold'), image=self.locate_icon,compound='left')
        self.city_label.place(x=90, y=58)
        # 戻るアイコン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command=self.back_to_SelectAreaScreen).place(x=40,y=65)
        
        # ボタン作成
        btn1 = Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.gomi_sep_icon, compound='center', bd=0, command= lambda: self.controller.show_frame("Gomi_separate"))
        btn2 = Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.gomi_dict_icon, compound='center', bd=0, command=lambda: self.controller.show_frame("Gomi_dict"))
        btn3 = Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.gomi_cal_icon, compound='center', bd=0, command=lambda: self.controller.show_frame("Gomi_Cal"))
        btn4 = Button(self, bg='#FFFFFF', activebackground='#FFFFFF', image=self.gomi_reminder_icon, compound='center', bd=0, command=lambda: self.controller.show_frame("Reminder"))
        # ボタン配置
        btn1.place(x=55, y=150)
        btn2.place(x=55, y=310)
        btn3.place(x=55, y=470)
        btn4.place(x=49, y=628)

    # 住所を変更するかどうかの確認関数
    def back_to_SelectAreaScreen(self):
        # 新しいウィンドウを作成
        yesno_win = Toplevel()
        yesno_win.config(bg='#FFFFFF')

        def change_address():
            # 住所変更画面を表示
            self.controller.show_frame("SelectAreaScreen")
            yesno_win.destroy()

        # 住所を変更するかどうかの確認ラベルを作成
        Label(yesno_win,image=self.home_icon,compound='left',text='  住所を変更しますか？',fg='#ffc938',font=("Arial", 18, 'bold'), bg='#FFFFFF').pack(padx=20,pady=(20,10))
        # クリック時にchange_addressメソッドを呼び出す
        Button(yesno_win,bg='#FFFFFF',activebackground='#FFFFFF',activeforeground='#ffc938', relief='flat',bd=0,text='はい', font=("Arial", 12, 'bold'), command=change_address).pack(side='left',padx=(70,20),pady=10)
        # クリック時に確認ウィンドウを閉じる
        Button(yesno_win,bg='#FFFFFF',activebackground='#FFFFFF', relief='flat',bd=0,text='いいえ',fg='gray', font=("Arial", 12, 'bold'), command=lambda: yesno_win.destroy()).pack(pady=20)

# 明日は何ごみ？画面
class Reminder(Frame): 
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # アイコンの画像パス
        self.reminder_text = PhotoImage(file='img/Reminder/reminder_text.png')
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/Reminder/reminder_icon.png')
        self.reminder_ui = PhotoImage(file='img/Reminder/reminder_UI.png')

        # ゴミの種類に応じた画像パス
        self.MOERU_PATH = 'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/Gomi_Cal/gomi_moeruS.png'
        self.MOENAI_PATH = 'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/Gomi_Cal/gomi_moenaiS.png'
        self.BIN_PATH = 'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/Gomi_Cal/gomi_binS.png'
        self.PLASTIC_PATH ='C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/Gomi_Cal/gomi_plasticS.png'
        self.KAMI_PATH = 'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/Gomi_Cal/gomi_kamiS.png'
        self.LEAVES_PATH = 'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/Gomi_Cal/gomi_leavesS.png'

        # ゴミカレンダーCSVの読み込み
        self.df_gomi_cal = pd.read_csv('csv/gomi_calendar.csv')
        # # ゴミの種類（番号）CSVの読み込み
        self.df_gomitypenumber = pd.read_csv('csv/gomitypenumber.csv')

        # タイトル
        Label(self, bg='#FFFFFF', image=self.reminder_text).place(x=88, y=58)
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("MenuScreen")).place(x=40,y=65)

        Label(self, image=self.reminder_ui, bd=0).place(x=18,y=250)
        # 時間のオプションメニュー
        time = ['ー:ー','ー:ー','00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00']
        selected_option = StringVar()

        # 時間のドロップダウンメニューを設定
        dropdown = ttk.OptionMenu(self, selected_option, *time, command=lambda val: self.set_time(val))
        dropdown.config(style="Custom.TMenubutton")
        style = ttk.Style()
        style.configure("Custom.TMenubutton", font=('Arial', 22), background='white', foreground='black')
        menu = dropdown['menu']
        menu.config(bg='white', font=('Arial', 12,'bold'), bd=0)
        dropdown.place(x=170,y=648)

    def get_gomitype_tmr(self):
        # 区の情報を取得する
        with open('saved_address/ku_part.txt','r') as f:
            ku_part = f.readline().replace('\n', '')

        # 明日の日付を取得する
        one_day = dt.timedelta(days=1) 
        today_date = dt.date.today()
        date_tmr = (today_date + one_day).strftime('%Y-%m-%d')

        # ゴミの種類（番号）を取得する
        target_row = self.df_gomi_cal[self.df_gomi_cal['日付'] == date_tmr]
        if not target_row.empty:
            self.gomitype_num = int(target_row.iloc[0][ku_part])
        
        # ゴミの種類（文字列）を取得する
        self.gomitype_str = self.df_gomitypenumber.loc[self.df_gomitypenumber['記号'] == self.gomitype_num,'ごみ種'].values[0]
        return self.gomitype_str, self.gomitype_num


    # 毎日のリマインダー時間を設定する
    def set_time(self, get_time):
        
        if not get_time == "ー:ー":
            #* 毎日通知を設定
            schedule.every().day.at(get_time).do(self.send_notification)
        
            #* デモ用
            # schedule.every(5).seconds.do(self.send_notification)

            self.start_scheduler()
        else:
            schedule.clear() # 時間が設定されていない場合、スケジュールをクリア
        
    def start_scheduler(self):
        # スケジューラーを開始する
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        # 新しいスレッドを作成し、非ブロッキングで実行
        threading.Thread(target=run_scheduler, daemon=True).start()

    def send_notification(self):
        # ごみの種類に応じた画像パスを定義する
        gomi_type = {
            1:self.MOERU_PATH, 
            2:self.MOENAI_PATH,
            8:self.BIN_PATH,
            9:self.PLASTIC_PATH,
            10:self.KAMI_PATH,
            11:self.LEAVES_PATH,
            0:'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/logo_yellowfishboneL.png',
        }
        
        img = {
            'src' : 'C:/Users/hekke/OneDrive/桌面/00_進級制作/ナニゴミ - 進級製作（２年生前期）/img/logo_yellowfishboneL.ico',
            'placement':'hero'
        }

        # トースト通知を送信する
        toast('ナ二ゴミ',f"明日のごみは\n{self.get_gomitype_tmr()[0]}ですよ！\n忘れないでね〜", duration='2',
              icon=gomi_type[self.get_gomitype_tmr()[1]]) # 明日のごみの種類を通知


# ごみカレンダーを表示
class Gomi_Cal(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # アイコン画像の読み込み
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.moeru_icon = PhotoImage(file='img/Gomi_Cal/gomi_moeruS.png')
        self.moenai_icon = PhotoImage(file='img/Gomi_Cal/gomi_moenaiS.png')
        self.bin_icon = PhotoImage(file='img/Gomi_Cal/gomi_binS.png')
        self.plastic_icon = PhotoImage(file='img/Gomi_Cal/gomi_plasticS.png')
        self.kami_icon = PhotoImage(file='img/Gomi_Cal/gomi_kamiS.png')
        self.leaves_icon = PhotoImage(file='img/Gomi_Cal/gomi_leavesS.png')
        self.yellowframe = PhotoImage(file='img/Gomi_Cal/yellowframe.png')
        self.cal_text = PhotoImage(file='img/Gomi_Cal/cal_text.png')
        self.logo = PhotoImage(file='img/Gomi_Cal/cal_icon.png')

        # 区の情報を取得
        self.ku_part = self.controller.ku_part

        # CSVファイルの読み込み (ゴミカレンダーとゴミタイプのナンバー)
        self.df_gomi_cal = pd.read_csv('csv/gomi_calendar.csv')
        self.df_gomitypenumber = pd.read_csv('csv/gomitypenumber.csv')
        
        # タイトル
        Label(self, bg='#FFFFFF',image=self.cal_text).place(x=88, y=58)
        # ロゴ
        Label(self, bg='#FFFFFF', image=self.logo).place(x=348, y=30)
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("MenuScreen")).place(x=40,y=65)

        # ゴミの種類を表示するラベル
        Label(self, bg='#FFFFFF', image=self.yellowframe).place(x=24,y=130)
        Label(self, bg='#FFFFFF', image=self.yellowframe).place(x=24,y=262)
        Label(self, bg='#FFFFFF', image=self.yellowframe).place(x=24,y=394)
        Label(self, bg='#FFFFFF', image=self.yellowframe).place(x=24,y=526)
        Label(self, bg='#FFFFFF', image=self.yellowframe).place(x=24,y=658)

        # カレンダーの日付ラベル
        date_lb1 = Label(self, text=self.get_date_jp()[0], bg='#ffdd59', font=("Arial", 18, 'bold'))
        date_lb2 = Label(self, text=self.get_date_jp()[1], bg='#ffdd59', font=("Arial", 20, 'bold'), fg='white')
        date_lb3 = Label(self, text=self.get_date_jp()[2], bg='#ffdd59', font=("Arial", 18, 'bold'))
        date_lb4 = Label(self, text=self.get_date_jp()[3], bg='#ffdd59', font=("Arial", 18, 'bold'))
        date_lb5 = Label(self, text=self.get_date_jp()[4], bg='#ffdd59', font=("Arial", 18, 'bold'))
        date_lb1.place(x=45,y=150)
        date_lb2.place(x=44,y=280)
        date_lb3.place(x=45,y=415)
        date_lb4.place(x=45,y=548)
        date_lb5.place(x=45,y=675)

        # ごみの種類を表示するラベル
        self.date_lb1 = Label(self, text=self.get_gomitype_str()[0], justify='left', font=("Arial", 12), bg='#ffdd59')
        self.date_lb2 = Label(self, text=self.get_gomitype_str()[1], justify='left', font=("Arial", 12), bg='#ffdd59')
        self.date_lb3 = Label(self, text=self.get_gomitype_str()[2], justify='left', font=("Arial", 12), bg='#ffdd59')
        self.date_lb4 = Label(self, text=self.get_gomitype_str()[3], justify='left', font=("Arial", 12), bg='#ffdd59')
        self.date_lb5 = Label(self, text=self.get_gomitype_str()[4], justify='left', font=("Arial", 12), bg='#ffdd59')
        self.date_lb1.place(x=63,y=195)
        self.date_lb2.place(x=63,y=325)
        self.date_lb3.place(x=63,y=460)
        self.date_lb4.place(x=63,y=592)
        self.date_lb5.place(x=63,y=720)

        # ごみのアイコンを表示するラベル
        Label(self,image=self.get_gomi_type_icon()[0],compound=RIGHT, bg='#ffdd59').place(x=350,y=150)
        Label(self,image=self.get_gomi_type_icon()[1],compound=RIGHT, bg='#ffdd59').place(x=350,y=285)
        Label(self,image=self.get_gomi_type_icon()[2],compound=RIGHT, bg='#ffdd59').place(x=350,y=415)
        Label(self,image=self.get_gomi_type_icon()[3],compound=RIGHT, bg='#ffdd59').place(x=350,y=545)
        Label(self,image=self.get_gomi_type_icon()[4],compound=RIGHT, bg='#ffdd59').place(x=350,y=675)


    # 5日分の日付を取得
    def get_date(self):

        today = dt.date.today() # 今日の日付を取得
        weekdays = []
        for i in range(5):
            # one_day create
            one_day = dt.timedelta(hours=24) # 1日分の時間を作成
            days = one_day * i 

            # 次の日付を取得
            nextday = today + days
            weekdays.append(nextday)
        return weekdays
    
    # 今日から5日間の日付を日本語形式で取得
    def get_date_jp(self):
        # 5日分の日付リストを取得
        weekdays_list = self.get_date()
        weekdays_jp = ['月','火','水','木','金','土','日']
        weekdays_list_jp = [] 
        for weekday in weekdays_list:
            # 日本語の形式にフォーマット
            formatted_date = weekday.strftime("%m月%d日")
            date_jp = f"【{weekdays_jp[weekday.weekday()]}】{formatted_date}"
            weekdays_list_jp.append(date_jp)
        return weekdays_list_jp
    
    # ゴミのアイコンを取得
    def get_gomi_type_icon(self):
        gomitype_num_list = self.get_gomitype_num()            
        gomi_type = {
            1:self.moeru_icon,
            2:self.moenai_icon,
            8:self.bin_icon,
            9:self.plastic_icon,
            10:self.kami_icon,
            11:self.leaves_icon,
            0:None,
        }
        gomi_type_icon_list = []
        for num in gomitype_num_list:
            gomi_type_icon = gomi_type[num]
            gomi_type_icon_list.append(gomi_type_icon)
        return gomi_type_icon_list


    # 区番号を使ってゴミの種類（番号）を取得
    def get_gomitype_num(self):
        if self.ku_part:
            gomitype_num_list = []
            for date in self.get_date():
                # 対応する日付をフィルター
                filtered_days = self.df_gomi_cal[self.df_gomi_cal['日付'] == str(date)]

                if not filtered_days.empty and self.ku_part in filtered_days.columns:
                    # ゴミの種類（番号）を取得
                    gomitype_num = int(filtered_days.iloc[0][self.ku_part])
                    gomitype_num_list.append(int(gomitype_num))
                else:
                    return 'gomitype num not found'
            return gomitype_num_list


    # ゴミの種類（番号）を文字に変換
    def get_gomitype_str(self):
        gomitype_num_list = self.get_gomitype_num()
        gomitype_str_list = []
        for num in gomitype_num_list:
            # 記号に対応するゴミの種類を取得
            filtered_df = self.df_gomitypenumber[self.df_gomitypenumber['記号'] == num]
            if not filtered_df.empty:
                # '/'を改行に置換
                gomitype_str = filtered_df.iloc[0]['ごみ種']
                gomitype_str = gomitype_str.replace('/', '\n')
                gomitype_str_list.append(gomitype_str)
            else:
                return 'gomitype num not found'
        return gomitype_str_list


# ゴミ辞書
class Gomi_dict(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # アイコン画像の読み込み
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/Gomi_dict/dict_icon.png')
        self.dict_text = PhotoImage(file='img/Gomi_dict/dict_text.png')
        self.dict_a = PhotoImage(file='img/Gomi_dict/dict_a.png')
        self.dict_ka = PhotoImage(file='img/Gomi_dict/dict_ka.png')
        self.dict_sa = PhotoImage(file='img/Gomi_dict/dict_sa.png')
        self.dict_ta = PhotoImage(file='img/Gomi_dict/dict_ta.png')
        self.dict_na = PhotoImage(file='img/Gomi_dict/dict_na.png')
        self.dict_ha = PhotoImage(file='img/Gomi_dict/dict_ha.png')
        self.dict_ma = PhotoImage(file='img/Gomi_dict/dict_ma.png')
        self.dict_ya = PhotoImage(file='img/Gomi_dict/dict_ya.png')
        self.dict_ra = PhotoImage(file='img/Gomi_dict/dict_ra.png')
        self.dict_wa = PhotoImage(file='img/Gomi_dict/dict_wa.png')


        # タイトル
        Label(self, bg='#FFFFFF', image=self.dict_text).place(x=88, y=58)
        # ロゴ
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=40)
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("MenuScreen")).place(x=40,y=65)

        # index buttons
        Button(self, command=lambda :self.get_index('あ'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_a , compound='center').grid(row=0,column=0,padx=(70,0),pady=(160,0))
        Button(self, command=lambda :self.get_index('さ'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_sa, compound='center').grid(row=1,column=0,padx=(70,0))
        Button(self, command=lambda :self.get_index('な'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_na, compound='center').grid(row=2,column=0,padx=(70,0))
        Button(self, command=lambda :self.get_index('ま'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_ma, compound='center').grid(row=3,column=0,padx=(70,0))
        Button(self, command=lambda :self.get_index('ら'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_ra, compound='center').grid(row=4,column=0,padx=(70,0))
        Button(self, command=lambda :self.get_index('か'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_ka, compound='center').grid(row=0,column=1,padx=(40,0),pady=(160,0))
        Button(self, command=lambda :self.get_index('た'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_ta, compound='center').grid(row=1,column=1,padx=(40,0))
        Button(self, command=lambda :self.get_index('は'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_ha, compound='center').grid(row=2,column=1,padx=(40,0))
        Button(self, command=lambda :self.get_index('や'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_ya, compound='center').grid(row=3,column=1,padx=(40,0))
        Button(self, command=lambda :self.get_index('わ'), bg='#FFFFFF', activebackground='#FFFFFF', bd=0, image=self.dict_wa, compound='center').grid(row=4,column=1,padx=(40,0))

    # インデックスを取得し、次の画面に遷移する関数
    def get_index(self,index):
        self.controller.index = index
        self.controller.show_frame("Gomi_type_search")


# ごみの種類の検索画面
class Gomi_type_search(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像を読み込む
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/Gomi_dict/dict_icon.png')
        self.searchingbar = PhotoImage(file='img/Gomi_dict/item_searchingbar.png')
        self.gomitype_text = PhotoImage(file='img/Gomi_dict/dict_gomitype_text.png')

        # CSVデータを読み込む（ゴミ辞書）
        self.df_gomi_dict = pd.read_csv('csv/gomi_dict.csv')

        # タイトル
        self.index = Label(self, bg='#FFFFFF', font=("Arial", 40, 'bold'))
        self.index.place(x=100, y=45)
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("Gomi_dict")).place(x=40,y=65)
        # ロゴ
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=40)

        # 検索バー
        Label(self, image=self.searchingbar, bg='#FFFFFF').place(x=25, y=140)
        # エントリーボックス
        self.search_term_ety = Entry(self, font=("Arial", 17), width=16, bd=0)
        self.search_term_ety.place(x=220,y=152)

        # リストボックスに曖昧検索結果を表示
        self.gomi_name_listbox = Listbox(self, activestyle='none',font=("Arial", 14,'bold'), width=35, height=23,bd=0,relief='flat',highlightbackground='black', highlightcolor='black',highlightthickness=4,selectbackground='black', selectforeground='#ffdd59')
        self.gomi_name_listbox.place(x=48,y=200)

        # 選択されたアイテムのごみ種類を表示
        Label(self, image=self.gomitype_text, bg='#FFFFFF').place(x=50,y=750)
        self.selected_gomi_type = Label(self, font=("impact", 17, 'bold'), bg='#FFFFFF', fg='red')
        self.selected_gomi_type.place(x=200,y=748)

        # イベント
        self.gomi_name_listbox.bind("<ButtonRelease-1>", lambda e:self.get_gomi_type())
        self.gomi_name_listbox.bind("<KeyRelease>", lambda e:self.get_gomi_type())
        self.gomi_name_listbox.bind("<KeyRelease>", lambda e:self.get_gomi_type())
        self.search_term_ety.bind("<KeyRelease>",lambda e: self.fuzzy_search())

        # ごみ名リストボックスにインデックスに関連する内容を表示
        self.show_related_index()

    def get_gomi_type(self):
        # 選択されたリストボックスアイテムを取得
        gominame = self.gomi_name_listbox.get(self.gomi_name_listbox.curselection()[0])
        gominame = gominame[1:]
        # データフレームからごみの種類を取得
        target_row = self.df_gomi_dict[self.df_gomi_dict['gomi_name'] == gominame]

        if not target_row.empty:
            # ごみの種類を取得
            gomi_type = list(target_row['gomi_type'])[0]
            if not gomi_type.find('（') == -1:
                stop = gomi_type.find('（')
                gomi_type = gomi_type[:stop]
            self.selected_gomi_type.config(text=gomi_type)


    def show_related_index(self):
        # リストボックスをクリア
        self.gomi_name_listbox.delete(0, END)

        # 選択されたインデックスを取得
        index = self.controller.index

        # ユーザーが選択したインデックスに基づくデータを取得
        result = self.df_gomi_dict[self.df_gomi_dict['index'] == index]
        gomi_name = result['gomi_name']

        if not gomi_name.empty:
            # リストボックスに追加
            for i in list(gomi_name):
                self.gomi_name_listbox.insert(END,f"・{i}")
        else:
            return "結果はありません"


    def fuzzy_search(self):
        # エントリー検索の内容を取得
        search_term = self.search_term_ety.get().replace('・', '')

        if search_term:
            # データフレームから曖昧検索結果を取得
            result = self.df_gomi_dict[self.df_gomi_dict['gomi_name'].str.contains(search_term, na=False)]

            if not result.empty:
                # gomi_name列のみを抽出
                gomi_name = result['gomi_name']
                self.gomi_name_listbox.delete(0,END)

                # リストボックスに追加
                for i in list(gomi_name):
                    self.gomi_name_listbox.insert(END,f"・{i}")
            else:
                self.gomi_name_listbox.delete(0,END)
                self.gomi_name_listbox.insert(0,'結果はありません')


# ゴミの分け方画面
class Gomi_separate(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # アイコンの画像パス
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.logo = PhotoImage(file='img/Gomi_sep/sep_icon.png')
        self.sep_text = PhotoImage(file='img/Gomi_sep/sep_text.png')
        self.moeru_icon = PhotoImage(file='img/Gomi_sep/gomi_moeruM.png')
        self.moenai_icon = PhotoImage(file='img/Gomi_sep/gomi_moenaiM.png')
        self.bin_icon = PhotoImage(file='img/Gomi_sep/gomi_binM.png')
        self.plastic_icon = PhotoImage(file='img/Gomi_sep/gomi_plasticM.png')
        self.kami_icon = PhotoImage(file='img/Gomi_sep/gomi_kamiM.png')
        self.leaves_icon = PhotoImage(file='img/Gomi_sep/gomi_leavesM.png')
        self.lighter_icon = PhotoImage(file='img/Gomi_sep/gomi_lighterM.png')
        self.battery_icon = PhotoImage(file='img/Gomi_sep/gomi_batteryM.png')
        self.spray_icon = PhotoImage(file='img/Gomi_sep/gomi_sprayM.png')

        # タイトル
        Label(self, bg='#FFFFFF', image=self.sep_text).place(x=88, y=58)
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("MenuScreen")).place(x=40,y=65)
        # ロゴ
        Label(self, bg='#FFFFFF', image=self.logo).place(x=350, y=30)


        # ボタンを配置
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('燃やせるごみ'), image=self.moeru_icon, bg='#FFFFFF', bd=0).place(x=50,y=170)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('燃やせないごみ'), image=self.moenai_icon, bg='#FFFFFF', bd=0).place(x=182,y=170)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('びん・缶・ペットボトル'), image=self.bin_icon, bg='#FFFFFF', bd=0).place(x=315,y=170)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('雑がみ'), image=self.kami_icon, bg='#FFFFFF', bd=0).place(x=50,y=350)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('容器包装プラスチック'), image=self.plastic_icon, bg='#FFFFFF', bd=0).place(x=182,y=350)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('枝・葉・草'), image=self.leaves_icon, bg='#FFFFFF', bd=0).place(x=315,y=350)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('ライター'), image=self.lighter_icon, bg='#FFFFFF', bd=0).place(x=50,y=530)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('筒型乾電池'), image=self.battery_icon, bg='#FFFFFF', bd=0).place(x=182,y=530)
        Button(self, activebackground='#FFFFFF', command=lambda :self.get_selected_data('スプレー缶'), image=self.spray_icon, bg='#FFFFFF', bd=0).place(x=315,y=530)

    # 選択されたごみの種類を取得して、次の画面に遷移
    def get_selected_data(self,gomitype):
        self.controller.gomisep_selection = gomitype
        self.controller.show_frame("Gomi_separate_choose")

# ゴミの分け方2
class Gomi_separate_choose(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')
        self.selection = self.controller.gomisep_selection

        # 画像の読み込み
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.btn_frame = PhotoImage(file='img/Gomi_sep/sep_frame.png')

        # データフレームの読み込み
        self.df_gomi_separate = pd.read_csv('csv/gomi_sep.csv')

        # タイトル
        self.gomisep_title = Label(self, text=self.selection,bg='#FFFFFF', font=("Arial", 23, 'bold'))
        self.gomisep_title.pack(padx=90, pady=60, anchor='w')
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("Gomi_separate")).place(x=40,y=65)

        # ボタンを配置するためのフレームを作成
        self.frame = Frame(self, bg='#FFFFFF')
        self.frame.place(x=40,y=120)
        self.get_df()

    # CSVから選択されたゴミの種類に基づいてデータを取得
    def get_df(self):
        df = self.df_gomi_separate
        n = df[df['gomi_type'] == self.selection]
        if not n.empty:
            return self.create_button(list(n['title']))

    # ボタンを作成してフレームに配置
    def create_button(self,category_list):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for btn_title in category_list:
            Button(self.frame, text=btn_title, image=self.btn_frame, compound='center', bd=0, command= lambda btn=btn_title: self.on_button_click(btn), bg='#FFFFFF', activebackground='#FFFFFF', font=("Arial", 12, 'bold')).pack(pady=2)
        
    # ボタンクリック時、次の画面に遷移
    def on_button_click(self,btn_title):
        self.controller.gomisep_selection_detail = btn_title
        self.controller.show_frame('Gomi_separate_detail')

# ゴミの分け方3
class Gomi_separate_detail(Frame):
    def __init__(self,parent,controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='#FFFFFF')

        # 画像の読み込み
        self.back_icon = PhotoImage(file='img/left_arrow.png')
        self.frame = PhotoImage(file='img/Gomi_sep/sep_free_frame.png')
        self.info_icon = PhotoImage(file='img/Gomi_sep/info.png')
        self.moeru_1 = PhotoImage(file='img/Gomi_sep/moeru_1.png')
        self.moeru_2 = PhotoImage(file='img/Gomi_sep/moeru_2.png')
        self.moeru_3 = PhotoImage(file='img/Gomi_sep/moeru_3.png')
        self.moeru_4 = PhotoImage(file='img/Gomi_sep/moeru_4.png')
        self.moeru_5 = PhotoImage(file='img/Gomi_sep/moeru_5.png')
        self.moeru_6 = PhotoImage(file='img/Gomi_sep/moeru_6.png')
        self.moeru_7 = PhotoImage(file='img/Gomi_sep/moeru_7.png')
        self.moeru_8 = PhotoImage(file='img/Gomi_sep/moeru_8.png')
        self.moeru_9 = PhotoImage(file='img/Gomi_sep/moeru_9.png')
        self.moenai_1 = PhotoImage(file='img/Gomi_sep/moenai_1.png')
        self.moenai_2 = PhotoImage(file='img/Gomi_sep/moenai_2.png')
        self.moenai_3 = PhotoImage(file='img/Gomi_sep/moenai_3.png')
        self.moenai_4 = PhotoImage(file='img/Gomi_sep/moenai_4.png')
        self.moenai_5 = PhotoImage(file='img/Gomi_sep/moenai_5.png')
        self.moenai_6 = PhotoImage(file='img/Gomi_sep/moenai_6.png')
        self.spray_1 = PhotoImage(file='img/Gomi_sep/spray_1.png')
        self.battery_1 = PhotoImage(file='img/Gomi_sep/battery_1.png')
        self.p_1 = PhotoImage(file='img/Gomi_sep/p_1.png')
        self.p_2 = PhotoImage(file='img/Gomi_sep/p_2.png')
        self.p_3 = PhotoImage(file='img/Gomi_sep/p_3.png')
        self.p_4 = PhotoImage(file='img/Gomi_sep/p_4.png')
        self.p_5 = PhotoImage(file='img/Gomi_sep/p_5.png')
        self.p_6 = PhotoImage(file='img/Gomi_sep/p_6.png')
        self.p_7 = PhotoImage(file='img/Gomi_sep/p_7.png')
        self.p_8 = PhotoImage(file='img/Gomi_sep/p_8.png')
        self.b_1 = PhotoImage(file='img/Gomi_sep/b_1.png')
        self.b_2 = PhotoImage(file='img/Gomi_sep/b_2.png')
        self.b_3 = PhotoImage(file='img/Gomi_sep/b_3.png')
        self.l_1 = PhotoImage(file='img/Gomi_sep/l_1.png')
        self.l_2 = PhotoImage(file='img/Gomi_sep/l_2.png')
        self.paper_1 = PhotoImage(file='img/Gomi_sep/paper_1.png')
        self.paper_2 = PhotoImage(file='img/Gomi_sep/paper_2.png')
        self.paper_3 = PhotoImage(file='img/Gomi_sep/paper_3.png')
        self.paper_4 = PhotoImage(file='img/Gomi_sep/paper_4.png')
        self.paper_5 = PhotoImage(file='img/Gomi_sep/paper_5.png')
        self.paper_6 = PhotoImage(file='img/Gomi_sep/paper_6.png')
        self.paper_7 = PhotoImage(file='img/Gomi_sep/paper_7.png')
        self.paper_8 = PhotoImage(file='img/Gomi_sep/paper_8.png')
        self.lighter_1 = PhotoImage(file='img/Gomi_sep/lighter_1.png')
        self.lighter_2 = PhotoImage(file='img/Gomi_sep/lighter_2.png')

        # 選択されたボタンのタイトルを取得
        self.selection_detail = self.controller.gomisep_selection_detail
        # データフレームの読み込み
        self.df_gomi_separate = pd.read_csv('csv/gomi_sep.csv')

        # タイトル
        self.gomisep_selection_detail = Label(self,justify='left', text=f"{self.selection_detail[:11]}\n{self.selection_detail[11:]}",bg='#FFFFFF', font=("Arial", 24, 'bold'))
        self.gomisep_selection_detail.pack(padx=90, pady=60, anchor='w')
        # 戻るボタン
        Button(self,image=self.back_icon,activebackground='white',bg='#FFFFFF', bd=0, command= lambda : self.controller.show_frame("Gomi_separate_choose")).place(x=40,y=65)

        # ラベルを配置するためのフレームを作成
        self.frame = Frame(self, bg='#FFFFFF')
        self.frame.place(x=35,y=135)

        self.get_df_data()

    def get_df_data(self):

        # フレームのウィジェットをリセット
        widgets = self.frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        # データフレームを取得
        df = self.df_gomi_separate
        # 対象の行を取得
        target_row = df[df['title'] == self.selection_detail]

        df_val_list = []
        if not target_row.empty:

            # 値を取得
            free = list(target_row['free'])[0]
            category = list(target_row['category'])[0]
            how_to = list(target_row['出し方'])[0]
            remark = list(target_row['remark'])[0]
        return self.show_in_label((free,category,how_to,remark))

    def get_icon(self):
        icon_dict = {
            '台所のごみ':self.moeru_1,
            '食用油':self.moeru_2,
            '製品プラスチック':self.moeru_3,
            '汚れた紙':self.moeru_4,
            '衣類・布類':self.moeru_5,
            '皮革製品':self.moeru_6,
            'ゴム・ビニール製品':self.moeru_7,
            '炭・乾燥剤・保冷剤・使い捨てカイロ':self.moeru_8,
            '木製品・木くず・材木類':self.moeru_9,
            '台所のごみ':self.moeru_1,
            '金属製・ガラス製の容器': self.moenai_1, 
            '小型家電製品': self.moenai_2, 
            '金属製品': self.moenai_3, 
            'ブロック・レンガ・土': self.moenai_4, 
            'ガラス・せともの': self.moenai_5, 
            '蛍光管': self.moenai_6,
            'スプレー缶・カセットボンベ':self.spray_1,
            '空きびん（使い捨てびん）': self.b_1,
            '空き缶': self.b_2,
            'ペットボトル': self.b_3,
            '筒型乾電池':self.battery_1,
            'パック・カップ類':self.p_1,
            'プラスチック製ボトル類':self.p_2,
            'トレイ類':self.p_3,
            'ポリ袋・ラップ類':self.p_4,
            'プラスチック製のふた・ラベル':self.p_5,
            'ネット類':self.p_6,
            'チューブ類':self.p_7,
            '緩衝材・発泡スチロール':self.p_8,
            '庭の刈った芝、草花、落ち葉':self.l_1,
            '庭木のせん定枝・幹・根':self.l_2,
            '紙箱類':self.paper_1,
            '紙缶・紙カップ類・ふた類':self.paper_2,
            'シュレッダーにより裁断した紙':self.paper_3,
            '包装紙類・紙袋類・トイレットペーパーの芯':self.paper_4, 
            '手紙・封筒・写真・カレンダー・レシート':self.paper_5, 
            '紙パック類':self.paper_6, 
            'チラシ・コピー用紙':self.paper_7, 
            'ノート・カタログ・パンフレット':self.paper_8, 
            '加熱式たばこ・電子たばこ':self.lighter_1,
            'ライター':self.lighter_2
        }        
        return icon_dict[self.selection_detail]

    def show_in_label(self,dataset):

        free, category, how_to, remark = dataset

        # 無料有料
        Label(self.frame, text=free, width=23, bg='#ffdd59',fg='white', font=("Arial", 20, 'bold'), pady=10).pack(pady=(10,0))
        
        # アイコン
        icon = self.get_icon()
        Label(self.frame, image=icon,bd=0).pack(pady=10)

        # カテゴリー情報
        category = f"・{category}"
        category = category.strip().replace('・', '\n・')
        category = category.strip().replace('、', '\n・')
        Label(self.frame, text=category, width=40, pady=10, bg='#FFFFFF', font=("Arial", 12,'bold'), justify='left').pack(pady=(10,0))

        # 出し方
        if how_to and not how_to == '0':
            how_to = how_to.replace('、', '、\n')
            Label(self.frame, text=how_to, justify='left', bg='#ffdd59', font=("Arial", 10, 'bold'), image=self.info_icon, compound='left',width=400).pack(pady=(10,0))

        # 備考情報
        if remark and not remark == '0':
            if not remark.find('、') == -1:
                remark = remark.replace(' ', '\n').replace('、', '\n')
            else:
                if len(remark) > 30:
                    remark = remark[:30] + '\n' + remark[30:]
            Label(self.frame, text=remark, width=67, pady=10, bg='#982B1C', fg='white', font=("Arial", 8)).pack(pady=(10,0))


if __name__ == '__main__':
    App = Application()
    App.mainloop()
