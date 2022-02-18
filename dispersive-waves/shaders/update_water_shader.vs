#version 330 core

// входные атрибуты вершин
layout (location = 0) in vec3 vrtx;

out vec2 coord;

void main()
{
    coord = 0.5 * vrtx.xz + 0.5;
    gl_Position = vec4(vrtx.xz, 0.0, 1.0);
}
