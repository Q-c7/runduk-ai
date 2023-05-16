from picker.app.logic.core import ProgramRunnerWithoutGUI
from picker.app.old_python_gui.picker_frame.prediction_display import PredictionDisplay
from picker.app.old_python_gui.stub import AbstractFrame


class DesktopProgramRunner(ProgramRunnerWithoutGUI):
    def __init__(self, model_path="latest"):
        super().__init__(model_path=model_path)

        self._ui_elements: list[AbstractFrame] = []
        self.prediction_display = None

    def set_prediction_display(self, prediction_display: PredictionDisplay) -> None:
        self.prediction_display = prediction_display

    def add_ui_element(self, new_element: AbstractFrame) -> None:
        self._ui_elements.append(new_element)

    def _redraw_predictions(self) -> None:
        assert self.prediction_display is not None

        for ui_element in self._ui_elements:
            ui_element.update_ui()

        self._refresh_predictions()

        self.prediction_display.update_preds(self.latest_predictions)
        self.prediction_display.update_ui()
