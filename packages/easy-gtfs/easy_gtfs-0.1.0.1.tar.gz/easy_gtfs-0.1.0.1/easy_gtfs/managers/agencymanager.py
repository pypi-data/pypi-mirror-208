"""
    Module to manage multiple 'Agency' models, write them to a file, load them from a file or parse them from a json object.

    Author: Felix Michelis
    Date: 12/05/2023
        dd/mm/yyyy
"""
from pydantic import ValidationError
from typing import Optional, List
import csv
from collections import Counter
import json


from ..utility import get_error_manager
from ..objects.agency import Agency
from ..models.errors import ErrorTypes, AgencyError




class Agencies():
    """A class to manage multiple 'Agency' models and write them to a file, load them from a file or parse them from a json object."""

    def __init__(self, error_manager = get_error_manager(), agencies: List[Agency] = None, file: str = None):
        """
            A class to manage multiple 'Agency' models and write them to a file, load them from a file or parse them from a json object.

            :param agencies [List[Agency]] -- A list of 'Agency' models, can be passed later with the respective function on function call
            :param file [str] -- The file to write to or load from, can be passed later with the respective function on function call
        """
        self.error_manager = error_manager
        self.agencies: List[Agency] = agencies
        self.file: str = file
    

    def to_file(self, agencies: Optional[List[Agency]] = None, file: Optional[str] = None) -> bool:
        """
            Writes a list of 'Agency' models to a file in csv format.

            :param agencies [Optional[List[Agency]]] -- A list containing 'Agency' models, if not given it will take 'self.agencies' if set
            :param file [Optional[str]] -- The file to write to, if not given it will take 'self.file' if set

            :return None
        """

        if not agencies:
            if self.agencies == None:
                raise TypeError("Got no agencies to write to file!")
            agencies = self.agencies

        if not file:
            if self.file == None:
                raise TypeError("Got no file to write to!")
            file = self.file


        headers: list = [variable for variable in agencies[0].dict(exclude_unset=False).keys()] # create a list of the headers for the csv file
        rows: list = []
        
        agencies_ids = [] # this list stores the ids of all the agencies that will be written to the file so we can verify that no agencies have the same id
        for obj in agencies:
            obj_as_dict = obj.dict(exclude_unset=False)
            agencies_ids.append(obj_as_dict["agency_id"]) # add the id of the agency to our ids list for verification later on
            rows.append(obj_as_dict) # add the agency as json to our rows that will be written to the csv file

        if len(agencies_ids) > 1:
            duplicates = [k for k, v in Counter(agencies_ids).items() if v>1] # returns a list with all duplicate ids; if the id '123' was for example at least 2 times in the ids list the output would be: ['123']
            if len(duplicates) > 0:
                if self.error_manager.is_silent_error():
                    self.error_manager.new_error(AgencyError(
                        caller = "AgencyManager",
                        error_type=ErrorTypes.AgencyErrorDuplicateID,
                        message="Multiple agencies cannot have the same id!",
                        values = duplicates
                    ))
                    return False
                else:
                    raise ValueError(f"Multiple agencies cannot have the same id! Got the following duplicate ids: {duplicates}")
            

        with open(file, "w", newline='') as _file:
            csvwriter = csv.DictWriter(_file, fieldnames=headers)
            csvwriter.writeheader()
            csvwriter.writerows(rows)


        return True



    def parse(self, agencies_list: List[dict]) -> List[Agency]:
        """
            Converts a list of dictionaries which each represent an 'Agency' to a list of 'Agency' models.
        """
        agencies = []

        for agency in agencies_list:
            if self.is_valid_agency(agency):
                agencies.append(Agency.parse_obj(agency))
            else:
                if self.error_manager.is_silent_error():
                    self.error_manager.new_error(AgencyError(
                        caller = "AgencyManager",
                        error_type = ErrorTypes.AgencyErrorInvalidAgency,
                        message="Invalid agency from dict!",
                        values = [agency]
                    ))
                    return False
                else:
                    raise ValueError(f"Invalid agency: {agency}")

        return agencies
    


    def load_file(self, file: Optional[str] = None) -> List[Agency]:
        """
            Reads a file in csv format and outputs a list of 'Agency' models contained in that file.

            :param file [Optional[str]] -- The file to read from, if not given it will take 'self.file' if its set

            :return List[Agency] -- A list conatining 'Agency' models
        """

        if not file:
            if self.file == None:
                raise TypeError("Got no file to load from!")
            file = self.file
        

        with open(file, "r") as _file:
            csvreader = list(csv.DictReader(_file)) # gives a list of dictionaries where each dict is a json representation of an agency
        
        agencies = self.parse(csvreader)

        agencies_ids = []

        for agency in agencies:
            if agency.agency_id in agencies_ids:
                if self.error_manager.is_silent_error():
                    self.error_manager.new_error(AgencyError(
                        caller = "AgencyManager",
                        error_type = ErrorTypes.AgencyErrorDuplicateID,
                        message="Cannot have multiple agencies with the same id!",
                        values = [agency.agency_id]
                    ))
                    return False
                else:
                    raise ValueError("Cannot have multiple agencies with the same id!")
            agencies_ids.append(agency.agency_id)

        return agencies

        
    def is_valid_agency(self, agency: dict) -> bool:
        """
            Checks if a dict is a valid 'Agency' model.

            :param agency [dict] -- The dict to validate
            
            :return bool -- 'True' if it contains a valid model, otherwise ('False', dict[argument_causing_error: error_message])
        """

        try:
            Agency.parse_obj(agency)

        except ValidationError as e:
            errors = {}

            for error in json.loads(e.json()):
                errors[error["loc"][0]] = error["msg"]

            return (False, errors)
        
        return True