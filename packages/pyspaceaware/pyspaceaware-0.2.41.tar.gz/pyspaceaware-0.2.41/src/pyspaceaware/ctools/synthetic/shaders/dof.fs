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
uniform sampler2D unblurred_tex;
uniform sampler2D blurred_tex;
uniform sampler2D depth_tex;

void main()
{
    // Texel color fetching from texture sampler
    float depth = texture(unblurred_tex, fragTexCoord).b;
    vec3 unblur = texture(unblurred_tex, fragTexCoord).rgb;
    vec3 blur = texture(blurred_tex, fragTexCoord).rgb;

    float focus_dist = 0.5;
    float focus_width = 0.5;
    float unfocus_frac;
    if (depth > focus_dist) {
        unfocus_frac = smoothstep(focus_dist, focus_dist+focus_width, depth);
    }
    else {
        unfocus_frac = 1 - smoothstep(focus_dist-focus_width, focus_dist, depth);
    }
    float focus_col = unblur.r * (1 - unfocus_frac) + blur.r * unfocus_frac;
    finalColor = vec4(focus_col, unblur.gb, 1.0);
    // finalColor = vec4(1-unfocus_frac, 0.0, 0.0, 1.0);
    // finalColor = vec4(depth, 0.0, 0.0, 1.0);
    // finalColor = vec4(gl_Position, 1.0);
}