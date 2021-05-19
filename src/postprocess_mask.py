import argparse
import numpy as np
import itk
import nibabel as nib
import os




def post_process (white_matter_file, directory, radiusValue):
	# radiusValue=radius
	
	# five_tt = args.five_tt
	# outputImage='/opt/lumargot/test/white_matter_101006_opening_binary.nii'

	# img = nib.load(five_tt)
	# data = img.get_fdata()
	# print(data.shape)

	# wm = data[:,:,:,3]
	# image=nib.Nifti1Image(wm, affine=img.affine)
	# nib.save(image, white_matter_file)


	################
	# binarize
	################

	insideValue=.0
	outsideValue=1.0

	upperThreshold=.2
	lowerThreshold=insideValue

	PixelType = itk.F
	Dimension = 3

	ImageType = itk.Image[PixelType, Dimension]

	reader = itk.ImageFileReader[ImageType].New()
	reader.SetFileName(white_matter_file)



	StructuringElementType = itk.FlatStructuringElement[Dimension]
	structuringElement = StructuringElementType.Cross(radiusValue)

	dilateFilter = itk.GrayscaleDilateImageFilter[ImageType, ImageType, StructuringElementType].New()
	dilateFilter.SetInput(reader.GetOutput())
	dilateFilter.SetKernel(structuringElement)


	writer = itk.ImageFileWriter[ImageType].New()
	# writer = WriterType.New()
	dilate_file = directory + "dilate.nii"
	writer.SetFileName(dilate_file)
	writer.SetInput(dilateFilter.GetOutput())

	writer.Update()



	thresholdFilter = itk.BinaryThresholdImageFilter[ImageType, ImageType].New()
	thresholdFilter.SetInput(dilateFilter.GetOutput())

	thresholdFilter.SetLowerThreshold(lowerThreshold)
	thresholdFilter.SetUpperThreshold(upperThreshold)
	thresholdFilter.SetOutsideValue(outsideValue)
	thresholdFilter.SetInsideValue(insideValue)

	writer = itk.ImageFileWriter[ImageType].New()
	# writer = WriterType.New()
	threshold_file = directory + "threshold.nii"
	writer.SetFileName(threshold_file)
	writer.SetInput(thresholdFilter.GetOutput())

	writer.Update()


	##############
	# erosion
	##############

	StructuringElementType = itk.FlatStructuringElement[Dimension]
	structuringElement = StructuringElementType.Cross(radiusValue)
					  # GrayscaleDilateImageFilter
	# erodeFilter = itk.GrayscaleDilateImageFilter[ImageType, ImageType, StructuringElementType].New()
	erodeFilter = itk.OpeningByReconstructionImageFilter[ImageType, ImageType, StructuringElementType].New()
	erodeFilter.SetInput(thresholdFilter.GetOutput())
	
	erodeFilter.SetKernel(structuringElement)
	# erodeFilter.SetForegroundValue(1)  		# Intensity value to erode
	# erodeFilter.SetBackgroundValue(0)  			# Replacement value for eroded voxels


	writer = itk.ImageFileWriter[ImageType].New()
	# writer = WriterType.New()
	opening_recontruction_file = directory + "opening_recontruction.nii"
	writer.SetFileName(opening_recontruction_file)
	writer.SetInput(erodeFilter.GetOutput())

	writer.Update()

	########################
	# Connected Componenent 
	########################

	PixelType = itk.UC
	OutputPixelType = itk.F
	Dimension = 3

	ImageType = itk.Image[PixelType, Dimension]
	OutputImageType = itk.Image[OutputPixelType, Dimension]

	reader = itk.ImageFileReader[ImageType].New()
	reader.SetFileName(opening_recontruction_file)




	connectedComponent = itk.ConnectedComponentImageFilter[ImageType, ImageType].New()
	# connectedComponent.SetFullyConnected(True)
	connectedComponent.SetInput(reader.GetOutput())
	connectedComponent.Update()

	print("number of objects:", connectedComponent.GetObjectCount())


	labelShapeKeepNObjects = itk.LabelShapeKeepNObjectsImageFilter[ImageType].New()
	labelShapeKeepNObjects.SetInput(connectedComponent.GetOutput())
	labelShapeKeepNObjects.SetBackgroundValue(0)
	labelShapeKeepNObjects.SetNumberOfObjects(1)

	print(labelShapeKeepNObjects.GetAttribute())
	labelShapeKeepNObjects.SetAttribute(100)


	castImageFilter = itk.CastImageFilter[ImageType, OutputImageType].New()
	castImageFilter.SetInput(labelShapeKeepNObjects.GetOutput())


	# rescaleFilter = itk.RescaleIntensityImageFilter[ImageType, ImageType].New()
	# rescaleFilter.SetInput(labelShapeKeepNObjects.GetOutput())
	# rescaleFilter.SetOutputMinimum(0)
	# # print(itk.NumericTraits[PixelType].max())
	# rescaleFilter.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())



	


	Dimension = 3

	
	writer = itk.ImageFileWriter[OutputImageType].New()
	# writer = WriterType.New()
	outputImage=directory + "white_matter_mask.nii"
	writer.SetFileName(outputImage)
	writer.SetInput(castImageFilter.GetOutput())

	writer.Update()

	return outputImage
	

	##################
	# conversion
	##################

	# PixelType = itk.F
	# Dimension = 3

	# ImageType = itk.Image[PixelType, Dimension]

	# reader = itk.ImageFileReader[ImageType].New()
	# reader.SetFileName(outputImage)


	# ImageType = itk.Image[PixelType, Dimension]

	# reader = itk.ImageFileReader[ImageType].New()
	# reader.SetFileName(white_matter_file)

	# thresholdFilter = itk.BinaryThresholdImageFilter[ImageType, ImageType].New()
	# thresholdFilter.SetInput(reader.GetOutput())

	# thresholdFilter.SetLowerThreshold(lowerThreshold)
	# thresholdFilter.SetUpperThreshold(upperThreshold)
	# thresholdFilter.SetOutsideValue(outsideValue)
	# thresholdFilter.SetInsideValue(insideValue)




	# writer = itk.ImageFileWriter[ImageType].New()
	# # writer = WriterType.New()
	# outputImage="/opt/lumargot/test/wm_uc_cc_float.nii"
	# writer.SetFileName(outputImage)
	# writer.SetInput(thresholdFilter.GetOutput())

	# writer.Update()


# if __name__ == '__main__':

# 	parser = argparse.ArgumentParser(description='post process of five tissues types image', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# 	input_params = parser.add_argument_group('Input parameters')
# 	input_params.add_argument('--radius', type=int, help='radius of strucuring element')
# 	input_params.add_argument('--five_tt', type=str, help='input five tissue type image')
# 	input_params.add_argument('--dir', type=str, help='ouput directory')


# 	args = parser.parse_args()

# 	main(args)
