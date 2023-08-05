"""
    @Title:             Database creation + handling of patients who failed.

    @Description:       Create the (possibly partial) HDF5 database, update the series description dictionary using the
                        information from the failed patients' images, and finally create the full HDF5 database.
"""

import env_examples  # Modifies path, DO NOT REMOVE

import json
from typing import Dict, List, Union

from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor, PatientWhoFailed


def get_updated_series_descriptions(
        patients_who_failed: List[PatientWhoFailed],
        series_descriptions: Union[str, Dict[str, List[str]]]
) -> Union[str, Dict[str, List[str]]]:
    """
    Add a series description to the series description list of the given series key.

    Parameters
    ----------
    patients_who_failed : List[PatientWhoFailed]
        List of patients with one or more images not added to the HDF5 database due to the absence of the series in
        the patient record.
    series_descriptions : Union[str, Dict[str, List[str]]], default = None.
        A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
        the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
        series descriptions. The images associated with these series descriptions do not need to have a
        corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
        must be added to the database is to be able to add images without their segmentation.
    """
    for patient in patients_who_failed:
        for image, image_series_descriptions in patient.failed_images.items():
            if not any([series in series_descriptions[image] for series in patient.available_series_descriptions]):
                while True:
                    new_series_description = input(
                        f"\nNo available series for {image}. \nAvailable series are "
                        f"{patient.available_series_descriptions}. \nName of the series description to add : ")

                    print(f"Given series description name is {new_series_description}.")

                    if new_series_description in patient.available_series_descriptions:
                        print(f"Series description successfully added to the series descriptions json file.")
                        break
                    else:
                        print(f"Invalid series description! \n{new_series_description} not found in the patient's "
                              f"dicom files. Please try again.")

                series_descriptions[image] += [new_series_description]

    return series_descriptions


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #     Create database (some images of some patients might fail to be added to the database due to the         #
    #                         absence of the series descriptions in the patient record)                           #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_extractor = PatientsDataExtractor(
        path_to_patients_folder="data/patients",
        series_descriptions="data/incorrect_series_descriptions.json"
    )

    database = PatientsDatabase(path_to_database="data/patients_database.h5")

    patients_who_failed = database.create(
        patients_data_extractor=patients_data_extractor,
        overwrite_database=True
    )

    # Print list of patients who failed
    print(f"Patients who failed the pipeline : {patients_who_failed}")

    # ----------------------------------------------------------------------------------------------------------- #
    #                                          Update series descriptions                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    with open("data/incorrect_series_descriptions.json", "r") as json_file:
        series_descriptions = json.load(json_file)

    updated_series_descriptions = get_updated_series_descriptions(
        patients_who_failed=patients_who_failed,
        series_descriptions=series_descriptions
    )

    with open("data/incorrect_series_descriptions.json", 'w', encoding='utf-8') as json_file:
        json.dump(updated_series_descriptions, json_file, ensure_ascii=False, indent=4)

    # ----------------------------------------------------------------------------------------------------------- #
    #                                           Create complete database                                          #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_extractor = PatientsDataExtractor(
        path_to_patients_folder="data/patients",
        series_descriptions=updated_series_descriptions
    )

    patients_who_failed = database.create(
        patients_data_extractor=patients_data_extractor,
        tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
        overwrite_database=True
    )

    # Print list of patients who failed. This list should be empty now.
    print(f"Patients who failed the pipeline : {patients_who_failed}")
