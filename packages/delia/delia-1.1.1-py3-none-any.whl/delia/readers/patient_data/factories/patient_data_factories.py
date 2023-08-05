"""
    @file:              patient_data_factories.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains all factories that inherit from the BasePatientDataFactory class.
"""

from typing import Dict, List, Optional

from delia.readers.patient_data.factories.base_patient_data_factory import BasePatientDataFactory
from delia.readers.image.dicom_reader import DicomReader
from delia.readers.segmentation.segmentation_reader import SegmentationReader
from delia.utils.data_model import ImageAndSegmentationDataModel, PatientDataModel


class DefaultPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The default factory consists in obtaining all
    the images.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            series_descriptions: Optional[Dict[str, List[str]]],
            erase_unused_dicom_files: bool = False
    ):
        """
        Constructor of the class DefaultPatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=series_descriptions,
            erase_unused_dicom_files=erase_unused_dicom_files
        )

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        data = []
        for image_idx, image in enumerate(self._images_data):
            segmentations = []
            for path_to_segmentation in self._paths_to_segmentations:
                seg_header = DicomReader.get_dicom_header(path_to_dicom=path_to_segmentation)
                reference_uid = self.get_segmentation_reference_uid(seg_header)

                if image.dicom_header.SeriesInstanceUID == reference_uid:
                    segmentation_reader = SegmentationReader(
                        image=image,
                        path_to_segmentation=path_to_segmentation
                    )

                    segmentations.append(segmentation_reader.get_segmentation_data())

            if segmentations:
                image_and_segmentation_data = ImageAndSegmentationDataModel(
                    image=image,
                    segmentations=segmentations
                )
                data.append(image_and_segmentation_data)
            else:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        patient_data = PatientDataModel(
            patient_id=self.patient_id,
            data=data
        )
        return patient_data


class SeriesDescriptionPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The series description patient data factory
    consists in obtaining only the images that have the given series descriptions and their corresponding segmentations.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            series_descriptions: Optional[Dict[str, List[str]]],
            erase_unused_dicom_files: bool = False
    ):
        """
        Constructor of the class SeriesDescriptionPatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=series_descriptions,
            erase_unused_dicom_files=erase_unused_dicom_files
        )

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        data = []
        for image_idx, image in enumerate(self._images_data):
            image_added = False
            series_description = image.dicom_header.SeriesDescription

            for series_key, list_of_series_descriptions in self._series_descriptions.items():
                if series_description in list_of_series_descriptions:
                    image.series_key = series_key

                    segmentations = []
                    for path_to_segmentation in self._paths_to_segmentations:
                        seg_header = DicomReader.get_dicom_header(path_to_dicom=path_to_segmentation)
                        reference_uid = self.get_segmentation_reference_uid(seg_header)

                        if image.dicom_header.SeriesInstanceUID == reference_uid:
                            segmentation_reader = SegmentationReader(
                                image=image,
                                path_to_segmentation=path_to_segmentation
                            )

                            segmentations.append(segmentation_reader.get_segmentation_data())

                    if segmentations:
                        image_and_segmentation_data = ImageAndSegmentationDataModel(
                            image=image,
                            segmentations=segmentations
                        )
                        data.append(image_and_segmentation_data)
                    else:
                        image_data = ImageAndSegmentationDataModel(image=image)
                        data.append(image_data)

                    image_added = True
                    break

            if image_added is False and self._erase_unused_dicom_files:
                self.erase_dicom_files(image)

        patient_data = PatientDataModel(
            patient_id=self.patient_id,
            data=data
        )
        return patient_data
