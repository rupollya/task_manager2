function formatDate(dateString) {
    const date = new Date(dateString);
    const day = date.getDate().toString().padStart(2, '0'); // Получаем день
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Получаем месяц (добавляем 1, т.к. январь = 0)
    const year = date.getFullYear(); // Получаем год
    return `${day}-${month}-${year}`; // Форматируем строку как день-месяц-год
}


document.addEventListener('DOMContentLoaded', function () {
    function formatDate(dateString) {
        const date = new Date(dateString);
        const options = {
            weekday: 'long',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        };
        const formatter = new Intl.DateTimeFormat('ru-RU', options);
        return formatter.format(date);
    }

    function getCurrentDate() {
        const date = new Date();
        const options = {
            weekday: 'short',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
        };
        const formatter = new Intl.DateTimeFormat('ru-RU', options);
        return formatter.format(date);
    }

    document.querySelectorAll('.date-text').forEach(element => {
        const originalText = element.textContent;
        const dateMatch = originalText.match(/Дата создания: (.+)/) || originalText.match(/Срок: (.+)/);

        if (dateMatch) {
            const formattedDate = formatDate(dateMatch[1]);
            element.textContent = originalText.replace(dateMatch[1], formattedDate);
        } else {
            // Если нет даты, вставляем текущее время
            const currentDate = getCurrentDate();
            element.textContent = `Дата создания: ${currentDate}`;
        }
    });
});
const urlParams = new URLSearchParams(window.location.search);
document.addEventListener('DOMContentLoaded', async function () {
    const taskId = urlParams.get('task_id');
    console.log('Task ID:', taskId); // Отладочный вывод

    if (taskId) {
        // Редактирование задачи
        try {
            const response = await fetch(`/task/editing/${taskId}`, {
                method: 'GET'
            });

            if (response.ok) {
                const task = await response.json();
                console.log(task)
                // Установка значений полей задачи...
                const headingInput = document.getElementById("heading");
                const editableDiv = document.getElementById('editableDiv');
                const prize = document.getElementById("prize");
                const creationDateElement = document.getElementById('creationDate');
                const completionDateInput = document.getElementById('completionDate'); 
                const checkbox = document.getElementById('completedCheckbox');
                const importantCheckbox = document.getElementById('importantCheckbox');
                const taskStatus = document.getElementById('taskStatus');
                const taskStatusContainer = document.getElementById('taskStatusContainer');

                headingInput.value = task.heading;
                editableDiv.innerHTML = task.task_text;
                prize.value = task.prize;
                importantCheckbox.checked = task.important;
                creationDateElement.innerText = task.created_at ? formatDate(task.created_at) : '';
                completionDateInput.value = task.data_stop ? task.data_stop.split('T')[0] : '';

                // Устанавливаем начальное состояние чекбокса
                checkbox.checked = task.completed;
                taskStatus.textContent = task.completed ? 'Задача завершенна' : 'Задача в процессе';

                // Слушаем событие изменения состояния чекбокса
                checkbox.addEventListener('change', function () {
                    taskStatus.textContent = checkbox.checked ? 'Задача завершенна' : 'Задача в процессе';
                });

                // Показать элементы, если задача редактируется
                taskStatusContainer.style.display = 'flex'; // Показываем контейнер
                console.log('Показать контейнер'); // Отладочный вывод
            } else {
                console.error('Ошибка при получении задачи:', response.statusText);
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    } else {
        // Создание новой задачи
        document.getElementById('creationDate').innerText = formatDate(new Date());
        document.getElementById('completionDate').value = '';
        document.getElementById('importantCheckbox').checked = false;
        document.getElementById('prize').value = '';
        document.getElementById('task_id').value = '';
        document.getElementById('heading').value = '';
        document.getElementById('editableDiv').innerText = '';

        // Скрыть элементы, если задача не редактируется
        const taskStatusContainer = document.getElementById('taskStatusContainer');
        const taskStatusContainertext = document.getElementById('taskStatusContainerText');
        console.log('Контейнер найден:', taskStatusContainer); // Отладочный вывод
        console.log('Текущий стиль:', taskStatusContainer.style.display); // Вывод текущего стиля

        if (taskStatusContainer) {
            taskStatusContainer.style.visibility = 'hidden'; 
            taskStatusContainertext.style.visibility = 'hidden';// Скрываем контейнер
            console.log('Скрыть контейнер'); // Отладочный вывод
            console.log('Новый стиль:', taskStatusContainer.style.display); // Вывод нового стиля
        } else {
            console.error('Контейнер не найден'); // Если контейнер не найден
        }
    }
});

async function saveTask() {
    const heading = document.getElementById('heading').value.trim();
    const task_text = document.getElementById('editableDiv').innerHTML;
    const prize = document.getElementById('prize').value.trim();
    const data_stop = document.getElementById('completionDate').value;

    if (!heading || !task_text || !data_stop) {
        document.getElementById('modalErrorMessage').innerText = 'Заполните все обязательные поля.';
        const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
        errorModal.show();
        return;
    }

    const taskId = parseInt(urlParams.get('task_id'));
    const important = document.getElementById('importantCheckbox').checked;
    const completed = document.getElementById('completedCheckbox').checked;

    const taskData = {
        heading,
        task_text,
        prize,
        important,
        completed,
        data_stop
    };

    const method = taskId ? 'PUT' : 'POST';
    const url = taskId ? `/task/editing/${taskId}` : '/task/create';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData),
        });

        if (response.ok) {
            console.log('Задача успешно сохранена');
            window.location.href = '/storage';
        } else {
            const errorText = await response.text();
            console.error('Ошибка при сохранении задачи:', errorText);
        }
    } catch (error) {
        console.error('Ошибка при сохранении задачи:', error);
    }
}
