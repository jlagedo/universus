"""
UI presentation layer for displaying market data.
"""

import sys
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class MarketUI:
    """UI handler for displaying market data."""
    
    @staticmethod
    def show_status(message: str):
        """Show a status message with spinner."""
        return console.status(f"[bold green]{message}")
    
    @staticmethod
    def print_success(message: str):
        """Print a success message."""
        console.print(f"[bold green]✓[/bold green] {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message."""
        console.print(f"[yellow]⚠[/yellow] {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print an error message."""
        console.print(f"[bold red]Error:[/bold red] {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print an info message."""
        console.print(f"[cyan]{message}[/cyan]")
    
    @staticmethod
    def print_dim(message: str):
        """Print a dimmed message."""
        console.print(f"[dim]{message}[/dim]")
    
    @staticmethod
    def show_datacenters(datacenters: List[Dict]):
        """Display datacenters in a table."""
        if not datacenters:
            MarketUI.print_warning("No datacenters found.")
            return
        
        table = Table(title="Final Fantasy XIV Datacenters", show_header=True, header_style="bold magenta")
        table.add_column("Datacenter", style="cyan", no_wrap=True)
        table.add_column("Region", style="green")
        table.add_column("Worlds", style="yellow")
        
        # Sort datacenters by region and name
        sorted_dcs = sorted(datacenters, key=lambda x: (x.get('region', ''), x.get('name', '')))
        
        for dc in sorted_dcs:
            name = dc.get('name', 'N/A')
            region = dc.get('region', 'N/A')
            worlds = dc.get('worlds', [])
            worlds_str = f"{len(worlds)} worlds" if worlds else "No worlds"
            table.add_row(name, region, worlds_str)
        
        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(datacenters)} datacenters")
    
    @staticmethod
    def show_init_tracking_header(world: str, limit: int):
        """Display header for init tracking operation."""
        console.print(f"[cyan]Initializing tracking for {world}...[/cyan]")
        console.print(f"[dim]Rate limit: 2 requests/second (respecting API limits)[/dim]\n")
    
    @staticmethod
    def show_init_tracking_progress(total: int):
        """Create and return a progress bar for init tracking."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )
    
    @staticmethod
    def show_init_tracking_results(world: str, top_items: List[Dict], db_path: str):
        """Display results of init tracking operation."""
        console.print(f"[green]Found items. Analyzing sale velocities...[/green]\n")
        
        table = Table(title=f"Tracking Top {len(top_items)} Items on {world}", 
                     show_header=True, header_style="bold magenta")
        table.add_column("Item ID", style="cyan")
        table.add_column("Daily Sales", justify="right", style="green")
        table.add_column("Avg Price", justify="right", style="yellow")
        
        for item in top_items:
            table.add_row(
                str(item['item_id']),
                f"{item['velocity']:.2f}",
                f"{item['avg_price']:,.0f} gil"
            )
        
        console.print(table)
        MarketUI.print_success(f"Initialized tracking for {len(top_items)} items on {world}")
        MarketUI.print_dim(f"Database: {db_path}")
    
    @staticmethod
    def show_update_header(world: str, item_count: int):
        """Display header for update operation."""
        console.print(f"[cyan]Updating {item_count} items on {world}...[/cyan]")
        console.print(f"[dim]Rate limit: 2 requests/second • This will take ~{item_count} seconds[/dim]\n")
    
    @staticmethod
    def show_update_progress(total: int):
        """Create and return a progress bar for update operation."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )
    
    @staticmethod
    def show_update_results(successful: int, failed: int):
        """Display results of update operation."""
        MarketUI.print_success(f"Updated {successful} items")
        if failed > 0:
            MarketUI.print_warning(f"Failed to update {failed} items")
        MarketUI.print_dim("Tip: Schedule this command daily via cron/Task Scheduler")
    
    @staticmethod
    def show_top_items(world: str, items: List[Dict], format_time_func):
        """Display top items table."""
        if not items:
            MarketUI.print_warning(f"No data available for {world}. Run 'update' first.")
            return
        
        table = Table(title=f"Top {len(items)} Items by Sales Volume on {world}",
                     show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Item ID", style="yellow")
        table.add_column("Daily Sales", justify="right", style="green")
        table.add_column("Avg Price", justify="right", style="magenta")
        table.add_column("Last Updated", style="dim")
        
        for idx, item in enumerate(items, 1):
            time_str = format_time_func(item['last_updated'])
            
            table.add_row(
                str(idx),
                str(item['item_id']),
                f"{item['sale_velocity']:.2f}" if item['sale_velocity'] else "N/A",
                f"{item['average_price']:,.0f} gil" if item['average_price'] else "N/A",
                time_str
            )
        
        console.print(table)
        console.print(f"\n[dim]Snapshot date: {items[0]['snapshot_date']}[/dim]")
    
    @staticmethod
    def show_item_report_header(world: str, item_id: int, days_count: int):
        """Display header for item report."""
        console.print(f"\n[bold cyan]Item {item_id} on {world}[/bold cyan]")
        console.print(f"[dim]Historical data for the last {days_count} days[/dim]\n")
    
    @staticmethod
    def show_item_report_table(snapshots: List[Dict]):
        """Display item report table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date", style="cyan")
        table.add_column("Daily Sales", justify="right", style="green")
        table.add_column("Avg Price", justify="right", style="yellow")
        table.add_column("Min Price", justify="right")
        table.add_column("Max Price", justify="right")
        table.add_column("Listings", justify="right")
        
        for snapshot in reversed(snapshots):  # Show oldest to newest
            table.add_row(
                snapshot['snapshot_date'],
                f"{snapshot['sale_velocity']:.2f}" if snapshot['sale_velocity'] else "N/A",
                f"{snapshot['average_price']:,.0f}" if snapshot['average_price'] else "N/A",
                f"{snapshot['min_price']:,}" if snapshot['min_price'] else "N/A",
                f"{snapshot['max_price']:,}" if snapshot['max_price'] else "N/A",
                str(snapshot['total_listings']) if snapshot['total_listings'] else "0"
            )
        
        console.print(table)
    
    @staticmethod
    def show_trends(trends: Dict[str, float]):
        """Display trend information."""
        if 'velocity_change' in trends:
            velocity_change = trends['velocity_change']
            velocity_emoji = "📈" if velocity_change > 0 else "📉"
            console.print(f"\n{velocity_emoji} Sales velocity trend: {velocity_change:+.1f}%")
        
        if 'price_change' in trends:
            price_change = trends['price_change']
            price_emoji = "💰" if price_change > 0 else "💸"
            console.print(f"{price_emoji} Price trend: {price_change:+.1f}%")
    
    @staticmethod
    def show_tracked_summary(by_world: Dict[str, List[Dict]]):
        """Display tracked items summary."""
        if not by_world:
            MarketUI.print_warning("No items being tracked. Run 'init-tracking' first.")
            return
        
        console.print(f"\n[bold cyan]Tracked Items Summary[/bold cyan]\n")
        
        for world, items in sorted(by_world.items()):
            console.print(f"[bold]{world}[/bold]: {len(items)} items")
            console.print(f"[dim]Last updated: {items[0]['last_updated']}[/dim]\n")
    
    @staticmethod
    def exit_with_error(message: str, exit_code: int = 1):
        """Print error and exit."""
        MarketUI.print_error(message)
        sys.exit(exit_code)
