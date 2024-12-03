# libnest2dLE

[![Conan Badge]][Conan]
[![Unit Test Badge]][Unit Test]

[![Size Badge]][Size]
[![License Badge]][License]

> **Notice:**  
> This library was developed as part of the [PrusaSlicer](https://github.com/prusa3d/PrusaSlicer) project. **You can find the original version [here](https://github.com/prusa3d/PrusaSlicer/tree/master/src/libnest2d).** This repository is a continuation of that original project by UltiMaker, now forked for use in Cura LulzBot Edition.

## License

libnest2dLE is released under terms of the LGPLv3 License. Terms of the license can be found in the LICENSE file or [on the GNU website.](http://www.gnu.org/licenses/lgpl.html)

> In general it boils down to:  
> **You need to share the source of any libnest2dLE modifications if you make an application with libnest2dLE.**

## System Requirements

### Windows

- Python 3.6 or higher
- Ninja 1.10 or higher
- VS2022 or higher
- CMake 3.23 or higher
- nmake

### MacOS

- Python 3.6 or higher
- Ninja 1.10 or higher
- apply clang 11 or higher
- CMake 3.23 or higher
- make

### Linux

- Python 3.6 or higher
- Ninja 1.10 or higher
- gcc 12 or higher
- CMake 3.23 or higher
- make

## How To Build

> **Note:**  
> We are currently in the process of switch our builds and pipelines to an approach which uses [Conan](https://conan.io/) and pip to manage our dependencies, which are stored on our JFrog Artifactory server and in the pypi.org. At the moment not everything is fully ported yet, so bare with us.

If you have never used [Conan](https://conan.io/) read their [documentation](https://docs.conan.io/en/latest/index.html)
which is quite extensive and well maintained. Conan is a Python program and can be installed using pip

### 1. Configure Conan

```bash
pip install conan --upgrade
conan config install https://github.com/lulzbot3d/conan-config-le.git
conan profile new default --detect --force
```

Community developers would have to remove the Conan cura-le repository because it requires credentials.

LulzBot developers need to request an account for our JFrog Artifactory server with IT

```bash
conan remote remove cura-le
```

### 2. Clone libnest2dLE

```bash
git clone https://github.com/lulzbot3d/libnest2dLE.git
cd libnest2d
```

### 3. Install & Build libnest2dLE (Release OR Debug)

> Note:  
> Within Conan, the actual package is titled "nest2dle" rather than "libnest2dle".

#### Release

```bash
conan install . --build=missing --update
# optional for a specific version: conan install . nest2dle/<version>@<user>/<channel> --build=missing --update
cmake --preset release
cmake --build --preset release
```

#### Debug

```bash
conan install . --build=missing --update build_type=Debug
cmake --preset debug
cmake --build --preset debug
```

## Creating a new libnest2dLE Conan package

To create a new libnest2dLE Conan package such that it can be used in CuraLE and UraniumLE, run the following command:

```shell
conan create . nest2dle/<version>@<username>/<channel> --build=missing --update
```

This package will be stored in the local Conan cache (`~/.conan/data` or `C:\Users\username\.conan\data` ) and can be used in downstream
projects, such as CuraLE and UraniumLE by adding it as a requirement in the `conanfile.py` or in `conandata.yml`.

Note: Make sure that the used `<version>` is present in the conandata.yml in the libnest2dLE root

You can also specify the override at the commandline, to use the newly created package, when you execute the `conan install`
command in the root of the consuming project, with:

```shell
conan install . -build=missing --update --require-override=nest2dle/<version>@<username>/<channel>
```

## Developing libnest2dLE In Editable Mode

You can use your local development repository downsteam by adding it as an editable mode package.
This means you can test this in a consuming project without creating a new package for this project every time.

```bash
conan editable add . nest2dle/<version>@<username>/<channel>
```

Then in your downsteam projects (CuraLE) root directory override the package with your editable mode package.

```shell
conan install . -build=missing --update --require-override=nest2dle/<version>@<username>/<channel>
```

## Example

A simple example may be the best way to demonstrate the usage of the library.

``` c++
#include <iostream>
#include <string>

// Here we include the libnest2d library
#include <libnest2d/libnest2d.hpp>

int main(int argc, const char* argv[]) {
    using namespace libnest2d;

    // Example polygons
    std::vector<Item> input1(23,
    {
        {-5000000, 8954050},
        {5000000, 8954050},
        {5000000, -45949},
        {4972609, -568550},
        {3500000, -8954050},
        {-3500000, -8954050},
        {-4972609, -568550},
        {-5000000, -45949},
        {-5000000, 8954050},
    });
    std::vector<Item> input2(15,
    {
       {-11750000, 13057900},
       {-9807860, 15000000},
       {4392139, 24000000},
       {11750000, 24000000},
       {11750000, -24000000},
       {4392139, -24000000},
       {-9807860, -15000000},
       {-11750000, -13057900},
       {-11750000, 13057900},
    });

    std::vector<Item> input;
    input.insert(input.end(), input1.begin(), input1.end());
    input.insert(input.end(), input2.begin(), input2.end());

    // Perform the nesting with a box shaped bin
    size_t bins = nest(input, Box(150000000, 150000000));

    // Retrieve resulting geometries
    for(Item& r : input) {
        auto polygon = r.transformedShape();
        // render polygon...
    }

    return EXIT_SUCCESS;
}
```

It is worth to note that the type of the polygon carried by the Item objects is the type defined as a polygon by the geometry backend. In the example we use the clipper backend and clipper works with integer coordinates.

Of course it is possible to configure the nesting in every possible way. The ```nest``` function can take placer and selection algorithms as template arguments and their configuration as runtime arguments. It is also possible to pass a progress indication functor and a stop condition predicate to control the nesting process. For more details see the ```libnest2d.h``` header file.

## Example output

![Alt text](doc/img/example.svg)

## Screenshot from Slic3r PE

For the record, **Slic3r PE** version 2.0 is now known as **PrusaSlicer 2.0**.

![Alt text](doc/img/slic3r_screenshot.png)

## References

- [SVGNest](https://github.com/Jack000/SVGnest)
- [An effective heuristic for the two-dimensional irregular
  bin packing problem](http://www.cs.stir.ac.uk/~goc/papers/EffectiveHueristic2DAOR2013.pdf)
- [Complete and robust no-fit polygon generation for the irregular stock cutting problem](https://www.sciencedirect.com/science/article/abs/pii/S0377221706001639)
- [Applying Meta-Heuristic Algorithms to the Nesting
  Problem Utilising the No Fit Polygon](http://www.graham-kendall.com/papers/k2001.pdf)
- [A comprehensive and robust procedure for obtaining the nofit polygon
  using Minkowski sums](https://www.sciencedirect.com/science/article/pii/S0305054806000669)

<!------------------------------------------------------------------------------------------------------->

[Conan Badge]: https://img.shields.io/github/actions/workflow/status/lulzbot3d/libnest2dLE/conan-package.yml?style=for-the-badge&logoColor=white&logo=Conan&label=Conan%20Package
[Unit Test Badge]: https://img.shields.io/github/actions/workflow/status/lulzbot3d/libnest2dLE/unit-test.yml?style=for-the-badge&logoColor=white&logo=Codacy&label=Unit%20Test
[Size Badge]: https://img.shields.io/github/repo-size/lulzbot3d/libnest2dLE?style=for-the-badge&logoColor=white&logo=GoogleAnalytics
[License Badge]: https://img.shields.io/github/license/lulzbot3d/libnest2dLE?style=for-the-badge&logoColor=white&logo=GNU

[Conan]: https://github.com/lulzbot3d/libnest2dLE/actions/workflows/conan-package.yml
[Unit Test]: https://github.com/lulzbot3d/libnest2dLE/actions/workflows/unit-test.yml
[Size]: https://github.com/lulzbot3d/libnest2dLE
[License]: LICENSE
