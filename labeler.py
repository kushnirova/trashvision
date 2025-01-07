import tkinter as tk
from tkinter import ttk
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

        self.categories = ["Plastik", "Metal", "Szkło", "Papier"]
        self.selected_category = tk.StringVar(value=self.categories[0])

        self.canvas = tk.Canvas(self.root, width=900, height=900, bg="black")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        controls_frame = tk.Frame(self.root)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.category_dropdown = ttk.Combobox(controls_frame, values=self.categories, textvariable=self.selected_category)
        self.category_dropdown.pack(pady=5)

        self.obj_listbox = tk.Listbox(controls_frame, height=20, width=30)
        self.obj_listbox.pack(pady=5)

        self.change_cat__button = tk.Button(controls_frame, text="Zmień kategorię obiektu", command=self.change_category)
        self.change_cat__button.pack(pady=5)

        self.delete_button = tk.Button(controls_frame, text="Usuń obiekt", command=self.delete_object)
        self.delete_button.pack(pady=5)

        self.root.bind("<Left>", self.previous_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("1", lambda e: self.selected_category.set("Plastik"))
        self.root.bind("2", lambda e: self.selected_category.set("Metal"))
        self.root.bind("3", lambda e: self.selected_category.set("Szkło"))
        self.root.bind("4", lambda e: self.selected_category.set("Papier"))
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_rectangle)
        self.root.bind("<Delete>", self.delete_object)
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
            self.obj_listbox.delete(0, tk.END)
            self.objects = []

            self.canvas.create_image(450, 450, anchor=tk.CENTER, image=self.tk_image)
            self.root.title(f"Labeler for TrashVision - {self.images[self.current_image_index]}")

            self.load_labels(image_path)
        except Exception as e:
            print(f"Nie można załadować obrazu {image_path}: {e}")

    def save_labels(self, image_path):
        txt_path = os.path.splitext(image_path)[0] + ".txt"
        with open(txt_path, "w") as file:
            for obj, coords, category, _ in self.objects:
                x1, y1, x2, y2 = coords
                x_center = ((x1 + x2) / 2) / self.image_width
                y_center = ((y1 + y2) / 2) / self.image_height
                width = abs(x2 - x1) / self.image_width
                height = abs(y2 - y1) / self.image_height
                category_id = self.categories.index(category)
                file.write(f"{category_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def load_labels(self, image_path):
        txt_path = os.path.splitext(image_path)[0] + ".txt"
        if os.path.exists(txt_path):
            with open(txt_path, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        category_id, x_center, y_center, width, height = map(float, parts)
                        category = self.categories[int(category_id)]
                        x1 = (x_center - width / 2) * self.image_width
                        y1 = (y_center - height / 2) * self.image_height
                        x2 = (x_center + width / 2) * self.image_width
                        y2 = (y_center + height / 2) * self.image_height
                        rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.get_category_color(category), width=2)
                        rect_id = len(self.objects) + 1
                        self.objects.append((rect, (x1, y1, x2, y2), category, rect_id))
                        self.obj_listbox.insert(tk.END, f"#{rect_id} śmieć - {category.lower()}")

    def next_image(self, event=None):
        if self.images:
            image_path = os.path.join(IMAGE_FOLDER, self.images[self.current_image_index])
            self.save_labels(image_path)
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.load_image()

    def previous_image(self, event=None):
        if self.images:
            image_path = os.path.join(IMAGE_FOLDER, self.images[self.current_image_index])
            self.save_labels(image_path)
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.load_image()

    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_object = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=self.get_category_color(self.selected_category.get()), width=2)

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

            category = self.selected_category.get()
            object_id = len(self.objects) + 1
            self.objects.append((self.current_object, object_coords, category, object_id))
            self.obj_listbox.insert(tk.END, f"#{object_id} śmieć - {category.lower()}")
            self.current_object = None

    def change_category(self):
        selected_index = self.obj_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            new_category = self.selected_category.get()
            object_id = self.objects[selected_index][3]
            self.objects[selected_index] = (
                self.objects[selected_index][0],
                self.objects[selected_index][1],
                new_category,
                object_id
            )
            self.obj_listbox.delete(selected_index)
            self.obj_listbox.insert(selected_index, f"#{object_id} śmieć - {new_category.lower()}")
            self.canvas.itemconfig(self.objects[selected_index][0], outline=self.get_category_color(new_category))

    def delete_object(self, event=None):
        selected_index = self.obj_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            object_id, _, _, _ = self.objects[selected_index]
            self.canvas.delete(object_id)
            self.obj_listbox.delete(selected_index)
            del self.objects[selected_index]


    def get_category_color(self, category):
        colors = {
            "Plastik": "yellow",
            "Metal": "red",
            "Szkło": "green",
            "Papier": "blue"
        }
        return colors.get(category, "white")

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingForTV(root)
    root.mainloop()
