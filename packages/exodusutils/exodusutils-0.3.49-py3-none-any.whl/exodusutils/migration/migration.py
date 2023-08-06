from logging import Logger

from pymongo.collection import Collection

from exodusutils.schemas.requests import MigrateAction, MigrateReqBody


def migration(
    req: MigrateReqBody,
    all_migrations,
    migration_collection: Collection,
    model_collection: Collection,
    logger: Logger,
) -> None:
    """
    Runs the migration scripts that are yet to be run.
    """
    should_reverse = req.action == MigrateAction.down
    migrations = sorted(
        all_migrations, key=lambda x: x.timestamp, reverse=should_reverse
    )
    if req.action == MigrateAction.up:
        migrations = [
            m
            for m in migrations
            if migration_collection.find_one({"name": m.mongo_name}) is None
        ]
        for m in migrations:
            try:
                m.up(model_collection)
                migration_collection.insert_one({"name": m.mongo_name})
                logger.info(f"Migrated up: {m.mongo_name}")
            except:
                logger.exception(f"Failed to run up: {m.mongo_name}")
    else:
        migrations = [
            m
            for m in migrations
            if migration_collection.find_one({"name": m.mongo_name}) is not None
        ]
        if not migrations:
            logger.warn("No migrations to run down")
        else:
            migration = migrations[0]
            try:
                migration.down(model_collection)
                migration_collection.delete_one({"name": migration.mongo_name})
                logger.info(f"Migrated down: {migration.mongo_name}")
            except:
                logger.warn(f"Failed to run down: {migration.mongo_name}")
