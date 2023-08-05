from datetime import datetime, timedelta

from lamin_logger import logger
from sqlalchemy import text

from lnhub_rest.orm import engine
from lnhub_rest.orm._sbclient import connect_hub_with_auth


def delete_ci_instances() -> None:
    hub = connect_hub_with_auth()
    try:
        # Delete instances created by the CI more than one hour ago
        instance_to_delete = (
            hub.table("instance")
            .select("id")
            .like("name", "lamin.ci.instance.%")
            .lt("created_at", datetime.now() - timedelta(hours=1))
            .execute()
            .data
        )

        for index, instance in enumerate(instance_to_delete):
            (
                hub.table("account_instance")
                .delete()
                .eq("instance_id", instance["id"])
                .execute()
                .data
            )
            (hub.table("instance").delete().eq("id", instance["id"]).execute().data)
        if len(instance_to_delete) > 0:
            logger.info(f"{index + 1} instances deleted")
    except Exception as exception:
        raise Exception(exception)
    finally:
        hub.auth.sign_out()


def delete_ci_auth_users():
    # Delete users in auth.user table created by the CI more than one hour ago
    query = f"""
    delete
    from auth.users
    where email like 'lamin.ci.user.%'
    and created_at < '{str(datetime.now() - timedelta(hours=1))}';
    """
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def delete_ci_accounts() -> None:
    # Delete accounts created by the CI more than one hour ago
    delete_ci_instances()  # Delete instances first to avoid foreign key errors
    query = f"""
    delete
    from account
    where handle like 'lamin.ci.user.%'
    and created_at < '{str(datetime.now() - timedelta(hours=1))}';
    """
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def clean_ci():
    query = f"""

        -- 1. delete entries from account_instance

        delete
        from account_instance
        where instance_id in (
          select id
          from instance
          where name like 'lamin.ci.instance.%'
          and created_at < '{str(datetime.now() - timedelta(minutes=20))}'
        );

        delete
        from account_instance
        where account_id in (
          select id
          from account
          where handle like 'lamin.ci.user.%'
          and created_at < '{str(datetime.now() - timedelta(minutes=20))}'
        );

        -- 2. delete entries from instance

        delete
        from instance
        where name like 'lamin.ci.instance.%'
        and created_at < '{str(datetime.now() - timedelta(minutes=20))}';

        delete
        from instance
        where account_id in (
          select id
          from account
          where handle like 'lamin.ci.user.%'
          and created_at < '{str(datetime.now() - timedelta(minutes=20))}'
        );

        -- 3. delete entries from storage

        delete
        from storage
        where root like 'lamin.ci.storage.%'
        and created_at < '{str(datetime.now() - timedelta(minutes=20))}';

        delete
        from storage
        where created_by in (
          select id
          from account
          where handle like 'lamin.ci.user.%'
          and created_at < '{str(datetime.now() - timedelta(minutes=20))}'
        );

        -- 4. delete entries from organization_user

        delete
        from organization_user
        where organization_id in (
          select id
          from account
          where handle like 'lamin.ci.org.%'
          and created_at < '{str(datetime.now() - timedelta(minutes=20))}'
        );

        -- 5. delete entries from account

        delete
        from account
        where (handle like 'lamin.ci.user.%' or handle like 'lamin.ci.org.%')
        and created_at < '{str(datetime.now() - timedelta(minutes=20))}';

        -- 6. delete entries from auth.users

        delete
        from auth.users
        where email like 'lamin.ci.user.%'
        and created_at < '{str(datetime.now() - timedelta(minutes=20))}';
    """

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def clean_ci_by_run_id(runId: str):
    query = f"""

        -- 1. delete entries from account_instance

        delete
        from account_instance
        where instance_id in (
          select id
          from instance
          where name like 'lamin.ci.instance.{runId}'
        );

        delete
        from account_instance
        where account_id in (
          select id
          from account
          where handle like 'lamin.ci.user.{runId}'
        );

        -- 2. delete entries from instance

        delete
        from instance
        where name like 'lamin.ci.instance.{runId}'

        delete
        from instance
        where account_id in (
          select id
          from account
          where handle like 'lamin.ci.user.{runId}'
        );

        -- 3. delete entries from storage

        delete
        from storage
        where root like 'lamin.ci.storage.{runId}'

        delete
        from storage
        where created_by in (
          select id
          from account
          where handle like 'lamin.ci.user.{runId}'
        );

        -- 4. delete entries from account

        delete
        from account
        where handle like 'lamin.ci.user.{runId}'

        -- 5. delete entries from auth.users

        delete
        from auth.users
        where email like 'lamin.ci.user.{runId}'
    """

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()
