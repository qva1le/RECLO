import argparse
import asyncio

from sqlalchemy import select

from src.database import async_session_maker
from src.models.users import UsersOrm
from src.utils.db_manager import DBManager


async def promote(email: str | None, name: str | None) -> None:
    async with DBManager(session_factory=async_session_maker) as db:
        stmt = select(UsersOrm)

        if email:
            stmt = stmt.filter(UsersOrm.email == email)
        elif name:
            stmt = stmt.filter(UsersOrm.name == name)
        else:
            raise ValueError("Нужен email или name")

        res = await db.session.execute(stmt.limit(1))
        user = res.scalar_one_or_none()

        if not user:
            raise SystemExit("Пользователь не найден")

        user.is_admin = True
        await db.session.commit()

        print(f"OK: user id = {user.id} is_admin={user.is_admin} email={getattr(user, 'email', None)}")


async def demote(email: str | None, name: str | None) -> None:
    async with DBManager(session_factory=async_session_maker) as db:
        stmt = select(UsersOrm)

        if email:
            stmt = stmt.filter(UsersOrm.email == email)
        elif name:
            stmt = stmt.filter(UsersOrm.email == email)
        else:
            raise ValueError("Нужен email или name")

        res = await db.session.execite(stmt)
        user = res.scalar_one_or_none()

        if not user:
            raise SystemExit("Пользователь не найден")

        user.is_admin = False
        await db.session.commit()

        print(f"OK: user id = {user.id} is_admin={user.is_admin} email={getattr(user, 'email', None)}")


def main():
    parser = argparse.ArgumentParser("Admin tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("promote", help="Make user admin")
    p1.add_argument("--email", type=str, default=None)
    p1.add_argument("--nickname", type=str, default=None)

    p2 = sub.add_parser("demote", help="Remove admin rights")
    p2.add_argument("--email", type=str, default=None)
    p2.add_argument("--nickname", type=str, default=None)

    args = parser.parse_args()

    if args.cmd == "promote":
        asyncio.run(promote(args.email, args.nickname))
    else:
        asyncio.run(demote(args.email, args.nickname))


if __name__ == "__main__":
    main()