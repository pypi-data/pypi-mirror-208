# Changelog

## 0.3.1

- Added documentation for the process, objects, and gates modules.
- Modified the gate decomposition process to exclusively use the CNOT gate as the multi-qubit gate.
- Added examples.

## 0.3.0

- Added support for decomposition of multi-controlled quantum gates.
- Added documentation for the C API.

## 0.2.3

- Introduced the `plugin` function in the `gates` module.

## 0.2.2

- Refactored the implementation of `Quant` and gate functions for improved usability.

## 0.2.1

- Included the `Quant` type and gate functions to enhance the functionality.

## 0.2.0

- Expanded the available dump types with `"shots"` and `"probability"`, in addition to `"vector"`.

## 0.1.1

- Fixed a bug related to inverse gate application.

## 0.1.0

- Ported the Libket library from C++ to Rust for increased usability and performance.
