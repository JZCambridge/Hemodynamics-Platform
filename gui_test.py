import sys
import matplotlib.pyplot as plt
from PySide2.QtWidgets import QApplication, QLabel, QWidget
from vtkmodules.vtkRenderingCore import vtkRenderWindow, vtkRenderer

# Matplotlib test
plt.plot([1, 2, 3], [4, 5, 1])
plt.title("Matplotlib Test")
plt.show(block=False)  # Non-blocking for concurrent Qt/VTK tests

# PySide2 test
app = QApplication.instance() or QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("PySide2 Test")
label = QLabel("GUI Working!", parent=window)
window.show()

# VTK test
renderer = vtkRenderer()
render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(400, 400)
render_window.SetWindowName("VTK Test")
render_window.Render()

# Keep everything open until closed
app.exec_()
plt.close('all')