#version 330

// Input vertex attributes (from vertex shader)
in vec2 fragTexCoord;
in vec4 fragColor;

// Input uniform values
uniform sampler2D texture0;
uniform vec4 colDiffuse;


// Output fragment color
out vec4 finalColor;

// NOTE: Add here your custom variables
// uniform sampler2d unblurred_tex;

// NOTE: Render size values must be passed from code
const float renderWidth = 512;
const float renderHeight = 512;

const float PI = 3.141592653589793;
const float sigma = 2.0f;
vec4 GaussianBlur()
{
    vec2 uv = fragTexCoord.xy;
	float twoSigmaSqu = 2 * sigma * sigma;
	int r = int(ceil(sigma * 2.57));
	float allWeight = 0.0f;
	vec4 col = vec4(0.0f, 0.0f, 0.0f, 0.0f);
    for (int ix = -r; ix < (r + 1); ix++) {
	for (int iy = -r; iy < (r + 1); iy++)
	{
		float weight = 1.0f / (PI * twoSigmaSqu) * exp(-((iy * iy + ix * ix)) / twoSigmaSqu);
		vec2 offset = vec2(1.0f / renderHeight * ix, 1.0f / renderHeight * iy);
		vec2 uv_offset = uv + offset;
		uv_offset.x = clamp(uv_offset.x, 0.0f, 1.0f);
		uv_offset.y = clamp(uv_offset.y, 0.0f, 1.0f);
		col += texture(texture0, uv_offset) * weight;
		allWeight += weight;
	}
    }
	col = col / allWeight;
	return col;
}

float offset[3] = float[](0.0, 1.3846153846, 3.2307692308);
float weight[3] = float[](0.2270270270, 0.3162162162, 0.0702702703);

void main()
{
    finalColor = GaussianBlur();
}