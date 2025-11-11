project(ros_idl_serde)

file(GLOB_RECURSE SRC_FILES "generated/**/*.cxx")

add_library(${PROJECT_NAME} STATIC ${SRC_FILES})

target_include_directories(${PROJECT_NAME} PUBLIC "generated")
