#version 330 core

in vec2 coord;

const float w = 1.985;
const float PI = 3.141592653589793238462643;
const float radius = 0.02;
const float strength = 0.015;

uniform sampler2D currTexture;
uniform sampler2D prevTexture;
uniform bool dropWater;
uniform bool moveSphere;
uniform vec2 center;
uniform float sphereRadius;
uniform vec3 nowCenter;
uniform vec3 oldCenter;
uniform float step;

float volumeInSphere(vec3 sphereCenter)
{
    vec3 toCenter = vec3(coord.x * 2.0 - 1.0, 0.0, coord.y * 2.0 - 1.0) - sphereCenter;
    float t = length(toCenter) / sphereRadius;
    float dy = exp(-pow(t * 1.5, 6.0));
    float ymin = min(0.0, sphereCenter.y - dy);
    float ymax = min(max(0.0, sphereCenter.y + dy), ymin + 2.0 * dy);

    return (ymax - ymin) * 0.1;
}

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

    if (dropWater)
    {
        float drop = max(0.0, 1.0 - length(center - coord) / radius);
        drop = 0.5 - cos(drop * PI) * 0.5;
        h += drop * strength;
    }

    if (moveSphere)
    {
        h += volumeInSphere(oldCenter);
        h -= volumeInSphere(nowCenter);
    }

    gl_FragColor = vec4(0.0, h, 0.0, 1.0);
}
