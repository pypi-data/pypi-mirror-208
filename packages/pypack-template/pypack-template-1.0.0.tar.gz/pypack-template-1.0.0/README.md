# How to

python -m pip-tools

pip-compile

python -m pip install build twine

python -m build

clang -Wno-unused-result -Wsign-compare -Wunreachable-code -DNDEBUG -fwrapv -O2 -Wall -fPIC -O2 -isystem /Users/dy/miniconda3/envs/pypack/include -arch arm64 -I/Users/dy/miniconda3/envs/pypack/include -fPIC -O2 -isystem /Users/dy/miniconda3/envs/pypack/include -arch arm64 -DVERSION_INFO=1 -Isrc/pypack/c -I/private/var/folders/dy/t3z25fx96xg5jvy0zvy4l2r40000gn/T/build-env-vsshcf__/lib/python3.9/site-packages/pybind11/include -I/private/var/folders/dy/t3z25fx96xg5jvy0zvy4l2r40000gn/T/build-env-vsshcf__/include -I/Users/dy/miniconda3/envs/pypack/include/python3.9 -c src/pypack/c/main.cpp -o build/temp.macosx-11.1-arm64-cpython-39/src/pypack/c/main.o -std=c++17 -mmacosx-version-min=10.14 -fvisibility=hidden -g0 -stdlib=libc++

clang -Wno-unused-result -Wsign-compare -Wunreachable-code -DNDEBUG -fwrapv -O2 -Wall -fPIC -O2 -isystem /Users/dy/miniconda3/envs/pypack/include -arch arm64 -I/Users/dy/miniconda3/envs/pypack/include -fPIC -O2 -isystem /Users/dy/miniconda3/envs/pypack/include -arch arm64 -DVERSION_INFO=1 -I/private/var/folders/dy/t3z25fx96xg5jvy0zvy4l2r40000gn/T/build-via-sdist-0vc7czfk/pypack-template-1.0.0/src/pypack/c -I/private/var/folders/dy/t3z25fx96xg5jvy0zvy4l2r40000gn/T/build-env-garxv7if/lib/python3.9/site-packages/pybind11/include -I/private/var/folders/dy/t3z25fx96xg5jvy0zvy4l2r40000gn/T/build-env-garxv7if/include -I/Users/dy/miniconda3/envs/pypack/include/python3.9 -c src/pypack/c/main.cpp -o build/temp.macosx-11.1-arm64-cpython-39/src/pypack/c/main.o -std=c++17 -mmacosx-version-min=10.14 -fvisibility=hidden -g0 -stdlib=libc++