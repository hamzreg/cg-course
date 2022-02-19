#version 330 core

in vec3 vFragPos;
in vec3 vNormal;
in vec2 vUV;

uniform sampler2D textureImage;
uniform vec3 lightPos;

void main() {
    vec3 norm = normalize(vNormal);
    vec3 lightDir = normalize(lightPos - vFragPos);
    vec4 diffuse = vec4(vec3(max(dot(norm, lightDir), 0.0)), 1.0);

    vec4 sphereColor = texture(textureImage, vUV);
    vec4 waterColor = vec4(0.0, 0.58, 0.71, 0.5);
    vec4 objectColor = sphereColor;
    vec4 ambient = objectColor * 0.5;

    gl_FragColor = max(ambient, diffuse) * objectColor;
}