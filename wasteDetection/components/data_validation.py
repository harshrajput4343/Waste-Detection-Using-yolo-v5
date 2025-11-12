import os,sys
import shutil
from pathlib import Path
from wasteDetection.logger import logging
from wasteDetection.exception import AppException
from wasteDetection.entity.config_entity import DataValidationConfig
from wasteDetection.entity.artifacts_entity import (DataIngestionArtifact,
                                                 DataValidationArtifact)






class DataValidation:
    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig,
    ):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config

        except Exception as e:
            raise AppException(e, sys) 
        


    
    def validate_all_files_exist(self)-> bool:
        try:
            # Check that feature store directory exists
            feature_store = Path(self.data_ingestion_artifact.feature_store_path)
            if not feature_store.exists():
                raise AppException(f"Feature store path not found: {feature_store}", sys)

            all_files = set(os.listdir(feature_store))
            required_files = set(self.data_validation_config.required_file_list)

            missing_files = required_files - all_files
            validation_status = len(missing_files) == 0

            # ensure validation dir exists and write a single status file with details
            os.makedirs(self.data_validation_config.data_validation_dir, exist_ok=True)
            with open(self.data_validation_config.valid_status_file_dir, 'w') as f:
                if validation_status:
                    f.write("Validation status: True\nAll required files present.")
                else:
                    f.write(f"Validation status: False\nMissing: {sorted(list(missing_files))}")

            return validation_status


        except Exception as e:
            raise AppException(e, sys)
        


    
    def initiate_data_validation(self) -> DataValidationArtifact: 
        logging.info("Entered initiate_data_validation method of DataValidation class")
        try:
            status = self.validate_all_files_exist()
            data_validation_artifact = DataValidationArtifact(
                validation_status=status)

            logging.info("Exited initiate_data_validation method of DataValidation class")
            logging.info(f"Data validation artifact: {data_validation_artifact}")

            if status:
                shutil.copy(self.data_ingestion_artifact.data_zip_file_path, os.getcwd())

            return data_validation_artifact

        except Exception as e:
            raise AppException(e, sys)
        