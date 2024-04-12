# для начала загрузим образ питона
FROM python:3.9.6
# потом скопируем туда все наши файлы из проекта
WORKDIR /recipes_backend
COPY . .
# загрузим все зависимости
RUN pip install mysql-connector-python==8.3.0
# и запустим проект
CMD ["python", "./main.py"]