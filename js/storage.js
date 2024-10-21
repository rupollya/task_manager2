const tasksContainer = document.getElementById('tasksContainer');
const taskDetailsContainer = document.getElementById('taskDetailsContainer');

document.addEventListener('DOMContentLoaded', function () {

    taskDetailsContainer.innerHTML = `
        <div class="no-task-message">
                        <p style="text-align:center; color: grey;" class="mt-2">Задача не открыта</p>
                    </div>
    `;

    document.querySelectorAll('.ramk').forEach(item => {
        item.addEventListener('click', event => {
            const category = item.getAttribute('data-category');
            console.log(category);
            loadTasks(category);
        });
    });

    async function loadTasks(category = 'task_all') {
        currentCategory = category;
        try {
            const response = await fetch(`/task/user/${category}`);
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            if (response.ok) {

                const tasks = await response.json();
                console.log(tasks);
                display_category(category);
                displayTasks(tasks);
            } else {
                console.error('Ошибка при загрузке задач:', response.statusText);
            }
        } catch (error) {
            console.error('Ошибка при загрузке задач:', error);
        }
    }

    async function display_category(category) {
        const selectElement = document.getElementById('select');
        if (category === 'task_all') {
            selectElement.textContent = 'Все задачи';
        } else if (category === 'completed') {
            selectElement.textContent = 'Завершенные';
        } else if (category === 'today') {
            selectElement.textContent = 'Сегодня';
        } else if (category === 'important') {
            selectElement.textContent = 'Важные';
        }
    }

    async function displayTasks(tasks) {

        tasksContainer.innerHTML = '';

        if (tasks.length === 0) {

            tasksContainer.innerHTML = `
        <div class="no-task-message">
            <p style="text-align:center; color: grey;" class="mt-2">Задач пока нет</p>
        </div>
    `;
        } else {
            tasks.forEach(task => {
                const maxLength = 20;
                const headingText = task.heading.length > maxLength
                    ? task.heading.slice(0, maxLength) + '...'
                    : task.heading;
                const taskElement = document.createElement('div');
                taskElement.classList.add('task');
                taskElement.setAttribute('data-task-id', task.task_id);
                taskElement.innerHTML = `
                <div class="d-flex justify-content-between selected-task-btn">
                   <div class="d-flex">
                       <img src="/images/love.png" width="45" height="45">
                       <button type="button" class="task_section2" data-task-id="${task.task_id}">
                           ${headingText} 
                        </button>
                    </div >
                    <div class="d-flex">

                    </div>
                </div >
                    `;
                tasksContainer.appendChild(taskElement);

                taskElement.querySelector('.selected-task-btn').addEventListener('click', function () {
                    const taskId = taskElement.getAttribute('data-task-id');
                    loadTaskDetails(taskId);
                });
            });
        }
    }

    async function loadTaskDetails(taskId) {
        try {
            const response = await fetch(`/task/user/task/${taskId}`);
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            if (response.ok) {
                const task = await response.json();
                displayTaskDetails(task);
            } else {
                console.error('Ошибка при загрузке деталей задачи:', response.statusText);
            }
        } catch (error) {
            console.error('Ошибка при загрузке деталей задачи:', error);
        }
    }

    async function displayTaskDetails(task) {
        taskDetailsContainer.innerHTML = `
                    <div class="task-container" data - task - id="${task.task_id}" >
        <div class="d-flex justify-content-between align-items-center mt-2">
           <a href="/task_dob?task_id=${task.task_id}" style="text-decoration: none;">
              <div class="ramk_section3 d-flex align-items-center flex-wrap redak-task-btn">
                   <img src="/images/redak.png" width="25" height="25">
                   <p class="nologo" style="text-decoration:none;padding-top: 15px;margin-left:3px;margin-right:5px">Редактировать</p>
              </div>
           </a>
             <img src="/images/bin.png" width="35" height="35" data-task-id="${task.task_id}" class="delete-task-btn" style="cursor:pointer;">
        </div>
        
        <div style="background-color:#7F7679;border-radius: 5pt">
        <div class="m-2">
        <h4 style="margin-top:30px;color:white; word-break: break-all;" class="pt-3">
            ${task.heading}
        </h4>
        <p style="color:white;">Дата создания: ${new Date(task.created_at).toLocaleDateString()}</p>
        <p style="color:white;">Срок: ${new Date(task.data_stop).toLocaleDateString()}</p>
        <p style="background-color: white;border-radius: 5pt;padding:5px; word-break: break-all;">
            ${task.task_text}
        </p>
        <p class="pb-3" style="color:white; word-break: break-all;"><b>Награда: ${task.prize}</b></p>
       </div>
        </div>

    </ >
                    `;

    }

    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-task-btn')) {
            event.stopPropagation();
            const taskId = event.target.dataset.taskId;
            const taskElement = event.target.closest('.task-container');
            deleteTask(taskId, taskElement);
            loadTasks();
        }
    });

    // Удаление задачи
    async function deleteTask(taskId, taskElement) {
        try {
            const response = await fetch(`task/delete/${taskId}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                console.log(`Задача с ID ${taskId} удалена`);
                taskElement.remove();

                taskDetailsContainer.innerHTML = `
                    <div class="no-task-message">
                        <p style="text-align:center; color: grey;" class="mt-2">Задача не открыта</p>
                    </div>
                `;
            } else {
                console.error('Ошибка при удалении задачи:', response.statusText);
            }
        } catch (error) {
            console.error('Ошибка при удалении задачи:', error);
        }
    }

    loadTasks();



    document.getElementById('searchInput').addEventListener('input', function () {
        const searchTerm = this.value.toLowerCase();


        const tasks = document.querySelectorAll('.task');

        tasks.forEach(task => {
            const taskHeading = task.querySelector('.task_section2').textContent.toLowerCase();

            if (taskHeading.includes(searchTerm)) {
                task.style.display = 'block';
            } else {
                task.style.display = 'none';
            }
        });
    });



});
