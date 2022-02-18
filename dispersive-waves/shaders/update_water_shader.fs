#version 330 core

in vec2 coord;

const float w = 1.985; // relaxation parameter
const float PI = 3.141592653589793238462643;
const float radius = 0.03;
const float strength = 0.015;

uniform sampler2D currTexture;
uniform sampler2D prevTexture;
uniform bool dropWater;
uniform vec2 center;
uniform float step;

void main()
{
    vec2 dx = vec2(step, 0.0);
    vec2 dy = vec2(0.0, step);

    float average = (texture(currTexture, coord + dy).y +
                     texture(currTexture, coord - dy).y +
                     texture(currTexture, coord + dx).y +
                     texture(currTexture, coord - dx).y  ) * 0.25;

    float prev = texture(prevTexture, coord).y;
    float h = (1.0 - w) * prev + w * average;

    if (dropWater) {
        float drop = max(0.0, 1.0 - length(center - coord) / radius);
        drop = 0.5 - cos(drop * PI) * 0.5;
        h += drop * strength;
    }

    gl_FragColor = vec4(0.0, h, 0.0, 1.0);
}
