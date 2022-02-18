#version 330 core

in vec3 vFragPos;
in vec3 vNormal;

uniform vec3 cameraPos;
uniform samplerCube skybox;

void main() 
{
    vec3 I = normalize(vFragPos - cameraPos);
    vec3 R = reflect(I, normalize(vNormal));
    gl_FragColor = vec4(texture(skybox, R).rgb, 0.8);
}
