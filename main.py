from py.database import *
from fastapi import Depends, FastAPI, Body
from fastapi import Response
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
import os
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = "rupollyalalalallai3yr273hfcqaid12ufdwd9q39hfge"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 160

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/js", StaticFiles(directory="js"), name="js")

# СТРАНИЦЫ


@app.get("/", summary="Получить: страница авторизации", tags=["Страницы"])
async def get_index_page():
    file_path = os.path.join("html", "index.html")

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(file_path)


@app.get("/registration", summary="Получить: страница регистрации", tags=["Страницы"])
async def get_registration_page():
    file_path = os.path.join("html", "registration.html")

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(file_path)


@app.get("/storage", summary="Получить: основная страница", tags=["Страницы"])
async def get_storage(request: Request):
    token = request.cookies.get("users_access_token")
    if not token:
        return RedirectResponse(url="/")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return RedirectResponse(url="/")

        if "exp" in payload:
            exp_timestamp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if exp_timestamp < datetime.now(timezone.utc):
                return RedirectResponse(url="/")
    except JWTError:
        return RedirectResponse(url="/")

    file_path = os.path.join("html", "storage.html")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@app.get(
    "/task_dob", summary="Получить: страница редактирования и создания задач", tags=["Страницы"]
)
async def get_storage(request: Request):

    token = request.cookies.get("users_access_token")
    if not token:
        return RedirectResponse(url="/")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return RedirectResponse(url="/")

        if "exp" in payload:

            exp_timestamp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if exp_timestamp < datetime.now(timezone.utc):
                return RedirectResponse(url="/")
    except JWTError:
        return RedirectResponse(url="/")

    file_path = os.path.join("html", "task_dob.html")

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(file_path)

# авторизация пользователя
@app.post("/users/login", summary="Авторизация пользователя", tags=["Пользователи"])
async def login_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Авторизует пользователя, кладет токен доступа в куки на сервере.
    - **login**: логин пользователя
    - **password**: пароль пользователя
    """ 
    user = db.query(UserDB).filter(UserDB.login == form_data.username).first()

    # проверяем
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
     
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


# регистрация пользователя
@app.post(
    "/user/registration", summary="Регистрация пользователя", tags=["Пользователи"]
)
async def registration_new_user(user_data: User, db: Session = Depends(get_db)):
    """
    - **login**: уникальный логин
    - **password**: пароль пользователя
    """
    # проверяем, существует ли пользователь с таким логином
    existing_user = db.query(UserDB).filter(UserDB.login == user_data.login).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует",
        )

    # хешируем пароль
    hashed_password = get_password_hash(user_data.password)

    # создаем нового пользователя
    new_user = UserDB(login=user_data.login, password=hashed_password)

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Ошибка при добавлении пользователя"
        )

    return {"message": "Пользователь добавлен"}


# Функция для получения задач пользователя
def get_tasks_by_user(db, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id).all()


# Получение задач определенного юзера
@app.get("/task/user/task_all", response_model=List[TaskResponse], summary="Получить задачи пользователя", tags=["Задачи"])
async def get_tasks(request: Request, db: Session = Depends(get_db)):
    """
    Возвращает все задачи опредленного пользователя.
    Требуется аутентификация пользователя по login в токене.
    """
    token = request.cookies.get("users_access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные",
        )

    # Декодирование JWT токена
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные",
        )

    # Получаем задачи пользователя
    tasks = get_tasks_by_user(db, int(user_id))
    return tasks


@app.post("/task/create", response_model=TaskResponse, summary="Создать задачу для опредленного пользователя", tags=["Задачи"])
async def create_task(
    request: Request, task: TaskCreate, db: Session = Depends(get_db)
):
    """
    Создает и добавляет задачу для определенного пользователя.
    Требуется аутентификация пользователя по login в токене.

    Поля для добавления задачи:
    - **heading**: Основной текст задачи
    - **task_text**: Дополнительный текст к задаче
    - **data_stop**: Дата завершения задачи
    - **prize**: Награда за выполнение задачи( по усмотрению пользователя)
    - **important**: Важность задачи
    - **completed**: Статус задачи
    """
    print(f"Received task data: {task}")
    token = request.cookies.get("users_access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception

    if not task.heading or not task.task_text or not task.data_stop:
        raise HTTPException(status_code=400, detail="Обязательные поля не заполнены")

    db = SessionLocal()
    try:
        new_task = Task(
            user_id=user_id,
            created_at=datetime.utcnow(),
            important=task.important,
            completed=task.completed,
            heading=task.heading,
            task_text=task.task_text,
            data_stop=task.data_stop,
            prize=task.prize,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    finally:
        db.close()


# удаление задачи
@app.delete("/task/delete/{task_id}", summary="Удалить задачу опредленного пользователя", tags=["Задачи"])
async def task_delete(task_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Удаляет задачу определенного пользователя.
    Требуется аутентификация пользователя по login в токене.
    """
    token = request.cookies.get("users_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные",
        )

     
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные",
        )

    db = SessionLocal()
    try:
        # Поиск задачи по task_id и user_id
        task = (
            db.query(Task)
            .filter(Task.task_id == task_id, Task.user_id == user_id)
            .first()
        )
        if task is None:
            return JSONResponse(
                status_code=404, content={"message": "Задача не найдена."}
            )

        # 
        print(f"Task found: {task}")

        
        db.delete(task)
        db.commit()

         
        return {"message": "Задача удалена."}
    finally:
        db.close()


# отображние только важных хадач
def get_tasks_by_user_important(db, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id, Task.important == True).all()


@app.get("/task/user/important", response_model=List[TaskResponse], summary="Получить важные задачи пользователя", tags=["Задачи"])
async def get_tasks_important(request: Request, db: Session = Depends(get_db)):
    """

    Возвращает все важные задачи опредленного пользователя.
    Требуется аутентификация пользователя по login в токене.

    """
    token = request.cookies.get("users_access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception

    db = SessionLocal()
    try:
        tasks = get_tasks_by_user_important(db, int(user_id))
    finally:
        db.close()

    return tasks


# отображние только важных хадач
def get_tasks_by_user_completed(db, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id, Task.completed == True).all()


@app.get("/task/user/completed", response_model=List[TaskResponse], summary="Получить завершенные задачи пользователя", tags=["Задачи"])
async def get_tasks_completed(request: Request, db: Session = Depends(get_db)):
    """

    Возвращает все завершенные задачи опредленного пользователя.
    Требуется аутентификация пользователя по login в токене.

    """
    token = request.cookies.get("users_access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception

    db = SessionLocal()
    try:
        tasks = get_tasks_by_user_completed(db, int(user_id))
    finally:
        db.close()

    return tasks


def get_tasks_by_user_today(db, user_id: int):
    today = datetime.utcnow().date()
    return (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.created_at >= today,
            Task.created_at < today + timedelta(days=1),
        )
        .all()
    )


# Получение сегодняшних задач определенного юзера
@app.get("/task/user/today", response_model=List[TaskResponse], summary="Получить сегодняшние задачи пользователя", tags=["Задачи"])
async def get_tasks_today(request: Request, db: Session = Depends(get_db)):
    """

    Возвращает все сегодняшние задачи опредленного пользователя.
    Требуется аутентификация пользователя по login в токене.

    """
    token = request.cookies.get("users_access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception

    db = SessionLocal()
    try:
        tasks = get_tasks_by_user_today(db, int(user_id))
    finally:
        db.close()

    return tasks


# Функция для получения задач пользователя
def get_tasks_by_user_task_id(db, user_id: int, task_id: int):
    return (
        db.query(Task).filter(Task.user_id == user_id, Task.task_id == task_id).first()
    )


# Получение задачи определенного юзера
@app.get("/task/user/task/{task_id}", response_model=TaskResponse, summary="Получить информацию о задачи по ее ID", tags=["Задачи"])
async def get_tasks_id(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db),
):
    """

    Возвращает информацию об опредленной задаче по ее ID.
    Требуется аутентификация пользователя по login в токене.
    Параметр пути: **task_id**

    """
    token = request.cookies.get("users_access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные",
        )

    # Декодирование JWT токена
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные",
        )

    db = SessionLocal()
    try:
        task = get_tasks_by_user_task_id(db, int(user_id), int(task_id))  #
        if task is None:
            raise HTTPException(status_code=404, detail="Задача не найдена.")
    finally:
        db.close()

    return task


# получение задачи по айди для редактирования
@app.get("/task/editing/{task_id}", response_model=TaskResponse, summary="Получить информацию о задачи по ее ID для редактирования", tags=["Задачи"])
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """

    Возвращает информацию об опредленной задаче по ее ID.
    Требуется аутентификация пользователя по login в токене.
    Параметр пути: **task_id**

    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@app.put("/task/editing/{task_id}", response_model=TaskResponse, summary="Обновить информацию о задачи по ее ID", tags=["Задачи"])
async def update_task(
    task_id: int,
    request: Request,
    task_update: TaskCreate,
    db: Session = Depends(get_db),
):
    """
    Обновляет информацию о задаче по её ID.
    Требуется аутентификация пользователя по login в токене.

    Поля для обновления задачи:
    - **heading**: Основной текст задачи
    - **task_text**: Дополнительный текст к задаче
    - **data_stop**: Дата завершения задачи
    - **prize**: Награда за выполнение задачи( по усмотрению пользователя)
    - **important**: Важность задачи
    - **completed**: Статус задачи
    """
    token = request.cookies.get("users_access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Обновляем поля задачи
    task.heading = task_update.heading
    task.task_text = task_update.task_text
    task.prize = task_update.prize
    task.important = task_update.important
    task.completed = task_update.completed
    task.data_stop = task_update.data_stop

    db.commit()
    db.refresh(task)

    return task
