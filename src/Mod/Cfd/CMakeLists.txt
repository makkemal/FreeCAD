
SET(Cfd_SRCS
    Init.py
    InitGui.py

    CfdAnalysis.py
    _CommandCfdAnalysis.py

    CfdSelectionObserver.py
    CfdTools.py
    CfdExample.py

    CfdMeshGmsh.py
    _CommandCfdMeshGmshFromShape.py
    _TaskPanelCfdMeshGmsh.py
    TaskPanelCfdMeshGmsh.ui
    _ViewProviderCfdMeshGmsh.py
    
    CfdResult.py
    _CommandCfdResult.py
    _TaskPanelCfdResult.py
    TaskPanelCfdResult.ui
    _ViewProviderCfdResult.py

    CfdSolver.py
    _CommandCfdSolverControl.py
    _TaskPanelCfdSolverControl.py
    TaskPanelCfdSolverControl.ui
    
   
    _CommandCfdFluidMaterial.py
    _FluidMaterial.py
    FluidMaterial.py
    _TaskPanelFluidMaterial.py
    TaskPanelFluidPropertiesNoUnits.ui
    TaskPanelFluidPropertiesWIthUnits.ui
    _ViewProviderCfdFluidMaterial.py

    # solver OpenFOAM
    CfdSolverFoam.py
    CfdRunnableFoam.py
    CfdCaseWriterFoam.py
    CfdResultFoamVTK.py
    _ViewProviderCfdSolverFoam.py
    _CommandCfdSolverFoam.py
)

SET(Cfd_FoamCaseBuilder_SRCS
    FoamCaseBuilder/__init__.py
    FoamCaseBuilder/BasicBuilder.py
    FoamCaseBuilder/FoamTemplateString.py
    FoamCaseBuilder/MultiphaseBuilder.py
    FoamCaseBuilder/Readme.md
    FoamCaseBuilder/Roadmap.md
    FoamCaseBuilder/TestBuilder.py
    FoamCaseBuilder/TestCase.unv
    FoamCaseBuilder/TestFoamDetection.py
    FoamCaseBuilder/ThermalBuilder.py
    FoamCaseBuilder/utility.py
)

SET(Cfd_defaults_simpleFoam_system
    defaults/simpleFoam/system/fvSolution
    defaults/simpleFoam/system/fvSchemes
    defaults/simpleFoam/system/controlDict
)

SOURCE_GROUP("" FILES ${Cfd_SRCS})

ADD_CUSTOM_TARGET(Cfd ALL
    SOURCES ${Cfd_SRCS} ${Cfd_FoamCaseBuilder_SRCS}
)

fc_copy_sources(Cfd "${CMAKE_BINARY_DIR}/Mod/Cfd" ${Cfd_SRCS} ${Cfd_FoamCaseBuilder_SRCS})

fc_target_copy_resource(Cfd
    ${CMAKE_SOURCE_DIR}/src/Mod/Cfd
    ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_DATADIR}/Mod/Cfd
    ${Cfd_defaults_simpleFoam_system}
)

INSTALL(
    FILES
        ${Cfd_SRCS} ${Cfd_FoamCaseBuilder_SRCS}
    DESTINATION Mod/Cfd
)

INSTALL(
    FILES
        ${Cfd_defaults_simpleFoam_system}
    DESTINATION
        ${CMAKE_INSTALL_DATADIR}/Mod/Cfd
)

