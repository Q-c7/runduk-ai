import base64
import PySimpleGUIWeb as sg

image_data = base64.b64encode(open("example.png", "rb").read()).decode("utf-8")
layout = [
    [
        sg.Graph(
            canvas_size=(800, 600),
            graph_bottom_left=(0, 600),
            graph_top_right=(800, 0),
            key="-GRAPH-",
            enable_events=True,
            drag_submits=True,
            background_color="white",
            button_press_event="BUTTON_PRESS",
            button_release_event="BUTTON_RELEASE",
            motion_event="MOTION",
        )
    ],
]

window = sg.Window("Image with button", layout)

graph = window["-GRAPH-"]
graph.draw_image(data=image_data, location=(0, 0))

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif event == "MOTION":
        x, y = values["-GRAPH-"]
        if graph.FindElemAtLocation((x, y)):
            graph.delete_figure("button")
            button_location = (x - 50, y - 20)
            graph.draw_rectangle(
                button_location,
                (x + 50, y + 20),
                fill_color="white",
                line_color="black",
                line_width=2,
                key="button",
            )
            graph.draw_text("Click", button_location, font=("Arial", 12), color="black")
    elif event == "BUTTON_PRESS":
        if "button" in values:
            print("Button clicked!")

window.close()
