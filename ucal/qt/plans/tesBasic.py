from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QSizePolicy,
)
from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal, Qt
from bluesky_queueserver_api import BPlan
from nbs_gui.plans.base import PlanWidget
from nbs_gui.plans.scanPlan import ScanPlanWidget
from nbs_gui.plans.sampleModifier import SampleSelectWidget


class TESCountWidget(PlanWidget):
    def __init__(self, model, parent=None):
        self.display_name = "TES Count"
        print("Initializing TES Count")
        super().__init__(
            model,
            parent,
            {"Count": "tes_count", "XES": "tes_xes"},
            num=int,
            energy=float,
            repeat=int,
            eslit=("Exit Slit", float),
            dwell=float,
            r=("Sample Angle", float),
            group_name=("Group Name", str),
            comment=str,
        )

    def setup_widget(self):
        super().setup_widget()
        self.sample_widget = SampleSelectWidget(self.model, self)
        self.sample_widget.editingFinished.connect(self.check_plan_ready)
        self.basePlanLayout.addWidget(self.sample_widget)

    def check_plan_ready(self):
        """
        Check if all selections have been made and emit the plan_ready signal if they have.
        """
        print("Checking XAS Plan")
        if self.sample_widget.check_ready():
            print("XAS Ready to Submit")
            self.plan_ready.emit(True)
        else:
            print("XAS not ready")
            self.plan_ready.emit(False)

    def submit_plan(self):
        plan = self.current_plan
        samples = self.sample_widget.get_value()
        params = self.get_params()
        for s in samples:
            item = BPlan(plan, **s, **params)
            self.run_engine_client.queue_item_add(item=item)


class TESCalibrateWidget(PlanWidget):
    def __init__(self, model, parent=None):
        print("Initializing TES Calibrate")
        self.display_name = "TES Calibrate"
        super().__init__(
            model,
            parent,
            "tes_calibrate",
            time=float,
            energy=float,
            repeat=int,
            eslit=("Exit Slit", float),
            dwell=float,
            r=("Sample Angle", float),
            group_name=("Group Name", str),
            comment=str,
        )

    def setup_widget(self):
        super().setup_widget()
        self.sample_widget = SampleSelectWidget(self.model, self)
        self.sample_widget.editingFinished.connect(self.check_plan_ready)
        self.basePlanLayout.addWidget(self.sample_widget)

    def check_plan_ready(self):
        """
        Check if all selections have been made and emit the plan_ready signal if they have.
        """
        print("Checking XAS Plan")
        if self.sample_widget.check_ready():
            print("XAS Ready to Submit")
            self.plan_ready.emit(True)
        else:
            print("XAS not ready")
            self.plan_ready.emit(False)

    def submit_plan(self):
        samples = self.sample_widget.get_params()
        params = self.get_params()
        time = params.pop("time")
        for s in samples:
            item = BPlan(self.current_plan, time, **s, **params)
            self.run_engine_client.queue_item_add(item=item)


class TESScanWidget(ScanPlanWidget):
    def __init__(self, model, parent=None):
        self.display_name = "TES Scans"
        print("Initializing TES Scan Widget")

        super().__init__(
            model,
            parent,
            {
                "Scan": "tes_scan",
                "Relative Scan": "tes_rel_scan",
                "List Scan": "tes_list_scan",
            },
        )

    def submit_plan(self):
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        params = self.get_params()
        # start = float(self.modifier_input_from.text())
        # end = float(self.modifier_input_to.text())
        # steps = int(self.modifier_input_steps.text())
        item = BPlan(
            self.current_plan,
            motor,
            params["start"],
            params["end"],
            params["steps"],
            dwell=params.get("dwell", None),
            comment=params.get("comment", None),
        )
        self.run_engine_client.queue_item_add(item=item)
