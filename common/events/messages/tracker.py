# TODO: pydantic модели

"""
//  Пользователь сменил роль
    {
        uuid: str,
        event_name: str,
        service: str,
        payload: {
            user: {
                id: str,
                full_name: str,
                email: str,
                last_updated: timestamp
            },
            old_role: {
                id: int,
                name: str,
                permissions: [str],
            },
            new_role: {
                id: int,
                name: str
            },
        },
        timestamp: int
    },

"""
