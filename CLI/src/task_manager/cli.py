from urllib import response

import typer
from rich.console import Console

from .api_client import (
    get_tasks,
    get_task,
    create_task,
    complete_task,
    update_task,
    delete_task,
    login_user,
    register_user,
)

from .auth import (
    save_tokens,
    load_tokens,
    logout,
)

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main():

    console.print(
        "\n[bold cyan]╭──────────────────────────────────────╮[/bold cyan]"
    )
    console.print(
        "[bold cyan]│        TASK MANAGER CLI              │[/bold cyan]"
    )
    console.print(
        "[bold cyan]╰──────────────────────────────────────╯[/bold cyan]"
    )
    console.print("\nWelcome to Task Manager CLI!")
    console.print("Type [bold]help[/bold] to see available commands.")
    console.print("Type [bold]exit[/bold] to quit.\n")

    while True:

        command = typer.prompt("task")

        # Exit the CLI
        if command.lower() == "exit":

            console.print("[yellow]Goodbye![/yellow]")
            break

        # Show available CLI commands
        elif command.lower() == "help":

            console.print("\n[bold cyan]AUTH[/bold cyan]")
            console.print("  register  - Create a new account")
            console.print("  login     - Login to your account")
            console.print("  logout    - Logout from your account")
            console.print("  me        - Show current user")

            console.print("\n[bold cyan]TASKS[/bold cyan]")
            console.print("  list      - Show your tasks")
            console.print("  get       - Get a task by ID")
            console.print("  create    - Create a new task")
            console.print("  update    - Update a task")
            console.print("  delete    - Delete a task")
            console.print("  done      - Mark a task as completed")

            console.print("\n[bold cyan]SYSTEM[/bold cyan]")
            console.print("  help      - Show this help")
            console.print("  clear     - Clear the terminal")
            console.print("  exit      - Exit the CLI\n")

        # Clear the terminal
        elif command.lower() == "clear":

            console.clear()

        # Register a new user account
        elif command.lower() == "register":

            """
            Flow:
            task: register
                ↓
            Ask username
                ↓
            Ask email
                ↓
            Ask password
                ↓
            api_client.py
                ↓
            POST /api/register/
                ↓
            Django creates the user
            """

            console.print("\n[bold cyan]Create Account[/bold cyan]")

            username = typer.prompt("Username")
            email = typer.prompt("Email")
            password = typer.prompt(
                "Password",
                hide_input=True
            )

            response = register_user(
                username,
                email,
                password
            )

            if response.status_code == 201:

                console.print(
                    "[green]✓ Account created successfully![/green]"
                )

            else:

                console.print(
                    f"[red]✗ Registration failed:[/red] "
                    f"{response.text}"
                )

        # Login and save JWT tokens locally
        elif command.lower() == "login":

            console.print("\n[bold cyan]Login[/bold cyan]")

            username = typer.prompt("Username")
            password = typer.prompt(
                "Password",
                hide_input=True
            )

            response = login_user(
                username,
                password
            )

            if response.status_code == 200:

                tokens = response.json()

                # Save access and refresh tokens locally
                save_tokens(tokens)

                console.print(
                    "[green]✓ Login successful![/green]"
                )

            else:

                console.print(
                    f"[red]✗ Login failed:[/red] "
                    f"{response.text}"
                )

        # Retrieve and display the user's tasks
        elif command.lower() == "list":

            # Load the saved JWT tokens
            tokens = load_tokens()

            if not tokens:

                console.print(
                    "[red]Please login first.[/red]"
                )
                continue

            # Send the access token with the API request
            response = get_tasks(
                tokens["access"]
            )

            if response.status_code == 200:

                tasks = response.json()

                # Check whether the user has any tasks
                if not tasks:

                    console.print(
                        "\n[yellow]You don't have any tasks yet.[/yellow]"
                    )
                    continue

                console.print(
                    "\n[bold cyan]Your Tasks[/bold cyan]"
                )
                console.print(
                    "────────────────────────────────────────"
                )

                # Display every task
                for task in tasks:

                    # Show ✓ for completed tasks
                    # Show ☐ for incomplete tasks
                    if task["done"]:
                        status_icon = "[green]✓[/green]"
                    else:
                        status_icon = "[yellow]☐[/yellow]"

                    console.print(
                        f"{status_icon} "
                        f"[bold]ID: {task['id']}[/bold]"
                    )

                    # Display the task title
                    console.print(
                        f"   [bold]{task['title']}[/bold]"
                    )

                    # Display the task description
                    description = task.get(
                        "description",
                        ""
                    )

                    # Break long descriptions into readable lines
                    words = description.split()
                    lines = []
                    current_line = ""

                    for word in words:

                        if len(current_line) + len(word) + 1 <= 60:

                            current_line += word + " "

                        else:

                            lines.append(
                                current_line.strip()
                            )
                            current_line = word + " "

                    if current_line:

                        lines.append(
                            current_line.strip()
                        )

                    for line in lines:

                        console.print(
                            f"   {line}"
                        )

                    console.print()

                console.print(
                    "────────────────────────────────────────"
                )

            else:

                console.print(
                    f"[red]Failed to get tasks:[/red] "
                    f"{response.text}"
                )

        # Create a new task
        elif command.lower() == "create":

            # Load the saved JWT tokens
            tokens = load_tokens()

            if not tokens:

                console.print(
                    "[red]Please login first.[/red]"
                )
                continue

            console.print(
                "\n[bold cyan]Create Task[/bold cyan]"
            )

            title = typer.prompt("Title")

            description = typer.prompt(
                "Description",
                default=""
            )

            # Send the new task to the Django API
            response = create_task(
                tokens["access"],
                title,
                description
            )

            if response.status_code == 201:

                console.print(
                    "[green]✓ Task created successfully![/green]"
                )

            else:

                console.print(
                    f"[red]✗ Failed to create task:[/red] "
                    f"{response.text}"
                )

        # Mark an existing task as completed
        elif command.lower() == "done":

            # Load the saved JWT tokens
            tokens = load_tokens()

            if not tokens:

                console.print(
                    "[red]Please login first.[/red]"
                )
                continue

            # Ask which task should be marked as completed
            task_id = typer.prompt("Task ID")

            # Send the completion request to the Django API
            response = complete_task(
                tokens["access"],
                task_id
            )

            if response.status_code == 200:

                console.print(
                    "[green]✓ Task marked as completed![/green]"
                )

            else:

                console.print(
                    f"[red]✗ Failed to complete task:[/red] "
                    f"{response.text}"
                )
        elif command.lower() == "edit":
            tokens = load_tokens()

            if not tokens:
                console.print("[red]Please login first.[/red]")
                continue

            console.print("\n[bold cyan]Edit Task[/bold cyan]")

            task_id = typer.prompt("Task ID")
            title = typer.prompt("New title")
            description = typer.prompt("New description")

            response = update_task(
            tokens["access"],
            task_id,
            title,
            description
            )

            if response.status_code == 200:
                console.print("[green]✓ Task updated successfully![/green]")
            else:
                console.print(
                f"[red]✗ Failed to update task:[/red] "
                f"{response.text}"
            )
                
        # Handle commands that are not implemented or recognized
        elif command.lower() == "get":
            tokens = load_tokens()

            if not tokens:
                console.print("[red]Please login first.[/red]")
                continue

            task_id = typer.prompt("Task ID")

            response = get_task(
                tokens["access"],
                task_id
            )

            if response.status_code == 200:
                task = response.json()

                status_icon = (
                "[green]✓[/green]"
                if task["done"]
                else "[yellow]☐[/yellow]"
            )

                console.print(f"\n{status_icon} [bold]ID: {task['id']}[/bold]")
                console.print(f"   [bold]{task['title']}[/bold]")
                console.print(f"   {task.get('description', '')}")
            else:
                console.print(
                f"[red]✗ Failed to get task:[/red] "
                f"{response.text}"
        )
        elif command.lower() == "delete":
            tokens = load_tokens()

            if not tokens:
                console.print("[red]Please login first.[/red]")
                continue

            task_id = typer.prompt("Task ID")

            confirm = typer.confirm(
            f"Are you sure you want to delete task {task_id}?"
            )

            if not confirm:
                console.print("[yellow]Delete cancelled.[/yellow]")
                continue

            response = delete_task(
                tokens["access"],
                task_id
            )

            if response.status_code == 204:
                console.print(
                "[green]✓ Task deleted successfully![/green]"
            )
            else:
                console.print(
            f"[red]✗ Failed to delete task:[/red] "
            f"{response.text}"
        )
        elif command.lower() == "logout":
            tokens = load_tokens()

            if not tokens:
                console.print("[yellow]You are not logged in.[/yellow]")
                continue

            logout()

            console.print("[green]✓ Logged out successfully![/green]")

        else:

            console.print(
                f"[red]Unknown command:[/red] {command}"
            )


if __name__ == "__main__":
    app()