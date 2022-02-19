#version 330 core

layout(location=0) in vec3 position;
layout(location=1) in vec2 sphereTexture;
layout(location=2) in vec3 normal;


const float time = 0.05;

uniform float change;
uniform mat4 perspective;
uniform mat4 view;
uniform mat4 model;
uniform mat3 TrInvModel;

out vec3 vFragPos;
out vec3 vNormal;
out vec2 vUV;

void main() {
    vec3 pos = position;

    if (pos.x < 1.0)
    {
        pos.x += change;
        pos.z += change;
    }

    gl_Position = perspective * view * model * vec4(pos, 1.0);
    vFragPos = vec3(model * vec4(position, 1.0));
    vNormal = TrInvModel * normal;
    vUV = sphereTexture;
}
