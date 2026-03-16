import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

def main():
    console.clear()
    
    # Membuat judul
    title = Text("🚀 Async Production-Ready API (FastAPI + pgvector)", style="bold cyan", justify="center")
    
    # Membuat tabel endpoint
    table = Table(show_header=True, header_style="bold magenta", expand=True, border_style="dim")
    table.add_column("Router/Tags", style="bold yellow")
    table.add_column("Endpoint", style="bold green")
    table.add_column("Method", style="bold blue")
    table.add_column("Auth/Security")
    table.add_column("Rate Limit")
    table.add_column("Description")
    
    table.add_row("Root", "/", "GET", "None", "-", "Root Hello World")
    table.add_row("General Data", "/api/v1/data/", "GET", "None", "None", "Retrieve records (Pagination)")
    table.add_row("General Data", "/api/v1/data/{id}", "GET", "None", "None", "Retrieve single record")
    table.add_row("General Data", "/api/v1/data/", "POST", "API Key", "30/min", "Insert new record")
    table.add_row("General Data", "/api/v1/data/{id}", "PUT/DEL", "API Key", "30/min", "Update/Delete record")
    table.add_row("Agent Memories", "/api/v1/memories/", "POST", "API Key", "30/min", "Ingest 768-dim Vector")
    table.add_row("Agent Memories", "/api/v1/memories/search", "POST", "None", "60/min", "Cosine Similarity (<=>)")
    table.add_row("Documentation", "/docs", "GET", "None", "None", "Swagger UI Docs Interface")
    
    # Membungkus tabel dalam panel
    panel = Panel(
        table,
        title=title,
        subtitle="[bold green]Executing Asynchronous Uvicorn Server...[/bold green]",
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print("\n[bold green]➜[/bold green] Server ready and listening at [bold cyan]http://localhost:8000[/bold cyan]")
    console.print("[bold green]➜[/bold green] Open Swagger UI Documentation at [bold cyan]http://localhost:8000/docs[/bold cyan]\n")
    console.print("[dim]Press CTRL+C to gently shut down the server...[/dim]\n")
    
    # Menjalankan uvicorn secara programatis
    try:
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        console.print("\n[bold red]Server shut down by the user.[/bold red]")

if __name__ == "__main__":
    main()
