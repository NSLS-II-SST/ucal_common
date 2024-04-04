from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QMessageBox,
    QDialog,
)
from sst_gui.widgets.views import AutoControl, AutoMonitor
from sst_gui.widgets.motor import MotorMonitor, MotorControl
from sst_gui.widgets.manipulator_monitor import (
    ManipulatorMonitor,
    PseudoManipulatorControl,
)

from bluesky_queueserver_api import BPlan


class EnergyMonitor(QGroupBox):
    """
    Display an Energy Model that has energy, gap, and phase
    """

    def __init__(self, energy, parent_model, *args, orientation=None, **kwargs):
        super().__init__("Energy Monitor", *args, **kwargs)
        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()
        for m in energy.energy.pseudo_axes_models:
            vbox1.addWidget(MotorMonitor(m, parent_model))
        vbox1.addWidget(
            MotorMonitor(parent_model.beamline.motors["Exit_Slit"], parent_model)
        )
        vbox1.addWidget(AutoMonitor(energy.cff, parent_model))
        vbox1.addWidget(MotorMonitor(energy.grating_motor, parent_model))
        vbox2 = QVBoxLayout()
        for m in energy.energy.real_axes_models:
            vbox2.addWidget(MotorMonitor(m, parent_model))
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        self.setLayout(hbox)


class EnergyControl(QGroupBox):
    def __init__(self, energy, parent_model, *args, orientation=None, **kwargs):
        super().__init__("Energy Control", *args, **kwargs)

        self.model = energy
        self.parent_model = parent_model
        self.REClientModel = parent_model.run_engine
        print("Creating Energy Control Vbox")
        vbox = QVBoxLayout()
        print("Creating Energy Motor")
        for m in energy.energy.pseudo_axes_models:
            vbox.addWidget(MotorControl(m, parent_model))
        # vbox.addWidget(PseudoManipulatorControl(energy.energy, parent_model))
        print("Creating Exit Slit")
        vbox.addWidget(
            MotorControl(parent_model.beamline.motors["Exit_Slit"], parent_model)
        )
        vbox.addWidget(AutoMonitor(energy.cff, parent_model))

        self.advancedControlButton = QPushButton("Advanced Controls")
        self.advancedControlButton.clicked.connect(self.showAdvancedControls)
        vbox.addWidget(
            self.advancedControlButton
        )  # Assuming vbox is your main QVBoxLayout
        self.setLayout(vbox)

    def showAdvancedControls(self):
        """
        Show the Advanced Energy Control dialog.
        """
        self.advancedDialog = QDialog(self)
        self.advancedDialog.setWindowTitle("Advanced Energy Control")
        layout = QVBoxLayout()
        advancedControl = AdvancedEnergyControl(
            self.model, self.parent_model, self.advancedDialog
        )
        layout.addWidget(advancedControl)
        self.advancedDialog.setLayout(layout)
        self.advancedDialog.exec_()


class AdvancedEnergyControl(QGroupBox):
    def __init__(self, model, parent_model, parent=None):
        super().__init__("Advanced Energy Control", parent)
        self.model = model
        self.parent_model = parent_model
        self.REClientModel = parent_model.run_engine

        layout = QVBoxLayout()
        layout.addWidget(AutoControl(model.cff, parent_model))

        print("Making hbox")
        hbox = QHBoxLayout()
        hbox.addWidget(MotorMonitor(model.grating_motor, parent_model))
        print("Making ComboBox")
        cb = QComboBox()
        self.cb = cb
        cb.addItem("250 l/mm", 2)
        cb.addItem("1200 l/mm", 9)
        self.button = QPushButton("Change Grating")
        self.button.clicked.connect(self.change_grating)
        hbox.addWidget(cb)
        hbox.addWidget(self.button)

        self.tuneButton = QPushButton("Tune grating offsets")
        self.tuneButton.clicked.connect(self.tune_grating)
        hbox.addWidget(self.tuneButton)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def tune_grating(self):
        if self.confirm_dialog("Ensure that beamline is opened to multimesh reference ladder for tune"):
            plan = BPlan("tune_grating")
            self.REClientModel._client.item_execute(plan)

    def change_grating(self):
        enum = self.cb.currentData()
        print(enum)
        if self.confirm_dialog("Are you sure you want to change gratings?"):
            if enum == 9:
                plan = BPlan("base_grating_to_1200")
            else:
                plan = BPlan("base_grating_to_250")
            self.REClientModel._client.item_execute(plan)

    def confirm_dialog(self, confirm_message):
        """
        Show the confirmation dialog with the proper message in case
        ```showConfirmMessage``` is True.

        Returns
        -------
        bool
            True if the message was confirmed or if ```showCofirmMessage```
            is False.
        """

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)

        msg.setText(confirm_message)

        # Force "Yes" button to be on the right (as on macOS) to follow common design practice
        msg.setStyleSheet("button-layout: 1")  # MacLayout

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        ret = msg.exec_()
        if ret == QMessageBox.No:
            return False
        return True
