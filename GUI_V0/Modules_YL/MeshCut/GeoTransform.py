# used to input x,y,z coordinates then calculate and return normal

import numpy
import numpy as np
import vtk
from numpy.linalg import det

class GeoTrans:
    def __init__(self):
        self.length = 6
        self.width = 6
        self.height = 6

        self.ExtRadius = 2
    def setSize(self, ExtRadius, height):
        # self.length = int(length)
        # self.width = int(width)
        # self.height = int(height)

        self.ExtRadius = float(ExtRadius)
        self.height = int(height)

    def GetSize(self):
        return self.length, self.width, self.height

    def Standlize(self, vector):
        sum = 0
        stand = []
        for item in vector:
            sum += np.square(item)

        modulus = numpy.sqrt(sum)

        for item in vector:
            stand.append(item / modulus)

        return stand

    # def __setLength__(self, length):
    #     self.length = length
    #
    # def __setWidth__(self, width):
    #     self.width = width
    #
    # def __setHeight__(self, height):
    #     self.height = height

    # test points
    # x = np.array([106.33936757420483, 109.74872248715933, 53.32491184564412])
    # y = np.array([106.95294918472675, 111.61944341091554, 53.46193778235961])
    # z = np.array([106.34523036867199, 109.29720436918845, 52.02688087182512])

    # x, y, z used to determine the plane, w is the point used to determine direction
    def calculate(self, x, y, z, w, flag):
        xy = np.subtract(y, x)
        xz = np.subtract(z, x)

        normal = np.cross(xy, xz)

        # center = np.add(x, y)
        # center = np.add(center, z)
        # center = np.divide(center, 3)



        # print('center equals to', center)

        center, radius = self.CrcumscribedCircle(x, y, z)

        print('radius is {}'.format(radius))

        # e1 = np.subtract(x, y)
        e1 = np.subtract(z, x)

        e1 = self.Standlize(e1)

        e2 = np.cross(normal, e1)
        e2 = self.Standlize(e2)
        # normal = standlize(normal)
        # print("normal equals", normal)
        # print("e1 equals", e1)
        # print("e2 equals", e2)

        print('extension is {}'.format(self.ExtRadius))

        newRadius = radius + self.ExtRadius

        self.length = newRadius * 2
        self.width = newRadius * 2
        self.height = self.height

        print("length is {}".format(self.length))
        print("width is {}".format(self.width))
        print("height is {}".format(self.height))

        a = np.multiply(e1, self.length / 2)
        b = np.multiply(e2, self.width / 2)

        c = np.multiply(e1, -self.length / 2)
        d = np.multiply(e2, -self.width / 2)

        # calculate the coordiate of points
        point1 = np.add(c, d)
        point1 = np.add(center, point1)

        point2 = np.add(a, b)
        point2 = np.add(center, point2)

        point3 = np.add(a, d)
        point3 = np.add(center, point3)

        point4 = np.add(b, c)
        point4 = np.add(center, point4)

        # correct the direction of normal
        navigate_point = w
        navigate_vector = np.subtract(navigate_point, center)

        normal_mold = np.linalg.norm(normal)

        b_mold = np.linalg.norm(navigate_vector)

        dot_product = np.dot(normal, navigate_vector)
        angle_val = dot_product / (normal_mold * b_mold)

        # print("angle value is", angle_val)
        distance = np.multiply(self.Standlize(normal), self.height)
        # distance = np.multiply(normal, self.height)
        print('center is ', center)
        print('distance is ', distance)

        if angle_val > 0 and flag == "Forward":
            trans_point1 = np.add(point1, distance)
            trans_point2 = np.add(point2, distance)
            trans_point3 = np.add(point3, distance)
            trans_point4 = np.add(point4, distance)

        elif angle_val > 0 and flag == "Backward":
            trans_point1 = np.subtract(point1, distance)
            trans_point2 = np.subtract(point2, distance)
            trans_point3 = np.subtract(point3, distance)
            trans_point4 = np.subtract(point4, distance)

        elif angle_val < 0 and flag == "Backward":
            trans_point1 = np.add(point1, distance)
            trans_point2 = np.add(point2, distance)
            trans_point3 = np.add(point3, distance)
            trans_point4 = np.add(point4, distance)

        else:
            trans_point1 = np.subtract(point1, distance)
            trans_point2 = np.subtract(point2, distance)
            trans_point3 = np.subtract(point3, distance)
            trans_point4 = np.subtract(point4, distance)

        normal2 = np.cross(np.subtract(trans_point1, trans_point4), np.subtract(trans_point2, trans_point4))
        normal3 = np.cross(np.subtract(point4, trans_point2), np.subtract(trans_point1, trans_point2))
        normal4 = np.cross(np.subtract(point2, trans_point2), np.subtract(trans_point3, trans_point2))
        normal5 = np.cross(np.subtract(point4, trans_point4), np.subtract(trans_point2, trans_point4))
        normal6 = np.cross(np.subtract(point1, trans_point1), np.subtract(trans_point3, trans_point1))

        # calculate the polar values of x,y,z
        # x_collection = []
        # y_collection = []
        # z_collection = []
        # names = locals()
        # for i in range(4):
        #     x_collection.append(names['point' + str(i+1)][0])
        #     x_collection.append(names['trans_point' + str(i+1)][0])
        #     y_collection.append(names['point' + str(i + 1)][1])
        #     y_collection.append(names['trans_point' + str(i + 1)][1])
        #     z_collection.append(names['point' + str(i + 1)][2])
        #     z_collection.append(names['trans_point' + str(i + 1)][2])

        # use calculated normal of each face to set plane function
        plane1 = vtk.vtkPlane()
        plane2 = vtk.vtkPlane()
        plane3 = vtk.vtkPlane()
        plane4 = vtk.vtkPlane()
        plane5 = vtk.vtkPlane()
        plane6 = vtk.vtkPlane()

        if angle_val > 0 and flag == "Forward":
            plane1.SetOrigin(point1)
            plane1.SetNormal(normal)

            plane2.SetOrigin(trans_point1)
            plane2.SetNormal(-normal2)

            plane3.SetOrigin(point4)
            plane3.SetNormal(-normal3)

            plane4.SetOrigin(point2)
            plane4.SetNormal(normal4)

            plane5.SetOrigin(point4)
            plane5.SetNormal(normal5)

            plane6.SetOrigin(point3)
            plane6.SetNormal(-normal6)

        elif angle_val > 0 and flag == "Backward":
            plane1.SetOrigin(point1)
            plane1.SetNormal(-normal)

            plane2.SetOrigin(trans_point1)
            plane2.SetNormal(normal2)

            plane3.SetOrigin(point4)
            plane3.SetNormal(normal3)

            plane4.SetOrigin(point2)
            plane4.SetNormal(-normal4)

            plane5.SetOrigin(point4)
            plane5.SetNormal(-normal5)

            plane6.SetOrigin(point3)
            plane6.SetNormal(normal6)

        elif angle_val < 0 and flag == "BackWard":
            plane1.SetOrigin(point1)
            plane1.SetNormal(normal)

            plane2.SetOrigin(trans_point1)
            plane2.SetNormal(-normal2)

            plane3.SetOrigin(point4)
            plane3.SetNormal(-normal3)

            plane4.SetOrigin(point2)
            plane4.SetNormal(normal4)

            plane5.SetOrigin(point4)
            plane5.SetNormal(normal5)

            plane6.SetOrigin(point3)
            plane6.SetNormal(-normal6)

        elif angle_val < 0 and flag == "Forward":
            plane1.SetOrigin(point1)
            plane1.SetNormal(-normal)

            plane2.SetOrigin(trans_point1)
            plane2.SetNormal(normal2)

            plane3.SetOrigin(point4)
            plane3.SetNormal(normal3)

            plane4.SetOrigin(point2)
            plane4.SetNormal(-normal4)

            plane5.SetOrigin(point4)
            plane5.SetNormal(-normal5)

            plane6.SetOrigin(point3)
            plane6.SetNormal(normal6)
        else:
            pass

        # set values for return value
        # collection = [x_max, x_min, y_max, y_min, z_max, z_min]
        # collection stores the plane info from three input points
        collection = [normal, point1, point3, point4]
        plane_collection = [plane1, plane2, plane3, plane4, plane5, plane6]

        point_collection = [point1, point2, point3, point4, trans_point1, trans_point2, trans_point3, trans_point4]
        normal_collection = [normal, normal2, normal3, normal4, normal5, normal6]

        return collection, plane_collection, point_collection, normal_collection


    def CrcumscribedCircle(self, p1, p2, p3):
        p1 = np.array(p1)
        p2 = np.array(p2)
        p3 = np.array(p3)
        num1 = len(p1)
        num2 = len(p2)
        num3 = len(p3)

        # 输入检查
        if (num1 == num2) and (num2 == num3):
            if num1 == 2:
                p1 = np.append(p1, 0)
                p2 = np.append(p2, 0)
                p3 = np.append(p3, 0)
            elif num1 != 3:
                print('\t仅支持二维或三维坐标输入')
                return None
        else:
            print('\t输入坐标的维数不一致')
            return None

        # 共线检查
        temp01 = p1 - p2
        temp02 = p3 - p2
        temp03 = np.cross(temp01, temp02)
        temp = (temp03 @ temp03) / (temp01 @ temp01) / (temp02 @ temp02)
        if temp < 10 ** -6:
            print(r'\t三点共线, 无法确定圆')
            return None

        temp1 = np.vstack((p1, p2, p3))
        temp2 = np.ones(3).reshape(3, 1)
        mat1 = np.hstack((temp1, temp2))  # size = 3x4

        m = +det(mat1[:, 1:])
        n = -det(np.delete(mat1, 1, axis=1))
        p = +det(np.delete(mat1, 2, axis=1))
        q = -det(temp1)

        temp3 = np.array([p1 @ p1, p2 @ p2, p3 @ p3]).reshape(3, 1)
        temp4 = np.hstack((temp3, mat1))
        temp5 = np.array([2 * q, -m, -n, -p, 0])
        mat2 = np.vstack((temp4, temp5))  # size = 4x5

        A = +det(mat2[:, 1:])
        B = -det(np.delete(mat2, 1, axis=1))
        C = +det(np.delete(mat2, 2, axis=1))
        D = -det(np.delete(mat2, 3, axis=1))
        E = +det(mat2[:, :-1])

        pc = -np.array([B, C, D]) / 2 / A
        r = np.sqrt(B * B + C * C + D * D - 4 * A * E) / 2 / abs(A)

        return pc, r

# dis1 = 0
# dis2 = 0


# def dis():
#     sum = 0
#     diff = np.subtract(point2, point1)
#     diff2 = np. subtract(trans_point1, point2)
#     for i in range(3):
#         sum += np.square(diff[i])
#
#     dis1 = np.sqrt(sum)
#     sum = 0
#
#     for i in range(3):
#         sum += np.square(diff2[i])
#     print(sum)
#
#     dis2 = np.sqrt(sum)
#
#     print('平面对角距离为', dis1)
#     print('空间对角距离为', dis2)
# dis()



