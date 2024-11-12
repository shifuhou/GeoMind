import json
import os
import random
import pandas as pd
import requests
import numpy as np
from python_code.keys import *
import openai
from openai import OpenAI

import ezdxf
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.patches import Circle

import pyvista as pv
from PIL import Image

client = OpenAI(api_key = gpt_key)
def get_embedding(texts, model="text-embedding-3-small",dim = 256):
   ebs = np.zeros((0, dim), dtype='float32')
   data = client.embeddings.create(input = texts, model=model, dimensions = dim).data
   for eb in data:
      ebs = np.concatenate((ebs,np.array([eb.embedding])),axis=0)
      
   return ebs


def save_sketch_fig(sketch_path,save_path):
    # 读取 DXF 文件
    doc = ezdxf.readfile(sketch_path)
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
    plt.savefig(save_path, dpi=300)
    plt.close(fig)

def save_stl_fig(stl_path, save_path):
    # 启动虚拟帧缓冲区
    pv.start_xvfb()

    # 加载 STL 文件
    mesh = pv.read(stl_path)

    # 保存不同视角的图片
    view_settings = [
        ("isometric_view.png", "isometric"),
        ("front_view.png", (1, 0, 0)),
        ("side_view.png", (0, 1, 0)),
        ("top_view.png", (0, 0, 1))
    ]

    # 遍历视角设置并保存每个视角的图片
    for filename, view in view_settings:
        # 每次创建新的绘图器
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(mesh, color="lightblue")
        
        # 设置不同的视角
        if view == "isometric":
            plotter.view_isometric()
        else:
            plotter.view_vector(view)

        # 保存截图而不显示
        plotter.screenshot(filename)
        plotter.close()

    # 使用 Matplotlib 和 PIL 拼接四张图片
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    # 加载图片
    images = [
        Image.open("isometric_view.png"),
        Image.open("front_view.png"),
        Image.open("side_view.png"),
        Image.open("top_view.png")
    ]

    # 在每个子图中显示图片
    titles = ["Isometric View", "Front View", "Side View", "Top View"]
    for ax, img, title in zip(axes.flatten(), images, titles):
        ax.imshow(img)
        ax.set_title(title)
        ax.axis('off')  # 去掉坐标轴

    # 调整布局并保存拼接后的图片
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close(fig)  # 关闭图形，防止显示在 Notebook 中
