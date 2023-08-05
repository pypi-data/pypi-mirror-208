#version 330

in vec3 fragPosition;
in vec2 fragTexCoord;
in vec3 fragNormal;
in vec3 lightPosition;

out vec4 fragColor;

uniform sampler2D texture0;
uniform float cam_far;
// Input lighting values

void main()
{
    vec3 lightDir = normalize(lightPosition);
    float d = -dot(fragPosition - lightPosition, lightDir) / cam_far;
    float lost_d = d-floor(255.0*d+0.5)/255.0;
    fragColor = vec4(d-lost_d, lost_d*255, 0.0, 1.0);
}
