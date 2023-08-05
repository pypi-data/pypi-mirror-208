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
    LIGHTING_SHADER_LOC_MODEL_INSTANCE
} LightingShaderLocationIndex;

void ReadLightCurveCommandFile(char *filename, Vector3 sun_vectors[], Vector3 viewer_vectors[], int data_points);
void printMatrix(Matrix m);
Matrix CalculateMVPFromCamera(Camera light_camera, Vector3 offset);
Matrix CalculateMVPBFromMVP(Matrix mvp_light);
void SaveCameraDepthMask(char fname[], Texture2D depth_texture);
void SaveScreen(char fname[], Texture2D rendered_texture);
void SaveModelMask(char fname[], Texture2D rendered_texture);
float CalculateCameraArea(Camera cam);
float CalculateMeshScaleFactor(Model model, Camera cam, int inst_count);
Model ApplyMeshScaleFactor(Model model, float sf);
Vector3 TransformOffsetToCameraPlane(Camera cam, Vector3 offset);
void GenerateTranslations(Vector3 *mesh_offsets, Camera cam, int inst_count);
void CalculateRightAndTop(Camera cam, float *right, float *top);
void InitializeCamera(Camera *cam);
void GetLCShaderLocations(Shader *depthShader, Shader *lighting_shader,
                          Shader *min_shader, int depth_light_mvp_locs[], 
                          int lighting_light_mvp_locs[], int inst_count);
void CalculateLightCurveValues(float lightCurveFunction[], RenderTexture2D minifiedLightCurveTex, 
                               RenderTexture2D brightnessTex, float clipping_area, int inst_count, 
                               float scale_factor);
void printVector3(Vector3 vec, const char name[]);
void WriteLightCurveResults(char results_file[], float light_curve_results[], int data_points);
void ClearLightCurveResults(char results_file[]);
void InitializeObjects(int inst_count, int *grid_width, char model_name[], Model *model, 
                       Camera *viewer_camera, Camera *light_camera, float *mesh_scale_factor);
void UnloadObjects(Model *model, Mesh *mesh);
void FurthestVectorInMeshFromVector(Mesh *mesh, Vector3 v0, Vector3 *v_far);
Vector3 MeshCentroid(Mesh *mesh);
void RotatePanels(Vector3 sun_vector, Vector3 rot_axis, Vector3 normal, Vector3 centroid, Mesh mesh);
void PanelVectors(Mesh panel_mesh, Vector3 *normal, Vector3 *rot_axis, Vector3 *centroid);
int CalculateLargestDisplacementMesh(Model model);

//----------------------------------------------------------------------------------
// Function definitions
//----------------------------------------------------------------------------------
void UnloadObjects(Model *model, Mesh *mesh)
{
    printf("Unloading model!\n");
    UnloadModel(*model);
}

void InitializeObjects(int inst_count, int *grid_width, char model_name[], Model *model, 
                       Camera *viewer_camera, Camera *light_camera, 
                       float *mesh_scale_factor)
{
    printf("Initializing objects\n");
    *grid_width = (int) ceil(sqrt(inst_count));
    *model = LoadModel(TextFormat("%s", model_name));
    InitializeCamera(viewer_camera);
    InitializeCamera(light_camera);
    *mesh_scale_factor = CalculateMeshScaleFactor(*model, *viewer_camera, inst_count);
    *model = ApplyMeshScaleFactor(*model, *mesh_scale_factor);
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
Matrix CalculateMVPFromCamera(Camera cam, Vector3 offset)
{
    Matrix matModel = MatrixRotateX(PI/3);
    Matrix matView = MatrixLookAt(cam.position, cam.target, cam.up);
    //Calculate camera view matrix

    float top;
    float right;
    float near = 0.0001f;
    float far = 1000.0f;
    CalculateRightAndTop(cam, &right, &top);
    Matrix matProj = MatrixOrtho(-right, right, -top, top, near, far);
    // Calculate camera projection matrix

    //Computes the light MVP matrix
    return MatrixMultiply(
           MatrixMultiply(matView, 
           MatrixTranslate(offset.x, offset.y, offset.z)), 
           matProj);
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

float CalculateCameraArea(Camera cam)
{
  float top;
  float right;
  CalculateRightAndTop(cam, &right, &top);
  return 4.0*top*right;
}

void CalculateRightAndTop(Camera cam, float *right, float *top)
{
  float aspect = 1;
  // Screen aspect ratio
  *top = (float) cam.fovy / 2.0;
  // Half-height of the clipping plane
  *right = *top * aspect;
  // Half-width of the clipping plane
}

void SaveCameraDepthMask(char fname[], Texture2D depth_texture) {
    Image image = LoadImageFromTexture(depth_texture); 
    ImageFlipHorizontal(&image);
    ExportImage(image, fname);
    printf("Saved camera depth mask!\n");
}

void SaveModelMask(char fname[], Texture2D rendered_texture) {
    Image image = LoadImageFromTexture(rendered_texture); 
    Color *pixels = LoadImageColors(image);

    for (int y = 0; y < image.height; y++) {
        for (int x = 0; x < image.width; x++) {
            int pos_left = y*image.width + x;
            float g = pixels[pos_left].g;
            pixels[pos_left].r = g;
            pixels[pos_left].g = g;
            pixels[pos_left].b = g;
        }
    }

    RL_FREE(image.data);
    image.data = pixels;
    ImageFlipHorizontal(&image);
    ExportImage(image, fname);
    printf("Saved model mask!\n");
}

// Saves the current screen image to a file
void SaveScreen(char fname[], Texture2D rendered_texture)
{
    Image image = LoadImageFromTexture(rendered_texture); 
    Color *pixels = LoadImageColors(image);

    for (int y = 0; y < image.height; y++) {
        for (int x = 0; x < image.width; x++) {
            int pos_left = y*image.width + x;
            pixels[pos_left].b = 0;
        }
    }

    RL_FREE(image.data);
    image.data = pixels;
    ImageFlipHorizontal(&image);
    ExportImage(image, fname);
    printf("Saved image!\n");
}

int CalculateLargestDisplacementMesh(Model model)
{
  if(model.meshCount == 1) return -1;
  float largest_disp = 0.0;
  int largest_disp_mesh;
  for(int m = 0; m < model.meshCount; m++) {
    for(int i = 0; i < model.meshes[m].vertexCount; i++) {
      Vector3 vertex = {model.meshes[m].vertices[i*3+0],
                        model.meshes[m].vertices[i*3+1],
                        model.meshes[m].vertices[i*3+2]};
      float vertex_disp = Vector3Length(vertex);

      if(vertex_disp > largest_disp) {
        largest_disp = vertex_disp;
        largest_disp_mesh = m;
      }
    }
  }
  return largest_disp_mesh;
}


// Finds the factor required to scale all vertices down to fit the model in a unit cube
float CalculateMeshScaleFactor(Model model, Camera cam, int inst_count)
{
  float largest_disp = 0.0;
  for(int m = 0; m < model.meshCount; m++) {
    for(int i = 0; i < model.meshes[m].vertexCount; i++) {
      Vector3 vertex = {model.meshes[m].vertices[i*3+0],
                        model.meshes[m].vertices[i*3+1],
                        model.meshes[m].vertices[i*3+2]};
      float vertex_disp = Vector3Length(vertex);

      if(vertex_disp > largest_disp) {
        largest_disp = vertex_disp;
      }
    }
  }
  int grid_width = (int) ceil(sqrt(inst_count));  
  float top;
  float right;
  CalculateRightAndTop(cam, &right, &top);

  return grid_width * largest_disp / top;
}

Model ApplyMeshScaleFactor(Model model, float sf)
{  
    for(int m = 0; m < model.meshCount; m++) {
      for(int i = 0; i < model.meshes[m].vertexCount; i++) {
          model.meshes[m].vertices[i*3] = model.meshes[m].vertices[i*3] / sf;
          model.meshes[m].vertices[i*3+1] = model.meshes[m].vertices[i*3+1] / sf;
          model.meshes[m].vertices[i*3+2] = model.meshes[m].vertices[i*3+2] / sf;
      }
      rlUpdateVertexBuffer(model.meshes[m].vboId[0], model.meshes[m].vertices, model.meshes[m].vertexCount*3*sizeof(float), 0);
      rlUpdateVertexBuffer(model.meshes[m].vboId[2], model.meshes[m].normals, model.meshes[m].vertexCount*3*sizeof(float), 0);
    }
    return model;
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

void GenerateTranslations(Vector3 *mesh_offsets, Camera cam, int inst_count) 
{
  float top;
  float right;
  CalculateRightAndTop(cam, &right, &top);

  int square_below = (int) ceil(sqrt(inst_count));

  int index = 0;
  for(int i = 0; i < square_below; i++) {
    for(int j = 0; j < square_below; j++) {
      Vector3 absolute_offset = {-right * (square_below - 1.0) + i * (square_below + 
                                 (4.0 - square_below)), -top * (square_below - 1.0) + 
                                 j * (square_below + (4.0 - square_below)), 0.0};

      mesh_offsets[index] = Vector3Scale(absolute_offset, 1.0 / (float) square_below);
      index++;
      if(index == inst_count) break;
    }
  }
}

void InitializeCamera(Camera *cam)
{
    cam->position = Vector3Zero();   // Camera position
    cam->target = Vector3Zero();     // Camera looking at point
    cam->up = Vector3Normalize((Vector3){0.0f, 0.0f, -1.0f});         // Camera up vector (rotation towards target)
    cam->fovy = 4.0f;                              // Camera field-of-view Y
    cam->projection = CAMERA_ORTHOGRAPHIC;         // Camera mode type
}

void GetLCShaderLocations(Shader *depthShader, Shader *lighting_shader, 
                          Shader *min_shader, int depth_light_mvp_locs[], 
                          int lighting_light_mvp_locs[], int inst_count) {
    depthShader->locs[LIGHTING_SHADER_LOC_VIEW_POS] = GetShaderLocation(*depthShader, "viewPos");
    depthShader->locs[LIGHTING_SHADER_LOC_LIGHT_POS] = GetShaderLocation(*depthShader, "lightPos");
    depthShader->locs[LIGHTING_SHADER_LOC_LIGHT_MVP] = GetShaderLocation(*depthShader, "light_mvp");
    depthShader->locs[LIGHTING_SHADER_LOC_MODEL_INSTANCE] = GetShaderLocation(*depthShader, "model_id");

    for (int i = 0; i < inst_count; i++)
    {
      const char *mat_name = TextFormat("light_mvps[%d].mat\0", i);
      depth_light_mvp_locs[i] = GetShaderLocation(*depthShader, mat_name);
    }

    lighting_shader->locs[LIGHTING_SHADER_LOC_VIEW_POS] = GetShaderLocation(*lighting_shader, "viewPos");
    lighting_shader->locs[LIGHTING_SHADER_LOC_LIGHT_POS] = GetShaderLocation(*lighting_shader, "lightPos");
    lighting_shader->locs[LIGHTING_SHADER_LOC_GRID_WIDTH] = GetShaderLocation(*lighting_shader, "grid_width");
    lighting_shader->locs[LIGHTING_SHADER_LOC_DEPTH_TEX] = GetShaderLocation(*lighting_shader, "depthTex");
    lighting_shader->locs[LIGHTING_SHADER_LOC_VIEW_MVP] = GetShaderLocation(*lighting_shader, "view_mvp");
    lighting_shader->locs[LIGHTING_SHADER_LOC_LIGHT_MVP] = GetShaderLocation(*lighting_shader, "light_mvp");
    lighting_shader->locs[LIGHTING_SHADER_LOC_BRDF_INDEX] = GetShaderLocation(*lighting_shader, "use_brdf");
    lighting_shader->locs[LIGHTING_SHADER_LOC_BRDF_CD] = GetShaderLocation(*lighting_shader, "cd_in");
    lighting_shader->locs[LIGHTING_SHADER_LOC_BRDF_CS] = GetShaderLocation(*lighting_shader, "cs_in");
    lighting_shader->locs[LIGHTING_SHADER_LOC_BRDF_N] = GetShaderLocation(*lighting_shader, "n_in");
    lighting_shader->locs[LIGHTING_SHADER_LOC_USE_MTL_FLAG] = GetShaderLocation(*lighting_shader, "use_mtl");
    
    min_shader->locs[LIGHTING_SHADER_LOC_GRID_WIDTH] = GetShaderLocation(*min_shader, "grid_width");
}

void CalculateLightCurveValues(float lightCurveFunction[], RenderTexture2D minifiedLightCurveTex,
                               RenderTexture2D brightnessTex, float clipping_area, int inst_count, 
                               float scale_factor) {
    int grid_width = (int) ceil(sqrt(inst_count));
    Image light_curve_image = LoadImageFromTexture(minifiedLightCurveTex.texture);
    int total_pixels = brightnessTex.texture.width * brightnessTex.texture.height;
    float instance_total_irrad_est[MAX_INSTANCES];
    int grid_pixel_height = light_curve_image.height / grid_width;
    float sf = 2.0; // Scale factor to account for camera distance
    
    // Calculating shaded light curve values
    for(int col = 0; col < light_curve_image.width; col++) {
      for(int row_instance = 0; row_instance < grid_width; row_instance++) {
        float lighting_factor = 0.0;
        for(int row_instance_pixel = row_instance * grid_pixel_height; row_instance_pixel 
            < (row_instance + 1) * grid_pixel_height; row_instance_pixel++) {
          Color pix_color = GetImageColor(light_curve_image, col, row_instance_pixel);
          // For all lit rows
          if((float) pix_color.g > 0.0) {
            // Number of lit pixels in row
            lighting_factor += ((float) pix_color.r / 255.0 + (float) pix_color.b / 255.0 * 100.0) * grid_pixel_height; 
            // Represents the average irrad of each row * the fraction of lit pixels on that row
          }
        }
        float fraction_of_pixels_lit = 1 / pow((double) grid_pixel_height, 2.0);
        float instance_clipping_area = 1.0 / (float) (grid_width * grid_width) * clipping_area;
        float apparent_model_lit_area_scaled = instance_clipping_area * fraction_of_pixels_lit;
        float apparent_model_lit_area_unscaled = apparent_model_lit_area_scaled * 
                                                 scale_factor * scale_factor; 
        // Removing the mesh scale factor
        
        instance_total_irrad_est[row_instance+grid_width*col] = 
          lighting_factor * apparent_model_lit_area_unscaled / pow(sf, 2.0);
      }
    }
  
    UnloadImage(light_curve_image);
    for(int i = 0; i < inst_count; i++) {
      lightCurveFunction[i] = instance_total_irrad_est[i];
    }
}

void WriteLightCurveResults(char results_file[], float light_curve_results[], int data_points)
{
  printf("Trying to write results... \n");
  FILE *fptr;
  fptr = fopen(results_file, "w");
  for(int i = 0; i < data_points; i++) {    
    fprintf(fptr, "%f\n", light_curve_results[i]);
  }
  fclose(fptr);
}

void ClearLightCurveResults(char results_file[])
{
  remove(results_file);
}

void FurthestVectorInMeshFromVector(Mesh *mesh, Vector3 v0, Vector3 *v_far) {
      float dmax = 0.0;
      int ind = 0;
      for(int f = 0; f < mesh->vertexCount; f++) {
          Vector3 v = (Vector3){mesh->vertices[3*f+0], 
                                mesh->vertices[3*f+1], 
                                mesh->vertices[3*f+2]};
          float di = Vector3Distance(v, v0);
          if(di > dmax) {
            ind = f;
            dmax = di;
          }
      }
    *v_far = (Vector3){mesh->vertices[3*ind+0], 
                      mesh->vertices[3*ind+1], 
                      mesh->vertices[3*ind+2]};
}

Vector3 MeshCentroid(Mesh *mesh) {
    Vector3 centroid = Vector3Zero();
    for(int f = 0; f < mesh->vertexCount; f++) {
        Vector3 dc = (Vector3){mesh->vertices[3*f+0]/mesh->vertexCount, 
                              mesh->vertices[3*f+1]/mesh->vertexCount, 
                              mesh->vertices[3*f+2]/mesh->vertexCount};
        centroid = Vector3Add(dc, centroid);
    }
    return centroid;
}

void RotatePanels(Vector3 sun_vector, Vector3 rot_axis, Vector3 normal, Vector3 centroid, Mesh mesh) {
  Vector3 nprot = Vector3Normalize(
                Vector3Subtract(sun_vector, 
                Vector3Scale(rot_axis, 
                Vector3DotProduct(sun_vector, rot_axis))));
  float thetap_ind = Vector3DotProduct(Vector3CrossProduct(normal, nprot), rot_axis);
  float thetap;
  if(thetap_ind > 0) {
    thetap = acos(Vector3DotProduct(nprot, normal));
  }
  else {
    thetap = -acos(Vector3DotProduct(nprot, normal));
  }
  Matrix panel_transform = MatrixRotate(rot_axis, thetap);
  Matrix panel_transform_for_normals = panel_transform;
  panel_transform = MatrixMultiply(panel_transform, MatrixTranslate(centroid.x, centroid.y, centroid.z));
  panel_transform = MatrixMultiply(MatrixTranslate(-centroid.x, -centroid.y, -centroid.z), panel_transform);
  float *newv = malloc(mesh.vertexCount*3*sizeof(float));
  float *newn = malloc(mesh.vertexCount*3*sizeof(float));

  for(int i = 0; i < mesh.vertexCount; i++) {
  Vector3 v = (Vector3) {mesh.vertices[i*3+0], mesh.vertices[i*3+1], mesh.vertices[i*3+2]};
  Vector3 nv = (Vector3) {mesh.normals[i*3+0], mesh.normals[i*3+1], mesh.normals[i*3+2]};
  v = Vector3Transform(v, panel_transform);
  nv = Vector3Transform(nv, panel_transform_for_normals);
  newv[i*3+0] = v.x; newv[i*3+1] = v.y; newv[i*3+2] = v.z;
  newn[i*3+0] = nv.x; newn[i*3+1] = nv.y; newn[i*3+2] = nv.z;
  }
  rlUpdateVertexBuffer(mesh.vboId[0], newv, mesh.vertexCount*3*sizeof(float), 0);
  rlUpdateVertexBuffer(mesh.vboId[2], newn, mesh.vertexCount*3*sizeof(float), 0);
  free(newv);
  free(newn);
}

void PanelVectors(Mesh panel_mesh, Vector3 *normal, Vector3 *rot_axis, Vector3 *centroid) {
    Vector3 v1; Vector3 v2;
    int si = 0;
    Vector3 v0 = (Vector3) {panel_mesh.vertices[3*si+0], panel_mesh.vertices[3*si+1], panel_mesh.vertices[3*si+2]};
    FurthestVectorInMeshFromVector(&panel_mesh, v0, &v1); // v1 is known to be a corner point
    FurthestVectorInMeshFromVector(&panel_mesh, v1, &v2); // v2-v1 is known to be a panel diagonal (v2 is opposing corner)

    Vector3 v3 = (Vector3){v1.x, v1.y, v1.z}; Vector3 v4 = Vector3Zero();
    while(Vector3Length(Vector3Subtract(v3, v1)) < 0.1 
          || Vector3Length(Vector3Subtract(v4, v1)) < 0.1
          || Vector3DotProduct(Vector3Subtract(v2, v1), Vector3Subtract(v4, v3)) < 0) { // Getting other diagonal
      si++;
      v0 = (Vector3) {panel_mesh.vertices[3*si+0], panel_mesh.vertices[3*si+1], panel_mesh.vertices[3*si+2]};
      FurthestVectorInMeshFromVector(&panel_mesh, v0, &v3);
      FurthestVectorInMeshFromVector(&panel_mesh, v3, &v4);
    }

    Vector3 diag1 = Vector3Subtract(v1, v2);
    Vector3 diag2 = Vector3Subtract(v3, v4);
    *rot_axis = Vector3Normalize(Vector3Add(diag1, diag2));
    *normal = Vector3Normalize(Vector3CrossProduct(diag1, diag2));
    *centroid = MeshCentroid(&panel_mesh);
    printVector3(*normal, "normal: ");
    printVector3(*rot_axis, "rot_axis: ");
    printVector3(*centroid, "centroid: ");
}