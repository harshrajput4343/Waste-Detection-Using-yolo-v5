import os,sys
import yaml
import shutil
import zipfile
import subprocess
from pathlib import Path
from wasteDetection.utils.main_utils import read_yaml_file
from wasteDetection.logger import logging
from wasteDetection.exception import AppException
from wasteDetection.entity.config_entity import ModelTrainerConfig
from wasteDetection.entity.artifacts_entity import ModelTrainerArtifact



class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
    ):
        self.model_trainer_config = model_trainer_config


    

    def initiate_model_trainer(self,) -> ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")

        try:
            logging.info("Unzipping data if data.zip exists")
            if Path("data.zip").exists():
                with zipfile.ZipFile('data.zip', 'r') as zip_ref:
                    zip_ref.extractall('.')
                try:
                    Path('data.zip').unlink()
                except Exception:
                    logging.info('Could not remove data.zip, skipping')

            with open("data.yaml", 'r') as stream:
                num_classes = str(yaml.safe_load(stream)['nc'])

            model_config_file_name = self.model_trainer_config.weight_name.split(".")[0]
            print(model_config_file_name)

            config = read_yaml_file(f"yolov5/models/{model_config_file_name}.yaml")

            config['nc'] = int(num_classes)


            with open(f'yolov5/models/custom_{model_config_file_name}.yaml', 'w') as f:
                yaml.dump(config, f)

            # run yolov5 training in a cross-platform way
            yolov5_dir = Path("yolov5")
            train_cmd = [
                sys.executable,
                "train.py",
                "--img",
                "416",
                "--batch",
                str(self.model_trainer_config.batch_size),
                "--epochs",
                str(self.model_trainer_config.no_epochs),
                "--data",
                "../data.yaml",
                "--cfg",
                "./models/custom_yolov5s.yaml",
                "--weights",
                str(self.model_trainer_config.weight_name),
                "--name",
                "yolov5s_results",
                "--cache",
            ]

            logging.info(f"Running training: {' '.join(train_cmd)} in {yolov5_dir}")
            subprocess.run(train_cmd, cwd=yolov5_dir, check=True)

            # locate the produced best.pt file robustly
            expected = yolov5_dir / 'runs' / 'train' / 'yolov5s_results' / 'weights' / 'best.pt'
            candidates = list((yolov5_dir / 'runs' / 'train').rglob('**/weights/best.pt')) if (yolov5_dir / 'runs' / 'train').exists() else []
            src = None
            if expected.exists():
                src = expected
            elif candidates:
                # pick the first candidate (there will usually be one)
                src = candidates[0]

            if src is None or not src.exists():
                raise AppException(f"Trained weights not found after training. Looked for {expected} and found: {candidates}", sys)

            # copy to repository yolov5/ and to configured trainer dir
            dest_repo = yolov5_dir / 'best.pt'
            shutil.copy2(src, dest_repo)

            os.makedirs(self.model_trainer_config.model_trainer_dir, exist_ok=True)
            dest_artifact = Path(self.model_trainer_config.model_trainer_dir) / 'best.pt'
            shutil.copy2(src, dest_artifact)

            # cleanup generated files/directories
            try:
                shutil.rmtree(yolov5_dir / 'runs')
            except Exception:
                logging.info('Could not remove yolov5/runs, skipping')

            for p in ['train', 'valid']:
                if Path(p).exists():
                    try:
                        shutil.rmtree(p)
                    except Exception:
                        logging.info(f'Could not remove {p}, skipping')

            try:
                if Path('data.yaml').exists():
                    Path('data.yaml').unlink()
            except Exception:
                logging.info('Could not remove data.yaml, skipping')

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=str(dest_artifact),
            )

            logging.info("Exited initiate_model_trainer method of ModelTrainer class")
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact


        except Exception as e:
            raise AppException(e, sys)
