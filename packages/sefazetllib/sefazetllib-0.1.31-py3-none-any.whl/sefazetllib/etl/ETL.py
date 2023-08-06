import argparse
import re
from typing import List

from pyspark.sql.functions import col

from sefazetllib.Builder import Builder, field
from sefazetllib.config.CustomLogging import RequestIdFilter, logger
from sefazetllib.extract.Extract import Extract
from sefazetllib.factory.platform.dataframe.Default import Default
from sefazetllib.factory.platform.Platform import Platform
from sefazetllib.load.Load import Load
from sefazetllib.transform.Transform import Transform
from sefazetllib.validate.Validate import Validate


@Builder
class ETL:
    """
    ETL class for executing data extraction, transformation, and loading operations.
    """

    platform: Platform = field(default_factory=Default)
    partition: List = field(default_factory=list)
    repository: str = field(default="")

    def setup(self) -> None:
        """
        Parse command-line arguments and store them in self.args.
        """
        self.args = self.__get_arguments()
        # logger.addFilter(RequestIdFilter(self.args.jobName, self.args.jobId))
        logger.addFilter(RequestIdFilter())

    def __get_arguments(self) -> argparse.Namespace:
        """Parse command-line arguments and return an argparse Namespace object.

        Returns:
            argparse.Namespace: Namespace object containing parsed command-line arguments.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--jobName", help="Job name identifier")
        parser.add_argument("--jobId", help="Unique job identifier")
        parser.add_argument("--extractUrl", help="DataLake extraction URL")
        parser.add_argument(
            "--extractPartitions", help="Partitions to extract from DataLake"
        )
        parser.add_argument(
            "--extractRepository", help="DataLake extraction repository"
        )
        parser.add_argument("--loadUrl", help="DataLake loading URL")
        parser.add_argument("--loadRepository", help="DataLake loading repository")
        parser.add_argument("--inputSchema", nargs="*", help="Input parameters schema")
        parser.add_argument("--inputArgs", nargs="*", help="Input parameters")
        return parser.parse_args()

    def extract(self, extractor: Extract):
        """Execute data extraction operation using the specified Extract object.

        Parameters:
            extractor (Extract): A Extract object to use for data extraction.

        Returns:
            ETL: Self-reference to ETL object.
        """
        try:
            logger.info("Starting %s extraction..", extractor.reference.upper())

            logger.info("Executing..")

            setattr(
                self,
                *extractor.execute(
                    platform=self.platform,
                    repository=self.repository,
                    partition=self.partition,
                    args=self.args,
                ),
            )

            logger.info("Extraction completed!")
        except Exception as e:
            logger.error("Failed in %s: %s", extractor.reference.upper(), e)
            raise

        return self

    def __get_transform(self, transformer):
        """Create a new instance of the specified transformer object and inject data into its attributes.

        Parameters:
            transformer: Transformer object to use for data transformation.

        Returns:
            Transformer object with data injected into its attributes.
        """
        if type(transformer) is not Builder:
            return transformer.setDf(self.__getattribute__(transformer.reference))

        model = transformer()
        attributes = [
            attribute for attribute in dir(model) if not attribute.startswith("_")
        ]
        setters_attributes = [
            attribute for attribute in attributes if attribute.startswith("set")
        ]
        non_setters_attributes = {
            f'set{attribute.replace("_", " ").title().replace(" ", "")}': attribute
            for attribute in attributes
            if not attribute.startswith("set")
        }
        transformer_objects = [
            non_setters_attributes[attribute]
            for attribute in setters_attributes
            if attribute in non_setters_attributes
        ]
        logger.info("Starting %s transformation..", transformer.instance)

        logger.info("Injecting data..")

        for transformer_object in transformer_objects:
            if (
                not transformer_object.startswith("_")
                and transformer_object != "execute"
                and "set" not in transformer_object
            ):
                try:
                    attribute = self.__getattribute__(transformer_object)
                    transformer_setter = (
                        transformer_object.replace("_", " ").title().replace(" ", "")
                    )
                    transformer = model.__getattribute__(f"set{transformer_setter}")(
                        attribute
                    )

                except Exception as e:
                    logger.error("Failed in %s: %s", transformer, e)
                    raise

        logger.info("Data injection completed")

        return model

    def transform(self, transformer: Transform):
        """Transforms the data using the given transformer object.

        Parameters:
            transformer (Transform): A Transform object representing the transformation process.

        Returns:
            ETL: Self-reference to ETL object.
        """
        try:
            transformer = self.__get_transform(transformer)

            logger.info("Executing..")

            setattr(self.__class__, *transformer.execute())

            logger.info("Transformation completed!")
        except Exception as e:
            logger.error("Failed in %s: %s", transformer, e)
            raise

        return self

    def validate(self, validator: Validate):
        try:
            logger.info("Starting %s validation..", validator.reference.upper())

            validator.setDf(self.__getattribute__(validator.reference))

            logger.info("Executing..")

            setattr(
                self.__class__,
                *validator.execute(
                    platform=self.platform, hook_reference=self.__get_reference
                ),
            )
            self.platform.session.sparkContext._gateway.shutdown_callback_server()

            df = self.__getattribute__(validator.output)

            df.show(n=df.count(), truncate=False, vertical=False)

            if df.isEmpty():
                raise RuntimeError("Validator object has no validations")

            if not df.filter(col("constraint_status").isin("Failure")).isEmpty():
                raise RuntimeError("Validation failed with errors")

            logger.info("Validation completed!")

        except RuntimeError as e:
            logger.error("Failed in %s: %s", validator.reference.upper(), e)
            raise

        except Exception as e:
            self.platform.session.sparkContext._gateway.shutdown_callback_server()
            logger.error("Failed in %s: %s", validator.reference.upper(), e)
            raise

        return self

    def load(self, loader: Load):
        """Loads the data using the given loader object.

        Parameters:
            loader (Load): A Load object representing the data loading process.

        Returns:
            ETL: Self-reference to ETL object.
        """
        try:
            logger.info("Starting %s loading..", loader.reference.upper())

            loader.__setattr__("df_writer", self.__getattribute__(loader.reference))

            logger.info("Executing..")

            setattr(
                self.__class__,
                *loader.execute(
                    platform=self.platform,
                    repository=self.repository,
                    args=self.args,
                ),
            )

            logger.info("Loading completed!")
        except Exception as e:
            logger.error("Failed in %s: %s", loader.reference.upper(), e)
            raise

        return self
