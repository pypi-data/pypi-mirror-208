#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "AMCL::core" for configuration "Release"
set_property(TARGET AMCL::core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(AMCL::core PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libamcl_core.a"
  )

list(APPEND _cmake_import_check_targets AMCL::core )
list(APPEND _cmake_import_check_files_for_AMCL::core "${_IMPORT_PREFIX}/lib/libamcl_core.a" )

# Import target "AMCL::curve_SECP256K1" for configuration "Release"
set_property(TARGET AMCL::curve_SECP256K1 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(AMCL::curve_SECP256K1 PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libamcl_curve_SECP256K1.a"
  )

list(APPEND _cmake_import_check_targets AMCL::curve_SECP256K1 )
list(APPEND _cmake_import_check_files_for_AMCL::curve_SECP256K1 "${_IMPORT_PREFIX}/lib/libamcl_curve_SECP256K1.a" )

# Import target "AMCL::curve_BLS381" for configuration "Release"
set_property(TARGET AMCL::curve_BLS381 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(AMCL::curve_BLS381 PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libamcl_curve_BLS381.a"
  )

list(APPEND _cmake_import_check_targets AMCL::curve_BLS381 )
list(APPEND _cmake_import_check_files_for_AMCL::curve_BLS381 "${_IMPORT_PREFIX}/lib/libamcl_curve_BLS381.a" )

# Import target "AMCL::pairing_BLS381" for configuration "Release"
set_property(TARGET AMCL::pairing_BLS381 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(AMCL::pairing_BLS381 PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libamcl_pairing_BLS381.a"
  )

list(APPEND _cmake_import_check_targets AMCL::pairing_BLS381 )
list(APPEND _cmake_import_check_files_for_AMCL::pairing_BLS381 "${_IMPORT_PREFIX}/lib/libamcl_pairing_BLS381.a" )

# Import target "AMCL::bls_BLS381" for configuration "Release"
set_property(TARGET AMCL::bls_BLS381 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(AMCL::bls_BLS381 PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libamcl_bls_BLS381.a"
  )

list(APPEND _cmake_import_check_targets AMCL::bls_BLS381 )
list(APPEND _cmake_import_check_files_for_AMCL::bls_BLS381 "${_IMPORT_PREFIX}/lib/libamcl_bls_BLS381.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
