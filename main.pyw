import tkinter as tk
import customtkinter
from customtkinter import CTkImage
from pathlib import Path
from grid_control import GridControl
import cv2
from PIL import ImageGrab, Image
from CTkColorPicker import *
import numpy as np

FONT_TYPE = "meiryo"

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.fonts = (FONT_TYPE, 15)
        self.filepath = None
        self.is_new_load = None

        self.setup_form()

    def setup_form(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.minsize(1000, 650)
        self.geometry("1000x650")
        self.title("Add grid on Image")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.read_file_frame = ReadFileFrame(master=self, header_name="ファイルの読み込み・保存先", on_path_selected=self.on_path_selected)
        self.read_file_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.image_main_frame = ImageMainFrame(master=self, header_name="画像表示")
        self.image_main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def on_path_selected(self, path, folder=False):
        if not folder:
            if isinstance(path, str):
                self.filepath = path
            self.is_new_load = True
            self.image_main_frame.update(file=path)
        else:
            config = {"output_dir":path}
            self.image_main_frame.update(config=config)

class ReadFileFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", on_path_selected=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        self.on_path_selected = on_path_selected
        self.output_dir = GridControl.read_config_file()["output_dir"]

        self.setup_form()

    def setup_form(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.read_path_textbox = customtkinter.CTkEntry(master=self, state='readonly', placeholder_text="画像のファイルパス", width=120, font=self.fonts)
        self.read_path_textbox.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")

        self.file_button = customtkinter.CTkButton(master=self,fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.file_button_callback, text="ファイルを開く", font=self.fonts)
        self.file_button.grid(row=1, column=1, padx=10, pady=(0,10))

        self.clipboard_button = customtkinter.CTkButton(master=self, command=self.clipboard_button_callback, text="クリップボード\nから開く", font=self.fonts)
        self.clipboard_button.grid(row=1, rowspan=2, column=2, padx=10, pady=(0,10))

        self.write_path_textbox = customtkinter.CTkEntry(master=self, state='readonly', placeholder_text="画像の保存先", width=120, font=self.fonts)
        self.write_path_textbox.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        ReadFileFrame.change_textbox(self.write_path_textbox, self.output_dir)

        self.write_button = customtkinter.CTkButton(master=self,fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.dir_button_callback, text="フォルダを選択", font=self.fonts)
        self.write_button.grid(row=2, column=1, padx=10, pady=(0,10))


    def file_button_callback(self):
        file_path = ReadFileFrame.dialog("file")

        if file_path is not None:
            ReadFileFrame.change_textbox(self.read_path_textbox, file_path)
            if self.on_path_selected:
                self.on_path_selected(path=file_path)

    def clipboard_button_callback(self):
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            ReadFileFrame.change_textbox(self.read_path_textbox, "Clipboard")
            if self.on_path_selected:
                self.on_path_selected(path=image)

    def dir_button_callback(self):
        folder_path = ReadFileFrame.dialog("folder")
        if folder_path is not None:
            ReadFileFrame.change_textbox(self.write_path_textbox, folder_path)
            if self.on_path_selected:
                self.on_path_selected(path=folder_path, folder=True)


    @staticmethod
    def change_textbox(textbox, text):
        textbox.configure(state='normal')
        textbox.delete(0, tk.END)
        textbox.insert(0, text)
        textbox.configure(state='readonly')

    @staticmethod
    def dialog(ask_type):
        current_dir = Path(__file__).resolve().parent
        if ask_type == "file":
            path = tk.filedialog.askopenfilename(filetypes=[("Image File","*.png;*.jpg")], initialdir=current_dir)
        else:
            path = tk.filedialog.askdirectory(initialdir=current_dir)
        if len(path) != 0:
            return path
        else:
            return None

class ImageMainFrame(customtkinter.CTkFrame):

    def __init__(self, *args, header_name="ImageMainFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        self.gridcontrol = GridControl()
        self.height = self.width = 600
        self.is_image_loaded = False
        self.befor_image = None

        self.setup_form()

    def setup_form(self):

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_edit_frame = GridConfigFrame(master=self, header_name="グリッドのカスタマイズ", grid_config=self.gridcontrol.config)
        self.grid_edit_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

        self.image_label = customtkinter.CTkLabel(self, text="")
        self.image_label.grid(row=0, column=1, padx=20, pady=20)

        self.button_save = customtkinter.CTkButton(master=self, command=self.button_save_callback, text="保存", font=self.fonts)
        self.button_save.grid(row=0, column=2, padx=10, pady=20, sticky="s")

    def update(self, file=None, config=None, crop=False, undo=False, aspect_ratio=None):
        if self.master.is_new_load and self.grid_edit_frame.undo_button:
            if not aspect_ratio:
                self.grid_edit_frame.undo_button.destroy()
                self.grid_edit_frame.cropping_button.configure(state="normal")
            self.master.is_new_load = False
        if file is not None:
            if crop == False:
                self.befor_image = file
            self.is_image_loaded = True
        if not self.is_image_loaded:
            if config:
                self.gridcontrol.add_grid(self.is_image_loaded, config=config)
            return
        if undo == True:
            image = self.gridcontrol.add_grid(self.is_image_loaded, self.befor_image, config)
            file = None
        image = self.gridcontrol.add_grid(self.is_image_loaded, file, config)
        image_height, image_width = image.shape[:2]
        if not aspect_ratio:
            aspect_ratio = image_width / image_height
            self.grid_edit_frame.is_image_loaded(image.shape[0], image.shape[1], aspect_ratio)
        height = None
        width = None
        if max(image_height, image_width) == image_height:
            calc = int(self.width / aspect_ratio)
            if min (calc, self.height) == self.height:
                height = self.height
                width = int(self.height * aspect_ratio)
            else:
                width = self.width
                height = calc
        else:
            calc = int(self.height * aspect_ratio)
            if min (calc, self.width) == self.width:
                width = self.width
                height = int(self.width / aspect_ratio)
            else:
                width = self.width
                height = self.height
        if width > 0 and height > 0:
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        else:
            return
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if height:
            pil_image = Image.fromarray(image_rgb)
        elif width:
            pil_image = Image.fromarray(image_rgb)
        self.ctk_img = CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
        self.image_label.configure(image=self.ctk_img)
        if pil_image.size[0] + 500 < 1500 and pil_image.size[1] + 230 < 1000:
            self.master.geometry(f"{pil_image.size[0] + 500}x{max((pil_image.size[1] + 200), 650)}")

    def button_save_callback(self):
        result = self.gridcontrol.save_images()
        if result is not None:
            tk.messagebox.showinfo("成功", f"ファイルに出力しました。")
        else:
            tk.messagebox.showerror("エラー", f"画像が開かれていません。")

class GridConfigFrame(customtkinter.CTkFrame):

    def __init__(self, *args, header_name="GridConfigFrame", grid_config=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 13)
        self.header_name = header_name
        self.grid_config = grid_config.copy()
        color_bgr = [int(x) for x in self.grid_config["color"].split(",")]
        self.color_hex = f"#{color_bgr[2]:02x}{color_bgr[1]:02x}{color_bgr[0]:02x}"
        self.widgets = []
        self.undo_button = None
        self.aspect_ratio_keep = True
        self.aspect_ratio = None
        self.is_user = True
        self.original_width = None
        self.original_height = None
        self.setup_form()

    def setup_form(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1, uniform="equal")
        self.grid_columnconfigure(2, weight=2)

        self.label = customtkinter.CTkLabel(self, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, columnspan=3, padx=20, sticky="nw")

        self.division_slider_label = customtkinter.CTkLabel(self, text=f'グリッドの分割数 {self.grid_config["division_number"]}', font=self.fonts)
        self.division_slider_label.grid(row=1, column=0, columnspan=3, padx=20, pady=(10,0))

        self.division_slider = customtkinter.CTkSlider(master=self, from_=3, to=15, number_of_steps=12, hover=False, width=150, command=self.division_slider_event)
        self.division_slider.grid(row=2, column=0, columnspan=3, padx=20, pady=0)
        self.division_slider.set(self.grid_config["division_number"])
        self.widgets.append(self.division_slider)

        self.line_slider_label = customtkinter.CTkLabel(self, text=f'ライン幅 {self.grid_config["line_width"]}', font=self.fonts)
        self.line_slider_label.grid(row=3, column=0, columnspan=3, padx=20, pady=(10,0))

        self.line_slider = customtkinter.CTkSlider(master=self, from_=1, to=15, number_of_steps=14, hover=False, width=150, command=self.line_slider_event)
        self.line_slider.grid(row=4, column=0, columnspan=3, padx=20, pady=0)
        self.line_slider.set(self.grid_config["line_width"])
        self.widgets.append(self.line_slider)

        self.color_button_label = customtkinter.CTkLabel(self, text=f'グリッドの色 {self.color_hex}', font=self.fonts)
        self.color_button_label.grid(row=5, column=0, columnspan=3, padx=20, pady=(10,0))

        self.color_button = customtkinter.CTkButton(self, text=" ", fg_color=self.color_hex, hover_color=self.color_hex, command=self.ask_color_event)
        self.color_button.grid(row=6, column=0, columnspan=3, padx=30, pady=0)
        self.widgets.append(self.color_button)

        self.alpha_slider_label = customtkinter.CTkLabel(self, text=f'不透明度 {int(self.grid_config["alpha"] / 255 * 100)}', font=self.fonts)
        self.alpha_slider_label.grid(row=7, column=0, columnspan=3, padx=20, pady=(10,0))

        self.alpha_slider = customtkinter.CTkSlider(master=self, from_=0, to=100, number_of_steps=100, hover=False, width=150, command=self.alpha_slider_event)
        self.alpha_slider.grid(row=8, column=0, columnspan=3, padx=20, pady=0)
        self.alpha_slider.set(round(self.grid_config["alpha"] / 255 * 100))
        self.widgets.append(self.alpha_slider)

        self.transparent_checkbox = customtkinter.CTkCheckBox(master=self, text="透過画像の同時出力", width=150, command=self.transparent_checkbox_event)
        self.transparent_checkbox.grid(row=9, column=0, columnspan=3, padx=30, pady=(15,0))
        if self.grid_config["transparent"]:
            self.transparent_checkbox.select()
        self.widgets.append(self.transparent_checkbox)

        self.size_textbox_label = customtkinter.CTkLabel(self, text="画像サイズ\n(横×縦)", font=self.fonts)
        self.size_textbox_label.grid(row=10, column=0, padx=(30, 0), pady=(10, 0))

        self.aspect_checkbox = customtkinter.CTkCheckBox(master=self, text="縦横比を維持", checkbox_height=15, checkbox_width=15, command=self.aspect_checkbox_event, font=(FONT_TYPE, 10))
        self.aspect_checkbox.grid(row=10, column=1, columnspan=2, padx=(10, 20), pady=(10,0))
        self.aspect_checkbox.select()
        self.widgets.append(self.aspect_checkbox)

        self.width_textbox = customtkinter.CTkEntry(self, width=50, validate="key", validatecommand=(self.register(self.width_key_event), "%P"))
        self.width_textbox.grid(row=11, column=0, padx=(20,10), pady=(10, 0), sticky="ew")
        self.widgets.append(self.width_textbox)

        self.cross_label = customtkinter.CTkLabel(self, text="×", font=self.fonts)
        self.cross_label.grid(row=11, column=1, padx=0, pady=(10, 0), sticky="ew")

        self.height_textbox = customtkinter.CTkEntry(self, width=10, validate="key", validatecommand=(self.register(self.height_key_event), "%P"))
        self.height_textbox.grid(row=11, column=2, padx=(10,20), pady=(10, 0), sticky="ew")
        self.widgets.append(self.height_textbox)

        self.cropping_button = customtkinter.CTkButton(self, text="選択範囲の切り取り", command=self.cropping_button_event)
        self.cropping_button.grid(row=12, column=0, columnspan=3, padx=30, pady=(15,0))
        self.cropping_button.configure(state="disabled")

    def division_slider_event(self, value):
        old_label = self.division_slider_label.cget("text")
        new_label = f"グリッドの分割数 {int(value)}"
        if old_label != new_label:
            self.division_slider_label.configure(text=new_label)
            self.grid_config["division_number"] = int(value)
            self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)

    def line_slider_event(self, value):
        old_label = self.line_slider_label.cget("text")
        new_label = f"ライン幅 {int(value)}"
        if old_label != new_label:
            self.line_slider_label.configure(text=new_label)
            self.grid_config["line_width"] = int(value)
            self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)

    def ask_color_event(self):
        pick_color = AskColor()
        color = pick_color.get()
        if color is not None:
            if color != self.color_hex:
                self.color_button_label.configure(text=f'グリッドの色 {color}')
            self.color_button.configure(fg_color=color, hover_color=color)
            bgr_color = f'{int(color[5:7], 16)}, {int(color[3:5], 16)}, {int(color[1:3], 16)}'
            self.grid_config["color"] = bgr_color
            self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)

    def alpha_slider_event(self, value):
        old_label = self.alpha_slider_label.cget("text")
        new_label = f"不透明度 {int(value)}"
        if old_label != new_label:
            self.alpha_slider_label.configure(text=new_label)
            self.grid_config["alpha"] = int(value / 100 * 255)
            self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)

    def transparent_checkbox_event(self):
        self.grid_config["transparent"] = bool(self.transparent_checkbox.get())
        self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)

    def cropping_button_event(self):
        self.disable_all_widgets()
        self.cropping_button.configure(state="disabled")
        result = self.master.gridcontrol.cropping_image()
        if isinstance(result, np.ndarray):
            self.master.update(result, self.grid_config, crop=True)
            self.undo_button = customtkinter.CTkButton(self, text="戻す", command=self.undo_button_event)
            self.undo_button.grid(row=13, column=0, columnspan=3, padx=30, pady=(10,0))
            self.cropping_button.configure(state="disabled")
            self.enable_all_widgets()
        else:
            self.cropping_button.configure(state="normal")
            self.enable_all_widgets()

    def undo_button_event(self):
        if self.undo_button:
            self.master.update(undo=True)
            self.undo_button.destroy()
            self.cropping_button.configure(state="normal")

    def disable_all_widgets(self):
        for widget in self.widgets:
            widget.configure(state="disabled")

    def enable_all_widgets(self):
        for widget in self.widgets:
            widget.configure(state="normal")

    def aspect_checkbox_event(self):
        if not self.aspect_ratio_keep and self.width_textbox.cget("state") == "normal":
            self.set_original()
        self.aspect_ratio_keep = bool(self.aspect_checkbox.get())

    def is_image_loaded(self, height, width, aspect_ratio):
        self.aspect_ratio = aspect_ratio
        self.original_width, self.original_height = width, height
        self.cropping_button.configure(state="normal")
        self.width_textbox.configure(state="normal")
        self.height_textbox.configure(state="normal")
        self.is_user = False
        self.width_textbox.delete(0, "end")
        self.width_textbox.insert(0, width)
        self.height_textbox.delete(0, "end")
        self.height_textbox.insert(0, height)
        self.is_user = True

    def set_original(self):
        self.is_user = False
        self.width_textbox.delete(0, "end")
        self.width_textbox.insert(0, self.original_width)
        self.height_textbox.delete(0, "end")
        self.height_textbox.insert(0, self.original_height)
        self.master.update(config=self.grid_config)
        self.is_user = True

    def width_key_event(self, value):
        if self.master.is_image_loaded:
            if self.is_user:
                if (value.isdigit() and 1 <= int(value) <= 9999 and value == str(int(value))) or value == "":
                    if value == "":
                        if not self.aspect_ratio_keep:
                            return True
                        self.is_user = False
                        self.height_textbox.delete(0, "end")
                        self.height_textbox.insert(0, 1)
                        self.is_user = True
                        return True
                    if self.aspect_ratio_keep:
                        height = int(float(value) / self.aspect_ratio)
                        if height == 0 or int(value) == 0:
                            height = value = 1
                        self.is_user = False
                        self.height_textbox.delete(0, "end")
                        self.height_textbox.insert(0, height)
                        self.is_user = True
                        self.grid_config["size"] = (int(value), height)
                        self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)
                    else:
                        if self.height_textbox.get() == "":
                            self.is_user = False
                            self.height_textbox.delete(0, "end")
                            self.height_textbox.insert(0, 1)
                            self.is_user = True
                        height = int(self.height_textbox.get())
                        if height == 0 or int(value) == 0:
                            height = value = 1
                        self.aspect_ratio = int(value) / height
                        if float(self.aspect_ratio) <= 1500 or abs(int(value) - height) < 3000:
                            if self.grid_config["size"] != (int(value), height):
                                self.grid_config["size"] = (int(value), height)
                            self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)
                    return True
                else:
                    return False
            else:
                return True
        else:
            self.after_idle(lambda: self.width_textbox.configure(state="readonly"))
            return False

    def height_key_event(self, value):
        if self.master.is_image_loaded:
            if self.is_user:
                if (value.isdigit() and 1 <= int(value) <= 9999 and value == str(int(value))) or value == "":
                    if value == "":
                        if not self.aspect_ratio_keep:
                            return True
                        self.is_user = False
                        self.width_textbox.delete(0, "end")
                        self.width_textbox.insert(0, 1)
                        self.is_user = True
                        return True
                    if self.aspect_ratio_keep:
                        width = int(float(value) * self.aspect_ratio)
                        if width == 0 or int(value) == 0:
                            width = value = 1
                        self.is_user = False
                        self.width_textbox.delete(0, "end")
                        self.width_textbox.insert(0, width)
                        self.is_user = True
                        self.grid_config["size"] = (width, int(value))
                        self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)
                    else:
                        if self.width_textbox.get() == "":
                            self.is_user = False
                            self.width_textbox.delete(0, "end")
                            self.width_textbox.insert(0, 1)
                            self.is_user = True
                        width = int(self.width_textbox.get())
                        if width == 0 or int(value) == 0:
                            width = value = 1
                        self.aspect_ratio = width / int(value)
                        if float(self.aspect_ratio) >= 0.01 or abs(width - int(value) < 3000):
                            if self.grid_config["size"] != (width, int(value)):
                                self.grid_config["size"] = (width, int(value))
                            self.master.update(config=self.grid_config, aspect_ratio=self.aspect_ratio)
                    return True
                else:
                    return False
            else:
                return True
        elif not self.is_user:
            return True
        else:
            self.after_idle(lambda: self.height_textbox.configure(state="readonly"))
            return False

if __name__ == "__main__":
    app = App()
    app.mainloop()