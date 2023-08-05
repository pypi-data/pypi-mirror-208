#version 330

// Input vertex attributes (from vertex shader)
in vec3 fragPosition;
in vec2 fragTexCoord;
in vec4 fragColor;
in vec3 fragNormal;
in vec4 shadowCoord;

// Input uniform values
uniform sampler2D texture0;
uniform vec4 colDiffuse;
uniform vec4 colSpecular;
uniform int use_brdf;
uniform float cam_far;

// Output fragment color
out vec4 finalColor;

struct Light {
    int enabled;
    int type;
    vec3 position;
    vec3 target;
    vec4 color;
};

// Input lighting values
uniform Light lights[1];
uniform vec3 viewPos;
uniform sampler2D depthTex;
uniform vec3 lightPos;

#define PI 3.14159

float rdot(vec3 v1, vec3 v2) {
    return max(dot(v1, v2), 0.0);
}

float zeta(float v) {
    return v > 0 ? 1 : 0;
}

float light_depth(vec3 fragPosition, vec3 lightPos) {
    // Shadowing offset to overcome shadow acne
    vec3 L = normalize(lightPos);
    vec3 normalOffset = 0.10*L;

    // Point to plane distance computation (from frag position to the oblique plane of the light)
    vec3 v1 = fragPosition + normalOffset;
    float d = -dot(v1 - lightPos, L);    
    return d;
}

float viewer_depth(vec3 fragPosition, vec3 viewPos) {
    vec3 O = normalize(viewPos);
    float d = -dot(fragPosition - viewPos, O);    
    return d;
}


bool shadowmapcheck(float textureDepth, float lightDepth, vec3 lightPos, vec3 N) {
    float theta = acos(dot(normalize(lightPos), N));
    float bias = clamp(0.002 * tan(theta), 0.001, 0.04);
    return (textureDepth < lightDepth - bias);
}

float brdf_diffuse(float cd) {
    return cd/PI;
}

float brdf_phong(vec3 N, vec3 L, vec3 O, vec3 R, float cd, float cs, float n) {
    float diff = brdf_diffuse(cd);
    float RdotO = rdot(R, O);
    float RdotOtoN = pow(RdotO, n);
    float spec = 0.0;
    if(cs > 0) {
        spec = cs * (n+1.0)/(2.0*PI * rdot(N, L)) * RdotOtoN;
    }
    return diff + spec;
}

float brdf_blinn_phong(vec3 N, vec3 L, vec3 O, vec3 R, float cd, float cs, float n) {
    vec3 H = normalize(O + L); // L = k1, O = k2
    float diff = brdf_diffuse(cd);
    float NdotH = rdot(N, H);
    float NdotHtoN = pow(NdotH, n);
    float spec = 0.0;
    if(cs > 0) {
        spec = cs * (n+1)/(2*PI)*NdotHtoN / (4 * rdot(N, L) * rdot(N, O));
    }
    return spec + diff;
}

float brdf_ashikhmin_shirley(vec3 N, vec3 L, vec3 O, float cd, float cs, float n) {
    vec3 H = normalize(O + L); // L = k1, O = k2
    vec3 U = normalize(cross(N, vec3(1.0,0.0,0.0)));
    vec3 V = normalize(cross(N, U));
    float NdH = rdot(N, H);
    float NdL = rdot(N, L);
    float NdO = rdot(N, O);
    float HdKi = rdot(H, L);
    float HdKo = rdot(H, O);
    float HdN = rdot(H, N);
    float HdU = rdot(H, U);
    float HdV = rdot(H, V);

    float fresnel_factor = cs + (1 - cs) * pow(1 - HdKi, 5);
    float specular_pre = (n+1)/(8*PI);
    float specular_main = pow(NdH, n) / (HdKo * max(NdL, NdO));
    float specular = specular_pre * specular_main * fresnel_factor;

    float diffuse_pre = 28 * cd / (23 * PI) * (1 - cs);
    float diffuse_main = (1 - pow(1 - NdL/2, 5)) * (1 - pow(1 - NdO/2, 5));
    float diffuse = diffuse_pre * diffuse_main;
    return diffuse + specular;
}

float cook_torrance_gp(vec3 V, vec3 H, vec3 N, float a) {
    float a2 = pow(a, 2.0);
    float VdH2 = pow(rdot(V, H), 2.0);
    return zeta(rdot(V,H)/rdot(V,N)) * 2 / (1 + sqrt(1 + a2*(1-VdH2)/VdH2));
}

float cook_torrance_gp_simple(vec3 O, vec3 H, vec3 N, vec3 L, float a) {
    float v1 = 2 * rdot(H, N) * rdot(N, O) / rdot(O, H);
    float v2 = 2 * rdot(H, N) * rdot(N, L) / rdot(O, H);
    return min(min(1, v1), v2);
}

float cook_torrance_beckmann(vec3 H, vec3 N, float a) {
    float cos2alpha = pow(rdot(N, H), 2.0);
    float a2 = pow(a, 2.0);
    float c1 = (1 - cos2alpha) / (cos2alpha * a2);
    return exp(-c1) / (PI * a2 * pow(cos2alpha, 2.0));
}

float brdf_cook_torrance(vec3 N, vec3 L, vec3 O, float cd, float cs, float a) {
    // Surface roughness a \in [0,1]
    float diffuse = brdf_diffuse(cd);
    vec3 H = normalize(O + L);
    float OdN2 = pow(rdot(O, N), 2.0);
    float a2 = pow(a, 2.0);
    // float D = a2 * zeta(dot(H, N)) / (PI * pow((OdN2 * (a2 + ((1-OdN2)/OdN2))), 2.0));
    float D = cook_torrance_beckmann(H, N, a);
    // float G = cook_torrance_gp(O, H, N, a) * cook_torrance_gp(L, H, N, a);
    float G = cook_torrance_gp_simple(O, H, N, L, a);
    float F = cs + (1 - cs) * pow(1 - rdot(H, L), 5.0);
    float specular = D * G * F / (4 * rdot(N, L) * rdot(N, O));
    return diffuse + specular;
}

float brdf_glossy(vec3 N, vec3 L, vec3 O, float cs, float s) {
    vec3 R = normalize(2 * dot(N, L) * N - L);
    float a = acos(rdot(R, O));
    float s2 = pow(s, 2.0);
    float a2 = pow(a, 2.0);
    return cs * 1/(2*PI*s2) * exp(-a2/(2*s2)) / rdot(N, L);
}

float brdf_oren_naymar(vec3 L, vec3 O, vec3 N, float cd, float s) {
    float ti = acos(rdot(L,N));
    float to = acos(rdot(O,N));
    vec3 Lp = normalize(L - rdot(L, N) * N);
    vec3 Op = normalize(O - rdot(O, N) * N);
    float cos_phi_diff = rdot(Lp, Op);
    float s2 = pow(s, 2.0);
    float A = 1 - 0.5 * (s2 / (s2 + 0.33));
    float B = 0.45 * (s2 / (s2 + 0.09));
    float alpha = max(ti, to);
    float beta = min(ti, to);
    return cd/PI * (A + (B*max(0,cos_phi_diff)*sin(alpha)*tan(beta)));
}

float rand(vec2 co){
  return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

void main()
{
    Light sun = lights[0];
    vec3 N = fragNormal;
    vec3 L = normalize(lightPos);
    vec3 O = normalize(viewPos);
    vec3 R = normalize(2 * dot(N, L) * N - L);

    float cd;
    float cs;
    float n;
    cd = colDiffuse.r;
    cs = 1 - cd;

    switch(use_brdf) {
        case 0:
            break;
        case 1:
        case 2:
        case 3:
            n = 100;
            break;
        case 4:
            n = 0.2;
            break;
        case 5:
            n = 0.9;
            break;
        case 6:
            n = 0.5;
            break;
    }

    float c = 0;
    switch(use_brdf) {
        case 0:
            c = brdf_diffuse(cd);
            break;
        case 1:
            c = brdf_phong(N, L, O, R, cd, cs, n);
            break;
        case 2:
            c = brdf_blinn_phong(N, L, O, R, cd, cs, n);
            break;
        case 3:
            c = brdf_ashikhmin_shirley(N, L, O, cd, cs, n);
            break;        
        case 4:
            c = brdf_cook_torrance(N, L, O, cd, cs, n);
            break;
        case 5:
            c = brdf_glossy(N, L, O, cs, n);
            break;
        case 6:
            c = brdf_oren_naymar(L, O, N, cd, n);
            break;
    }
    float brightness_factor = 2.5;
    finalColor = vec4(brightness_factor * c * rdot(N, L), 0.0, 0.0, 1.0);
    
    // Depth from the depth texture
    float normalizedTextureDepth = texture(depthTex, shadowCoord.xy).x + texture(depthTex, shadowCoord.xy).y / 255.0;
    float realTextureDepth = normalizedTextureDepth * cam_far;
    float realLightDepth = light_depth(fragPosition, sun.position);
    bool is_shadowed = shadowmapcheck(realTextureDepth, realLightDepth, sun.position, N);

    if(is_shadowed) {
        finalColor.rgb = vec3(0.0, 0.0, 0.0);
    }
    finalColor.g = 1.1/255;
    finalColor.b = viewer_depth(fragPosition, viewPos) / cam_far;

    float current_fract = fract(finalColor.r * 255.0);
    float floor_col = floor(finalColor.r * 255.0);
    float rnum = rand(shadowCoord.xy);
    if (rnum > current_fract) { // ex. if current_fract = 0.3, 70% of the time this triggers
        finalColor.r = floor_col/255.0;
    }
    else { // and 30% of the time this triggers
        finalColor.r = (floor_col + 1)/255.0;
    }
}   