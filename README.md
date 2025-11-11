To generate:

```
generate.sh
```

To use:

```cmake
include(FetchContent)

FetchContent_Declare(
    ros_idl_serde
    GIT_REPOSITORY https://github.com/mlomb/ros-idl-serde.git
    GIT_TAG main
)

FetchContent_MakeAvailable(ros_idl_serde)

target_link_libraries(your_app ros_idl_serde)
```

```cpp
#include <sensor_msgs/msg/JointState.h>
```
