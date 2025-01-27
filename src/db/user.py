import aiosqlite

from src.utils.format import combine_data, columns


class UserIsLoggedIn(Exception):
    pass
class PlayerNotFound(Exception):
    pass


class UserSet:


    @staticmethod
    async def set(db: aiosqlite.Connection, username, **kwargs):
        h = [] # какая восхитительная дырка! я бы сюда инъекцией бы поставился
        for x in [(key, value) for key, value in kwargs.items()]:
            c = f"{x[0]}=?"
            h.append(c)
        j = ', '.join(h)
        query = "UPDATE Accounts SET {} where username = ?".format(j)
        print(query)
        cursor = await db.execute(query, (*kwargs.values(), username))
        await db.commit()




class UserGet:
    basic_columns = ", ".join(x for x in columns) # god save please us
    get_query = "SELECT {basic_columns} FROM Accounts WHERE {columns} LIMIT {limit} OFFSET {offset}"

    @staticmethod
    async def get(db: aiosqlite.Connection, offset=0, limit=50, **kwargs):

        h = []
        for x in [(key, value) for key, value in kwargs.items()]:
            c = f"{x[0]}=?"
            h.append(c)
        j = ' AND '.join(h)
        print(j)
        print(User.get_query.format(basic_columns=User.basic_columns, columns=j, limit=limit, offset=offset))
        cursor = await db.execute(User.get_query.format(basic_columns=User.basic_columns, columns=j, limit=limit, offset=offset), (*kwargs.values(), ) )

        fetch = await cursor.fetchmany(limit)
        print(fetch)
        await cursor.close()
        return fetch

    @staticmethod
    async def get_by_username(db: aiosqlite.Connection, username):
        players = await User.get(db, limit=1, username=username)
        try:
            ply = combine_data(columns, players[0])
        except IndexError:
            raise PlayerNotFound
        else:
            return ply

class UserTools:
    @staticmethod
    async def set_freeze(db: aiosqlite.Connection, username, status):
        ply = await User.get_by_username(db, username)
        if ply['isLoggedIn']:
            raise UserIsLoggedIn()

        await User.execute(db, "UPDATE Accounts SET isAccFrozen = ? WHERE username = ?", (status, username,))
        await db.commit()

    @staticmethod
    async def set_premium(db: aiosqlite.Connection, username, days):
        ply = await User.get_by_username(db, username)

        print(ply)
        if ply['isLoggedIn']:
            raise UserIsLoggedIn()

        premiums_query = 'INSERT OR REPLACE INTO Premiums (client_id,delivery_time,expire_time) VALUES (?,datetime(CURRENT_TIMESTAMP),datetime(CURRENT_TIMESTAMP, ?));'
        await User.execute(db, premiums_query, (ply['id'], f"{days} days)"))
        await User.execute(db, "UPDATE Accounts SET isModerator = ? WHERE username = ?", (1, username,))
        await db.commit()

class User(UserGet, UserSet, UserTools):

    @staticmethod
    async def execute(db: aiosqlite.Connection, query, params):
        cursor = await db.execute(query, params)
        await cursor.close()




