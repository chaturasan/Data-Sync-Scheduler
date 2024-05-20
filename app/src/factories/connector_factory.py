from app.src.services.connectors.s3_connector import S3Connector


class ConnectorFactory:
    """
    Factory class for creating connectors based on the connector type.
    """

    def __init__(self):
        self.__s3connector = S3Connector()

    def get_connector(self, connector_type):
        """
        Returns the connector based on the connector type.

        Args:
            connector_type (str): The type of connector to create.

        Returns:
            tuple: A tuple containing the connector object and an error message.
                The connector object is returned as the first element of the tuple.
                If the connector type is invalid, the error message is returned as
                the second element of the tuple.
        """
        if connector_type.upper() == "S3":
            return self.__s3connector, None

        return None, f"Invalid connector type: {connector_type}"
