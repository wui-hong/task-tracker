# Hong's Task List
#### Video Demo: https://youtu.be/x_QmJuAolDE
#### Description:
  This project is basically a simple task list for scheduling and noting down to do's. Its functions include a home page, the addition of new tasks, sorting tasks by completed/uncompleted, viewing the full history of tasks logged, searching for task(s) via title, description, tag or even the due date, filtering tasks by the number of days left to complete them, and a very simple change of password.
  
  All the html files take the basic layout from layout.html, which basically provides the footer and the top header navigation bar. There are 2 sql tables; users just keeps tack of the userid, username and password while tasks keeps track of the task and its relevant information; title, details, due date, user that created it, tag, whether it has been completed, and if so, when.
  
  The home page (index.html) basically shows all the tasks that the user has yet to complete. Below the navigation bar will be another header that tells the user the number of remaining tasks to do. The home page also allows the user to mark tasks as completed and update their tasklist or to delete any task.
  
  The new task (new.html) function allows the user to log a new task, and it asks for the title of the task, its details, a tag of the task for easier sorting, as well as the due date of the task. I wanted to make it sort of fancy so I made the submit button change color when hovered over :)
  
  The completed task(history.html) function basically allows the user to view all the completed tasks, and also delete them if possible. I faced some difficulty figuring out how to make a separate delete box for each task but eventually managed to get around it and make it work. I used the same html page as viewing history so as to avoid making unnecessary duplicate html files.
  
  The history (history.html) function basically shows all the tasks that have been created and their relevant details. To avoid unnecessary code, the "completed on" field will just show none if the task has yet to been completed. I considered allowing users to mark their tasks as completed as well on this page but figured that would be unnecessary as it would be more fool proof if they just did so from the home page. The history page also allows users to delete any tasks that they want to.
  
  The search function(search.html, searched.html) allows the user to search through all their tasks. It requires them to input minimum 1 field, which include title, details, tag, the specific due date of the task or a range of due dates for the tasks. To be honest I could have used history.html to display the results as well as there is no real difference between the results pages. Both allow for the deletion of tasks.
  
  The filter page (filter.html, history.html) allows the user to view all/completed/uncompleted tasks that are due X amount of days from the current day. It also uses history.html to display the results.
  
  The change password function(password.html) is just a simple function that allows the users to change their password.
  The login and logout, register (login.html, register.html) just allow users to register, login and logout.


