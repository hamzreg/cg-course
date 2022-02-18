#version 330 core

in vec3 vSkyboxPos;

uniform samplerCube skybox;

void main() {
    gl_FragColor = texture(skybox, vSkyboxPos);
}
