#include "synthetic_include/raylib.h"
#include "synthetic_include/synthetic_image.c"
#include "synthetic_include/rlgl.h"

#define RLIGHTS_IMPLEMENTATION
#include "synthetic_include/rlights.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <Python.h>

#define PY_SSIZE_T_CLEAN
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

void * failure(PyObject *type, const char *message) {
    PyErr_SetString(type, message);
    return NULL;
}

void * success(PyObject *var){
    Py_INCREF(var);
    return var;
}

#define MAX_DATA_POINTS        10000
#define MAX_DIR_LENGTH 100

double numpy_arr_el(PyArrayObject *a, int row, int col) {
    double *el_ptr = PyArray_GETPTR2(a, row, col);
    return *el_ptr;
}

void numpy_to_v3(PyArrayObject *a, Vector3 v[]) {
    int nrows = PyArray_DIM(a, 0);
    for(int i = 0; i < nrows; i++) {
            v[i] = (Vector3) {numpy_arr_el(a, i, 0), 
                              numpy_arr_el(a, i, 1), 
                              numpy_arr_el(a, i, 2)};
    }
}

static PyObject *method_add(PyObject *self, PyObject *args) {
    int width_pix;
    Vector3 sun_vectors[MAX_DATA_POINTS];
    Vector3 viewer_pos[MAX_DATA_POINTS]; 
    Vector3 viewer_look[MAX_DATA_POINTS]; 
    Vector3 viewer_up[MAX_DATA_POINTS]; 
    char *model_file = NULL;
    int brdf_index;
    float cam_far;
    float fov_deg;

    PyArrayObject *sv;
    PyArrayObject *vp;
    PyArrayObject *vl;
    PyArrayObject *cu; // Camera up vector
    if (!PyArg_ParseTuple(args, "O!O!O!O!isiff", 
                            &PyArray_Type, &sv, 
                            &PyArray_Type, &vp,
                            &PyArray_Type, &vl,
                            &PyArray_Type, &cu,
                            &width_pix, 
                            &model_file,
                            &brdf_index,
                            &cam_far,
                            &fov_deg))
        return failure(PyExc_RuntimeError, "Failed to parse parameters.");
    
    if (PyArray_DESCR(sv)->type_num != NPY_DOUBLE)
        return failure(PyExc_TypeError, "Type np.float64 expected for sun vector array.");
    if (PyArray_NDIM(sv)!=2)
        return failure(PyExc_TypeError, "Sun vector must be a 2 dimensionnal array.");

    int data_points = PyArray_DIM(sv, 0);
    numpy_to_v3(sv, sun_vectors);
    numpy_to_v3(vp, viewer_pos);
    numpy_to_v3(vl, viewer_look);
    numpy_to_v3(cu, viewer_up);
    printf("Model name: %s\n", model_file);
    printf("Pixel width: %d\n", width_pix); 
    printf("Data points: %d\n", data_points);
    printf("BRDF index: %d\n", brdf_index);
    printf("Camera far: %f\n", cam_far);

    SetConfigFlags(FLAG_MSAA_4X_HINT);
    InitWindow(width_pix, width_pix, "SyntheticRPO");
    SetTargetFPS(1000);

    Model model;
    Camera viewer_camera;
    Camera light_camera;

    float mesh_scale_factor;

    const Model *model_path = TextFormat("%s/%s", getenv("MODELDIR"), model_file);
    InitializeObjects(model_path, &model, &viewer_camera, &light_camera, &mesh_scale_factor, fov_deg);

    // Loading shaders
    char *shader_path = TextFormat("%s/%s", getenv("SYNTHDIR"), "shaders");
    printf("%s", shader_path);
    char *shadow_vs = TextFormat("%s/shadow_depth.vs", shader_path);
    char *shadow_fs = TextFormat("%s/shadow_depth.fs", shader_path);
    shader_path = TextFormat("%s/%s", getenv("SYNTHDIR"), "shaders");
    Shader depthShader = LoadShader(shadow_vs, shadow_fs);
    char *light_vs = TextFormat("%s/lighting.vs", shader_path);
    char *light_fs = TextFormat("%s/lighting.fs", shader_path);
    shader_path = TextFormat("%s/%s", getenv("SYNTHDIR"), "shaders");
    Shader lightingShader = LoadShader(light_vs, light_fs);
    char *base_vs = TextFormat("%s/base.vs", shader_path);
    char *blur_fs = TextFormat("%s/blur.fs", shader_path);
    shader_path = TextFormat("%s/%s", getenv("SYNTHDIR"), "shaders");
    Shader blurShader = LoadShader(base_vs, blur_fs);
    base_vs = TextFormat("%s/base.vs", shader_path);
    char *dof_fs = TextFormat("%s/dof.fs", shader_path);
    shader_path = TextFormat("%s/%s", getenv("SYNTHDIR"), "shaders");
    Shader dofShader = LoadShader(base_vs, dof_fs);

    GetLCShaderLocations(&depthShader, &lightingShader, &blurShader, &dofShader);

    Light sun = CreateLight(LIGHT_DIRECTIONAL, Vector3Zero(), Vector3Zero(), WHITE, 
                            lightingShader);                    

    RenderTexture2D depthTex = LoadRenderTexture(width_pix*2, width_pix*2);
    RenderTexture2D renderedTex = LoadRenderTexture(width_pix, width_pix);
    RenderTexture2D blurredTex = LoadRenderTexture(width_pix, width_pix);
    RenderTexture2D mixedTex = LoadRenderTexture(width_pix, width_pix);


    for(int m = 0; m < model.meshCount; m++) {
      Mesh mesh = model.meshes[m];
      rlUpdateVertexBuffer(mesh.vboId[0], mesh.vertices, mesh.vertexCount*3*sizeof(float), 0);
      rlUpdateVertexBuffer(mesh.vboId[2], mesh.normals, mesh.vertexCount*3*sizeof(float), 0);
    }

    int frame_number = 0;
    while ((!WindowShouldClose()) & (frame_number < data_points)) // Detect window close button or ESC key
    {
        BeginTextureMode(depthTex); // Enable drawing to texture
            ClearBackground(BLACK); // Clear texture background
        EndTextureMode();

        BeginTextureMode(renderedTex); // Enable drawing to texture
            ClearBackground(BLACK); // Clear texture background
        EndTextureMode();

        sun.position = sun_vectors[frame_number];
        viewer_camera.position = viewer_pos[frame_number];
        viewer_camera.target = viewer_look[frame_number];
        viewer_camera.up = viewer_up[frame_number];
        light_camera.position = sun.position;
        UpdateLightValues(lightingShader, sun);
        UpdateLightValues(depthShader, sun);

        //----------------------------------------------------------------------------------
        // Write to depth texture
        //----------------------------------------------------------------------------------

        Matrix mvp_light = CalculateMVPFromCamera(light_camera, (Vector3) {0, 0, 0}, cam_far); 
        Matrix mvp_viewer = CalculateMVPFromCamera(viewer_camera, (Vector3) {0, 0, 0}, cam_far);
        Matrix mvp_light_biases = CalculateMVPBFromMVP(mvp_light);

        BeginTextureMode(depthTex);
        // Enable drawing to texture
            BeginMode3D(light_camera);
            // Begin 3d mode drawing
                for(int m = 0; m < model.materialCount; m++) {
                    model.materials[m].shader = depthShader;
                }
                //Sends the light position vector to the lighting shader
                SetShaderValueMatrix(depthShader, depthShader.locs[LIGHTING_SHADER_LOC_LIGHT_MVP], mvp_light);
                SetShaderValue(depthShader, depthShader.locs[LIGHTING_SHADER_LOC_LIGHT_POS], 
                  &sun.position, SHADER_UNIFORM_VEC3);
                //Sends the light position vector to the depth shader
                SetShaderValue(depthShader, depthShader.locs[LIGHTING_SHADER_LOC_CAM_FAR], 
                  &cam_far, SHADER_UNIFORM_FLOAT);

                // Assign depth texture shader to model
                DrawModel(model, Vector3Zero(), 0.0f, WHITE);
            EndMode3D();
        EndTextureMode();
        // ----------------------------------------------------------------------------------
        // Write to the rendered texture
        // ----------------------------------------------------------------------------------
        BeginTextureMode(renderedTex);
            for(int m = 0; m < model.materialCount; m++) {
            model.materials[m].shader = lightingShader;
            }
            // Sets the model's shader to the lighting shader (was the depth shader)

            for(int m = 0; m < model.meshCount; m++) {
                DrawTextureRec(depthTex.texture, (Rectangle){0, 0, 0, 0}, (Vector2){0, 0}, WHITE);
                SetShaderValueTexture(lightingShader, lightingShader.locs[LIGHTING_SHADER_LOC_DEPTH_TEX], depthTex.texture);
                // Sends depth texture to the main lighting shader    

                BeginMode3D(viewer_camera);
                    SetShaderValue(lightingShader, lightingShader.locs[LIGHTING_SHADER_LOC_VIEW_POS], 
                    &viewer_camera.position, SHADER_UNIFORM_VEC3); 
                    SetShaderValue(lightingShader, lightingShader.locs[LIGHTING_SHADER_LOC_LIGHT_POS], 
                    &sun.position, SHADER_UNIFORM_VEC3); 
                    SetShaderValue(lightingShader, lightingShader.locs[LIGHTING_SHADER_LOC_BRDF_INDEX], 
                    &brdf_index, SHADER_UNIFORM_INT); 
                    SetShaderValueTexture(lightingShader, 
                    lightingShader.locs[LIGHTING_SHADER_LOC_DEPTH_TEX], depthTex.texture);
                    SetShaderValueMatrix(lightingShader, 
                    lightingShader.locs[LIGHTING_SHADER_LOC_VIEW_MVP], mvp_viewer);
                    SetShaderValueMatrix(lightingShader, 
                    lightingShader.locs[LIGHTING_SHADER_LOC_LIGHT_MVP], mvp_light_biases);
                    SetShaderValue(lightingShader, lightingShader.locs[LIGHTING_SHADER_LOC_CAM_FAR], 
                    &cam_far, SHADER_UNIFORM_FLOAT);

                    Matrix matTrans = MatrixTranslate(0, 0, 0);
                    DrawMesh(model.meshes[m], model.materials[model.meshMaterial[m]], matTrans);
                    DrawTextureRec(depthTex.texture, (Rectangle){0, 0, 0, 0}, (Vector2){0, 0}, WHITE);
                EndMode3D();
            }
        EndTextureMode();

        BeginTextureMode(blurredTex); // Enable drawing to texture
            ClearBackground(BLACK); // Clear texture background
            BeginShaderMode(blurShader);
                DrawTextureRec(renderedTex.texture, (Rectangle){0, 0, renderedTex.texture.width, (float) -renderedTex.texture.height}, (Vector2){0, 0}, WHITE);
            EndShaderMode();
        EndTextureMode();

        BeginTextureMode(mixedTex); // Enable drawing to texture
            ClearBackground(BLACK); // Clear texture background
            BeginShaderMode(dofShader);
                SetShaderValueTexture(dofShader, 
                dofShader.locs[DOF_SHADER_LOC_BLURRED_TEX], blurredTex.texture);
                SetShaderValueTexture(dofShader, 
                dofShader.locs[DOF_SHADER_LOC_UNBLURRED_TEX], renderedTex.texture);
                DrawTextureRec(renderedTex.texture, (Rectangle){0, 0, depthTex.texture.width, (float) -depthTex.texture.height}, (Vector2){0, 0}, WHITE);
            EndShaderMode();
        EndTextureMode();

        BeginDrawing();
            ClearBackground(BLACK);
        DrawTextureRec(mixedTex.texture, (Rectangle){0, 0, depthTex.texture.width, 
                                                        (float) -depthTex.texture.height}, 
                                                        (Vector2){0, 0}, WHITE);
        EndDrawing();
        char img_fname[300];
        const char *out_dir = TextFormat("%s/%s", GetWorkingDirectory(), "out");
        sprintf(img_fname, "%s/frame%d.png", out_dir, frame_number);
        SaveScreen(img_fname, mixedTex.texture);
        frame_number++;
    }
    CloseWindow();

    return success(sv);
}

static PyMethodDef FputsMethods[] = {
    {"run", method_add, METH_VARARGS, "Runs the RPO synthetic image generation tool"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "synth_rpo",
    "Python interface adding stuff in C",
    -1,
    FputsMethods
};

PyMODINIT_FUNC PyInit_synth_rpo(void) {
    // I don't understand why yet, but the program segfaults without this.
    import_array();
    return PyModule_Create(&module);
}

