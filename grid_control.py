import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import datetime
import json

class GridControl:

    def __init__(self):
        self.config = GridControl.read_config_file()
        self.color = None
        self.color_rgba = None
        self.image = None
        self.np_image = None
        self.original_image = None
        self.temp_image = None
        self.transparent_image = None
        self.filepath = None
        self.height = self.width = None
        self.x_step = self.y_step = None

        self.height = self.width = 800
        self.sx = self.sy = 0
        self.tx = self.ty = 0
        self.current_x = self.current_y = 0
        self.drawing = False
        self.done = False

    def add_grid(self, isloaded, file=None, config=None):
        if config is not None:
            self.config.update(config)
        if not isloaded:
            return
        if isinstance(file, str):
            self.filepath = file
            self.np_image = np.array(Image.open(file))
        elif isinstance(file, np.ndarray):
            self.np_image = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)
        elif file is not None:
            self.np_image = np.array(file)
        self.color = tuple(map(int, self.config["color"].split(",")))
        self.color_rgba = (*self.color, self.config["alpha"])
        image = cv2.cvtColor(self.np_image, cv2.COLOR_BGR2RGB)
        self.original_image = image.copy()
        self.height, self.width = image.shape[:2]
        self.y_step = round(self.height/self.config["division_number"])
        self.x_step = round(self.width/self.config["division_number"])
        overlay = image.copy()
        for y in range(self.y_step, self.height, self.y_step):
            if y + (self.y_step / 2) >= self.height:
                continue
            cv2.line(overlay, (0, y), (self.width, y), self.color, self.config["line_width"])
        for x in range(self.x_step, self.width, self.x_step):
            if x + (self.x_step / 2) >= self.width:
                continue
            cv2.line(overlay, (x, 0), (x, self.height), self.color, self.config["line_width"])
        self.image = cv2.addWeighted(overlay, (self.config["alpha"] / 255.0), image, 1 - (self.config["alpha"] / 255.0), 0, dst=image)
        if self.config["transparent"]:
            self.create_transparent(self.height, self.width, self.y_step, self.x_step)
        return image

    def cropping_image(self):
        result = None
        self.done = False
        cv2.namedWindow("Select Area")
        cv2.setMouseCallback("Select Area", self.draw_rectangle)
        self.temp_image = cv2.cvtColor(self.np_image.copy(), cv2.COLOR_BGR2RGB)
        if not self.done:
            if self.temp_image.shape[0] > 1000 or self.temp_image.shape[0] > 500:
                height = round(self.width / self.temp_image.shape[1] * self.temp_image.shape[0])
                self.temp_image = cv2.resize(self.temp_image, (self.width, height))
            if self.temp_image.shape[1] > 1000 or self.temp_image.shape[1] > 500:
                width = round(self.height / self.temp_image.shape[0] * self.temp_image.shape[1])
                self.temp_image = cv2.resize(self.temp_image, (width, self.height))
        while True:
            temp_image = self.temp_image.copy()
            if self.drawing:
                cv2.rectangle(temp_image, (self.sx, self.sy), (self.current_x, self.current_y), (0, 0, 255), 3)
            cv2.imshow("Select Area", temp_image)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or self.done or cv2.getWindowProperty("Select Area", cv2.WND_PROP_VISIBLE) < 1:
                if not self.done:
                    result = "closed"
                break
        cv2.destroyAllWindows()
        x1, x2 = min(self.sx, self.tx), max(self.sx, self.tx)
        y1, y2 = min(self.sy, self.ty), max(self.sy, self.ty)
        if result == "closed":
            return result
        result = self.temp_image[y1:y2, x1:x2]
        if result.shape == (0, 0, 3):
            result = "invalid"
        return result

    def draw_rectangle(self, event, x, y, flags, param):
        x = max(0, min(x, self.temp_image.shape[1] - 1))
        y = max(0, min(y, self.temp_image.shape[0] - 1))
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.sx, self.sy = x, y
            self.current_x, self.current_y = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.current_x, self.current_y = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.tx, self.ty = x, y
            self.done = True
            self.current_x, self.current_y = x, y

    def create_transparent(self, height, width, y_step, x_step):
        image = np.zeros((height, width, 4), dtype=np.uint8)
        for y in range(y_step, height, y_step):
            if y + (y_step / 2) >= height:
                continue
            cv2.line(image, (0, y), (width, y), self.color_rgba, self.config["line_width"])
        for x in range(x_step, width, x_step):
            if x + (x_step / 2) >= width:
                continue
            cv2.line(image, (x, 0), (x, height), self.color_rgba, self.config["line_width"])
        return image

    def save_images(self):
        if self.image is not None:
            now = datetime.datetime.now()
            now_date = now.strftime('%Y-%m-%d')
            now_time = now.strftime('%H-%M')
            if not Path(f'{self.config["output_dir"]}/{now_date}').is_dir():
                Path(f'{self.config["output_dir"]}/{now_date}').mkdir(parents=True, exist_ok=True)
            file_path = f'{self.config["output_dir"]}/{now_date}/{now_date}_{now_time}'
            if self.config["size"]:
                width, height = self.config["size"]
                GridControl.imwrite(f'{file_path}_{width}x{height}_grid.png', cv2.resize(self.image.copy(), (width, height), interpolation=cv2.INTER_LANCZOS4))
                GridControl.imwrite(f'{file_path}_{width}x{height}_original.png', cv2.resize(self.original_image.copy(), (width, height), interpolation=cv2.INTER_LANCZOS4))
            else:
                GridControl.imwrite(f'{file_path}_{self.image.shape[1]}x{self.image.shape[0]}_grid.png', self.image)
                GridControl.imwrite(f'{file_path}_{self.original_image.shape[1]}x{self.original_image.shape[0]}_original.png', self.original_image)
            if self.config["transparent"]:
                transparent_image = self.create_transparent(self.height, self.width, self.y_step, self.x_step)
                if self.config["size"]:
                    GridControl.imwrite(f'{file_path}_{width}x{height}_transparent.png', cv2.resize(transparent_image.copy(), (self.config["size"]), interpolation=cv2.INTER_LANCZOS4))
                else:
                    GridControl.imwrite(f'{file_path}_{transparent_image.shape[1]}x{transparent_image.shape[0]}_transparent.png', transparent_image)
            with open("config.json", "w", encoding="utf-8") as f:
                config = self.config
                del config["size"]
                json.dump(config, f, indent=4)
            return "success"
        else:
            return

    @staticmethod
    def read_config_file():
        default = {"division_number":5, "line_width":5, "color":"0, 0, 255", "alpha":255, "transparent": True, "size":None, "output_dir":f'{(Path(__file__).resolve().parent).as_posix()}/output'}
        if Path("config.json").exists() and Path("config.json").is_file():
            with open("config.json", "r", encoding="utf-8") as f:
                try:
                    dict = json.load(f)
                    config = default.copy()
                    config.update(dict)
                    config["size"] = None
                    return config
                except Exception:
                    return default
        else:
            return default

    @staticmethod
    def imwrite(filepath, image, params=None):
        result, data = cv2.imencode('.png', image, params)
        if result:
            with open(filepath, mode='w+b') as f:
                data.tofile(f)