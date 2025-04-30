# save as vtk_test.py
import vtk
import os
import sys

# Create a cone
cone = vtk.vtkConeSource()
cone.SetHeight(3.0)
cone.SetRadius(1.0)
cone.SetResolution(10)
cone.Update()

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cone.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer and render window
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)

# Test offscreen rendering
renderWindow = vtk.vtkRenderWindow()
renderWindow.SetSize(300, 300)
renderWindow.SetOffScreenRendering(1)
renderWindow.AddRenderer(renderer)

print("Starting offscreen render...")
renderWindow.Render()
print("Offscreen render successful!")

# Save to file
windowToImageFilter = vtk.vtkWindowToImageFilter()
windowToImageFilter.SetInput(renderWindow)
windowToImageFilter.Update()

writer = vtk.vtkPNGWriter()
writer.SetFileName("test_offscreen.png")
writer.SetInputConnection(windowToImageFilter.GetOutputPort())
writer.Write()
print("Saved offscreen render to test_offscreen.png")

# If not launched with "--offscreen" argument, try interactive rendering too
if len(sys.argv) < 2 or sys.argv[1] != "--offscreen":
    try:
        print("Attempting interactive rendering...")
        # Try interactive rendering
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(300, 300)
        renderWindow.AddRenderer(renderer)

        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)
        renderWindowInteractor.Initialize()
        
        renderWindow.Render()
        print("Interactive render window displayed.")
        print("Close the window to continue...")
        renderWindowInteractor.Start()
    except Exception as e:
        print(f"Interactive rendering failed: {e}")