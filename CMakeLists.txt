project(ros_idl_serde)

# fastcdr
message("Fetching eProsima/Fast-CDR from GitHub...")
include(FetchContent)
FetchContent_Declare(
    fastcdr
    GIT_REPOSITORY https://github.com/eProsima/Fast-CDR.git
    GIT_TAG v1.1.1
)
FetchContent_MakeAvailable(fastcdr)

file(GLOB_RECURSE SRC_FILES "generated/**/*.cxx")

add_library(${PROJECT_NAME} STATIC ${SRC_FILES})

target_link_libraries(${PROJECT_NAME} PUBLIC fastcdr)
target_include_directories(${PROJECT_NAME} PUBLIC "generated")
