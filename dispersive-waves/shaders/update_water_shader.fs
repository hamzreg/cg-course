#version 330 core

in vec2 coord;

const float w = 1.985; // relaxation parameter
const float PI = 3.141592653589793238462643;
const float radius = 0.03;
const float strength = 0.015;

uniform sampler2D currTexture;
uniform sampler2D prevTexture;
uniform bool dropWater;
uniform bool moveSphere;
uniform vec3 center;
uniform vec3 oldCenter;
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

    // if (dropWater) {
    //     float drop = max(0.0, 1.0 - length(center - coord) / radius);
    //     drop = 0.5 - cos(drop * PI) * 0.5;
    //     h += drop * strength;
    // }

    if (moveSphere) {
        vec3 toCenter1 = vec3(coord.x * 2.0 - 1.0, 0.0, coord.y * 2.0 - 1.0) - oldCenter;
        float t1 = length(toCenter1) / radius;
        float dy1 = exp(-pow(t1 * 1.5, 6.0));
        float ymin1 = min(0.0, oldCenter.y - dy1);
        float ymax1 = min(max(0.0, oldCenter.y + dy1), ymin1 + 2.0 * dy1);

        h += (ymax1 - ymin1) * 0.1;

        vec3 toCenter2 = vec3(coord.x * 2.0 - 1.0, 0.0, coord.y * 2.0 - 1.0) - center;
        float t2 = length(toCenter2) / radius;
        float dy2 = exp(-pow(t2 * 1.5, 6.0));
        float ymin2 = min(0.0, center.y - dy2);
        float ymax2 = min(max(0.0, center.y + dy2), ymin2 + 2.0 * dy2);

        h -= (ymax2 - ymin2) * 0.1;
    }

    gl_FragColor = vec4(0.0, h, 0.0, 1.0);
}
