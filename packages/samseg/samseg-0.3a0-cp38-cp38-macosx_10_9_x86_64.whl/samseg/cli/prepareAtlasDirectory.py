#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
from scipy import ndimage

import numpy as np
from samseg import gems
from samseg import initVisualizer
from samseg import requireNumpyArray
from samseg.io import GMMparameter
from samseg.io import kvlReadCompressionLookupTable
from samseg.io import kvlWriteCompressionLookupTable
from samseg.io import kvlWriteSharedGMMParameters
from samseg.io import kvlReadSharedGMMParameters
from samseg.merge_alphas import kvlMergeAlphas
from samseg.merge_alphas import kvlGetMergingFractionsTable


def readAndSimplifyCompressionLookupTable( compressionLookupTableFileName, 
                                           uninterestingStructureSearchStrings=None ):
    # Read the original compressionLookupTable
    FreeSurferLabels, names, colors = \
           kvlReadCompressionLookupTable( compressionLookupTableFileName )
    
    # Remove structures that are in the original atlas mesh but that we're not interested in.
    # These will be merged into the very first structure in the list (which is assumed to be
    # background)
    # Create a binary list indicating which structures to merge together
    mask = [ False ] * len( names )
    if uninterestingStructureSearchStrings:
        for searchString in uninterestingStructureSearchStrings:
            for structureNumber, name in enumerate( names ):
                if searchString in name:
                    mask[ structureNumber ] = True
        survivingFreeSurferLabels = []
        survivingNames = []
        survivingColors = []
        for structureNumber, uninteresting in enumerate( mask ):
            if not uninteresting: 
                survivingFreeSurferLabels.append( FreeSurferLabels[ structureNumber ] )
                survivingNames.append( names[ structureNumber ] )
                survivingColors.append( colors[ structureNumber ] )
        FreeSurferLabels = survivingFreeSurferLabels
        names = survivingNames
        colors = survivingColors
    mask[ 0 ] = True
    
    #
    return FreeSurferLabels, names, colors, mask  



def readAndSimplifyMeshCollection( meshCollectionFileName, 
                                   compressionLookupTableFileName,
                                   uninterestingStructureSearchStrings=None,
                                   sharedGMMParameters=None,
                                   affineClassDefinitions=None ):
    # Read mesh, and only retain the reference (average across subjects) position -- the rest
    # is nobody's bussiness and having to read dozens of warped mesh positions to the training
    # subjects for no purpose at all is slow
    meshCollection = gems.KvlMeshCollection()
    meshCollection.read( meshCollectionFileName )
    referencePosition = meshCollection.reference_position
    meshCollection.set_positions( referencePosition, [ referencePosition ] )
    
    # Get the names of the structures (needed to remove and/or merge structures)
    _, names, _ = kvlReadCompressionLookupTable( compressionLookupTableFileName )

    # Remove structures that are in the original atlas mesh but that we're not interested in.
    # These will be merged into the very first structure in the list (which is assumed to be
    # background)
    _, names, _, mask = \
          readAndSimplifyCompressionLookupTable( compressionLookupTableFileName, 
                                                 uninterestingStructureSearchStrings )
    alphas = meshCollection.reference_mesh.alphas
    alphas = np.concatenate( ( alphas[ :, mask ].sum( axis=1, keepdims=True ), 
                              alphas[ :, np.logical_not( mask ) ] ), axis=1 )
    meshCollection.reference_mesh.alphas = alphas


    # We merge structures into mixture models as defined by the user, and then still merge 
    # mixture models into "classes" for MI-based registration (as also specified by the user)
    if sharedGMMParameters:
        #
        alphas = meshCollection.reference_mesh.alphas
      
        # First merge structures belongint to the same mixture
        classFractions, _ = kvlGetMergingFractionsTable( names, sharedGMMParameters )
        alphas = kvlMergeAlphas( alphas, classFractions )

        # Now abuse the same infrastructure to merge mixtures into even bigger superstructures
        if affineClassDefinitions:
            # 
            mergedNames = [ param.mergedName for param in sharedGMMParameters ]
            tmp = [ GMMparameter(mergedName='', numberOfComponents=-1, searchStrings=z) 
                    for z in affineClassDefinitions ]
            mixtureFractions, _ = kvlGetMergingFractionsTable( mergedNames, tmp )
            alphas = kvlMergeAlphas( alphas, mixtureFractions )

        #
        meshCollection.reference_mesh.alphas = alphas


    #
    return meshCollection



def smoothMeshCollection( meshCollection, sigma, returnPriors=False, showFigures=False ):
    #
    if showFigures:
        visualizer = initVisualizer( True, True )
    else:
        visualizer = initVisualizer( False, False )
      

    #
    if sigma == 0: return
  
    # 
    print( 'Doing smoothing with sigma: ', sigma )

    #
    size = np.array( meshCollection.reference_position.max( axis=0 ) + 1.5, dtype=int )

    # Optional Gaussian smoothing of each component
    priors = meshCollection.reference_mesh.rasterize( size, -1 )
    visualizer.show( probabilities=priors )
    priors = ndimage.gaussian_filter( priors.astype( float ), 
                                      sigma=( sigma, sigma, sigma, 0 ) ).astype( priors.dtype )
    visualizer.show( probabilities=priors )
    alphas = meshCollection.reference_mesh.fit_alphas( priors , 10 )
    meshCollection.reference_mesh.alphas = alphas
    visualizer.show( probabilities=meshCollection.reference_mesh.rasterize( size, -1 ) )

    #
    if returnPriors:
        #
        return priors
    else:
        return




def prepareAtlasDirectory( directoryName,
                           meshCollectionFileName, 
                           compressionLookupTableFileName,
                           sharedGMMParameters,
                           templateFileName,
                           uninterestingStructureSearchStrings=None, 
                           smoothingSigmaForFirstLevel=2.0, meshCollectionFileNameForFirstLevel=None,
                           smoothingSigmaForAffine=2.0, meshCollectionFileNameForAffine=None,
                           affineClassDefinitions=None,
                           FreeSurferLookupTableFileName=None,
                           showFigures=True ):
    #
    if showFigures:
        visualizer = initVisualizer( True, True )
    else:    
        visualizer = initVisualizer( False, False )


    # Create the output directory
    os.makedirs( directoryName, exist_ok=True )


    # Write sharedGMMParameters to file
    kvlWriteSharedGMMParameters( sharedGMMParameters, 
                                 os.path.join( directoryName, 'sharedGMMParameters.txt' ) )


    # Create a custom template that color-codes the affine atlas label probabilities (just for 
    # visualization purposes) 
    meshCollection = readAndSimplifyMeshCollection( meshCollectionFileName, 
                                                    compressionLookupTableFileName,
                                                    uninterestingStructureSearchStrings,
                                                    sharedGMMParameters,
                                                    affineClassDefinitions )
    template = gems.KvlImage( templateFileName )
    priors = meshCollection.reference_mesh.rasterize( template.getImageBuffer().shape, -1 ) / 65535
    size = priors.shape[ 0:3 ]
    numberOfClasses = priors.shape[ -1 ]
    templateImageBuffer = priors.reshape( ( np.prod( size ), -1 ) ) @ \
                              np.arange( 0, numberOfClasses )
    templateImageBuffer = templateImageBuffer.reshape( size )
    visualizer.show( images=templateImageBuffer )
    gems.KvlImage( requireNumpyArray( templateImageBuffer ) ).write( 
                    os.path.join( directoryName, 'template.nii'), template.transform_matrix )


    # Create the ultimate atlas (at multi-resolution level 2)
    meshCollection = readAndSimplifyMeshCollection( meshCollectionFileName, 
                                                    compressionLookupTableFileName,
                                                    uninterestingStructureSearchStrings )
    visualizer.show( mesh=meshCollection.reference_mesh, shape=size, title="Final atlas" )
    meshCollection.write( os.path.join( directoryName, 'atlas_level2.txt' ) )


    # Create a blurrier atlas (at multi-resolution level 1) by spatial smoothing. 
    # If a specific atlas file name is given for this purpose, use that one instead of the 
    # ultimate atlas we just created.
    if meshCollectionFileNameForFirstLevel:
        # Use a user-specified mesh with a simpler topology
        meshCollection = readAndSimplifyMeshCollection( meshCollectionFileNameForFirstLevel, 
                                                        compressionLookupTableFileName,
                                                        uninterestingStructureSearchStrings )
    smoothMeshCollection( meshCollection, smoothingSigmaForFirstLevel )
    visualizer.show( mesh=meshCollection.reference_mesh, shape=size, title="Intermediate atlas" )
    meshCollection.write( os.path.join( directoryName, 'atlas_level1.txt' ) )

    
    # Write the corresponding compressionLookupTable (remember to remove uninteresting structures)
    FreeSurferLabels, names, colors, _ =  \
        readAndSimplifyCompressionLookupTable( compressionLookupTableFileName, 
                                               uninterestingStructureSearchStrings )
    kvlWriteCompressionLookupTable( os.path.join( directoryName, 'compressionLookupTable.txt' ),
                                    FreeSurferLabels, names, colors )


    # Create a separate atlas mesh for affine registration purposes. If a separate atlas 
    # file name is given for this purpose, read and smooth that; otherwise read and smooth
    # the original atlas, and re-mesh with low-res, regular resolution
    if meshCollectionFileNameForAffine:
        #
        meshCollection = readAndSimplifyMeshCollection( meshCollectionFileNameForAffine, 
                                                        compressionLookupTableFileName,
                                                        uninterestingStructureSearchStrings,
                                                        sharedGMMParameters,
                                                        affineClassDefinitions )
        smoothMeshCollection( meshCollection, smoothingSigmaForAffine )
      
    else:
        #
        meshCollection = readAndSimplifyMeshCollection( meshCollectionFileName,
                                                        compressionLookupTableFileName,
                                                        uninterestingStructureSearchStrings,
                                                        sharedGMMParameters,
                                                        affineClassDefinitions )
        priors = smoothMeshCollection( meshCollection, smoothingSigmaForAffine, returnPriors=True )
        #visualizer.show( probabilities=priors )
        meshCollection.construct( [ 30, 30, 30 ], priors.shape[ 0:3 ], 1000.0, 2, 1 )
        alphas = meshCollection.reference_mesh.fit_alphas( priors , 10 )
        meshCollection.reference_mesh.alphas = alphas
        #visualizer.show( probabilities=meshCollection.reference_mesh.rasterize( 
        #                                                    priors.shape[ 0:3 ], -1 ) )
        #visualizer.show( mesh=meshCollection.reference_mesh, shape=priors.shape[ 0:3 ] )


    visualizer.show( mesh=meshCollection.reference_mesh, shape=size, title="Atlas for affine" )
    meshCollection.write( os.path.join( directoryName, 'atlasForAffineRegistration.txt' ) )


    # Copy the FreeSurferLookupTable
    if FreeSurferLookupTableFileName:
        #
        shutil.copy( FreeSurferLookupTableFileName, 
                     os.path.join( directoryName, 'modifiedFreeSurferColorLUT.txt' ) )

    return
  
def parseArguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--atlasdir", required=True, help="The atlas directory to create")
    parser.add_argument("-m", "--mesh", required=True, help="The filename of the mesh collection to use (output of kvlBuildAtlasMesh)")
    parser.add_argument("-c", "--compression_lut", required=True, help="The compression lookup table to use (output of kvlBuildAtlasMesh)")
    parser.add_argument("-g", "--shared_gmm_params", required=True, help="The filename of the shared GMM parameters to use")
    parser.add_argument("-t", "--template", required=True, help="The filename of the template nifti to use")
    parser.add_argument("-l", "--fs_lookup_table", help="The FreeSurfer lookup table to use")
    parser.add_argument("-m1", "--mesh_level_1", help="The filename of the mesh collection to use at the first (lower) level (output of kvlBuildAtlasMesh)")
    parser.add_argument("-ma", "--mesh_affine", help="The filename of the mesh collection to use for affine registration (output of kvlBuildAtlasMesh)")
    parser.add_argument("-s1", "--smoothing_level_1", default=2.0, type=float, help="Smoothing factor (sigma) for first mesh level")
    parser.add_argument("-sa", "--smoothing_level_affine", default=2.0, type=float, help="Smoothing factor (sigma) for affine mesh")
    parser.add_argument("-us", "--uninteresting_structure_search_strings", nargs='+', help="Uninteresting structures that will be merged to background class (assumed to be the first class)") 
    parser.add_argument("-ac", "--affine_class_definitions", nargs='+', action='append', help="List of list of merged-structures names to be merged for affine registration")
    parser.add_argument("-sf", "--show_figs", default=False)

    args = parser.parse_args(argv)

    return args

def main():

    args = parseArguments(sys.argv[1:])

    if not os.path.exists(args.mesh):
        print("ERROR: Can't find the mesh file " + args.mesh)
    if not os.path.exists(args.compression_lut):
        print("ERROR: Can't find the compression LUT file " + args.compression_lut)
    if not os.path.exists(args.shared_gmm_params):
        print("ERROR: Can't find the shared GMM params file " + args.shared_gmm_params)
    if not os.path.exists(args.template):
        print("ERROR: Can't find the template file " + args.template)
    if args.mesh_level_1 is not None and not os.path.exists(args.mesh_level_1):
        print("ERROR: Can't find the mesh file " + args.mesh_level_1)
    if args.mesh_affine is not None and not os.path.exists(args.mesh_affine):
        print("ERROR: Can't find the mesh file " + args.mesh_affine)
    if args.fs_lookup_table is not None and not os.path.exists(args.fs_lookup_table):
        print("ERROR: Can't find FreeSurfer LUT file " + args.fs_lookup_table)

    shared_gmm_params = kvlReadSharedGMMParameters(args.shared_gmm_params)
    prepareAtlasDirectory(directoryName=args.atlasdir,
                          meshCollectionFileName=args.mesh,
                          compressionLookupTableFileName=args.compression_lut,
                          sharedGMMParameters=shared_gmm_params,
                          templateFileName=args.template,
                          meshCollectionFileNameForFirstLevel=args.mesh_level_1,
                          meshCollectionFileNameForAffine=args.mesh_affine,
                          FreeSurferLookupTableFileName=args.fs_lookup_table,
                          smoothingSigmaForFirstLevel=args.smoothing_level_1,
                          smoothingSigmaForAffine=args.smoothing_level_affine,
                          uninterestingStructureSearchStrings=args.uninteresting_structure_search_strings,
                          affineClassDefinitions=args.affine_class_definitions,
                          showFigures=args.show_figs)

if __name__ == "__main__":
    main()
