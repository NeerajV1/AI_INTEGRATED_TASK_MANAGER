
document.addEventListener("DOMContentLoaded",getalldata
)
function addtask(){
    let input = document.getElementById("form-adder");
    input.innerHTML = `
    <form onsubmit="createTask(event)">
        <input type="text" id="task-name" placeholder="Task Name" required>
        <input type="text" id="task-desc" placeholder="Task Description">
        <input type="date" id="task-date" required>

        <label for="task-priority">Priority:</label>
        <select id="task-priority">
            <option value="low">Low</option>
            <option value="medium" selected>Medium</option>
            <option value="high">High</option>
        </select>

        <label for="task-status">Status:</label>
        <select id="task-status">
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
        </select>

        <button type="submit">Add Task</button>
    </form>
    `;
    
}
async function createTask(event) { // Added 'async'
    if(event) event.preventDefault();
    
    let taskname = document.getElementById("task-name").value;
    let taskdesc = document.getElementById("task-desc").value;
    let taskdate = document.getElementById("task-date").value;
    let taskpriority = document.getElementById("task-priority").value;
    let taskstatus = document.getElementById("task-status").value;

    // Added 'await' so we wait for the server
    const result = await fetch("/sendtask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials:"include",
        body: JSON.stringify({
            title: taskname,        // Changed 'name' to 'title'
            description: taskdesc,
            deadline: taskdate,
            priority: taskpriority,
            status: taskstatus
        })
    });
    getalldata();
    if (result.ok) {
        const data = await result.json(); // Use lowercase 'result', added 'await'
        alert(data["message"]);
        document.getElementById("form-adder").innerHTML = ""; // Close form on success
    } else {
        const errorData = await result.json();
        alert("Error: " + (errorData.detail || "Check your input format"));
    }

}

async function getalldata() {
    let viewTasks = document.getElementById("view-tasks");
    viewTasks.innerHTML = "Loading..."; // Feedback for the user

    const result = await fetch("/alltasks", {
        method: 'GET',
        credentials: "include"
    });

    if (result.ok) {
        const data = await result.json();
        let htmlBuffer = ""; // Build the string here first

        for (const taskItem of data) {
            try {
                const responseCheck = await fetch(`/check/${taskItem.taskid}`, {
                    method: 'POST',
                    headers: { "content-type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify(taskItem) // Just send the whole object
                });

                if (responseCheck.ok) {
                    const responseData = await responseCheck.json();
                    // Only add to buffer if the task is still valid (result 0)
                    if (responseData["result"] === 0) {
                        htmlBuffer += `
                            <div id="task-${taskItem.taskid}" class="task-card">
                                <b>${taskItem.title}</b>
                                <p>${taskItem.description}</p>
                                <span>Deadline: ${taskItem.deadline}</span>
                                <div class="${taskItem.priority}">${taskItem.priority}</div>
                                <br><br>
                                <button onclick="deleteData('${taskItem.title}')">Delete</button>
                                <button onclick="update('${taskItem.title}','${taskItem.description}','${taskItem.deadline}','${taskItem.priority}','${taskItem.status}')">Update</button>
                            </div>`;
                    }
                }
            } catch (err) {
                console.error("Task check failed:", err);
            }
        }
        // FINAL UI UPDATE: One single DOM touch
        viewTasks.innerHTML = htmlBuffer || "<p>No active tasks found.</p>";
    }
}
async function deleteData(name) {
    const res = await fetch("/gettaskid", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
            title: name
        })
    });

    if (!res.ok) {
        alert("Task not found!");
        return;
    }

    const response = await res.json();

    if (!response.taskid) {
        alert("Task not found!");
        return;
    }

    const res2 = await fetch(`/delete/${response.taskid}`, {
        method: 'DELETE',
        credentials: "include"
    });

    if (res2.ok) {
        alert("Deleted successfully!");
    } else {
        alert("Delete failed!");
    }
    getalldata();
}
async function update(name, desc, deadline, priority, status) {
    const res = await fetch("/gettaskid", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({ title: name })
    });

    if (!res.ok) {
        alert("task not found 1");
        return;
    }

    const data = await res.json();

    if (!data.taskid) {
        alert("task not found 2");
        return;
    }

    let taskid = data.taskid;

    let area = document.getElementById(`task-${taskid}`);

    area.innerHTML = `
    <form onsubmit="event.preventDefault(); getUpdatedData(${taskid})">
        <input type="text" id="task-name-${taskid}" value="${name}" required>
        <input type="text" id="task-desc-${taskid}" value="${desc}">
        <input type="date" id="task-date-${taskid}" value="${deadline}" required>

        <select id="task-priority-${taskid}">
            <option value="low" ${priority === 'low' ? 'selected' : ''}>Low</option>
            <option value="medium" ${priority === 'medium' ? 'selected' : ''}>Medium</option>
            <option value="high" ${priority === 'high' ? 'selected' : ''}>High</option>
        </select>

        <select id="task-status-${taskid}">
            <option value="pending" ${status === 'pending' ? 'selected' : ''}>Pending</option>
            <option value="completed" ${status === 'completed' ? 'selected' : ''}>Completed</option>
            <option value="failed" ${status === 'failed' ? 'selected' : ''}>Failed</option>
        </select>

        <button type="submit">submit</button>
    </form>
    `;
}
async function getUpdatedData(taskid) {
    let taskname = document.getElementById(`task-name-${taskid}`).value;
    let taskdesc = document.getElementById(`task-desc-${taskid}`).value;
    let taskdate = document.getElementById(`task-date-${taskid}`).value;
    let taskpriority = document.getElementById(`task-priority-${taskid}`).value;
    let taskstatus = document.getElementById(`task-status-${taskid}`).value;

    const res2 = await fetch(`/update_task/${taskid}`, {
        method: 'PUT',
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
            title: taskname,
            description: taskdesc,
            deadline: taskdate,
            priority: taskpriority,
            status: taskstatus
        })
    });

    if (res2.ok) {
        alert("task updated successfully!");
    } else {
        alert("some error occurred");
    }
    getalldata(); 
}
async function createTasksViatext() {
    let viewTasks = document.getElementById("view-tasks");
    let text=document.getElementById("input-text").value;
    try {
        // 1. Added await here
        const response = await fetch("/createTaskViaAI", {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            
            body: JSON.stringify({ "text": text }) 
        });

        if (!response.ok) {
            
            const errorData = await response.json();
            alert("Error: " + (errorData.detail || "Something went wrong"));
            return;
        }

        const result = await response.json();
        
        
        alert(result.message); 
        
        
        getalldata();

    } catch (err) {
        console.error("Network error:", err);
        alert("Could not connect to the server.");
    }
}