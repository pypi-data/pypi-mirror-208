from ssb_altinn3_util.database import schema
from ssb_altinn3_util.database.altinn_mottak_db_adapter import AltinnMottakDbAdapter


def init_db_adapter(
    user_name: str,
    database_name: str,
    project_id: str,
    spanner_instance_id: str,
    user_password: str = None,
    in_memory: bool = False,
) -> AltinnMottakDbAdapter:
    """
    Initiates the database adapter enabling database storage through the database.crud module

    :param user_name: Name of the database user used for the connection.  Regular database user when running locally,
    IAM enabled user when running against a cloud sql instance
    :param database_name: The name of the database to connect to
    :param project_id: If Spanner is used, provide the project-id
    :param spanner_instance_id: If Spanner is used, provide the Spanner instance-id
    :param user_password: Password for the database user.  Only required when using local database or ordinary database
    authentication.
    :param in_memory: If set to True a sqllite instance for in_memory use is created
    :return: A configured data adapter ready for use.
    """
    adapter = AltinnMottakDbAdapter()
    adapter.init_engine(
        user_name=user_name,
        user_password=user_password,
        database_name=database_name,
        spanner_instance_id=spanner_instance_id,
        project_id=project_id,
        in_memory=in_memory,
    )
    schema.AltinnMottakDbAdapter.Base.metadata.create_all(bind=adapter.engine)
    return adapter
