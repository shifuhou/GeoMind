import ezdxf
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.patches import Circle

# 读取 DXF 文件
doc = ezdxf.readfile("static/files/output.dxf")
msp = doc.modelspace()

# 创建一个图形和轴
fig, ax = plt.subplots()
ax.set_aspect('equal', adjustable='datalim')
ax.margins(0.05)

# 删除坐标轴
ax.axis('off')

# 遍历模型空间中的所有实体
for e in msp:
    if e.dxftype() == 'LINE':
        start = e.dxf.start
        end = e.dxf.end
        ax.plot([start.x, end.x], [start.y, end.y], color='black')
    elif e.dxftype() == 'ARC':
        center = e.dxf.center
        radius = e.dxf.radius
        start_angle = e.dxf.start_angle
        end_angle = e.dxf.end_angle
        arc = Arc((center.x, center.y), 2 * radius, 2 * radius, angle=0, theta1=start_angle, theta2=end_angle)
        ax.add_patch(arc)
    elif e.dxftype() == 'SPLINE':
        # 提取样条曲线的点
        spline_points = list(e.approximate_bezier())
        for bezier in spline_points:
            x = [pt.x for pt in bezier.control_points]
            y = [pt.y for pt in bezier.control_points]
            t = np.linspace(0, 1, 100)
            bezier_x = np.polyval(np.polyfit(t, x, len(x) - 1), t)
            bezier_y = np.polyval(np.polyfit(t, y, len(y) - 1), t)
            ax.plot(bezier_x, bezier_y, color='black')
    elif e.dxftype() == 'CIRCLE':
        center = e.dxf.center
        radius = e.dxf.radius
        circle = Circle((center.x, center.y), radius, edgecolor='black', facecolor='none')
        ax.add_patch(circle)

# 设置坐标轴范围
ax.autoscale_view()

# 保存为图片
plt.savefig('static/imgs/sketch.png', dpi=300)


