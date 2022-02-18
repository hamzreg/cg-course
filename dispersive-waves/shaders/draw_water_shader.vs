#version 330 core

layout (location = 0) in vec3 vrtx;

uniform sampler2D heightMap;
uniform float step;
uniform mat4 perspective;
uniform mat4 view;
uniform mat4 model;
uniform mat3 TrInvModel;

out vec3 vFragPos;
out vec3 vNormal;

void main() {
    vec2 coord = 0.5 * vrtx.xz + 0.5; // [-1.0, 1.0] to [0.0, 1.0]
    float h = texture2D(heightMap, coord).y;
    gl_Position = perspective * view * model * vec4(vrtx.x, h, vrtx.z, 1.0);
    vFragPos = vec3(model * vec4(vrtx.x, h, vrtx.z, 1.0));

    vec3 dx = vec3(step, texture(heightMap, vec2(coord.x + step, coord.y)).y - h, 0.0);
    vec3 dz = vec3(0.0, texture(heightMap, vec2(coord.x, coord.y + step)).y - h, step);
    vNormal = normalize(cross(dz, dx));
    vNormal = TrInvModel * vNormal;
    vNormal = normalize(vNormal);
}
