import tkinter as tk
from PIL import Image, ImageTk
import os

IMAGE_FOLDER = "images"

class LabelingForTV:
    def __init__(self, root):
        self.root = root
        self.root.title("Labeler for TrashVision")

        self.images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg'))]
        if not self.images:
            print("Folder jest pusty lub nie zawiera obrazów.")
            return

        self.current_image_index = 0
        self.objects = []
        self.current_object = None
        self.start_x = None
        self.start_y = None
        self.canvas = tk.Canvas(self.root, width=900, height=900, bg="black")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        controls_frame = tk.Frame(self.root)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.root.bind("<Left>", self.previous_image)
        self.root.bind("<Right>", self.next_image)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_rectangle)

        self.load_image()

    def load_image(self):
        if not self.images:
            return

        image_path = os.path.join(IMAGE_FOLDER, self.images[self.current_image_index])
        try:
            self.image = Image.open(image_path)
            self.image_width, self.image_height = self.image.size
            self.image.thumbnail((900, 900))
            self.tk_image = ImageTk.PhotoImage(self.image)

            self.canvas.delete("all")
            self.objects = []

            self.canvas.create_image(450, 450, anchor=tk.CENTER, image=self.tk_image)
            self.root.title(f"Labeler for TrashVision - {self.images[self.current_image_index]}")

        except Exception as e:
            print(f"Nie można załadować obrazu {image_path}: {e}")

    def next_image(self, event=None):
        if self.images:
            image_path = os.path.join(IMAGE_FOLDER, self.images[self.current_image_index])
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.load_image()

    def previous_image(self, event=None):
        if self.images:
            image_path = os.path.join(IMAGE_FOLDER, self.images[self.current_image_index])
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.load_image()

    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_object = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def draw_rectangle(self, event):
        if self.current_object:
            self.canvas.coords(self.current_object, self.start_x, self.start_y, event.x, event.y)

    def finish_rectangle(self, event):
        if self.current_object:
            object_coords = self.canvas.coords(self.current_object)
            width = abs(object_coords[2] - object_coords[0])
            height = abs(object_coords[3] - object_coords[1])

            if width < 30 or height < 30:
                self.canvas.delete(self.current_object)
                self.current_object = None
                return
                
            self.current_object = None


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingForTV(root)
    root.mainloop()
