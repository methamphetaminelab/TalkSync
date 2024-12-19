# TalkSync

## API

- `/ws/{user_id}`
    > Подключение к веб-сокету. Указывается id пользователя.  

- `{type: "[тип_сообщения]", "receiverId": "[id_получателя]", "text": "[текст]"}`
    > `{"type": "privateMessage", "receiverId": "2", "text": "Hello!"}` - приватное сообщение пользователю с id 2  
    > `{"type": "globalMessage", "text": "Hello!"}` - общее сообщение всем пользователям

## CHANGELOG

### api v1.0.0
> Релиз апи

### client-cli v1
> Релиз клиента командной строки