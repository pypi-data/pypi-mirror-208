#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "raylib.h"
#include "raymath.h"

#define HEADER_OFFSET     21
#define DATA_OFFSET       11
#define DATA_LINE_LENGTH  66
#define GLSL_VERSION      330
#define MAX_INSTANCES     25

// Shader location index
typedef enum {
    LIGHTING_SHADER_LOC_VIEW_POS = 15,
    LIGHTING_SHADER_LOC_LIGHT_POS,
    LIGHTING_SHADER_LOC_GRID_WIDTH,
    LIGHTING_SHADER_LOC_DEPTH_TEX,
    LIGHTING_SHADER_LOC_VIEW_MVP,
    LIGHTING_SHADER_LOC_LIGHT_MVP,
    LIGHTING_SHADER_LOC_BRDF_INDEX,
    LIGHTING_SHADER_LOC_BRDF_CD,
    LIGHTING_SHADER_LOC_BRDF_CS,
    LIGHTING_SHADER_LOC_BRDF_N,
    LIGHTING_SHADER_LOC_USE_MTL_FLAG,
    LIGHTING_SHADER_LOC_CAM_FAR
} LightingShaderLocationIndex;

typedef enum {
    BLUR_SHADER_LOC_UNBLURRED_TEX = 15
} BlurShaderLocationIndex;

typedef enum {
    DOF_SHADER_LOC_UNBLURRED_TEX = 15,
    DOF_SHADER_LOC_BLURRED_TEX,
    DOF_SHADER_LOC_DEPTH_TEX
} DofShaderLocationIndex;


void ReadLightCurveCommandFile(char *filename, Vector3 sun_vectors[], Vector3 viewer_vectors[], int data_points);
void printMatrix(Matrix m);
Matrix CalculateMVPFromCamera(Camera light_camera, Vector3 offset, float cam_far);
Matrix CalculateMVPBFromMVP(Matrix mvp_light);
void SaveCameraDepthMask(char fname[], Texture2D depth_texture);
void SaveScreen(char fname[], Texture2D rendered_texture);
void SaveModelMask(char fname[], Texture2D rendered_texture);
Vector3 TransformOffsetToCameraPlane(Camera cam, Vector3 offset);
void InitializeCamera(Camera *cam, float fov_deg);
void GetLCShaderLocations(Shader *depthShader, Shader *lighting_shader, Shader *blurShader, Shader *dofShader);
void printVector3(Vector3 vec, const char name[]);
void InitializeObjects(char model_path[], Model *model, 
                       Camera *viewer_camera, Camera *light_camera, float *mesh_scale_factor,
                       float fov_deg);
void UnloadObjects(Model *model, Mesh *mesh);

//----------------------------------------------------------------------------------
// Function definitions
//----------------------------------------------------------------------------------
void UnloadObjects(Model *model, Mesh *mesh)
{
    printf("Unloading model!\n");
    UnloadModel(*model);
}

void InitializeObjects(char model_path[], Model *model, 
                       Camera *viewer_camera, Camera *light_camera, 
                       float *mesh_scale_factor, float fov_deg)
{
    printf("Initializing objects\n");
    *model = LoadModel(model_path);
    InitializeCamera(viewer_camera, fov_deg);
    InitializeCamera(light_camera, fov_deg);
}

void ReadLightCurveCommandFile(char *filename, Vector3 sun_vectors[], Vector3 viewer_vectors[], int data_points)
{
  char *file_contents = LoadFileText(filename);
  int begin_data_index = TextFindIndex(file_contents, "Begin data");

  //Sun and observer data parsing
  for(int line_num = 0; line_num < data_points; line_num++) {
    char *data = strtok(file_contents + begin_data_index + 10 + DATA_LINE_LENGTH * line_num, "\n");

    if(line_num > 1) {
      data = strtok(file_contents + begin_data_index + 10 + DATA_LINE_LENGTH * line_num - line_num + 1, "\n");
    }

    data = TextReplace(data, "   ", ",");
    data = TextReplace(data, "  ", ",");
    data = TextReplace(data, " ", ",");

    double sun_vector_x = atof(strtok(data, ","));
    double sun_vector_y = atof(strtok(NULL, ","));
    double sun_vector_z = atof(strtok(NULL, ","));

    double viewer_vector_x = atof(strtok(NULL, ","));
    double viewer_vector_y = atof(strtok(NULL, ","));
    double viewer_vector_z = atof(strtok(NULL, ","));

    sun_vectors[line_num] = (Vector3){sun_vector_x, sun_vector_y, sun_vector_z};
    viewer_vectors[line_num] = (Vector3){viewer_vector_x, viewer_vector_y, viewer_vector_z};
  }

  return;
}

void printVector3(Vector3 vec, const char name[])
{
  printf("%s: %.4f, %.4f, %.4f\n", name, vec.x, vec.y, vec.z);
}

void printMatrix(Matrix m) 
{
    printf("\n[ %f %f %f %f\n %f %f %f %f\n %f %f %f %f\n %f %f %f %f ]\n", 
    m.m0, m.m4, m.m8, m.m12, 
    m.m1, m.m5, m.m9, m.m13,  
    m.m2, m.m6, m.m10, m.m14,  
    m.m3, m.m7, m.m11, m.m15);
}

//Calculates the MVP matrix for a camera
Matrix CalculateMVPFromCamera(Camera cam, Vector3 offset, float cam_far)
{
    Matrix matView = MatrixLookAt(cam.position, cam.target, cam.up);
    //Calculate camera view matrix

    float near = 0.01f;
    Matrix matProj = MatrixPerspective(cam.fovy * PI / 180.0f, 1, near, cam_far);
    // Calculate camera projection matrix
    return MatrixMultiply(MatrixMultiply(matView, MatrixTranslate(offset.x, offset.y, offset.z)), matProj);
}

// Calculates the biased MVP matrix for texture sampling
Matrix CalculateMVPBFromMVP(Matrix MVP)
{
    Matrix bias_matrix = {0.5, 0.0, 0.0, 0.0,
                          0.0, 0.5, 0.0, 0.0,
                          0.0, 0.0, 0.5, 0.0,
                          0.5, 0.5, 0.5, 1.0}; 
    // Row-major form of the bias matrix (takes homogeneous coords [-1, 1] -> texture coords [0, 1])

    return MatrixMultiply(MVP, MatrixTranspose(bias_matrix)); 
    // Adds the bias for texture sampling
}

// Saves the current screen image to a file
void SaveScreen(char fname[], Texture2D tex)
{
    Image image = LoadImageFromTexture(tex); 
    ExportImage(image, fname);
    printf("Saved image!\n");
}



Vector3 TransformOffsetToCameraPlane(Camera cam, Vector3 offset)
{
  Vector3 basis1 = cam.up;
  Vector3 normal = Vector3Scale(cam.position, 1.0 / Vector3Length(cam.position));
  Vector3 basis2 = Vector3CrossProduct(basis1, normal);
  Matrix camera_basis = MatrixTranspose((Matrix) {basis2.x, basis2.y, basis2.z, 0.0,
                  basis1.x, basis1.y, basis1.z, 0.0,
                  normal.x, normal.y, normal.z, 0.0,
                  0.0, 0.0, 0.0, 1.0});

  Vector3 transformed_offset = Vector3Transform(offset, camera_basis);
  return transformed_offset;
}

void InitializeCamera(Camera *cam, float fov_deg)
{
    cam->position = Vector3Zero();   // Camera position
    cam->target = Vector3Zero();     // Camera looking at point
    cam->up = Vector3Normalize((Vector3){0.0f, 0.0f, -1.0f});         // Camera up vector (rotation towards target)
    cam->fovy = fov_deg;                              // Camera field-of-view Y
    cam->projection = CAMERA_PERSPECTIVE;         // Camera mode type
}

void GetLCShaderLocations(Shader *depthShader, Shader *lighting_shader, Shader *blurShader, Shader *dofShader) {
    depthShader->locs[LIGHTING_SHADER_LOC_VIEW_POS] = GetShaderLocation(*depthShader, "viewPos");
    depthShader->locs[LIGHTING_SHADER_LOC_LIGHT_POS] = GetShaderLocation(*depthShader, "lightPos");
    depthShader->locs[LIGHTING_SHADER_LOC_LIGHT_MVP] = GetShaderLocation(*depthShader, "light_mvp");
    depthShader->locs[LIGHTING_SHADER_LOC_CAM_FAR] = GetShaderLocation(*depthShader, "cam_far");

    lighting_shader->locs[LIGHTING_SHADER_LOC_VIEW_POS] = GetShaderLocation(*lighting_shader, "viewPos");
    lighting_shader->locs[LIGHTING_SHADER_LOC_LIGHT_POS] = GetShaderLocation(*lighting_shader, "lightPos");
    lighting_shader->locs[LIGHTING_SHADER_LOC_GRID_WIDTH] = GetShaderLocation(*lighting_shader, "grid_width");
    lighting_shader->locs[LIGHTING_SHADER_LOC_DEPTH_TEX] = GetShaderLocation(*lighting_shader, "depthTex");
    lighting_shader->locs[LIGHTING_SHADER_LOC_VIEW_MVP] = GetShaderLocation(*lighting_shader, "view_mvp");
    lighting_shader->locs[LIGHTING_SHADER_LOC_LIGHT_MVP] = GetShaderLocation(*lighting_shader, "light_mvp");
    lighting_shader->locs[LIGHTING_SHADER_LOC_BRDF_INDEX] = GetShaderLocation(*lighting_shader, "use_brdf");
    lighting_shader->locs[LIGHTING_SHADER_LOC_CAM_FAR] = GetShaderLocation(*lighting_shader, "cam_far");

    // blurShader->locs[BLUR_SHADER_LOC_UNBLURRED_TEX] = GetShaderLocation(*blurShader, "unblurred_tex");

    dofShader->locs[DOF_SHADER_LOC_UNBLURRED_TEX] = GetShaderLocation(*dofShader, "unblurred_tex");
    dofShader->locs[DOF_SHADER_LOC_BLURRED_TEX] = GetShaderLocation(*dofShader, "blurred_tex");
    // dofShader->locs[DOF_SHADER_LOC_DEPTH_TEX] = GetShaderLocation(*dofShader, "depth_tex");
}